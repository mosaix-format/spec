---
title: §4 Links and the graph
type: section
updated: 2026-09-03
tags: [spec, links, graph]
status: sourced
summary: "Every note needs an incoming link; every wikilink must resolve; links mirrors outbound links; the graph is derived from files and is never the source of truth."
keywords: [orphan, broken link, incoming link, graph derived, wikilink resolution, connectedness, source of truth]
entities:
  - {name: Mosaix Format, type: project}
relations: []
links: [R3 Connectedness, key links, §2 Substrate]
rev: 3c9a17f2e6b0
---

# §4 Links and the graph

A note with no incoming link is an orphan: a conformance error ([[R3 Connectedness]]). An unresolved wikilink is an error. [[key links]] is the machine-readable mirror of outbound links. Notes, entities, relations and wikilinks form the graph; the graph is derived, never authoritative.
