---
id: 01JXAC00000000000000000006
title: Missing Updated Key
tags: [test, error-testing]
summary: "Test note that deliberately omits the required updated field to trigger E002 for a missing required CORE key; title is present but updated is absent from the frontmatter."
keywords: [test, e002, missing-key, required, updated, conformance]
entities:
  - {name: Test Suite, type: project}
rev: 000000000000
status: sourced
---

This note is missing the required `updated` field, which triggers E002.
Note: the `title` key is optional (derivable from filename) and its absence never triggers E002.
