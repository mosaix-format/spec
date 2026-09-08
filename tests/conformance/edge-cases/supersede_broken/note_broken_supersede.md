---
id: 01JXAG00000000000000000005
title: Broken Supersede Note
updated: 2026-09-01
tags: [test, archived]
summary: "A superseded note whose superseded_by field points to a note that does not exist; the v1.0 checker does not validate this field, so no E009 or other error is emitted."
keywords: [superseded, broken, reference, missing, test, conformance]
entities:
  - {name: Test Suite, type: project}
superseded_by: nonexistent_replacement
rev: 000000000000
status: superseded
---

The `superseded_by` field points to `nonexistent_replacement`, which does not exist.
The checker does not validate `superseded_by`, so no error is produced. This documents v1.0 behavior.
