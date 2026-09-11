# Zenodo Upload — Mosaix Format v1.2.0

## 1. Creare lo ZIP dal tag

```bash
git archive --format=zip --prefix=mosaix-format-spec-v1.2.0/ v1.2.0 -o mosaix-format-spec-v1.2.0.zip
```

Verifica il contenuto:

```bash
unzip -l mosaix-format-spec-v1.2.0.zip | head -20
```

## 2. Creare il deposito su Zenodo

1. Vai su https://zenodo.org/deposit/new
2. Fai login (o crea un account se necessario)
3. Carica il file `mosaix-format-spec-v1.2.0.zip` nella sezione **Files**

## 3. Compilare i metadati

Copia i valori da `zenodo.json` nei campi del form:

| Campo Zenodo | Valore |
|---|---|
| **Upload type** | Software |
| **Title** | Mosaix Format Specification v1.2.0 |
| **Publication date** | 2026-09-09 |
| **Authors** | Fiorino, Andrea — Affiliation: Independent |
| **Description** | Mosaix Format v1.2.0 introduces three optional CORE keys: question (the single question a note answers, enforcing atomicity rule R1), origin (who wrote the note: human, distilled, or observed), and as_of (when the described fact was true, distinct from the last-edit date). The reference auditor now uses graduated exit codes (0 = clean, 1 = errors, 2 = warnings only), supports extensible entity types via the meta note's entity_registry, resolves Obsidian-aware paths, and handles ULID id-first link resolution. The format is also available as a Python library on PyPI (pip install mosaix) with CLI commands for checking, scaffolding, and migrating vaults — stdlib-only, zero external dependencies. |
| **Version** | 1.2.0 |
| **Language** | English |
| **License** | Creative Commons Attribution Share Alike 4.0 International |
| **Keywords** | knowledge management, structured notes, MCP, Model Context Protocol, AI retrieval, Obsidian, knowledge vault, semantic enrichment, open specification |

### Related identifiers

Aggiungi due related identifiers:

1. **Identifier:** `https://mosaixformat.org` — **Relation:** is supplement to
2. **Identifier:** `https://pypi.org/project/mosaix/` — **Relation:** is supplement to — **Resource type:** Software

## 4. Pubblicare e ottenere il DOI

1. Clicca **Preview** per verificare che tutto sia corretto
2. Clicca **Publish** — Zenodo assegna un DOI del tipo `10.5281/zenodo.XXXXXXX`
3. Copia il DOI e il badge Markdown dalla pagina del record

## 5. Inserire il DOI nel repository

### README.md

Aggiungi il badge DOI nella riga dei badge (dopo il badge version):

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

### CHANGELOG.md

Aggiungi il DOI alla sezione `## 1.2.0`:

```markdown
## 1.2.0 — 2026-09-09

DOI: [10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXX)
```

### Site (mosaixformat.org)

Aggiungi il DOI nella pagina principale o nella sezione Citing:

```markdown
> Fiorino, A. (2026). *Mosaix Format — Specification v1.2.0*.
> https://mosaixformat.org — DOI: [10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXX)
```

### CITATION.cff (opzionale)

Se il repository ha un file `CITATION.cff`, aggiorna il campo `doi`:

```yaml
doi: 10.5281/zenodo.XXXXXXX
```

## Note

- Il DOI è permanente: una volta pubblicato, il record non può essere eliminato (solo una nuova versione può essere aggiunta).
- Per le release future, Zenodo può essere collegato al repository GitHub per generare automaticamente un DOI a ogni tag. Vai su https://zenodo.org/account/settings/github/ per abilitare l'integrazione.
- Lo ZIP generato da `git archive` non include la directory `.git`, quindi è pulito e pronto per l'archiviazione.
