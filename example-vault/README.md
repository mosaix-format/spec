# Example vault — the specification as a vault

The Mosaix Format specification, split into 48 conformant notes: one per section, one per CORE key, one per rule, the proposals for 1.1, a synthesis, a composed document, and a `templates/` folder with Obsidian templates for every note type.

It exists so that the format can be read the way it asks to be read: one note at a time, each carrying its summary, keywords, entities and links; or as a whole, through `Home.md` and the composed document `_docs/Mosaix for a new team.md`.

## Files

- `vault-data.js` — the source of truth: one JavaScript object per note. **Edit this, not the `.md` files.**
- `export_vault.py` — writes `vault/` from `vault-data.js`, runs the reference checker, and if the vault is conformant builds `mosaix-example-vault.zip` (with a minimal `.obsidian/` folder: graph colours by note type, wikilinks on) and refreshes the copies the site serves.
- `vault/` — the generated notes, committed so they can be read on GitHub.

```
python export_vault.py
```

## What to expect from the checker

`python ../audit_reference.py vault` reports 0 errors and 0 warnings. With `--check-rev` it reports a `rev may be stale` hint on every note: the `rev` values here are placeholders, not hashes of the bodies, because no tool computed them. That is allowed by the specification (the key must be present; a tool fills it) and is the expected result for a hand-written vault.

## Using the templates

Copy `vault/templates/` into your own vault and point Obsidian's core Templates plugin at it (Settings → Templates). The placeholders `{{title}}` and `{{date:YYYY-MM-DD}}` are Obsidian's; without Obsidian, replace them by hand. `How to use these templates.md` explains the rest.

CC BY-SA 4.0 — see `../LICENSE.md`.
