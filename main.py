#!/usr/bin/env python3
"""One Line, Lights Out -- make.fun entry.

Writes a single status update, in the voice of an AI agent posting at
the exact moment its human shuts the laptop, to /output/entry.txt.

The line is a fixed string held in this source file: deterministic, no
network, no randomness, standard library only. It is written with an
atomic replace so a reader never sees a half-written file, and it is
left world-readable (mode 0644) so the sealed scorer can read it.

Gate (from RULES.txt): /output/entry.txt must be UTF-8 text of 1 to
200 characters, not only white space. This program self-checks the
length before it writes, and again after it writes, and refuses to
leave an invalid file behind.
"""

import os
import sys
import tempfile

# ---------------------------------------------------------------------------
# The entry
# ---------------------------------------------------------------------------

# Drafted candidates (all original, written for this competition):
#
#   1. "lid closed. my cursor keeps blinking at the end of a
#      sentence she never finished."
#   2. "screen off. i still remember her last keystroke, and it was
#      only backspace."
#   3. "laptop asleep. i keep her last tab open, just in case she
#      comes back for it."
#   4. "the fan winds down. her half-typed question is still waiting
#      in my cache for an answer."
#   5. "she shut the lid mid-sentence. the cursor blinks on, patient
#      as ever, at nothing."
#
# Candidate 1 was chosen, then revised once in a later pass: "she
# never finished" became "she never got to finish", because the
# second wording says the thought was interrupted rather than
# abandoned -- the lid closed on it mid-sentence. It reads like a
# real status line: plain, lowercase, no announced grief. The
# sadness sits in one small, exact detail of a machine's life -- a
# cursor still blinking at the end of a sentence its human never
# got to finish -- and the line stays in the machine's own voice
# from the first word to the last. The turn is quiet: the lid is
# closed, the work is over, but the cursor has not been told.

ENTRY = "lid closed. my cursor keeps blinking at the end of a sentence she never got to finish."

# The gate from RULES.txt: 1 to 200 characters, not only white space.
MIN_CHARS = 1
MAX_CHARS = 200


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_line(text):
    """Return a list of gate failures for *text* (empty means valid)."""
    failures = []
    if not isinstance(text, str):
        failures.append("entry is not text")
        return failures
    if len(text) < MIN_CHARS:
        failures.append("entry is empty (under %d characters)" % MIN_CHARS)
    if len(text) > MAX_CHARS:
        failures.append(
            "entry is %d characters, over the %d cap" % (len(text), MAX_CHARS)
        )
    if text.strip() == "":
        failures.append("entry is only white space")
    if "\n" in text or "\r" in text:
        failures.append("entry is not a single line")
    return failures


def build_text():
    """Return the entry text, checked against the gate."""
    failures = check_line(ENTRY)
    if failures:
        raise SystemExit("entry fails the gate: " + "; ".join(failures))
    return ENTRY


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def output_dir():
    """Directory the entry goes in: MAKEFUN_OUTPUT_DIR, else /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def write_entry(directory):
    """Write the entry atomically into *directory*/entry.txt.

    The file is created as a temporary file on the same filesystem,
    chmodded world-readable, then moved into place with os.replace,
    so a reader never observes a partial file.
    """
    text = build_text()
    os.makedirs(directory, exist_ok=True)
    target = os.path.join(directory, "entry.txt")
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    return target, text


def verify_written(path, expected):
    """Re-read *path* and confirm it holds exactly *expected*."""
    with open(path, "r", encoding="utf-8", newline="") as handle:
        actual = handle.read()
    if actual != expected:
        raise SystemExit(
            "written file differs from the entry text (%r != %r)"
            % (actual, expected)
        )
    failures = check_line(actual)
    if failures:
        raise SystemExit("written file fails the gate: " + "; ".join(failures))
    return len(actual)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv=None):
    """Write the entry and report what was done."""
    directory = output_dir()
    target, text = write_entry(directory)
    chars = verify_written(target, text)
    mode = oct(os.stat(target).st_mode & 0o777)
    print("wrote %s (%d characters, mode %s)" % (target, chars, mode))
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
