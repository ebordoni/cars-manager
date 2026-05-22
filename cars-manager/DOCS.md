# Cars Manager - Documentazione

## Panoramica

**Cars Manager** è un addon per Home Assistant che ti permette di gestire le autovetture di famiglia in modo semplice e completo.

## Funzionalità

### Il Mio Garage

Aggiungi tutte le auto di famiglia con i relativi dati: marca, modello, anno, targa, colore, VIN, tipo carburante e data di acquisto.

### Calendario Scadenze

Tieni traccia di tutte le scadenze:

- **Manutenzioni** ordinarie e straordinarie
- **Revisioni** periodiche obbligatorie
- **Bollo** auto
- **Assicurazione** RC Auto e Kasko

Il dashboard ti avverte delle scadenze imminenti e di quelle già scadute.

### Documenti

Carica e organizza i documenti per ogni auto:

- Libretto di circolazione
- Certificati assicurativi
- Fatture di officina e interventi
- Qualsiasi altro documento utile

### Guasti e Segnalazioni

Segnala guasti e malfunzionamenti con:

- Titolo e descrizione dettagliata
- Livello di gravità (bassa, media, alta, critica)
- Possibilità di risolverli con note e costo dell'intervento

### Contatti

Mantieni una rubrica di concessionarie e autofficine di fiducia, con indirizzo, telefono, email e sito web.

### Invio Preventivi via Email

Dalla pagina di un guasto aperto, seleziona un contatto e invia direttamente una richiesta di preventivo via email. Il testo è pre-compilato con i dettagli del guasto.

### Chilometraggio

Aggiorna periodicamente il chilometraggio di ogni auto e visualizza lo storico.

### Reportistica

Dashboard con grafici su:

- Costi per tipo di manutenzione
- Guasti per gravità e stato
- Andamento mensile dei costi

---

## Configurazione

### Parametri SMTP (opzionali, per invio email)

| Parametro       | Descrizione                       | Default |
| --------------- | --------------------------------- | ------- |
| `smtp_server`   | Hostname del server SMTP          | -       |
| `smtp_port`     | Porta del server SMTP             | `587`   |
| `smtp_username` | Username/email per autenticazione | -       |
| `smtp_password` | Password per autenticazione       | -       |
| `smtp_from`     | Indirizzo mittente delle email    | -       |
| `smtp_use_tls`  | Usare STARTTLS                    | `true`  |

### Esempio configurazione Gmail

```yaml
smtp_server: smtp.gmail.com
smtp_port: 587
smtp_username: tua.email@gmail.com
smtp_password: "app_password_generata_da_google"
smtp_from: tua.email@gmail.com
smtp_use_tls: true
```

> **Nota:** Per Gmail è necessario usare una "App Password" (non la password dell'account). Abilitala da Account Google → Sicurezza → Verifica in due passaggi → App Password.

---

## Dati e Backup

Tutti i dati (database SQLite e file caricati) sono salvati nella cartella `/data` dell'addon, che corrisponde a un volume persistente di Home Assistant. I dati **non vengono persi** in caso di aggiornamento o riavvio dell'addon.

Per effettuare un backup manuale, copia il contenuto della cartella tramite le funzionalità di backup di Home Assistant.

---

## Note Tecniche

- L'addon espone un'interfaccia web sulla porta `5000`
- Supporta l'ingress nativo di Home Assistant (accessibile direttamente dal pannello laterale)
- Il database è SQLite, ottimale per uso domestico
- Dimensione massima per upload singolo: 20 MB
- Formati documenti supportati: PDF, JPG, JPEG, PNG, DOCX, XLSX
