---
id: 01ANCH00000000000000000006
title: note_subfolder
updated: 2026-09-09
tags: [anchor]
summary: "Test note that links to [[subfolder/Nota#Heading]] where subfolder/Nota.md exists. The checker must strip both the subfolder prefix and the heading anchor, resolving to the Nota basename without a false E006."
keywords: [heading anchor, subfolder link, basename resolution, conformance, e006, test]
entities:
  - {name: Mosaix Format, type: document}
rev: 000000000006
status: sourced
---

This note links to a note in a subfolder with a heading anchor: [[subfolder/Nota#Heading]].

The checker should strip the subfolder prefix (resolve by basename) and strip the anchor, finding Nota.md and reporting no E006. ✅
