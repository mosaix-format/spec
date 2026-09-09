---
id: 01ANCH00000000000000000004
title: note_valid
updated: 2026-09-09
tags: [anchor]
summary: "Test note that links to [[Home#Introduction]] where Home.md exists in the vault. The heading anchor must be stripped so the link resolves to Home and produces zero E006 broken-link errors."
keywords: [heading anchor, valid link, existing target, conformance, e006, test]
entities:
  - {name: Mosaix Format, type: document}
rev: 000000000004
status: sourced
---

This note links to an existing note using a heading anchor: [[Home#Introduction]].

The checker should resolve this to Home.md and report no E006. ✅
