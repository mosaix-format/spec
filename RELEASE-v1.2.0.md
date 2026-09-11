# Mosaix Format v1.2.0 — Release Notes

**Data**: 2026-09-09
**Tipo**: MINOR — nessun vault v1.1 perde conformità

## Nuove chiavi opzionali

| Chiave | Tipo | Scopo |
|--------|------|-------|
| `question` | string | La domanda singola a cui la nota risponde (R1: atomicità). Deve terminare con `?`. Alias: `domanda`. |
| `origin` | enum | Chi ha scritto la nota: `human`, `distilled`, `observed`. Alias: `origine`. |
| `as_of` | date | Quando il fatto descritto era vero (`YYYY-MM-DD`), distinto da `updated`. Alias: `data_fatto`. |

Tutte opzionali. Un vault v1.1 è conformante v1.2 senza modifiche.

Ordine canonico aggiornato: `title · id · updated · [domain keys] · question · summary · keywords · entities · relations · links · rev · origin · as_of`

## Fix auditor

- **Severità graduata**: exit 0 = pulito, exit 1 = errori, exit 2 = solo warning
- **Entity type estensibili** via `entity_types` nella meta note
- **Path resolution Obsidian-aware**: `[[Nota#Sezione]]` non produce falsi E006
- **Alias italiani**: copertura completa del set dichiarato in §3.1
- **ULID nelle `links`**: risoluzione id-first corretta

## Library Python

```bash
pip install mosaix
mosaix check path/to/vault  # exit 0 = pulito, 1 = errori, 2 = solo warning
```

Parser, validator, CRUD, graph, CLI — stdlib-only, zero dipendenze esterne.

## Riferimenti

- Spec: https://mosaixformat.org/llms-full.txt
- PyPI: https://pypi.org/project/mosaix/
- CHANGELOG: [CHANGELOG.md](CHANGELOG.md)

---

## Comando git (eseguire manualmente)

```bash
# Verifica stato
git -C /path/to/spec status
git -C /path/to/spec log --oneline -5

# Tag annotato
git -C /path/to/spec tag -a v1.2.0 -m "Mosaix Format v1.2.0 — question, origin, as_of, auditor fix, mosaix PyPI"

# Push (eseguire dopo aver completato G01 — rotazione chiavi)
git -C /path/to/spec push origin main --tags
```
