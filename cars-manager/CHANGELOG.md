# Changelog

Tutte le modifiche notevoli al progetto saranno documentate in questo file.

Il formato si basa su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto segue il [Versionamento Semantico](https://semver.org/lang/it/).

---

## [1.0.6] - 2026-05-26

### Aggiunto

- Modifica documenti: possibilità di aggiornare tipo, titolo, note e costo di un documento già caricato
- Sostituzione file: nel form di modifica è possibile caricare un nuovo file che sostituisce il precedente (il vecchio viene rimosso dal disco)
- Campo **Costo (€)** nella gestione documentale per associare una spesa al documento (es. fattura officina)
- Badge costo visibile nella lista documenti

---

## [1.0.5] - 2026-05-25

### Aggiunto

- Campo Costo (€) nel form di creazione/modifica scadenza
- Ricorrenza quadriennale (ogni 48 mesi) tra le opzioni di periodicità

---

## [1.0.4] - 2026-05-25

### Aggiunto

- Scadenze periodiche: possibilità di impostare una ricorrenza (6 mesi, annuale,
  biennale, triennale) su ogni scadenza
- Al completamento di una scadenza ricorrente viene creata automaticamente
  la scadenza successiva con la data calcolata in base all'intervallo
- Migrazione automatica del database per i record esistenti

---

## [1.0.3] - 2026-05-25

### Corretto

- Fix avvio addon: rimosso `CMD ["/init"]` dal Dockerfile — l'immagine base HA
  usa già `ENTRYPOINT ["/init"]`, la duplicazione causava `s6-overlay-suexec:
fatal: can only run as pid 1`
- Porta cambiata da 5000 a 8000 per evitare conflitti

---

## [1.0.2] - 2026-05-25

### Corretto

- Fix critico: opzioni SMTP con stringa vuota `""` causavano fallimento della validazione
  dello schema HA (`str?` non ammette stringa vuota, solo assente/null)
- Cambio tipo schema `smtp_password` da `str?` a `password?` (campo mascherato in UI)

---

## [1.0.1] - 2026-05-25

### Corretto

- Fix errore Jinja2: filtro `enumerate` non disponibile nella pagina storico chilometraggio
- Fix errore Jinja2: test `in` e `eq` non validi in `selectattr` nella pagina dettaglio auto
- Risolto problema installazione pip su Alpine con PEP 668 (`--break-system-packages`)
- Rimossa dipendenza non necessaria `python-magic`

---

## [1.0.0] - 2026-05-22

### Aggiunto

- Gestione autovetture: crea e visualizza il tuo garage di famiglia
- Calendario scadenze per manutenzioni, revisioni, bollo e assicurazioni
- Caricamento documenti (libretto, certificati assicurativi, fatture)
- Segnalazione guasti e malfunzionamenti con livelli di gravità
- Rubrica contatti per concessionarie e autofficine
- Invio email per richiesta preventivo direttamente da un guasto segnalato
- Aggiornamento periodico del chilometraggio con storico
- Reportistica con grafici su costi, guasti e manutenzioni
- Dashboard riepilogativa con scadenze imminenti e guasti aperti
- Supporto ingress di Home Assistant
- Configurazione SMTP per invio email tramite interfaccia HA
