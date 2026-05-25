# Changelog

Tutte le modifiche notevoli al progetto saranno documentate in questo file.

Il formato si basa su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto segue il [Versionamento Semantico](https://semver.org/lang/it/).

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
