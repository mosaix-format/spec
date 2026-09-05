---
title: §10 Conformance
type: section
updated: 2026-09-03
tags: [spec, conformance, checker]
status: sourced
summary: "A vault is Mosaix 1.0 conformant when the file checks report zero errors: frontmatter, key ranges, entity coverage, resolving links, no orphans, a MOC, a ledger, a meta note; warnings allowed."
keywords: [conformance, checker, audit_reference.py, errors and warnings, zero errors, conformant vault, exit code]
entities:
  - {name: audit_reference.py, type: tool}
relations:
  - {from: audit_reference.py, type: verifies, to: §10 Conformance}
links: [§7 Rules, R2 Self-description, R3 Connectedness]
rev: 6f1b3d8a2e07
---

# §10 Conformance

Errors: missing frontmatter or core keys, summary outside 120–240, keywords outside 6–8, entity coverage under 80%, unresolved links, orphans, no MOC, no ledger, no meta note, a document with fewer than two fragments. Warnings: undeclared tags or keys, stale rev, no reliability marker. The reference checker is `audit_reference.py`.
