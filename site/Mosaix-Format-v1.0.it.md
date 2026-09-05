---
title: Mosaix Format — Specifica v1.0
version: 1.0.0
status: pubblicata
updated: 2026-09-04
license: CC BY-SA 4.0
author: Andrea Fiorino
summary: "Formato a livello di file per vault di conoscenza fatti di note atomiche e autodescrittive, che le macchine recuperano una alla volta e le persone leggono come documenti composti."
keywords: [vault di conoscenza, note atomiche, frontmatter, wikilink, markdown, contesto LLM, contesto delimitato, specifica]
---

# Mosaix Format — Specifica v1.0

> Traduzione di cortesia. In caso di discrepanza fa fede la versione inglese (`Mosaix-Format-v1.0.en.md`).

## 0. Stato del documento

Questo documento specifica il **Mosaix Format**, versione 1.0. Il nome viene dal mosaico: ogni nota è una tessera che sta in piedi da sola, e l'immagine esiste solo nell'insieme. È rilasciato con licenza [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/): si può copiare, adattare e ridistribuire, anche commercialmente, citando l'autore e rilasciando le derivate con la stessa licenza. Il nome "Mosaix Format" e la numerazione di versione fanno parte della specifica: un vault può dichiararsi conforme a "Mosaix 1.0" solo se soddisfa il §10.

Le parole chiave DEVE, NON DEVE, DOVREBBE, NON DOVREBBE e PUÒ vanno interpretate come in RFC 2119 (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY).

## 1. Scopo

Un vault in questo formato è un corpo di conoscenza su un dominio (un cliente, un prodotto, una base di codice, un progetto) scritto in modo che:

1. **una macchina possa recuperare una nota alla volta** e avere abbastanza contesto per agire, senza leggere il resto del vault;
2. **una persona possa leggere molte note come un solo documento**, senza aprirle una a una;
3. **niente vada perso o sovrascritto in silenzio**: le contraddizioni si registrano, le note superate si marcano, le modifiche delle macchine si propongono invece di applicarle.

Il formato è volutamente piccolo. Fissa *cosa porta con sé una nota* e *quali regole rispetta il vault*. Non fissa come le note vengono prodotte, arricchite, cercate, ordinate, composte o modificate: quelle sono implementazioni (§8).

## 2. Substrato

Un vault Mosaix è un albero di directory di file di testo.

- Le note sono file UTF-8 con estensione `.md` in Markdown CommonMark.
- Ogni nota PUÒ iniziare con un blocco frontmatter YAML delimitato da righe `---`.
- Le note si riferiscono l'una all'altra con **wikilink**: `[[Titolo nota]]`, opzionalmente `[[Titolo nota|testo]]`, opzionalmente con un'intestazione `[[Titolo nota#Sezione]]`. Un wikilink si risolve sul **nome file senza estensione** della nota destinazione, in modo case-sensitive, ovunque nel vault.
- Gli embed usano `![[Titolo nota]]` e `![[file.ext]]`, risolti allo stesso modo.
- I tag sono token `#tag` o `#spazio/tag` nel corpo, oppure voci della lista `tags` nel frontmatter. Le due forme sono equivalenti.

Qualunque strumento che legge file Markdown da disco legge un vault Mosaix. Non serve alcuna applicazione. Obsidian è l'applicazione host di riferimento (§9), non una dipendenza.

## 3. La nota (la "tessera")

Una **nota** risponde a una domanda. Se una bozza risponde a due, sono due note. La lunghezza del corpo non è vincolata; lo è l'*ambito*.

### 3.1 Frontmatter — CORE (obbligatorio per la conformità)

| Chiave | Tipo | Scritta da | Scopo |
|---|---|---|---|
| `title` | stringa | persona, o derivata dal nome file | il nome del nodo |
| `updated` | data `AAAA-MM-GG` | persona o sistema | ultima modifica sostanziale; governa l'obsolescenza della nota |
| `tags` | lista di stringhe | persona | tassonomia e filtri |
| `summary` | stringa, 120–240 caratteri | persona o arricchimento | una frase dichiarativa che dice cosa contiene la nota; l'unità che una macchina legge per prima |
| `keywords` | lista di 6–8 stringhe minuscole | persona o arricchimento | come qualcuno cercherebbe questa nota: sinonimi, formulazioni parlate, domande. NON DEVE duplicare `tags` |
| `entities` | lista di `{name, type}`, al massimo 12 | arricchimento o persona | cose con un nome citate nella nota; `type` DEVE essere uno fra `person`, `company`, `product`, `project`, `tool`, `place`, `document`, `event`, oppure un tipo dichiarato nella nota meta (§5.4) |
| `relations` | lista di `{from, type, to}` | arricchimento o persona | collegamenti tipizzati fra entità con nome; `type` è una breve locuzione verbale al presente (`owns`, `depends on`, `supplies`), oppure un valore del vocabolario di relazioni del vault se dichiarato |
| `links` | lista di stringhe | arricchimento o persona | destinazioni wikilink a cui questa nota punta; ognuna DEVE risolversi in una nota esistente |
| `rev` | stringa, 12 caratteri esadecimali | sistema | hash del corpo al momento in cui `entities`, `relations` e `links` sono stati calcolati; se non coincide con il corpo attuale i metadati sono obsoleti |

Note:

- `summary` NON DEVE ripetere il titolo e NON DEVE iniziare con "Questa nota…" o equivalente. Si scrive per chi non ha aperto la nota.
- **Alias.** Un vault PUÒ scrivere qualunque chiave CORE con un alias dichiarato nella nota meta (§5.4); i checker trattano un alias dichiarato come la chiave canonica. I seguenti alias sono riconosciuti di default, così che i vault creati prima di questa versione restino conformi: `mcp_entita` → `entities`, `mcp_relazioni` → `relations`, `mcp_collegamenti` → `links`, `mcp_rev` → `rev`, `aggiornato` → `updated`, `titolo` → `title`, `riassunto` → `summary`, `parole_chiave` → `keywords`; nelle voci di entità e relazioni, `nome` → `name`, `tipo` → `type`, `da` → `from`, `a` → `to`; e i valori di tipo entità `persona azienda prodotto progetto strumento luogo documento evento` → `person company product project tool place document event`.
- `entities` DOVREBBE elencare al massimo 12 voci. Una nota che nomina più cose di così di solito risponde a più di una domanda (R1); un checker segnala l'eccesso come avviso. I MOC e la nota meta sono esenti: elencare è il loro compito.
- L'ordine canonico delle chiavi è `title · updated · [chiavi di dominio] · summary · keywords · entities · relations · links · rev`. Gli strumenti DOVREBBERO preservarlo.
- **Il corpo non viene mai toccato dalle operazioni sui metadati.** Qualunque processo che riscrive il frontmatter DEVE lasciare il corpo identico byte per byte.

### 3.2 Frontmatter — assi di affidabilità (raccomandati)

Due domande indipendenti, con due marcatori indipendenti. POSSONO essere espressi come chiavi frontmatter, come tag, o come simboli inline nel corpo; un vault DEVE scegliere una convenzione e documentarla nella nota meta (§5.4). La convenzione raccomandata è una chiave `status`.

**Asse A — è vero?**

| Marcatore | Valore `status` | Significato |
|---|---|---|
| ✅ da fonte | `sourced` | viene da un documento, un sistema o una conversazione di lavoro; la fonte è nominata |
| ⚠️ da confermare | `to-confirm` | ipotesi, bozza, placeholder; non ancora validato |
| — superato | `superseded` | non più valido, tenuto al suo posto (R7) |

**Asse B — esiste?** (dove il vault descrive qualcosa in costruzione)

| Marcatore | Significato |
|---|---|
| 🟢 implementato | esiste e funziona come descritto |
| 🟡 deciso | deciso, non costruito |
| ⚠️ aperto | non deciso |
| ❌ escluso | deciso di non farlo |

Un'affermazione può essere ✅ da fonte e 🟡 non implementata: un fatto verificato su qualcosa che ancora non esiste. Tenere separati gli assi è ciò che permette, mesi dopo, di distinguere un'intenzione da un fatto. Alias di default per i valori di `status`: `ok` → `sourced`, `confermare` → `to-confirm`, `superato` → `superseded`; `stato` → `status`.

### 3.3 Frontmatter — chiavi di dominio (per vault)

Un vault PUÒ aggiungere le chiavi che gli servono (`campaign`, `client`, `country`, `reliability`, `stage`…). Le chiavi di dominio DEVONO essere dichiarate nella nota meta (§5.4) con i valori ammessi. Le chiavi non dichiarate sono un avviso di conformità, non un errore.

### 3.4 Tipi di nota

La chiave `type` (o un tag `#type/...`) PUÒ classificare le note. Tre tipi hanno significato a livello di formato:

| `type` | Ruolo |
|---|---|
| `moc` | *Map of Content*: punto d'ingresso che racconta un'area ed elenca le sue note. Un vault DEVE averne almeno uno, di solito `Home` o `00-Indice`. |
| `synthesis` | sintesi scritta per essere letta da sola come contesto per un compito; vive in `_synthesis/` (§5.2) |
| `document` | **documento composto**: nota il cui frontmatter elenca le note da cui è assemblata (§6) |

Alias di default: `tipo` → `type`; `sintesi` → `synthesis`; `documento` → `document`.

### 3.5 Esempio

```markdown
---
title: Portwest — scheda player
updated: 2026-08-12
tags: [player, dpi, competitor]
status: sourced
summary: "Produttore irlandese di DPI presente in oltre 130 paesi con una linea a marchio proprio che batte i distributori sul prezzo; il competitor di riferimento per il prezzo."
keywords: [portwest, competitor di prezzo, marchio proprio, produttore dpi irlandese, 130 paesi, private label]
entities:
  - {name: Portwest, type: company}
relations:
  - {from: Portwest, type: competes with, to: Ateş}
links: [Consolidamento DPI 2025, Scenari strategici]
rev: a81c0d33ef21
---

# Portwest — scheda player

Vende in oltre 130 paesi. La linea a marchio proprio batte i distributori. ✅ da fonte (sito aziendale, 2026-07).
Vedi [[Consolidamento DPI 2025]] e [[Scenari strategici]].
```

## 4. Collegamenti e grafo

- Una nota DEVE avere almeno un wikilink entrante da un'altra nota o da un MOC. Una nota senza link entranti è **orfana** ed è un errore di conformità.
- Ogni wikilink DEVE risolversi. Un wikilink non risolto è un errore di conformità.
- `links` è lo specchio leggibile dalla macchina dei wikilink uscenti della nota. PUÒ essere un sottoinsieme dei wikilink nel corpo; NON DEVE contenere destinazioni che non esistono.
- Le note, le loro `entities`, `relations` e i wikilink formano insieme il grafo del vault. Il grafo è derivato dai file; non è mai la fonte di verità.

## 5. Struttura del vault

### 5.1 Layout libero, nomi riservati

Le cartelle sono libere. I prefissi numerati (`00-Indice`, `01-Azienda`, …) sono una convenzione comune e vanno letti come **ordine di lettura**, non di costruzione. Tre nomi di cartella sono riservati:

| Cartella | Contenuto |
|---|---|
| `_meta/` | il governo del vault stesso: nota meta, tassonomia, domande aperte (§5.4) |
| `_synthesis/` | note di sintesi scritte per essere consumate da sole come contesto |
| `_inbox/` | materiale entrato nel vault ma non ancora trasformato in note; niente in `_inbox/` conta per la conformità |

`_sintesi/` è riconosciuta come alias di `_synthesis/`. Un vault PUÒ inoltre tenere una cartella `_private/` esclusa dal controllo di versione per materiale di lavoro personale. Niente in `_private/` fa parte del vault. Le cartelle che contengono esportazioni di contenuti che non sono note POSSONO essere dichiarate come **payload** nella nota meta e sono allora escluse dal controllo del frontmatter.

### 5.2 Note di sintesi

Una nota in `_synthesis/` condensa un'area del vault in un testo leggibile da solo. DEVE linkare le note che riassume. È l'unità raccomandata da consegnare a una macchina o a un nuovo arrivato prima di qualunque compito in quell'area. *Non* sostituisce le note: quando è in disaccordo con una nota, vince la nota e la sintesi è obsoleta.

### 5.3 Registro delle domande aperte

Il vault DEVE avere una nota che elenca ciò che non si sa ancora o è contraddittorio. La sua posizione canonica è `_meta/Open questions.md`. Ogni voce registra: la domanda, le versioni in competizione con date e fonti, la conseguenza pratica di scegliere l'una o l'altra, e chi dovrebbe risolverla. `Assunzioni da confermare.md` e `Domande aperte.md` sono riconosciuti come alias.

### 5.4 Nota meta

Il vault DEVE avere una nota (`_meta/Conventions.md`, oppure un `README.md` / `CLAUDE.md` alla radice) che dichiara: il contratto delle cartelle (a quale domanda risponde ciascuna), la convenzione di affidabilità scelta (§3.2), le chiavi di dominio e i loro valori (§3.3), la tassonomia dei tag con ogni tag in uso, eventuali alias per le chiavi CORE, eventuali tipi di entità aggiuntivi, un eventuale vocabolario chiuso di relazioni, eventuali cartelle payload, e le persone responsabili delle aree. La tassonomia PUÒ vivere in una nota propria dentro `_meta/`. **Un tag usato in una nota e assente dalla tassonomia è un avviso di conformità.** La tassonomia si aggiorna nella stessa modifica che introduce il tag.

La nota meta dichiara questi elementi nel proprio frontmatter, così che gli strumenti possano leggerli. Questo blocco fa parte della 1.0: il checker di riferimento lo legge (`aliases`, `entity_types`, `relation_types`, `payload`, e `tags` come tassonomia).


```yaml
mosaix: "1.0"
folders: {01-Azienda: chi sono, 02-Mercato: dove vendono}
reliability: {key: status, values: [sourced, to-confirm, superseded]}
tags: [moc, meta, ledger, player, mercato]
domain_keys: {client: string, country: ISO-3166 alpha-2}
aliases: {aggiornato: updated}
entity_types: [department, regulation]
relation_types: [owns, supplies, competes with, depends on]
payload: [exports/]
maintainers: [{name: A. Fiorino, area: mercato}]
```

Tutte opzionali tranne `mosaix`.

## 6. Documenti composti

Le note atomiche sono per le macchine. Le persone leggono documenti. Il formato definisce quindi un tipo di nota che è una **vista su altre note** senza duplicarle.

Una nota con `type: document` DEVE avere:

| Chiave | Tipo | Significato |
|---|---|---|
| `fragments` | lista ordinata di titoli di note | le note che compongono il documento, in ordine di lettura |
| `pool` | lista di titoli di note (opzionale) | note candidate considerate ma non incluse |
| `layout` | mappa (opzionale) | indicazioni di presentazione (copertina, sezioni, formato pagina); libera |

Alias di default: `mcp_frammenti` → `fragments`, `mcp_pool` → `pool`, `mcp_layout` → `layout`.

Esempio di frontmatter di un documento composto, con una mappa `layout`. La mappa è libera; le chiavi mostrate sono quelle usate dalle implementazioni di riferimento, e uno strumento DEVE ignorare le chiavi che non capisce:

```yaml
type: document
fragments: [Consolidamento DPI 2025, Portwest — scheda player, Scenari strategici]
pool: [Fiere DPI Europa 2026]
layout:
  cover: {title: Brief di ingresso — DPI, Europa, subtitle: Lettura per il board, date: 2026-09-03}
  page: A4
  sections:
    - {title: Mercato, fragments: [Consolidamento DPI 2025, Portwest — scheda player]}
    - {title: Raccomandazione, fragments: [Scenari strategici]}
  show: [summary, status]      # cosa stampare del frontmatter di ogni frammento
```

Il corpo PUÒ contenere una narrazione che collega i frammenti e PUÒ incorporarli con `![[Nota]]`. La regola è: **i frammenti restano atomici e separati; il documento è solo la vista che li unisce.** Una modifica fatta leggendo il documento composto appartiene alla nota del frammento, non al documento.

Poiché il documento composto è a sua volta una nota, eredita gratis versionamento, revisione, ricerca e collegamenti. Non serve un secondo canale di archiviazione.

## 7. Regole del vault

Un vault conforme rispetta quanto segue. R1–R5 sono verificabili dai file; R6–R8 sono regole di processo che la nota meta si impegna a rispettare.

- **R1 — Atomicità.** Una nota risponde a una domanda.
- **R2 — Autodescrizione.** Ogni nota porta il frontmatter CORE (§3.1).
- **R3 — Connessione.** Nessuna orfana, nessun link rotto (§4).
- **R4 — Tassonomia dichiarata.** Ogni tag e ogni chiave di dominio è dichiarata nella nota meta (§5.4).
- **R5 — Composizione, non duplicazione.** Il contenuto che va letto insieme si unisce con un documento composto (§6) o una sintesi (§5.2), mai copiandolo.
- **R6 — Registrare, non risolvere.** Una contraddizione fra note si inserisce nel registro delle domande aperte con entrambe le versioni. Nessuno sceglie un vincitore in silenzio. Numeri, prezzi, date e impegni verso terzi non si scelgono mai per conto del proprietario.
- **R7 — Superare, non cancellare.** Una nota non più valida si marca come superata (`status: superseded`, `#status/archived`, o un banner) e si lascia al suo posto, perché altre note la linkano. La cancellazione è riservata alle note create per errore.
- **R8 — Proporre, non applicare.** Qualunque processo automatico che scrive nel vault scrive su un branch, una pull request o un'area di staging che una persona rivede. I processi automatici non scrivono mai sulla linea principale del vault. `rev` è il meccanismo che permette a chi rivede di vedere se una proposta è stata fatta sul corpo attuale.

## 8. Fuori ambito

I seguenti aspetti **non** sono definiti da questa specifica. Sono implementazioni, e implementazioni diverse possono competere su di essi producendo e consumando vault conformi:

- come vengono generati `summary`, `keywords`, `entities`, `relations`, `links` (arricchimento);
- come i documenti vengono trasformati in note (ingestione, suddivisione, deduplicazione);
- come le note vengono recuperate per un compito (ricerca, ranking, embedding, budget di contesto);
- come i documenti composti vengono modificati, impaginati o stampati (editor);
- come il vault viene esposto agli agenti (strumenti MCP, API) o sincronizzato (git, mirror);
- come il grafo viene visualizzato.

Un vault prodotto a mano, senza alcuno strumento, può essere pienamente conforme.

## 9. Profilo dell'applicazione host: Obsidian

Obsidian è l'host di riferimento: la risoluzione di wikilink ed embed, la sintassi dei tag e la gestione del frontmatter coincidono esattamente con il §2. Un vault PUÒ usare in aggiunta funzioni di Obsidian; sono **fuori dal formato** e NON DEVONO essere richieste da alcuna regola:

- Query Dataview, Bases (`.base`), Canvas, plugin mappa: viste, non contenuto. DOVREBBERO vivere dentro le note così da essere versionate con il vault.
- Callout (`> [!tip]`): un vault PUÒ assegnare un significato ai tipi di callout; in tal caso il significato è documentato nella nota meta.
- La cartella `.obsidian/` è stato dell'host, non contenuto del vault; `workspace.json` DOVREBBE essere escluso dal controllo di versione.

Altri host noti che leggono il substrato (§2): Logseq, Foam, Dendron, Zettlr, e gli editor Markdown con estensioni per i wikilink.

## 10. Conformità

Un vault è **conforme a Mosaix 1.0** quando un controllo sui suoi file riporta zero errori per:

| Controllo | Regola |
|---|---|
| Frontmatter presente su ogni nota fuori da `_inbox/`, `_private/` e dalle cartelle payload dichiarate | R2 |
| `title`, `updated`, `tags`, `summary`, `keywords`, `rev` presenti (canonici o con alias) | R2 |
| lunghezza di `summary` 120–240 caratteri | R2 |
| numero di `keywords` 6–8 | R2 |
| `entities` presente su ≥ 80 % delle note; ogni `type` nell'insieme ammesso | R2 |
| ogni wikilink e ogni voce di `links` si risolve | R3 |
| nessuna nota orfana | R3 |
| almeno una nota `type: moc` | §3.4 |
| esistono il registro delle domande aperte e la nota meta | §5.3, §5.4 |
| ogni nota `type: document` elenca ≥ 2 `fragments`, tutti risolti | §6 |

e zero o più **avvisi** per: tag non dichiarati nella tassonomia, chiavi di dominio non dichiarate, `rev` più vecchio del corpo (metadati obsoleti), note senza alcun marcatore di affidabilità, più di 12 `entities` su una nota che non è un MOC.

Un checker di riferimento, `audit_reference.py`, accompagna questa specifica. Usa solo la libreria standard di Python e produce la tabella sopra. Il suo output è il rapporto di conformità.

## 11. Versionamento della specifica

Le versioni seguono `MAJOR.MINOR.PATCH`. Una versione MINOR può aggiungere chiavi opzionali, tipi di nota o avvisi; non trasforma mai un vault conforme in uno non conforme. Una versione MAJOR può farlo. I vault DOVREBBERO dichiarare la versione a cui puntano nella nota meta (`mosaix: "1.0"`).

In discussione per la 1.1, non parte della 1.0: una chiave `id` stabile perché i link sopravvivano ai rinomini; una chiave `question` che registra la singola domanda a cui la nota risponde; un vocabolario chiuso di relazioni obbligatorio; un registro delle entità con alias; `origin` (human · distilled · observed) e `as_of`, la data in cui un fatto era vero.

## 12. Riconoscimenti e provenienza

Il formato è stato estratto da tre vault in uso in produzione (documentazione di codice, intelligence di mercato industriale, marketing per la formazione), misurando quali convenzioni ciascuno aveva inventato e tenendo l'intersezione su cui una macchina poteva contare. Quei vault usavano nomi di chiave in italiano; sono mantenuti come alias di default così che restino conformi senza modifiche. Il modello di affidabilità a due assi, il registro delle domande aperte e la regola superare-non-cancellare vengono dalla pratica di lavorare con più fonti di date diverse. Il tipo documento composto viene dall'osservazione che un vault di buone note atomiche è illeggibile per le persone che ne hanno più bisogno.

---

**Per citare questa specifica.** Fiorino, A. (2026). *Mosaix Format — Specification v1.0.0*. Boom Digital. https://mosaixformat.org — tag sorgente `mosaix-format/spec@v1.0.0`.

*Mosaix Format v1.0 — un formato di SLIM — © 2026 Andrea Fiorino — CC BY-SA 4.0.*
