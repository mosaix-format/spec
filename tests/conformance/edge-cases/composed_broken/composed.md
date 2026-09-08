---
title: composed
id: 01000000000000000000000133
updated: 2026-09-08
type: document
tags: [concept]
status: sourced
summary: "Broken composed document that references frag1 (which exists) and missing_frag (which does not). The missing fragment triggers E011 fragment_not_found conformance error when the vault is audited."
keywords: [composed broken, missing fragment, e011, document type, conformance, edge case]
entities:
  - {name: Mosaix Format, type: document}
fragments: [frag1, missing_frag]
links: [frag1]
rev: deadbeef0133
---

# composed

Assembles [[frag1]] and missing_frag (missing — triggers E011).
