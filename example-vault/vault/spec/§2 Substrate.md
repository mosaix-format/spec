---
title: §2 Substrate
type: section
updated: 2026-09-03
tags: [spec, substrate, markdown]
status: sourced
summary: "The substrate is plain text: UTF-8 Markdown files, optional YAML frontmatter, wikilinks resolved by basename, embeds with ![[ ]], tags in body or frontmatter."
keywords: [markdown, frontmatter, wikilink, embed, transclusion, basename, plain files, utf-8]
entities:
  - {name: CommonMark, type: document}
  - {name: Obsidian, type: tool}
relations:
  - {from: Mosaix Format, type: builds on, to: CommonMark}
links: [§9 Host profile, §4 Links and the graph]
rev: 9f0d3b7ae255
---

# §2 Substrate

Notes are `.md` files in CommonMark. A wikilink (the target title in double square brackets) resolves by the target's basename, case-sensitive, anywhere in the vault ([[§4 Links and the graph]]). Any tool that reads Markdown reads a Mosaix vault; Obsidian is the reference host ([[§9 Host profile]]), not a dependency.
