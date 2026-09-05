---
title: §11 Versioning
type: section
updated: 2026-09-03
tags: [spec, versioning]
status: sourced
summary: "Versions follow MAJOR.MINOR.PATCH: a MINOR version adds optional keys, note types or warnings and never breaks a conformant vault; a MAJOR version may; vaults state their target version."
keywords: [versioning, semver, minor never breaks, major may break, mosaix 1.0 key, target version, 1.1]
entities:
  - {name: Mosaix Format, type: project}
relations: []
links: [§0 Status, Open questions]
rev: 4e8c2a9f7d63
---

# §11 Versioning

Vaults SHOULD state `mosaix: "1.0"` in their meta note. What 1.1 may add is tracked in [[Open questions]].
