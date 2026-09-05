---
title: How to use these templates
type: guide
updated: 2026-09-05
tags: [template, guide]
status: sourced
summary: "How to copy the templates folder into your own vault, point Obsidian's Templates plugin at it, and replace the placeholders by hand if you are not using Obsidian at all."
keywords: [how to use templates, copy templates folder, obsidian templates plugin, settings templates, placeholders by hand, no obsidian needed, getting started]
entities:
  - {name: Mosaix Format, type: project}
  - {name: Obsidian, type: tool}
relations: []
links: [Template — note, Template — MOC, Template — synthesis, Template — document, Template — Conventions, Template — Open questions]
rev: 1a2b3c4d5e6f
---

# How to use these templates

Copy the `templates/` folder into your own vault, then start every new note from the matching file: [[Template — note]] for an ordinary note, [[Template — MOC]] for a map of content, [[Template — synthesis]] for a synthesis, [[Template — document]] for a composed document, [[Template — Conventions]] for the meta note, and [[Template — Open questions]] for the ledger.

In Obsidian, open Settings → Templates (the core Templates plugin), enable it, and set the template folder to `templates/`. Insert a template into a new note and Obsidian fills in `{{title}}` and `{{date:YYYY-MM-DD}}` for you; the `:YYYY-MM-DD` part is the plugin's date-format syntax, so keep it if you change the date shown.

The templates work without Obsidian too: open the file in any text editor, replace `{{title}}` with the note's title and `{{date:YYYY-MM-DD}}` with today's date, and fill in the rest by hand. Nothing here depends on any application beyond that.
