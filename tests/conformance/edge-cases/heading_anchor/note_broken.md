---
id: 01ANCH00000000000000000005
title: note_broken
updated: 2026-09-09
tags: [anchor]
summary: "Test note that links to [[Nonexistent#Section]] where Nonexistent.md does not exist in the vault. The checker must strip the anchor and detect the missing target, producing exactly one E006 error."
keywords: [heading anchor, broken link, missing target, conformance, e006, test]
entities:
  - {name: Mosaix Format, type: document}
rev: 000000000005
status: sourced
---

This note links to a note that does not exist, using a heading anchor: [[Nonexistent#Section]].

The checker should strip the anchor, find Nonexistent.md is absent, and report E006. ✅
