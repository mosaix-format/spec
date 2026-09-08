---
title: W008_stale_rev
id: 01000000000000000000000054
updated: 2026-09-08
tags: [concept]
status: sourced
summary: "Test note for W008: the stored rev value does not match sha256(body)[:12]. This mismatch indicates stale metadata and triggers W008, but only when the checker is run with the --check-rev flag."
keywords: [stale rev, w008, hash, sha256, conformance, warning]
entities:
  - {name: Mosaix Format, type: document}
rev: 000000000000
---

# W008_stale_rev

The `rev` field is `000000000000` which does not match the actual sha256 of this body.
Should trigger W008 when the checker is run with `--check-rev`.
