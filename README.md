# CARS_M – Gestione Autovetture di Famiglia

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Addon-blue?logo=home-assistant)](https://www.home-assistant.io/)
[![Version](https://img.shields.io/badge/version-1.0.7-green)](cars-manager/CHANGELOG.md)

Repository di addon per Home Assistant per la gestione completa delle autovetture di famiglia.

---

## Addon disponibili

| Addon                         | Versione | Descrizione                                                 |
| ----------------------------- | -------- | ----------------------------------------------------------- |
| [Cars Manager](cars-manager/) | 1.0.7    | Gestione garage, scadenze, documenti, guasti e reportistica |

---

## Installazione

### 1. Aggiungere il repository a Home Assistant

1. Vai su **Impostazioni → Add-on → Store degli add-on**
2. Clicca sul menu **⋮** in alto a destra → **Repositori**
3. Inserisci l'URL del repository:
   ```
   https://github.com/YOUR_GITHUB_USERNAME/CARS_M
   ```
4. Clicca **Aggiungi** e chiudi la finestra
5. **Cars Manager** apparirà nello store

### 2. Installare l'addon

1. Cerca **Cars Manager** nello store
2. Clicca su **Installa**
3. (Opzionale) Configura i parametri SMTP per l'invio email
4. Clicca **Avvia**
5. Abilita **Mostra nel pannello laterale** per accesso rapido

---

## Funzionalità

### 🚗 Il Mio Garage

Aggiungi e gestisci le auto di famiglia con marca, modello, anno, targa, VIN, colore e tipo carburante.

### 📅 Calendario Scadenze

Tieni traccia di manutenzioni, revisioni, bollo auto e assicurazioni. Il sistema avvisa per le scadenze imminenti.

### 📄 Documenti

Archivia libretti, polizze assicurative, fatture di officina in formato PDF, JPG, PNG, DOCX. Ogni documento supporta un campo **costo** opzionale e può essere modificato (metadati e file) o eliminato.

### ⚠️ Guasti & Segnalazioni

Segnala problemi con livello di gravità (bassa/media/alta/critica), gestiscine il ciclo di vita e segna la risoluzione con costo.

### 📧 Richiesta Preventivi via Email

Da un guasto aperto, seleziona un contatto (officina/concessionaria) e invia una email di richiesta preventivo pre-compilata.

### 📏 Chilometraggio

Aggiorna periodicamente il chilometraggio con storico completo dei rilevamenti.

### 📊 Reportistica

Grafici e statistiche su: costi mensili, costi per tipo di manutenzione, guasti per gravità.

---

## Configurazione SMTP (per invio email)

| Parametro       | Descrizione             | Default |
| --------------- | ----------------------- | ------- |
| `smtp_server`   | Server SMTP             | —       |
| `smtp_port`     | Porta SMTP              | `587`   |
| `smtp_username` | Username                | —       |
| `smtp_password` | Password / App password | —       |
| `smtp_from`     | Indirizzo mittente      | —       |
| `smtp_use_tls`  | Usa STARTTLS            | `true`  |

Per Gmail usa una **App Password** (Account Google → Sicurezza → Verifica in due passaggi → App Password).

---

## Struttura del repository

```
CARS_M/
├── README.md
├── repository.json          ← Metadata repository HA
└── cars-manager/
    ├── config.yaml          ← Configurazione addon
    ├── Dockerfile           ← Build image
    ├── build.yaml           ← Architetture target
    ├── CHANGELOG.md
    ├── DOCS.md
    └── rootfs/
        ├── etc/s6-overlay/  ← Service manager
        └── app/             ← Applicazione Flask
            ├── main.py
            ├── database.py
            ├── email_utils.py
            ├── routes/
            └── templates/
```

---

## Dati & Privacy

Tutti i dati sono salvati **localmente** nella cartella `/data` dell'addon (volume persistente di Home Assistant). Nessun dato viene inviato a servizi esterni, ad eccezione delle email inviate tramite il server SMTP configurato.

---

## Contribuire

Pull request e segnalazioni di bug sono benvenuti. Apri un issue per proporre nuove funzionalità.

## Licenza

MIT License
