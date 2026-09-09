---
id: 01RV0000000000000000000003
title: bad_relation
updated: 2026-09-09
tags: [navigation]
summary: "Note with a relation type 'invented by' which is not in the relation_vocabulary declared in the meta note. This triggers W002."
keywords: [relation, vocabulary, undeclared, w002, conformance, test]
entities:
  - {name: Mosaix Format, type: document}
  - {name: Andrea Fiorino, type: person}
relations:
  - {from: Andrea Fiorino, type: invented by, to: Mosaix Format}
rev: 000000000000
status: sourced
---

# bad_relation

Uses a relation type not in `relation_vocabulary` → W002.
