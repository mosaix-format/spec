---
title: W002_unknown_relation
id: 01000000000000000000000051
updated: 2026-09-08
tags: [concept]
status: sourced
summary: "Test note for W002: contains a relation with type 'invented by' which is not in the relation_types vocabulary declared in the meta note. This triggers the undeclared relation type warning."
keywords: [unknown relation, w002, relation type, vocabulary, conformance, warning]
entities:
  - {name: Mosaix Format, type: document}
  - {name: Andrea Fiorino, type: person}
relations:
  - {from: Andrea Fiorino, type: invented by, to: Mosaix Format}
rev: deadbeef0051
---

# W002_unknown_relation

Has a relation type not in the declared vocabulary — should trigger W002.
