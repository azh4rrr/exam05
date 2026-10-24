"""Compile / run / compare machinery shared by every exercise."""

import os
import shlex
import shutil
import signal
import subprocess
import threading

RUN_TIMEOUT = 10          # seconds allowed for one run of the student's program
COMPILE_TIMEOUT = 120
OUTPUT_CAP = 8 * 1024 * 1024

CC = os.environ.get("EXAM_CC", "cc")
CXX = os.environ.get("EXAM_CXX", "c++")
CFLAGS = shlex.split(os.environ.get("EXAM_CFLAGS", "-Wall -Wextra -Werror"))
# The real exam accepts C++11 calls (std::to_string) and code with warnings, so warnings
# stay warnings by default; --strict turns them into errors and forces C++98.
CXXFLAGS = "-Wall -Wextra"
CXXFLAGS_STRICT = "-Wall -Wextra -Werror -std=c++98"


def cxxflags(strict):
    return shlex.split(os.environ.get("EXAM_CXXFLAGS", CXXFLAGS_STRICT if strict else CXXFLAGS))


class GradeFailure(Exception):
    """The student's submission failed. `reason` is the one-liner shown in the shell."""

    def __init__(self, reason):
        Exception.__init__(self, reason)
        self.reason = reason


class GraderError(Exception):
    """Something is wrong with the grader itself (reference does not build, ...)."""


class Result(object):
    def __init__(self, stdout, stderr, returncode, timed_out, truncated):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.timed_out = timed_out
        self.truncated = truncated

    def crash(self):
        """Human readable description of an abnormal termination, or None."""
        if self.timed_out:
            return "Timeout (more than %ds)" % RUN_TIMEOUT
        if self.truncated:
            return "Output too big (more than %d bytes), killed" % OUTPUT_CAP
        if self.returncode is not None and self.returncode < 0:
            try:
                name = signal.Signals(-self.returncode).name
            except ValueError:
                name = "signal %d" % -self.returncode
            pretty = {"SIGSEGV": "Segmentation fault", "SIGBUS": "Bus error",
                      "SIGABRT": "Abort", "SIGFPE": "Floating point exception"}
            return "%s (%s)" % (pretty.get(name, "Killed by signal"), name)
        return None


def run(cmd, cwd=None, stdin=None, timeout=RUN_TIMEOUT, cap=OUTPUT_CAP):
    """Run cmd, feeding `stdin` (bytes or None) and capturing at most `cap` bytes of output."""
    proc = subprocess.Popen(cmd, cwd=cwd,
                            stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outputs = {"out": [], "err": []}
    truncated = [False]

    def reader(stream, key):
        total = 0
        while True:
            chunk = stream.read(65536)
            if not chunk:
                break
            total += len(chunk)
            if total > cap:
                truncated[0] = True
                try:
                    proc.kill()
                except OSError:
                    pass
                break
            outputs[key].append(chunk)
        stream.close()

    def writer():
        try:
            proc.stdin.write(stdin)
        except (BrokenPipeError, OSError):
            pass
        try:
            proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass

    threads = [threading.Thread(target=reader, args=(proc.stdout, "out")),
               threading.Thread(target=reader, args=(proc.stderr, "err"))]
    if stdin is not None:
        threads.append(threading.Thread(target=writer))
    for t in threads:
        t.daemon = True
        t.start()
    timed_out = False
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        proc.wait()
    for t in threads:
        t.join(2)
    return Result(b"".join(outputs["out"]), b"".join(outputs["err"]),
                  proc.returncode, timed_out, truncated[0])


def cat_e(data, max_lines=60):
    """Render bytes like `cat -e` so trailing spaces and missing newlines are visible."""
    if not data:
        return "    (empty)\n"
    text = data.decode("utf-8", "replace")
    lines = text.split("\n")
    out = []
    for i, line in enumerate(lines):
        last = i == len(lines) - 1
        if last and line == "":
            break
        if len(out) >= max_lines:
            out.append("    ... (%d more lines)" % (len(lines) - max_lines))
            break
        out.append("    " + line + ("" if last else "$"))
    if lines[-1] != "":
        out[-1] += "   <- no newline at end"
    return "\n".join(out) + "\n"


def first_difference(expected, got):
    exp = expected.decode("utf-8", "replace").split("\n")
    act = got.decode("utf-8", "replace").split("\n")
    for i in range(max(len(exp), len(act))):
        e = exp[i] if i < len(exp) else None
        a = act[i] if i < len(act) else None
        if e != a:
            def show(s):
                return "(nothing)" if s is None else repr(s)
            return "first difference at line %d:\n    expected: %s\n    yours:    %s\n" % (
                i + 1, show(e), show(a))
    return ""


class Context(object):
    """Holds the state of one grading attempt and the trace that goes with it."""

    def __init__(self, exercise, rendu_dir, work_dir, cache_dir, rng, strict=False):
        self.exercise = exercise
        self.strict = strict
        self.rendu = rendu_dir
        self.work = work_dir
        self.cache = cache_dir
        self.rng = rng
        self.trace = []
        self.test_count = 0
        os.makedirs(self.work)

    def log(self, text=""):
        self.trace.append(text)

    # ------------------------------------------------------------------ files

    def check_rendu_dir(self):
        if not os.path.isdir(self.rendu):
            self.log("Directory not found: " + self.rendu)
            raise GradeFailure("no directory rendu/%s" % os.path.basename(self.rendu))

    def check_expected_files(self, names):
        self.check_rendu_dir()
        missing = [n for n in names if not os.path.isfile(os.path.join(self.rendu, n))]
        self.log("Expected files: " + ", ".join(names))
        if missing:
            self.log("Missing in %s: %s" % (self.rendu, ", ".join(missing)))
            raise GradeFailure("missing file(s): " + ", ".join(missing))

    def student_sources(self, exts):
        """Every top-level file of the rendu with one of the given extensions."""
        if not os.path.isdir(self.rendu):
            return []
        return sorted(f for f in os.listdir(self.rendu)
                      if os.path.isfile(os.path.join(self.rendu, f))
                      and os.path.splitext(f)[1] in exts)

    # -------------------------------------------------------------- compiling

    def _compile(self, compiler, flags, build_dir, sources, out, who):
        cmd = [compiler] + flags + sources + ["-o", out]
        res = run(cmd, cwd=build_dir, timeout=COMPILE_TIMEOUT)
        if res.returncode != 0 or res.timed_out:
            msg = (res.stdout + res.stderr).decode("utf-8", "replace")
            if who == "ref":
                raise GraderError("reference solution failed to build:\n$ %s\n%s"
                                  % (" ".join(cmd), msg))
            self.log("$ " + " ".join(cmd))
            self.log(msg.rstrip())
            raise GradeFailure("compilation error")
        if who == "student":
            self.log("$ " + " ".join(cmd) + "   -> OK")
            warnings = (res.stdout + res.stderr).decode("utf-8", "replace").strip()
            if warnings:
                self.log("compiler warnings (not fatal):")
                self.log(warnings)
        return os.path.join(build_dir, out)

    def build_cpp(self, tag, student_files, provided, main, ref_dir=None):
        """Build `student_files` from the rendu (or the reference in `ref_dir`) together
        with the `provided` subject files and the test `main`."""
        who = "ref" if ref_dir else "student"
        base = self.cache if ref_dir else self.work
        build_dir = os.path.join(base, "%s-%s" % (who, tag))
        binary = os.path.join(build_dir, "prog")
        if ref_dir and os.path.exists(binary):
            return binary
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        os.makedirs(build_dir)
        src_dir = ref_dir or self.rendu
        for name in student_files:
            shutil.copy(os.path.join(src_dir, name), build_dir)
        for path in provided:
            shutil.copy(path, build_dir)
        shutil.copy(main, os.path.join(build_dir, "main.cpp"))
        sources = sorted(set(f for f in os.listdir(build_dir) if f.endswith(".cpp")))
        flags = cxxflags(True) if ref_dir else cxxflags(self.strict)
        return self._compile(CXX, flags, build_dir, sources, "prog", who)

    def build_c(self, tag="main"):
        self.check_rendu_dir()
        sources = self.student_sources((".c",))
        headers = self.student_sources((".h",))
        if not sources:
            self.log("No .c file found in " + self.rendu)
            raise GradeFailure("no .c file in your rendu")
        build_dir = os.path.join(self.work, "student-" + tag)
        os.makedirs(build_dir)
        for name in sources + headers:
            shutil.copy(os.path.join(self.rendu, name), build_dir)
        return self._compile(CC, CFLAGS, build_dir, sources, "prog", "student")

    def forbidden_symbols(self, binary, allowed):
        """Best effort: list imported functions that are not in `allowed`.
        Only reported as a warning, compilers replace some calls (printf -> puts...)."""
        nm = shutil.which("nm")
        if not nm:
            return []
        res = run([nm, "-u", binary], timeout=30)
        if res.returncode != 0:
            return []
        ignore = set(["puts", "putc", "fwrite", "fputc", "putchar_unlocked", "memset", "memcpy",
                      "memmove", "bzero", "exit", "abort", "dyld_stub_binder", "strlen",
                      "__chkstk_darwin", "__stack_chk_fail", "__stack_chk_guard", "__error",
                      "__libc_start_main", "__cxa_finalize", "__gmon_start__", "__stdoutp",
                      "__stdinp", "__memcpy_chk", "__memset_chk", "__memmove_chk",
                      "__getdelim", "getdelim", "_IO_putc", "__overflow", "__fprintf_chk",
                      "__printf_chk", "__stack_chk_guard", "_ITM_deregisterTMCloneTable",
                      "_ITM_registerTMCloneTable", "__isoc99_fscanf", "__isoc23_fscanf",
                      "__assert_rtn", "__assert_fail", "__isoc23_strtol", "__isoc99_sscanf"])
        found = []
        for line in res.stdout.decode("utf-8", "replace").split("\n"):
            parts = line.split()
            if not parts:
                continue
            sym = parts[-1].split("@")[0]
            if sym in ignore or sym.startswith("_ITM_"):
                continue
            if sym.startswith("_") and not sym.startswith("__"):
                sym = sym[1:]          # macOS prefixes C symbols with '_'
            elif sym.startswith("___"):
                sym = sym[1:]
            if sym and sym not in allowed and sym not in ignore:
                found.append(sym)
        return sorted(set(found))

    # ---------------------------------------------------------------- testing

    def expect(self, title, display, res, expected, input_display=None, ok=None):
        """Compare one run with the expected stdout. `ok` may override the comparison."""
        self.test_count += 1
        header = "---- test %d: %s" % (self.test_count, title)
        crash = res.crash()
        passed = crash is None and (ok(res) if ok else res.stdout == expected)
        if passed:
            self.log(header + "  [OK]")
            return
        self.log(header + "  [KO]")
        self.log("$ " + display)
        if input_display is not None:
            self.log("input:")
            self.log(input_display.rstrip("\n"))
        if crash:
            self.log("your program: " + crash)
        self.log("expected output (cat -e):")
        self.log(cat_e(expected).rstrip("\n"))
        self.log("your output (cat -e):")
        self.log(cat_e(res.stdout).rstrip("\n"))
        if res.stderr:
            self.log("your stderr:")
            self.log(cat_e(res.stderr, 15).rstrip("\n"))
        if not crash and not ok:
            self.log(first_difference(expected, res.stdout).rstrip("\n"))
        raise GradeFailure("test %d (%s): %s" % (self.test_count, title,
                                                 crash or "wrong output"))
