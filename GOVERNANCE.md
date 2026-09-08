# Governance — Mosaix Format

## 1. Versioning policy (SemVer)

- **MAJOR** (2.0, 3.0...): rompe backward compatibility. Un vault conformant
  alla versione precedente potrebbe non essere conformant alla nuova. Esempi:
  rimuovere una CORE key, cambiare la semantica di una regola, rendere obbligatoria
  una chiave prima opzionale.

- **MINOR** (1.1, 1.2...): aggiunge chiavi opzionali, nuove raccomandazioni,
  o tooling. Non rompe mai la conformità di vault esistenti. Esempi: aggiungere
  `question` come CORE key opzionale, nuovi entity types, nuovi warning nel checker.

- **PATCH** (1.0.1, 1.0.2...): fix a typo nella spec, chiarimenti testuali,
  correzioni al checker senza cambi semantici, aggiornamenti alla documentazione.

Il numero di versione corrente è in `spec.yaml` (source of truth).

## 2. RFC process

Chiunque può proporre un cambiamento:

1. Apri una Issue su GitHub con il template "RFC"
2. Il template richiede:
   - **Problem**: quale problema risolve questa proposta
   - **Proposal**: cosa cambia nella spec (testo specifico, non vago)
   - **Backward compatibility**: questo cambiamento rompe vault esistenti? Come?
   - **Checker impact**: cosa cambia in `audit_reference.py`
   - **Skill impact**: quali skill vanno aggiornate
   - **Conformance corpus impact**: quali test case vanno aggiunti/modificati
3. Discussione aperta per 30 giorni (minimo)
4. Decisione finale del maintainer con motivazione scritta nella Issue
5. Se accettata: PR che include modifiche a TUTTI i file coinvolti
   (spec, `spec.yaml`, checker, skill, conformance corpus, `CHANGELOG.md`)

Un RFC non viene mai accettato senza la PR completa — la modifica alla spec
da sola non basta.

## 3. Backward compatibility guarantee

- Le CORE keys non vengono mai rimosse in una MINOR
- Le regole (R1–R7) non cambiano semantica in una MINOR
- Nuove chiavi aggiunte in MINOR sono opzionali per almeno una MINOR release
- Il checker versione N deve poter validare vault conformi a N-1 con al più
  warning (mai errori nuovi su vault prima conformi)
- Le raccomandazioni (come R8) possono essere aggiunte in MINOR senza vincoli
  di backward compatibility (non sono normative)

## 4. Deprecation policy

- Una feature deprecata genera WARNING per almeno una MINOR release prima
  di diventare ERROR
- Documentata nel `CHANGELOG.md` con data e versione di rimozione prevista
- Esempio: `id` è warning in v1.0 → diventerà error in v2.0

## 5. Version declaration

Una nota PUÒ dichiarare `mosaix_version: 1.1` nel frontmatter. Il checker
valida contro la versione dichiarata. Se non dichiarata, valida contro
l'ultima versione supportata dal checker.

Questo permette vault con note a versioni diverse durante la migrazione.

## 6. Maintainer

BDFL (Benevolent Dictator For Life): Andrea Fiorino
Contact: via GitHub Issues

Il BDFL può delegare la revisione di RFC a contributor fidati, ma la decisione
finale resta sua. Se il BDFL diventa inattivo per 12+ mesi senza nominare un
successore, il contributor con più RFC accettate può assumere il ruolo aprendo
una Issue di successione.

## 7. Code of conduct

Il progetto adotta il [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
Comportamenti inaccettabili vanno segnalati via Issue privata o email.
