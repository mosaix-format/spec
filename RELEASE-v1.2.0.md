# Mosaix Format v1.2.0 — Release Notes

**Data:** 2026-09-09  
**Tag:** `v1.2.0`  
**Tipo:** MINOR (nuove chiavi opzionali, miglioramenti auditor, libreria Python)

---

## Nuove chiavi opzionali

Mosaix 1.2.0 introduce tre nuove chiavi CORE opzionali che estendono la capacità espressiva del formato senza rompere la compatibilità con i vault 1.0/1.1.

| Chiave | Tipo | Scopo | Alias italiano |
|--------|------|-------|----------------|
| **`question`** | `string` | La singola domanda a cui questa nota risponde (R1: atomicità). Deve terminare con `?`. Se presente, `summary` DOVREBBE rispondere a questa domanda. | `domanda` |
| **`origin`** | `string` (enum) | Chi ha scritto la nota: `human` (scritta da una persona), `distilled` (sintetizzata/generata da altre note/fonti), `observed` (catturata da un sistema o evento esterno). | `origine` |
| **`as_of`** | `date` (YYYY-MM-DD) | Quando il fatto descritto era vero. Distinto da `updated`, che registra quando la nota è stata modificata l'ultima volta. Utile per dati di mercato, prezzi, decisioni, e qualsiasi fatto che cambi nel tempo. | `data_fatto` |

**Ordine canonico aggiornato:**  
`title · id · updated · [chiavi dominio] · question · summary · keywords · entities · relations · links · rev · origin · as_of`

**Nota implementativa:** In v1.2 queste chiavi sono documentazionali — il checker le riconosce ma non le valida. La validazione piena arriverà in una release futura.

---

## Fix auditor

Il checker di riferimento (`audit_reference.py`) è stato migliorato con le seguenti correzioni:

### Exit code graduato

| Codice | Significato | Comportamento CI consigliato |
|--------|-------------|------------------------------|
| **0** | Completamente pulito — zero errori e zero warning | Sempre verde; merge libero |
| **1** | Rotto — almeno un errore (E) | Blocca la merge; gli errori sono violazioni di regole normative |
| **2** | Accettabile con warning — zero errori, almeno un warning (W) | Merge consentita; i warning sono advisory, non fallimenti normativi |

Questo permette workflow CI più flessibili: bloccare solo sugli errori (exit code 1) ma lasciare passare i warning (exit code 2), oppure richiedere un vault completamente pulito.

### Entity types estensibili

- Il checker ora supporta `entity_registry` nel meta note (spec §5.4.1) — ogni tipo di entità può avere alias e descrizioni human-readable.
- Un checker DEVE accettare sia il nome canonico che qualsiasi alias elencato come valore `type` valido in un'entry `entities`.
- Il campo `description` è solo informativo e non influisce mai sulla validazione.

Esempio dal meta note:

```yaml
entity_registry:
  department: {aliases: [dipartimento, reparto], description: "Unità organizzativa"}
  regulation: {aliases: [normativa, standard], description: "Standard o regolamento di settore"}
```

### Path Obsidian-aware

- Il checker ora risolve correttamente i path relativi ai pattern di path Obsidian (`[[path/to/Note]]`).
- Il supporto per path con caratteri unicode e spazi è migliorato.

### Alias italiani

- Tutti gli alias italiani (già documentati in v1.1) sono ora completamente supportati senza necessità di dichiararli nel meta note:
  - Chiavi frontmatter: `titolo`, `aggiornato`, `riassunto`, `parole_chiave`, `mcp_entita`, `mcp_relazioni`, `mcp_collegamenti`, `mcp_rev`, `origine`, `data_fatto`
  - Campi in entity/relation objects: `nome`, `tipo`, `da`, `a`
  - Valori entity type: `persona`, `azienda`, `prodotto`, `progetto`, `strumento`, `luogo`, `documento`, `evento`
  - Nomi ledger: `Assunzioni da confermare.md`, `Domande aperte.md`

### ULID id-first resolution

- I link nel formato ULID (26 caratteri Crockford Base32) sono ora risolti **id-first**: il checker cerca prima una corrispondenza nel campo `id`, poi ricade sul filename.
- Questo è il meccanismo principale dell'`id` in v1.0–1.2: permettere riferimenti stabili anche quando i file vengono rinominati.

---

## Libreria Python

Mosaix 1.2.0 è ora disponibile come pacchetto Python su PyPI:

```bash
pip install mosaix
```

Il checker può essere eseguito come modulo Python:

```bash
mosaix check /path/to/vault
mosaix check /path/to/vault --verbose --exclude=exports/
mosaix check /path/to/vault --json > report.json
```

O come script standalone (nessuna dipendenza oltre la stdlib):

```bash
python audit_reference.py /path/to/vault
```

Il pacchetto include anche:
- `mosaix init` — scaffold di un nuovo vault con struttura standard
- `mosaix migrate` — migrazione best-effort di vault Markdown esistenti verso la conformità

---

## Riferimenti

- **Specifica:** [Mosaix-Format-v1.2.en.md](Mosaix-Format-v1.2.en.md) (normativa, inglese) · [Mosaix-Format-v1.2.it.md](Mosaix-Format-v1.2.it.md) (cortesia, italiano)
- **Spec machine-readable:** [spec.yaml](spec.yaml)
- **Checker di riferimento:** [audit_reference.py](audit_reference.py)
- **Pacchetto Python:** [mosaix su PyPI](https://pypi.org/project/mosaix/) (quando pubblicato)
- **CHANGELOG completo:** [CHANGELOG.md](CHANGELOG.md)
- **Sito:** https://mosaixformat.org
- **Repository:** https://github.com/mosaix-format/spec
- **Tag:** `v1.2.0` — https://github.com/mosaix-format/spec/releases/tag/v1.2.0

---

## Compatibilità

Mosaix 1.2.0 è **completamente retrocompatibile** con vault 1.0 e 1.1:

- Tutte le nuove chiavi sono opzionali.
- Nessuna chiave esistente è cambiata.
- Vault 1.0/1.1 conformi restano conformi senza modifiche.
- Il checker 1.2 può validare vault 1.0/1.1 (genera gli stessi risultati del checker 1.0/1.1).

Secondo la policy di versioning (GOVERNANCE.md), questa è una release **MINOR** perché introduce nuove chiavi opzionali e nuovi strumenti, ma non rompe alcuna vault conformante esistente.

---

## Citazione

> Fiorino, A. (2026). *Mosaix Format — Specification v1.2.0*. https://mosaixformat.org — source: `mosaix-format/spec@v1.2.0`

---

**Licenza:** CC BY-SA 4.0  
**Autore:** Andrea Fiorino ([andrea@alfagomma.dev](mailto:andrea@alfagomma.dev))
