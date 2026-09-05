# Mosaix example vault — Forno Vialetto

A second example vault for the Mosaix Format, built on ordinary knowledge: a fictional artisan bakery called Forno Vialetto, three partners, five products, three suppliers, a neighbourhood, two competitors and a Saturday market. Twenty-six notes, fully conformant.

**Why it exists.** The first example vault is the specification itself — elegant but self-referential. This vault shows the format on a domain anyone can recognise without reading the spec first.

**Everything is invented.** Names, places, prices, dates: none of it is real. The `rev` values are fictitious 12-hex strings, so `--check-rev` will report warnings — that is expected.

**Regenerate the vault and the zip:**

```
python export_vault.py
```

This writes `vault/`, runs `audit_reference.py --verbose`, creates `mosaix-bakery-vault.zip` and copies it to `site/`. `vault-data.js` is the single source of truth.

License: [CC BY-SA 4.0](../LICENSE.md).
