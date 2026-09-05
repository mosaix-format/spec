---
title: §3 The note
type: section
updated: 2026-09-03
tags: [spec, note, frontmatter, core]
status: sourced
summary: "The note is the tile: it answers one question and carries the CORE frontmatter of nine keys; the body is never touched by metadata operations; aliases are allowed if declared."
keywords: [the note, tile, core keys, nine keys, frontmatter core, one question, byte identical body, aliases]
entities:
  - {name: Mosaix Format, type: project}
relations:
  - {from: §3 The note, type: defines, to: CORE frontmatter}
links: [key summary, key keywords, key entities, key relations, key links, key rev, key updated, key tags, key title, R1 Atomicity]
rev: 1b6e4d8c0a73
---

# §3 The note

A note answers one question ([[R1 Atomicity]]). CORE keys: [[key title]], [[key updated]], [[key tags]], [[key summary]], [[key keywords]], [[key entities]], [[key relations]], [[key links]], [[key rev]]. Italian key names used by earlier vaults (mcp_entita, mcp_relazioni, mcp_collegamenti, mcp_rev) are accepted as aliases. Any process that rewrites frontmatter MUST leave the body byte-identical.
