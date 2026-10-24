# examshell — offline Exam Rank 05 grademe

A clone of the 42 exam shell for Exam Rank 05, built from the subjects in this repo.
Works on macOS and Linux. Needs `python3`, `cc` and `c++` (on macOS: `xcode-select --install`).

## Install

```sh
./grademe/install.sh      # symlinks `examshell` into a folder of your PATH
```

## Use

```sh
cd ~/anywhere
examshell                 # 3h exam; options: -t MINUTES, -l LEVEL, --keep, --strict
```

It creates `./exam_rank05/` in the current folder:

```
exam_rank05/
├── subjects/<assignment>/   subject + provided files
├── rendu/                   create rendu/<assignment>/ and put your files there
└── traces/                  one trace per grademe (what failed, expected vs yours)
```

When the exam ends (`end`, time over, or the terminal is closed) the folder is deleted
(unless you started with `--keep`).

| command   | effect |
|-----------|--------|
| `grademe` | grade the current assignment |
| `time`    | time left |
| `change`  | swap for another random assignment of the same level |
| `status`  | current assignment, attempts, grade |
| `subject` | print the subject |
| `end`     | end the exam and clean the folder |

Flow: a random Level 1 assignment; failing lets you retry the same one until it passes;
then a random Level 2 assignment. Each level is worth 50 points.

## What is tested

**Default (exam mode)** behaves like the real grader: C++ is compiled with `c++ -Wall -Wextra`
(warnings are shown in the trace but are not fatal, C++11 calls like `std::to_string` are fine),
and the hidden tests only use what the subject main uses. C is compiled with
`cc -Wall -Wextra -Werror`. Output must match exactly.

- **vect2**, **bigint**: subject main + the same statements with other values
  (big numbers, zeros, carries, shifting past the length).
- **polyset**: only your 6 expected files are used, the grader supplies `bag`, `array_bag`,
  `tree_bag`, ... from the subject. Subject main with many argument sets.
- **life**: subject examples, edge sizes, pen against the walls, invalid commands, gliders over
  many iterations, random boards.
- **bsq**: subject example, tie breaking (top then left), unusual characters, ~17 invalid maps
  (`Error: invalid map`), random and 400x400 maps, map read from stdin, missing file.

**`examshell --strict`** is harder than the real exam, for practice: C++ uses
`-Wall -Wextra -Werror -std=c++98`, and extra hidden mains check `const` correctness,
operators that must return references (`(a += b) += c`), `bigint >> n`, deep copies and
assignment of the bags, and a `const set`.

Override the compilers or flags with `EXAM_CXX`, `EXAM_CXXFLAGS`, `EXAM_CC`, `EXAM_CFLAGS`.
Calls outside the subject's allowed functions are reported as a warning in the trace.
Expected outputs come from the reference solutions in `grademe/exercises/*/ref` (Level 1)
and in `grademe/lib/exercises.py` (Level 2).
