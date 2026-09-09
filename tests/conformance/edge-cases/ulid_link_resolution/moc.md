---
id: 01JVKE4X2PFNRW8BQDP5MHCGBB
title: Home
type: moc
updated: 2026-09-09
tags: [navigation]
summary: "MOC for the ulid_link_resolution vault; links note_a, note_b, and note_c so all notes are reachable and the only expected error is E008 from note_c's unresolvable ULID reference."
keywords: [index, navigation, moc, ulid, link-resolution, test, e008]
entities:
  - {name: Test Suite, type: project}
links: [note_a, note_b, note_c]
rev: 000000000000
status: sourced
---

## Index

- [[note_a]] — Note A (carries the target ULID as its id)
- [[note_b]] — Note B (links by ULID → resolves to Note A)
- [[note_c]] — Note C (links by non-existent ULID → E008)
