---
title: §9 Host profile
type: section
updated: 2026-09-03
tags: [spec, obsidian, host]
status: sourced
summary: "Obsidian is the reference host: its wikilink, embed, tag and frontmatter handling match the substrate; Dataview, Bases, Canvas and callouts are outside the format and never required."
keywords: [obsidian, host application, dataview, bases, canvas, callouts, logseq foam dendron zettlr, not a dependency]
entities:
  - {name: Obsidian, type: tool}
  - {name: Logseq, type: tool}
  - {name: Foam, type: tool}
relations:
  - {from: Obsidian, type: is reference host of, to: Mosaix Format}
links: [§2 Substrate]
rev: 2a7d9e4b6c10
---

# §9 Host profile

Obsidian matches [[§2 Substrate]] exactly. Host features (Dataview, `.base`, Canvas, callouts) are views, not content, and MUST NOT be required. `.obsidian/` is host state; `workspace.json` should stay out of version control. Other hosts: Logseq, Foam, Dendron, Zettlr.
