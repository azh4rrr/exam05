"""examshell: an offline clone of the 42 exam shell for Exam Rank 05."""

import argparse
import os
import random
import shutil
import signal
import sys
import threading
import time

import exercises
from grader import Context, GradeFailure, GraderError, CC, CXX

FOLDER = "exam_rank05"
MARKER = ".examshell_session"
WARNINGS = [3600, 1800, 900, 300, 60]

USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def color(code, text):
    return "\033[%sm%s\033[0m" % (code, text) if USE_COLOR else text


def green(t): return color("1;32", t)
def red(t): return color("1;31", t)
def yellow(t): return color("1;33", t)
def cyan(t): return color("1;36", t)
def bold(t): return color("1", t)


def fmt_duration(seconds):
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return "%dh %02dm %02ds" % (h, m, s)


class Session(object):
    def __init__(self, root, minutes, start_level, keep, seed, strict=False):
        self.strict = strict
        self.root = root
        self.subjects = os.path.join(root, "subjects")
        self.rendu = os.path.join(root, "rendu")
        self.traces = os.path.join(root, "traces")
        self.internal = os.path.join(root, ".grading")
        self.duration = minutes * 60
        self.keep = keep
        self.rng = random.Random(seed)
        self.levels = exercises.levels()
        self.level_ids = sorted(self.levels)
        self.level_pos = self.level_ids.index(start_level)
        self.current = None
        self.attempts = 0
        self.total_attempts = 0
        self.history = []          # (level, name, attempts, result)
        self.passed_levels = 0
        self.complete = False
        self.finished = False
        self.lock = threading.RLock()
        self.start = None
        self.end_at = None

    # ------------------------------------------------------------- lifecycle

    def setup(self):
        for d in (self.subjects, self.rendu, self.traces, self.internal):
            os.makedirs(d)
        with open(os.path.join(self.root, MARKER), "w") as fh:
            fh.write("created by examshell, removed when the exam ends\n")
        self.start = time.time()
        self.end_at = self.start + self.duration
        self.assign(self.pick(self.level_ids[self.level_pos]))

    def cleanup(self):
        if self.keep:
            print("Session folder kept (--keep): " + self.root)
            return
        if os.path.isfile(os.path.join(self.root, MARKER)):
            shutil.rmtree(self.root, ignore_errors=True)
            print("Session folder removed: " + self.root)

    def finish(self, reason, from_thread=False):
        with self.lock:
            if self.finished:
                return
            self.finished = True
            print()
            print(bold("=" * 60))
            print(bold("  Exam over: " + reason))
            if self.current and not self.complete:
                self.history.append((self.current.level, self.current.name,
                                     self.attempts, "not validated"))
            for level, name, attempts, result in self.history:
                tag = green(result) if result == "validated" else red(result)
                print("  Level %d  %-8s  %2d attempt(s)  %s" % (level, name, attempts, tag))
            print("  Final grade: " + bold("%d/100" % self.grade()))
            print("  Time used:   " + fmt_duration(time.time() - self.start))
            print(bold("=" * 60))
            self.cleanup()
            sys.stdout.flush()
        if from_thread:
            os._exit(0)

    def grade(self):
        return self.passed_levels * 100 // len(self.level_ids)

    def remaining(self):
        return self.end_at - time.time()

    def timer(self):
        warned = set(w for w in WARNINGS if w >= self.duration)
        while not self.finished:
            left = self.remaining()
            if left <= 0:
                sys.stdout.write("\n" + red("Time is up!") + "\n")
                self.finish("time is up", from_thread=True)
                return
            for w in WARNINGS:
                if left <= w and w not in warned:
                    warned.add(w)
                    sys.stdout.write("\n" + yellow("[examshell] %s left" % fmt_duration(left))
                                     + "\nexamshell> ")
                    sys.stdout.flush()
            time.sleep(1)

    # ---------------------------------------------------------- assignments

    def pick(self, level, exclude=None):
        pool = [e for e in self.levels[level] if e is not exclude]
        return self.rng.choice(pool)

    def assign(self, ex):
        self.current = ex
        self.attempts = 0
        dst = os.path.join(self.subjects, ex.name)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(ex.subject, dst, ignore=shutil.ignore_patterns(".DS_Store"))
        self.show_assignment()

    def show_assignment(self):
        ex = self.current
        print()
        print(bold("=" * 60))
        print("  Level %s  -  assignment: %s" % (bold(str(ex.level)), cyan(ex.name)))
        print("  Expected files : " + ex.expected)
        print("  Subject        : " + os.path.join(self.subjects, ex.name))
        print("  Turn in to     : " + os.path.join(self.rendu, ex.name) + "/  (create it)")
        print("  Time left      : " + fmt_duration(self.remaining()))
        print(bold("=" * 60))
        print("Type 'help' for the list of commands.")

    # ------------------------------------------------------------- commands

    def cmd_help(self, _):
        print("""Commands:
  grademe   grade the current assignment (files in rendu/<assignment>/)
  time      show how much time you have left
  change    swap the current assignment for another one of the same level
  status    show the current assignment, attempts and grade
  subject   print the subject of the current assignment
  end       end the exam (the session folder is deleted)
  help      show this help""")

    def cmd_time(self, _):
        left = self.remaining()
        print("Time left: %s   (elapsed %s, exam ends at %s)" % (
            bold(fmt_duration(left)), fmt_duration(time.time() - self.start),
            time.strftime("%H:%M:%S", time.localtime(self.end_at))))

    def cmd_status(self, _):
        print("Grade: %s   Time left: %s" % (bold("%d/100" % self.grade()),
                                             fmt_duration(self.remaining())))
        for level, name, attempts, result in self.history:
            print("  Level %d  %-8s  %2d attempt(s)  %s" % (level, name, attempts, result))
        if self.complete:
            print("  All levels validated. Type 'end' to finish.")
        else:
            print("  Level %d  %-8s  %2d attempt(s)  in progress" % (
                self.current.level, self.current.name, self.attempts))
            print("  Rendu: " + os.path.join(self.rendu, self.current.name))

    def cmd_subject(self, _):
        if self.complete:
            print("Nothing left to do. Type 'end' to finish.")
            return
        print(self.current.subject_text())

    def cmd_change(self, _):
        if self.complete:
            print("All levels are already validated.")
            return
        level = self.current.level
        if len(self.levels[level]) < 2:
            print("There is no other assignment in level %d." % level)
            return
        old = self.current
        self.history.append((level, old.name, self.attempts, "changed"))
        new = self.pick(level, exclude=old)
        print("Changing %s -> %s" % (old.name, new.name))
        self.assign(new)

    def cmd_end(self, _):
        if not self.keep:
            print(yellow("This will end the exam and delete " + self.root))
        if confirm("Are you sure you want to end the exam? [y/N] "):
            self.finish("ended by you")
            return True
        return False

    def cmd_grademe(self, _):
        if self.complete:
            print("You already validated every level. Type 'end' to finish.")
            return
        ex = self.current
        self.attempts += 1
        self.total_attempts += 1
        print("Grading %s (attempt %d), please wait..." % (bold(ex.name), self.attempts))
        work = os.path.join(self.internal, "attempt%d" % self.total_attempts)
        cache = os.path.join(self.internal, "ref-cache", ex.name)
        if not os.path.isdir(cache):
            os.makedirs(cache)
        ctx = Context(ex, os.path.join(self.rendu, ex.name), work, cache,
                      random.Random(self.rng.random()), self.strict)
        ctx.log("examshell trace - assignment %s - attempt %d - %s" % (
            ex.name, self.attempts, time.strftime("%Y-%m-%d %H:%M:%S")))
        ok, reason = False, None
        try:
            ex.grade(ctx)
            ok = True
        except GradeFailure as e:
            reason = e.reason
        except GraderError as e:
            print(red("Internal grader error, this attempt does not count:"))
            print(str(e))
            self.attempts -= 1
            return
        except KeyboardInterrupt:
            print(yellow("\nGrading interrupted, this attempt does not count."))
            self.attempts -= 1
            return
        finally:
            shutil.rmtree(work, ignore_errors=True)
        ctx.log()
        ctx.log("RESULT: " + ("SUCCESS" if ok else "FAILURE - " + reason))
        trace = os.path.join(self.traces, "%02d-%s.trace" % (self.total_attempts, ex.name))
        with open(trace, "w") as fh:
            fh.write("\n".join(ctx.trace) + "\n")
        if ok:
            print(green(">>>>>>>>>> SUCCESS <<<<<<<<<<"))
            print("%d tests passed." % ctx.test_count)
            self.history.append((ex.level, ex.name, self.attempts, "validated"))
            self.passed_levels += 1
            self.level_pos += 1
            print("Current grade: " + bold("%d/100" % self.grade()))
            if self.level_pos >= len(self.level_ids):
                self.complete = True
                print(green("Congratulations, you validated every level!"))
                print("Type 'end' to finish the exam.")
            else:
                self.assign(self.pick(self.level_ids[self.level_pos]))
        else:
            print(red(">>>>>>>>>> FAILURE <<<<<<<<<<"))
            print("Reason: " + reason)
            print("Trace:  " + trace)
            print("Fix your code and type 'grademe' again (same assignment).")

    COMMANDS = {
        "help": cmd_help, "time": cmd_time, "status": cmd_status, "subject": cmd_subject,
        "change": cmd_change, "end": cmd_end, "grademe": cmd_grademe,
    }

    def loop(self):
        while not self.finished:
            try:
                line = input("examshell> ")
            except KeyboardInterrupt:
                print("\n(type 'end' to leave the exam)")
                continue
            except EOFError:
                if sys.stdin.isatty():
                    print("\n(type 'end' to leave the exam)")
                    continue
                self.finish("input closed")
                return
            words = line.split()
            if not words:
                continue
            fn = self.COMMANDS.get(words[0].lower())
            if fn is None:
                print("Unknown command '%s'. Type 'help'." % words[0])
                continue
            with self.lock:
                if self.finished:
                    return
            if fn(self, words[1:]) is True:
                return


def confirm(prompt):
    try:
        return input(prompt).strip().lower() in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(prog="examshell",
                                     description="Offline clone of the 42 exam shell (Exam Rank 05).")
    parser.add_argument("-t", "--time", type=int, default=180, metavar="MINUTES",
                        help="exam duration in minutes (default: 180)")
    parser.add_argument("-l", "--level", type=int, default=None,
                        help="level to start from (default: the first one)")
    parser.add_argument("--keep", action="store_true",
                        help="do not delete the session folder when the exam ends")
    parser.add_argument("--strict", action="store_true",
                        help="add stricter hidden tests than the real exam (const, chaining, ...)")
    parser.add_argument("--seed", type=int, default=None, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    levels = sorted(exercises.levels())
    start_level = levels[0] if args.level is None else args.level
    if start_level not in levels:
        parser.error("level must be one of: " + ", ".join(map(str, levels)))
    if args.time <= 0:
        parser.error("time must be positive")

    missing = [c for c in (CC, CXX) if not shutil.which(c)]
    if missing:
        print(red("Compiler not found: " + ", ".join(missing)))
        if sys.platform == "darwin":
            print("Install the command line tools with: xcode-select --install")
        return 1

    root = os.path.join(os.getcwd(), FOLDER)
    if os.path.exists(root):
        if not os.path.isfile(os.path.join(root, MARKER)):
            print(red("%s already exists and was not created by examshell, refusing to touch it."
                      % root))
            return 1
        print(yellow("A previous exam session folder exists: " + root))
        if not confirm("Delete it and start a new exam? [y/N] "):
            return 1
        shutil.rmtree(root)

    session = Session(root, args.time, start_level, args.keep, args.seed, args.strict)

    def on_signal(signum, _frame):
        session.finish("terminated (signal %d)" % signum, from_thread=True)

    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGHUP, on_signal)

    print(bold("examshell - Exam Rank 05 (offline clone)"))
    print("Exam duration: %s. Work in another terminal, then come back here." %
          fmt_duration(args.time * 60))
    if args.strict:
        print(yellow("Strict mode: extra hidden tests that the real exam does not run."))
    session.setup()
    threading.Thread(target=session.timer, daemon=True).start()
    try:
        session.loop()
    finally:
        if not session.finished:
            session.finish("examshell stopped")
    return 0
