"""Exercise definitions: what each assignment gets tested with.

Level 1 expected outputs come from compiling the reference solution (grademe/exercises/<ex>/ref)
with the same mains as the student. Level 2 expected outputs come from the Python references below.
"""

import os
import shlex

from grader import GradeFailure, run

GRADEME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(GRADEME)
DATA = os.path.join(GRADEME, "exercises")


def subject_dir(level, name):
    return os.path.join(REPO, "Level %d" % level, name, "subject")


class Exercise(object):
    name = None
    level = None
    expected = None          # what the subject calls "Expected files"

    @property
    def subject(self):
        return subject_dir(self.level, self.name)

    def subject_text(self):
        for f in sorted(os.listdir(self.subject)):
            if "subject" in f and f.endswith(".txt"):
                with open(os.path.join(self.subject, f)) as fh:
                    return fh.read()
        return ""

    def grade(self, ctx):
        raise NotImplementedError


# ============================================================================ Level 1

class CppExercise(Exercise):
    files = []               # files taken from the rendu
    provided = []            # subject files the grader supplies itself
    value_mains = []         # the subject main's statements with other values (always run)
    strict_mains = []        # stricter hidden mains, only with `examshell --strict`

    @property
    def expected(self):
        return ", ".join(self.files)

    def provided_paths(self):
        return [os.path.join(self.subject, f) for f in self.provided]

    def mains(self, strict):
        out = [("subject main", os.path.join(self.subject, "main.cpp"))]
        for m in self.value_mains + (self.strict_mains if strict else []):
            out.append(("hidden main " + m, os.path.join(DATA, self.name, "mains", m)))
        return out

    def runs(self, main_index, rng):
        """Argument lists used to run the program built with mains()[main_index]."""
        return [[]]

    def grade(self, ctx):
        ctx.check_expected_files(self.files)
        ref = os.path.join(DATA, self.name, "ref")
        for i, (label, main) in enumerate(self.mains(ctx.strict)):
            tag = "main%d" % i
            ref_bin = ctx.build_cpp(tag, self.files, self.provided_paths(), main, ref_dir=ref)
            ctx.log()
            ctx.log("==== compiling your files with the %s" % label)
            stud_bin = ctx.build_cpp(tag, self.files, self.provided_paths(), main)
            for args in self.runs(i, ctx.rng):
                expected = run([ref_bin] + args).stdout
                got = run([stud_bin] + args, cwd=os.path.dirname(stud_bin))
                ctx.expect(("%s %s" % (label, " ".join(args))).strip(),
                           " ".join(["./a.out"] + [shlex.quote(a) for a in args]),
                           got, expected)


class Vect2(CppExercise):
    name = "vect2"
    level = 1
    files = ["vect2.cpp", "vect2.hpp"]
    value_mains = ["main_values1.cpp", "main_values2.cpp"]
    strict_mains = ["strict_extra.cpp"]


class Bigint(CppExercise):
    name = "bigint"
    level = 1
    files = ["bigint.cpp", "bigint.hpp"]
    value_mains = ["main_values1.cpp", "main_values2.cpp", "main_values3.cpp"]
    strict_mains = ["strict_big.cpp"]


class Polyset(CppExercise):
    name = "polyset"
    level = 1
    files = ["searchable_array_bag.cpp", "searchable_array_bag.hpp",
             "searchable_tree_bag.cpp", "searchable_tree_bag.hpp", "set.cpp", "set.hpp"]
    provided = ["bag.hpp", "searchable_bag.hpp", "array_bag.cpp", "array_bag.hpp",
                "tree_bag.cpp", "tree_bag.hpp"]
    strict_mains = ["strict_extra.cpp"]

    def runs(self, main_index, rng):
        if main_index != 0:
            return [[]]
        fixed = [["1"], ["3", "1", "2"], ["5", "3", "8", "1", "4", "7", "9", "2", "6"],
                 ["3", "3", "3", "1", "1"], ["-5", "0", "5", "-10", "10", "0"],
                 ["42", "-42", "0", "2147483647", "-2147483647"], []]
        rand = [[str(rng.randint(-50, 50)) for _ in range(rng.randint(10, 40))]
                for _ in range(3)]
        return fixed + rand


# ============================================================================ Level 2

def life_ref(cmds, width, height, iterations):
    board = [[0] * width for _ in range(height)]
    x = y = 0
    pen = False
    for c in cmds.decode("latin-1"):
        if c == "w" and y > 0:
            y -= 1
        elif c == "s" and y < height - 1:
            y += 1
        elif c == "a" and x > 0:
            x -= 1
        elif c == "d" and x < width - 1:
            x += 1
        elif c == "x":
            pen = not pen
        if pen:
            board[y][x] = 1
    for _ in range(iterations):
        nxt = [[0] * width for _ in range(height)]
        for i in range(height):
            for j in range(width):
                n = 0
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        if (di or dj) and 0 <= i + di < height and 0 <= j + dj < width:
                            n += board[i + di][j + dj]
                nxt[i][j] = 1 if n == 3 or (board[i][j] and n == 2) else 0
        board = nxt
    return "".join("".join("O" if v else " " for v in row) + "\n" for row in board).encode()


class Life(Exercise):
    name = "life"
    level = 2
    expected = "*.c *.h"
    allowed = ["atoi", "read", "putchar", "malloc", "calloc", "realloc", "free"]

    def cases(self, rng):
        glider = b"dxdxsxsaxa"   # a glider in the top left corner
        cases = [
            (b"sdxddssaaww\n", 5, 5, 0),
            (b"sdxssdswdxddddsxaadwxwdxwaa\n", 10, 6, 0),
            (b"dxss\n", 3, 3, 0),
            (b"dxss\n", 3, 3, 1),
            (b"dxss\n", 3, 3, 2),
            (b"", 5, 3, 0),
            (b"", 4, 4, 7),
            (b"x", 1, 1, 0),
            (b"x", 1, 1, 1),
            (b"xwwwwaaaa", 4, 4, 0),
            (b"xdddddddddddddddd", 6, 1, 0),
            (b"xdddddddddddddddd", 6, 1, 1),
            (b"xssssssssssss", 1, 5, 2),
            (b"sxdd", 4, 4, 0),
            (b"sxdd", 4, 4, 1),
            (b"sxdd", 4, 4, 9),
            (b"dxsdxwx", 4, 4, 0),
            (b"dxsdxwx", 4, 4, 3),
            (b"xdsa", 6, 6, 4),
            (glider, 12, 12, 0),
            (glider, 12, 12, 4),
            (glider, 12, 12, 20),
            (glider, 12, 12, 47),
            (b"sdxqqddz ssy\taa\nww", 5, 5, 0),
            (b"sdxqqddz ssy\taa\nww", 5, 5, 3),
            (b"WASDxddddSSSS", 8, 4, 0),
            (b"xdxdxdxdxdxd", 13, 2, 0),
            (b"xdxdxdxdxdxd", 13, 2, 1),
        ]
        for _ in range(6):
            w, h = rng.randint(1, 40), rng.randint(1, 25)
            cmds = "".join(rng.choice("wasdwasdwasdx") for _ in range(rng.randint(0, 400)))
            cases.append((cmds.encode(), w, h, rng.randint(0, 40)))
        return cases

    def grade(self, ctx):
        binary = ctx.build_c()
        bad = ctx.forbidden_symbols(binary, self.allowed)
        if bad:
            ctx.log("warning: your binary uses functions outside the allowed list: "
                    + ", ".join(bad))
        for cmds, w, h, it in self.cases(ctx.rng):
            args = [str(w), str(h), str(it)]
            res = run([binary] + args, stdin=cmds)
            ctx.expect("life %s" % " ".join(args),
                       "printf %s | ./life %s | cat -e" % (shlex.quote(cmds.decode("latin-1")),
                                                          " ".join(args)),
                       res, life_ref(cmds, w, h, it))


ERR_MAP = b"Error: invalid map\n"


def bsq_ref(data):
    nl = data.find(b"\n")
    if nl < 0:
        return ERR_MAP
    header = data[:nl]
    if len(header) < 4:
        return ERR_MAP
    count, chars = header[:-3], header[-3:]
    empty, obst, full = chars[0], chars[1], chars[2]
    if not count.isdigit() or int(count) <= 0:
        return ERR_MAP
    if len(set(chars)) != 3 or any(c < 32 or c > 126 for c in chars):
        return ERR_MAP
    body = data[nl + 1:]
    if not body.endswith(b"\n"):
        return ERR_MAP
    lines = body[:-1].split(b"\n")
    if len(lines) != int(count) or not lines[0]:
        return ERR_MAP
    width = len(lines[0])
    for line in lines:
        if len(line) != width or any(c != empty and c != obst for c in line):
            return ERR_MAP
    best, bi, bj = 0, 0, 0
    prev = [0] * width
    for i, line in enumerate(lines):
        cur = [0] * width
        for j in range(width):
            if line[j] == obst:
                continue
            cur[j] = 1 if i == 0 or j == 0 else 1 + min(prev[j], cur[j - 1], prev[j - 1])
            if cur[j] > best:
                best, bi, bj = cur[j], i, j
        prev = cur
    rows = [bytearray(l) for l in lines]
    for i in range(bi - best + 1, bi + 1):
        for j in range(bj - best + 1, bj + 1):
            rows[i][j] = full
    return b"".join(bytes(r) + b"\n" for r in rows)


def random_map(rng, rows, cols, density, chars=".ox"):
    lines = ["%d%s" % (rows, chars)]
    for _ in range(rows):
        lines.append("".join(chars[1] if rng.random() < density else chars[0]
                             for _ in range(cols)))
    return ("\n".join(lines) + "\n").encode()


class Bsq(Exercise):
    name = "bsq"
    level = 2
    expected = "*.c *.h"
    allowed = ["malloc", "calloc", "realloc", "free", "fopen", "fclose", "getline", "fscanf",
               "fputs", "fprintf", "printf", "stdout", "stdin"]

    def cases(self, rng):
        example = (b"9.ox\n"
                   b"...........................\n"
                   b"....o......................\n"
                   b"............o..............\n"
                   b"...........................\n"
                   b"....o......................\n"
                   b"...............o...........\n"
                   b"...........................\n"
                   b"......o..............o.....\n"
                   b"..o.......o................\n")
        valid = [
            ("subject example", example),
            ("single empty cell", b"1.ox\n.\n"),
            ("single obstacle", b"1.ox\no\n"),
            ("only obstacles", b"3.ox\nooo\nooo\nooo\n"),
            ("only empty", b"4.ox\n......\n......\n......\n......\n"),
            ("one line", b"1.ox\n....o...\n"),
            ("one column", b"5.ox\n.\n.\no\n.\n.\n"),
            ("tie: highest wins", b"4.ox\no...\no...\n...o\n...o\n"),
            ("biggest square at the bottom", b"5.ox\no...\no...\n...o\n...o\n....\n"),
            ("tie: leftmost wins", b"2.ox\n..o..\n..o..\n"),
            ("tie: higher beats more left", b"4.ox\no..o\no..o\n..oo\n..oo\n"),
            ("other characters", b"4 #@\n  # \n    \n#   \n    \n"),
            ("digit as character", b"3.9x\n...\n9..\n...\n"),
            ("multi-digit line count", b"12abc\n" + b"aaaaaaa\n" * 5 + b"aabaaaa\n" + b"aaaaaaa\n" * 6),
            ("letters as characters", b"3ox.\noxo\nooo\nxoo\n"),
            ("leading zero line count", b"03.ox\n..\n..\n..\n"),
        ]
        invalid = [
            ("empty file", b""),
            ("no newline at all", b"1.ox"),
            ("header only", b"3.ox\n"),
            ("fewer lines than announced", b"3.ox\n...\n...\n"),
            ("more lines than announced", b"2.ox\n...\n...\n...\n"),
            ("lines of different length", b"3.ox\n...\n....\n...\n"),
            ("unknown character in map", b"3.ox\n...\n.a.\n...\n"),
            ("two identical characters", b"3..x\n...\n...\n...\n"),
            ("empty == full", b"3.o.\n...\n...\n...\n"),
            ("missing a character", b"3.o\n...\n...\n...\n"),
            ("extra character on first line", b"3.oxy\n...\n...\n...\n"),
            ("zero lines", b"0.ox\n"),
            ("no line count", b".ox\n...\n"),
            ("negative line count", b"-1.ox\n...\n"),
            ("last line without newline", b"2.ox\n...\n..."),
            ("empty lines", b"2.ox\n\n\n"),
            ("line count is not a number", b"2a.ox\n...\n...\n"),
        ]
        cases = [(n, d, True) for n, d in valid] + [(n, d, False) for n, d in invalid]
        for k in range(5):
            r, c = rng.randint(1, 35), rng.randint(1, 70)
            cases.append(("random %dx%d" % (r, c),
                          random_map(rng, r, c, rng.choice([0.02, 0.05, 0.1, 0.3])), True))
        cases.append(("random with '-' 'X' '#'", random_map(rng, 20, 40, 0.07, "-X#"), True))
        cases.append(("big 400x400", random_map(rng, 400, 400, 0.002), True))
        return cases

    def grade(self, ctx):
        binary = ctx.build_c()
        bad = ctx.forbidden_symbols(binary, self.allowed)
        if bad:
            ctx.log("warning: your binary uses functions outside the allowed list: "
                    + ", ".join(bad))
        tests_dir = os.path.join(ctx.work, "maps")
        os.makedirs(tests_dir)
        cases = self.cases(ctx.rng)
        for idx, (title, data, _) in enumerate(cases):
            path = os.path.join(tests_dir, "map%02d" % idx)
            with open(path, "wb") as fh:
                fh.write(data)
            res = run([binary, path])
            ctx.expect(title, "./bsq map  (map is shown below)", res, bsq_ref(data),
                       input_display=_show_map(data))
        # the same program must also read the map on stdin
        on_stdin = ["subject example", "only empty", "fewer lines than announced", "big 400x400"]
        for title, data, _ in [c for c in cases if c[0] in on_stdin]:
            res = run([binary], stdin=data)
            ctx.expect(title + " (stdin)", "./bsq < map  (map is shown below)", res,
                       bsq_ref(data), input_display=_show_map(data))
        res = run([binary, os.path.join(tests_dir, "this_file_does_not_exist")])
        ctx.expect("file that does not exist", "./bsq this_file_does_not_exist", res,
                   b"Error: <a meaningful message>\n",
                   ok=lambda r: (r.stdout + r.stderr).startswith(b"Error"))


def _show_map(data):
    from grader import cat_e
    return cat_e(data, 40)


ALL = [Vect2(), Bigint(), Polyset(), Life(), Bsq()]


def levels():
    out = {}
    for ex in ALL:
        out.setdefault(ex.level, []).append(ex)
    return out
