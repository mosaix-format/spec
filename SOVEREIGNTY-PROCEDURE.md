---
title: Procedura di verifica della sovranità
tags: [mnemora, sovranità, sicurezza, compliance, governance]
updated: 2026-09-13
summary: "Procedura eseguibile in 20 minuti per verificare le garanzie di sovranità: inferenza e corpus. Richiesta da 6/6 del panel R13."
keywords: [sovranità, byok, modello interno, github, drive, procedura verifica, test rete, log egress, dpa]
mcp_entita:
  - {nome: Mnemora, tipo: prodotto}
  - {nome: vault-mcp, tipo: strumento}
mcp_relazioni:
  - {da: Mnemora, tipo: verifica sovranità con, a: procedura 6 passi}
mcp_collegamenti: [MOSAIX_HAREM_DECISIONI_R13, SOLUZIONE, QUADRO-DEL-SERVIZIO]
---

# Procedura di verifica della sovranità

**Perché questo documento**: 6/6 del panel R13 hanno chiesto una procedura eseguibile, non una promessa. *«"Nessun dato esce" è marketing; "ecco come lo verifichi in 20 minuti" è vendibile.»* (CTO, R13)

**Consenso R13**: Nessuno crede alla frase; tutti chiedono prove **eseguibili dal cliente**.

---

## Le due sovranità — distinzione critica

**Trovato in R13** (PM concorrente): la sovranità del modello non è la sovranità del corpus. Sono due garanzie diverse.

### Sovranità dell'inferenza

**Cosa garantisce**: nessun fornitore di modelli vede i dati del cliente.

**Come si ottiene**: 
- Modello interno via BYOK (Bring Your Own Key)
- `base_url` configurabile, puntato verso endpoint interno
- Nessun fallback silenzioso al cloud

**Configurazioni conformi**:
- Drive + modello interno
- GitHub del cliente + modello interno
- Origin locale + modello interno

### Sovranità del corpus

**Cosa garantisce**: nessun terzo vede i documenti del cliente.

**Configurazioni conformi**:
- **GitHub del cliente (organizzazione propria) + modello interno**: solo l'organizzazione del cliente ha accesso
- **Origin locale + modello interno**: solo il volume del cliente

**Configurazione NON conforme sul corpus** (trovato in R13):
> **Drive + modello interno**: il fornitore LLM non vede i dati (sovranità dell'inferenza), ma **Google ha comunque i blob a riposo**. È sovranità dell'inferenza, non del corpus.

**Tabella delle configurazioni**:

| Configurazione | Sovranità inferenza | Sovranità corpus | Chi ha accesso al corpus |
|---|---|---|---|
| Drive + modello cloud | ❌ | ❌ | Google + fornitore LLM |
| Drive + BYOK cloud | ⚠️ (contrattuale) | ❌ | Google + fornitore LLM (per contratto) |
| **Drive + modello interno** | ✅ | ❌ | **Google** |
| **GitHub cliente + modello interno** | ✅ | ✅ | Solo organizzazione cliente |
| **Origin locale + modello interno** | ✅ | ✅ | Solo volume cliente |

**Dichiarazione obbligatoria** (R13): *«Se il vault sta su Drive, Google ha comunque i blob a riposo: sovranità del modello non è sovranità del corpus. Se non lo dite voi, lo dico io in call competitive e vi apro il fianco.»* (PM concorrente)

---

## La procedura in sei passi

**Target**: cliente con requisiti di compliance o governance rigorosi (procurement, legal, settori regolati).

**Tempo stimato**: 20 minuti.

**Output**: checklist firmata dal cliente che conferma le garanzie.

### Passo 1 — Installazione locale e configurazione modello interno

**Azione**:
1. Installare Mnemora in locale: `docker compose up`
2. Configurare `base_url` verso il modello interno del cliente (es. endpoint interno aziendale)
3. Verificare che il sistema si avvii senza errori

**Cosa dimostra**: Il sistema può girare completamente on-premise.

**Documentazione richiesta**: endpoint del modello interno, credenziali (se necessarie).

---

### Passo 2 — Test di rete: egress negato

**Azione**:
1. Configurare firewall per **negare l'egress verso tutto** tranne l'endpoint del modello interno configurato in Passo 1
2. Eseguire tutte le funzioni promise:
   - Arricchimento note (read, search, enrichment)
   - Chat con agenti (via MCP tools)
   - Scrittura mediata (apply_write)
   - Compositore documenti
3. Verificare che **il sistema funziona al 100%** delle funzioni dichiarate

**Cosa dimostra**: Nessuna chiamata nascosta verso servizi esterni. Se funziona con egress bloccato, non può esfiltrare dati.

**Output atteso**: Log di rete che mostra **zero tentativi di connessione** verso endpoint esterni non autorizzati.

---

### Passo 3 — Nessun fallback silenzioso al cloud

**Azione**:
1. Spegnere il modello interno (o bloccare il suo endpoint)
2. Tentare un'operazione che richiede il modello (es. arricchimento, chat)
3. Verificare che il sistema **si ferma e notifica l'errore esplicitamente**

**Cosa dimostra**: Non c'è degradazione "gentile" verso il cloud. Se il modello interno non risponde, il sistema non chiama in segreto un endpoint cloud di backup.

**Citazione R13** (PM concorrente): *«Se degrada "in modo gentile" verso il cloud, avete mentito.»*

**Output atteso**: Errore esplicito (`ERR_MODEL_UNAVAILABLE` o simile), nessuna chiamata a servizi cloud esterni.

---

### Passo 4 — Log delle chiamate in uscita ispezionabile

**Azione**:
1. Abilitare logging completo delle chiamate in uscita
2. Eseguire una sessione di lavoro tipica (arricchimento + chat + scrittura)
3. Ispezionare i log per verificare:
   - **Destinazione**: solo `{base_url}/models` (o endpoint configurato)
   - **Impronta del payload**: nessun dato sensibile in chiaro (hash o dimensione del payload)

**Cosa dimostra**: Trasparenza totale su dove vanno i dati. Il cliente può auditare ogni chiamata.

**Documentazione richiesta**: Formato log standardizzato, retention policy, accesso CLI o web per ispezione.

**Citazione R13** (procurement): *«"Non inviamo il contenuto" non basta se un errore serializza il prompt in un sistema di osservabilità.»*

---

### Passo 5 — Prova di ricostruzione: nessuno stato nascosto

**Azione**:
1. Cancellare completamente l'indice locale e il clone del vault
2. Rigenerare tutto dal repository sorgente (GitHub/Drive/locale)
3. Verificare che:
   - La ricerca torna **identica** a prima
   - Tutte le note sono presenti e corrette
   - Nessuna perdita di dati

**Cosa dimostra**: Tutto è riderivabile dalla fonte di verità. Nessuno stato intermedio critico vive solo nel sistema Mnemora.

**Output atteso**: Diff tra indice pre- e post-ricostruzione = vuoto.

---

### Passo 6 — Dichiarazione esplicita dei limiti

**Azione**: Il fornitore (Mnemora) consegna un documento che dichiara **esplicitamente**:

1. **Dove sta il corpus**:
   - Se su GitHub del cliente: solo l'organizzazione del cliente ha accesso
   - Se su Drive: **Google ha i blob a riposo** (non sovranità del corpus)
   - Se locale: solo il volume del cliente

2. **Chi vede cosa**:
   - Fornitore modelli: **mai** (se configurato con modello interno)
   - Mnemora (il servizio): **mai** (nessun telemetry, nessun log centralizzato)
   - Google (se Drive): **sempre i blob a riposo**

3. **Cosa succede in caso di errore**:
   - Nessun fallback cloud automatico
   - Log di errore scritto localmente, mai inviato a servizi esterni

4. **DPA (Data Processing Agreement)**:
   - Sub-responsabili dichiarati (es. Google se Drive, nessuno se GitHub/locale)
   - Procedura di incidente (chi notifica, tempi, remediation)

**Citazione R13** (procurement): *«DPA, sub-responsabili, procedura di incidente.»*

---

## Prove richieste dal panel (R13)

| Prova | Ruolo richiedente | Coperta da |
|---|---|---|
| `docker compose up` locale | CTO, titolare | Passo 1 |
| Test di rete: nega egress → sistema funziona | CTO, PM, sviluppatore | Passo 2 |
| Nessun fallback silenzioso al cloud | PM | Passo 3 |
| Audit del codice per telemetria nascosta | CTO, procurement, PM | Passo 4 |
| `{base_url}/models` come unico punto di contatto esterno | DeepSeek | Passo 4 |
| DPA, sub-responsabili, procedura di incidente | procurement | Passo 6 |
| Prova di ricostruzione (cancella → rigenera → identico) | CTO | Passo 5 |
| Dichiarazione esplicita: Drive = Google ha i blob | PM | Passo 6 |

---

## Cosa mettere in pagina (landing/commerciale)

**Non mettere**: *"Nessun dato lascia il perimetro del cliente"* senza spiegare come verificarlo.

**Mettere**:
1. **Headline**: *"Sovranità verificabile in 20 minuti"* (o simile)
2. **Link alla procedura** (questo documento o versione pubblica)
3. **Configurazioni supportate** (tabella sopra, chiara e onesta)
4. **CTA**: *"Scarica la checklist di verifica"* → PDF della procedura a 6 passi

**Citazione R13** (6/6): *«Una checklist eseguibile — "ecco come lo verifichi in 20 minuti" — con test di rete, log delle chiamate in uscita, e i limiti dichiarati. "Nessun dato esce" è marketing; "ecco come lo verifichi" è vendibile.»*

---

## Errori da evitare

1. **Non dire «nessun dato esce» senza questa procedura** (6/6 R13)
2. **Non omettere che su Drive i blob restano a Google** (PM R13)
3. **Non degradare in modo gentile verso il cloud** se il modello interno non risponde (PM R13)
4. **Non presentare la sovranità dell'inferenza come se fosse anche sovranità del corpus** — sono due cose diverse

---

## Fonti

- `MOSAIX_HAREM_DECISIONI_R13.md` §1.2 (prova per sovranità), §1.3 (buco Drive/Google)
- `SOLUZIONE.md` §5 (checklist a 6 passi)
- `QUADRO-DEL-SERVIZIO.md` §6 (da correggere con distinzione inferenza/corpus)

---

## Prossimi passi

1. **Correggere `QUADRO-DEL-SERVIZIO.md` §6**: integrare la distinzione inferenza/corpus (azione #1 di R13)
2. **Versione pubblica di questo documento**: pubblicare su sito Mnemora come prova scaricabile
3. **DPA template**: preparare il Data Processing Agreement con sub-responsabili dichiarati
4. **Script di test automatico** per Passo 2 (egress test) e Passo 5 (ricostruzione)
