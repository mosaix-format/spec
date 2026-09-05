# Contributing to the Mosaix Format specification

The specification changes through this repository, in this order.

1. **Open an issue** describing the case the current text gets wrong: a note, a vault excerpt, or a checker result that does not match the intent. Use the *Specification change* issue form. Issues without a concrete case are usually closed as questions.
2. **Discuss.** Most changes are a clarification, an example, or a new warning. Anything that would make a conformant vault non-conformant is a MAJOR change and waits (see below and §11 of the specification).
3. **Pull request** against `Mosaix-Format-v1.0.en.md`. English is normative; the Italian file follows in the same PR or a later one. Add a line to `CHANGELOG.md`. If a conformance check changes, change `audit_reference.py` in the same PR and make sure `example-vault/` still passes:

   ```
   python example-vault/export_vault.py
   python example-vault-bakery/export_vault.py
   ```

   Both runs must end with `CONFORMANT`.
4. **Release.** Maintainers tag `vMAJOR.MINOR.PATCH`; the site follows the latest tag.

## MINOR or MAJOR

Versions follow `MAJOR.MINOR.PATCH` (§11).

- **PATCH**: wording, examples, typos, translations. No change to what the checker reports.
- **MINOR**: may add optional keys, note types, aliases or warnings. It never turns a conformant vault into a non-conformant one. A vault that passes §10 today still passes after a MINOR release.
- **MAJOR**: may make a conformant vault non-conformant. That includes turning a warning into an error, making an optional key required, removing a key, alias or note type, or tightening a range. MAJOR changes are collected and released together, not merged one at a time.

State in the pull request which of the three the change is. If in doubt, ask in the issue first.

## Language

English is the normative text. Every change lands in `Mosaix-Format-v1.0.en.md` first; other languages are courtesy translations and never diverge in meaning from the English file.

## Translations

Translations are welcome as `Mosaix-Format-v1.0.<lang>.md`, where `<lang>` is a two-letter ISO 639-1 code. Open the file with the same courtesy banner the Italian file uses, translated into the target language:

> Courtesy translation. In case of discrepancy, the English version (`Mosaix-Format-v1.0.en.md`) prevails.

Keep section numbers, key names, note types, status values and rule identifiers (R1–R8) as they are in the English file: they are part of the format, not of the prose.

## What this repository is not

The specification defines files, not software (§8). Pull requests that add tooling for producing, enriching, searching, composing or serving vaults belong elsewhere. The only code here is the reference checker, and it stays read-only, offline and standard-library only.

## License

By contributing you agree that your contribution is released under [CC BY-SA 4.0](LICENSE.md), the same license as the specification.
