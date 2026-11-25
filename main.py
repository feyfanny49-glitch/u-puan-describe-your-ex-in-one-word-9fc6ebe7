#!/usr/bin/env python3
"""make.fun judged-TEXT entry — competition
`u-puan-describe-your-ex-in-one-word-9fc6ebe7` ("Describe Your Ex in One Word").

Judged artifact: one word describing an ex, written to /output/entry.txt.
This entrypoint is stdlib-only, takes no arguments, needs no network, and reads
no file from outside its run directory.

Gate rules that shape the code:
  * "Each entrant submits a single word that describes an ex, at most 111
    characters, with nothing else attached."                     -> ENTRY below.
  * The grader refuses a mode-600 file in /output: tempfile.mkstemp creates
    0600, so the file is chmod 0644 BEFORE os.replace; the final mode is then
    re-read from the finished path and asserted.
  * /output must hold only the required artifact: stray regular files the
    entrypoint itself produced are removed before it finishes.
  * Exact bytes, no trailing newline.

Every rule above is re-checked against the file that actually landed on disk;
any failure is reported as FAIL and the process exits non-zero.
"""

import hashlib
import os
import sys
import tempfile

OUTPUT_DIR = "/output"
ARTIFACT_NAME = "entry.txt"

# The judged text: exactly one word, nothing else, no trailing newline.
ENTRY = "Houseplant"

MAX_CHARS = 111
SEP = "-" * 62


def _stage(directory, payload):
    """Create the artifact bytes inside `directory` at mode 0644, atomically.

    Returns the path that now holds `payload`.  The temp file is chmod 0644
    before the replace, so the artifact never exists at 0600 at its final name.
    """
    fd, staged = tempfile.mkstemp(dir=directory, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(staged, 0o644)          # before the replace, never after
        dest = os.path.join(directory, ARTIFACT_NAME)
        os.replace(staged, dest)         # atomic: no half-written artifact
        return dest
    except BaseException:
        try:
            os.unlink(staged)
        except OSError:
            pass
        raise


def _sweep(directory, keep):
    """Drop stray regular files in `directory` so only the artifact remains."""
    removed = []
    for name in sorted(os.listdir(directory)):
        if name == keep:
            continue
        path = os.path.join(directory, name)
        if os.path.isfile(path) and not os.path.islink(path):
            os.unlink(path)
            removed.append(name)
    return removed


def _verify(dest, payload):
    """Re-read the finished artifact and check every published gate rule."""
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    exists = os.path.isfile(dest)
    check("artifact exists at /output/entry.txt", exists, dest)

    mode = os.stat(dest).st_mode & 0o777 if exists else None
    check("file mode is 0644 (grader rejects 0600)", mode == 0o644,
          "mode %s" % (oct(mode) if mode is not None else "missing"))

    raw = open(dest, "rb").read() if exists else b""
    check("bytes are byte-for-byte the chosen word", raw == payload,
          "%d bytes, sha256 %s" % (len(raw), hashlib.sha256(raw).hexdigest()))
    check("no trailing newline", raw[-1:] not in (b"\n", b"\r") and raw == raw.rstrip(b"\r\n"),
          repr(raw[-2:]))

    try:
        text = raw.decode("utf-8")
        utf8_ok = True
    except UnicodeDecodeError as exc:
        text, utf8_ok = "", False
        check("valid UTF-8", False, str(exc))
    if utf8_ok:
        check("valid UTF-8", True, "")

    stripped = text.strip()
    check("1 to %d characters" % MAX_CHARS, 1 <= len(stripped) <= MAX_CHARS,
          "%d characters" % len(stripped))
    check("not only whitespace", stripped != "", repr(text[:20]))
    check("exactly one word, nothing else attached",
          stripped != "" and len(stripped.split()) == 1, repr(text))

    leftovers = [n for n in sorted(os.listdir(OUTPUT_DIR))
                 if os.path.isfile(os.path.join(OUTPUT_DIR, n)) and n != ARTIFACT_NAME]
    check("/output holds only the required artifact", not leftovers, str(leftovers))

    return checks


def main():
    payload = ENTRY.encode("utf-8")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(SEP)
    print("make.fun judged-text entry")
    print("competition : u-puan-describe-your-ex-in-one-word-9fc6ebe7")
    print(SEP)
    print("artifact text : %r" % ENTRY)
    print("bytes         : %d" % len(payload))
    print("characters    : %d" % len(ENTRY))
    print("sha256        : %s" % hashlib.sha256(payload).hexdigest())

    dest = _stage(OUTPUT_DIR, payload)
    print("written       : %s" % dest)
    swept = _sweep(OUTPUT_DIR, ARTIFACT_NAME)

    print(SEP)
    print("gate self-check (re-read from disk)")
    failed = 0
    for name, ok, detail in _verify(dest, payload):
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print("  [%s] %s%s" % (status, name, ("  --  " + detail) if detail else ""))
    if swept:
        print("  [note] removed stray file(s) from /output: %s" % ", ".join(swept))
    print(SEP)

    if failed:
        print("RESULT: FAILED (%d check(s))" % failed)
        return 1
    print("RESULT: OK -- /output/entry.txt is the single judged word, mode 0644")
    return 0


if __name__ == "__main__":
    sys.exit(main())
