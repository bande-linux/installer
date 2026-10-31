# bande-linux installer

the source of truth; keep it current. Open work goes to
[NOTES/backlog.md](NOTES/backlog.md).

The rules below override your defaults. Follow them unless I say otherwise in the session.

## 1. No comments

Write none, in Python or shell. The only exception is a fact this repository cannot tell the
reader:

- behaviour of a system we do not own (diskutil, bputil, kmutil, APFS, recoveryOS, Apple's IMG4
  and IPSW formats, vendor firmware packages)
- a magic value copied from outside, with its source

One line. Never write what the next line does, a note to the reviewer ("now", "replaces",
"fixed"), a defence of a design, a banner, or a doc comment that restates a name or signature.
Doc comments are comments.

Existing comments stay as they are. Removing them is its own commit, never part of a change.

## 2. No explanatory text in the installer

The installer is an interactive Terminal program and every word on screen is read. A screen
carries a question, choices, data and state, nothing that explains them:

- a state or a problem in one short sentence ("Not enough free space.")
- keep a warning only for data loss ("This erases the selected partition.")
- keep instructions only for a step the person must do themselves (recoveryOS, the boot policy
  prompt)
- no ellipses in prompts or choices

Background, reasons and examples belong in README.md.

## 3. No tests without a motivation

Do not add a test because you changed code. A new test needs one of these motivations, stated in
its name or first line:

- it reproduces a bug that actually happened and would come back unseen
- it pins behaviour of a system we do not own; fixtures are real diskutil output or real firmware
  images, never written from our parser
- it guards a safety property: only the chosen partition is resized or erased, nothing is written
  before the person confirms, an unsupported macOS or firmware version is refused

Even then, propose it in one line and wait for a yes. Prefer a test through the installer's entry
points with recorded inputs over a unit test of a helper.

Never write tests of constants, getters or formatting, a return value restated, mocks asserting
they were called, one test per branch, or edge-case sweeps.

When your change breaks an existing test: fix it if it guards one of the motivations above;
delete it if it only restated the old code, and list every deletion in your reply.

## 4. Before you finish

Re-read your diff. Delete every comment that fails §1, every string that fails §2 and every test
you added that fails §3. Expect that to be most of them.

## 5. Scope and consent

- Do what I asked, then stop. Name adjacent problems in one line at the end of your reply; don't
  fix them.
- No unrequested docs, renames or formatting passes. No CI or packaging work unless asked.
- Reuse before you add: search `src/` and the firmware package first. Duplicate logic is a bug;
  factor it out the second time, inside your scope. No speculative optimisation.
- Ask first, in two or three sentences with the trade-off, before you:
  - touch more than a handful of files
  - move, rename or split a module or the firmware package
  - change an interface with the bootloader (its version marker, the variable block, `chosen.*`
    variables) or with the installed OS (ESP layout, where firmware is placed)
  - change where the installer downloads from or reports to
  - add a dependency (Python package, bundled tool)
  - run anything as root, or anything that touches disks, partitions or the boot policy of a real
    Mac, including `test.sh`
- Commit in small commits of one intent on a branch and push it. A branch reaches main only with
  green CI, never by a force-push.

## 6. Architecture

- Runs on the target Mac, from macOS or recoveryOS, with a bundled Python. It resizes the macOS
  container, creates a stub macOS that carries the system firmware, installs the bootloader as
  the custom boot object, and installs an OS image.
- The bootloader is the `unboot/` submodule; its stage 1 is built from it and its version is read
  from the binary.
- Firmware for Wi-Fi, Bluetooth and other blocks is extracted from macOS into the ESP; the
  installed OS reads it from there.
- Nothing is written to disk before the person has confirmed the target. No data leaves the
  machine except downloads from the repositories it is configured with.
