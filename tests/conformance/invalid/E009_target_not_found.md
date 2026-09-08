---
title: E009_target_not_found
id: 01000000000000000000000029
updated: 2026-09-08
tags: [concept]
status: sourced
summary: "Test note for E009: the links list contains a plain filename reference 'nota_inesistente' which does not match any file in the vault. The checker emits E009 for non-ULID links that fail filename resolution."
keywords: [target not found, e009, links, filename resolution, conformance, error]
entities:
  - {name: Mosaix Format, type: document}
links: [nota_inesistente]
rev: deadbeef0029
---

# E009_target_not_found

The `links` key contains a filename that does not exist — should trigger E009.
