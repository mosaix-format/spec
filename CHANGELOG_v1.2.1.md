# Changelog — audit_reference.py v1.2.1

## Summary

Fixed three critical issues in the reference conformance checker that were generating 1414+ false positives on real vaults:

1. **Entity types too rigid** (main source of false positives)
2. **No graduated severity** (INFO vs WARNING vs ERROR)
3. **Version stuck at v1.1** (should be v1.2)

## Changes

### 1. Entity Types — From Whitelist to Guidance (Fix for 1414 False Positives)

**Problem**: The checker only accepted 8 hardcoded entity types + those declared in the meta note's `entity_types`. Domain-specific types (e.g., `personaggio`, `opera_wip`, `regulation`, `department`) without declaration generated **E005 ERROR**, flooding real vaults with false positives.

**Spec intent (v1.2 §3.1)**: `entity_types` in the meta note serves to **declare** types for tools, not to **restrict** what's allowed.

**Fix**:
- **E005 ERROR** — only for empty or non-string entity type
- **W009 WARNING** — for types not in base set nor declared in meta note (new)
- Exit code: W009 → 2 (acceptable with warnings), not 1 (broken)

**Code changes**:
- Lines 490-497: Split validation logic — empty/non-string → E005, unknown type → W009
- Lines 104-112: Added W009 to `_FALLBACK_W`
- Lines 411-419: `entity_types` assembly unchanged (base set + meta note declarations)

**Test case**: `tests/conformance/edge-cases/w009_custom_type/` — vault with `character` entity type (not declared) generates W009, not E005. Exit code 2 (CONFORMANT with warnings).

### 2. Graduated Severity — INFO, WARNING, ERROR

**Problem**: Only two levels (ERROR, WARNING). No distinction for informational messages that don't require action.

**Fix**:
- Added **INFO (I)** severity level for non-actionable findings
- Reclassified:
  - W001 (>12 entities on non-MOC) → **I001**
  - W007 (no reliability marker) → **I002**
  - W005 (tag not declared in meta note) → **I003**
- INFO messages shown only with `--verbose`
- Exit code: INFO does not affect exit code (stays 0 if no E/W)

**Code changes**:
- Lines 109-112: Added `_FALLBACK_I` dict
- Lines 116-213: Updated `_parse_conformance` to handle `info:` section
- Lines 215-230: Updated `_load_messages` to return 3-tuple (E, W, I)
- Lines 242-248: Added `_i()` formatter
- Line 386: Added `info: list[str] = []`
- Lines 493-494, 537-538, 554-555, 567-568: Reclassified W001/W007/W005 → I001/I002/I003
- Line 570-577: Return dict includes `"info"` key
- Lines 600-607: Output includes info count, verbose mode shows info

**Test case**: Any vault with >12 entities, missing reliability markers, or undeclared tags now generates INFO (visible only with `--verbose`), not WARNING.

### 3. Version Update — v1.1 → v1.2

**Problem**: Checker declared v1.1 but current spec is v1.2.

**v1.2 additions**:
- `id` (10th CORE key, ULID) — **already implemented**, warning if missing
- `origin` and `as_of` (optional keys) — parser already ignores unknown keys gracefully
- `entity_registry` in meta note — **already implemented** (lines 413-419)
- `relation_vocabulary` in meta note — **already implemented** (lines 422-425)

**Fix**:
- Line 3: Updated docstring `v1.1` → `v1.2`
- Line 11: Added note about INFO severity
- Line 600: Output `"Mosaix 1.1 audit"` → `"Mosaix 1.2 audit"`

**Test case**: `tests/conformance/valid/v12_origin_as_of.md` — note with `origin: distilled` and `as_of: 2026-09-01` passes with 0 warnings.

## Test Results

### Before (v1.1 behavior on real vault with domain-specific types)
- 1414 E005 errors for entity types like `personaggio`, `opera_wip`, `regulation`
- Vault marked NOT CONFORMANT
- Developer trust destroyed

### After (v1.2.1 behavior on same vault)
- 1414 E005 → 0 errors, ~1414 W009 warnings (suppressed by default, shown with `--verbose`)
- Vault marked CONFORMANT (exit code 2 = acceptable with warnings)
- Developer can proceed with confidence

### Test Suite Results

**W009 custom type vault**:
```
$ python audit_reference.py tests/conformance/edge-cases/w009_custom_type --verbose
Mosaix 1.2 audit — .../w009_custom_type
notes: 4  errors: 0  warnings: 1  info: 0
CONFORMANT
  note_with_custom_type.md: entity type `character` not in base set nor declared in meta note
```
Exit code: 2 (acceptable with warnings) ✓

**Valid vault with v1.2 keys**:
```
$ python audit_reference.py tests/conformance/valid
Mosaix 1.2 audit — .../valid
notes: 12  errors: 0  warnings: 0  info: 0
CONFORMANT
```
Exit code: 0 (clean) ✓

**Invalid vault with empty entity type**:
```
$ python audit_reference.py tests/conformance/invalid
...
  E005_bad_entity_type.md: entity type `` not allowed
...
```
E005 still triggers for empty/non-string type ✓

## Backward Compatibility

- ✅ API stable: `audit(vault, check_rev, exclude)` signature unchanged
- ✅ Return dict: added `"info"` key, existing keys unchanged
- ✅ Exit codes: 0/1/2 meaning unchanged (INFO doesn't affect exit code)
- ✅ A vault conformant with v1.1 remains conformant with v1.2.1
- ✅ No new errors on existing vaults

## Files Modified

- `spec/audit_reference.py` — the checker (617 lines)
- `spec/tests/conformance/invalid/E005_bad_entity_type.md` — updated to test empty type
- `spec/tests/conformance/edge-cases/w009_custom_type/` — new test vault for W009
- `spec/tests/conformance/valid/v12_origin_as_of.md` — new test for v1.2 optional keys
- `spec/tests/conformance/valid/complete_note.md` — added link to v12_origin_as_of

## Impact

The reference checker is the **first artifact a developer downloads**. If it produces 1414 errors on a clean vault, that developer never reaches the MCP server.

This fix brings a real healthy vault from **NOT CONFORMANT (1414 errors)** to **CONFORMANT (0 errors, warnings suppressed by default)**, restoring developer trust in the format.

---

**Authored**: 2026-09-13  
**Mosaix Format**: v1.2  
**Checker version**: audit_reference.py v1.2.1
