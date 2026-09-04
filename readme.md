# Deploy e monitoraggio di un modello di Sentiment Analysis per recensioni

## Progetto finale del modulo di DevOps e Gestione del ciclo di vita del software di Professional AI

## Progetto di Roberto Pisoni

## Panoramica del Progetto
Questo progetto finale implementa un sistema automatizzato per il deploy e il monitoraggio di un modello di Sentiment Analysis destinato a una piattaforma di e-commerce.
Il sistema analizza le recensioni dei prodotti in lingua inglese per determinare il sentimento (positivo, negativo, neutro) in modo da supportare le decisioni aziendali per migliorare i prodotti e il servizio clienti.
L'infrastruttura garantisce scalabilità e affidabilità automatizzando i processi tramite una pipeline CI/CD.

## Architettura CI/CD (Jenkins)
La pipeline CI/CD è gestita tramite uno script `Jenkinsfile` che si avvia in automatico (trigger automatico) ad ogni nuovo commit sul repository. 
La pipeline esegue le seguenti fasi in sequenza, senza alcun intervento manuale:
* **Build**: Effettua la compilazione del modello e crea l'immagine Docker dell'applicazione.
* **Test**: Esegue test automatizzati, sia unit test che test di integrazione, per validare le previsioni.
* **Deploy**: Gestisce la pubblicazione del modello su un container Docker.
* **Notifiche**: Il sistema è predisposto per inviare notifiche in caso di errore o successo della pipeline.

## Utilizzo dell'API REST
L'applicazione è sviluppata in FastAPI per servire il modello di Machine Learning.

### Predizione del Sentimento
* **Endpoint**: `POST /predict`.
* **Funzionamento**: Accetta una recensione testuale in formato JSON e restituisce il sentimento analizzato.
* **Esempio di Richiesta JSON**: 
  `{"review": "This product is amazing! I love it."}`
* **Esempio di Risposta JSON**: 
  `{"sentiment": "positive", "confidence": 0.95}`

### Esportazione delle Metriche
* **Endpoint**: `GET /metrics`.
* **Funzionamento**: Espone le metriche del sistema in un formato standard leggibile da Prometheus.

## Infrastruttura di Monitoraggio
Il sistema include uno stack dedicato al monitoraggio proattivo, utile per identificare e risolvere rapidamente eventuali colli di bottiglia o problemi nel modello
* **Prometheus:** Raccoglie costantemente i dati esposti dall'API REST, tenendo traccia del tempo di risposta delle richieste, degli eventuali errori di predizione e dell'utilizzo di risorse hardware come CPU e memoria.
* **Grafana:** Si interfaccia con i dati raccolti da Prometheus per visualizzare in tempo reale le prestazioni dell'intero sistema tramite dashboard interattive.

## Istruzioni per la Manutenzione
* **Configurazione Iniziale:** Il repository contiene tutti gli script necessari; l'intero ecosistema è containerizzato tramite Docker, semplificando l'installazione e la configurazione.
* **Sviluppo Continuo:** Grazie a Jenkins, ogni successiva modifica al codice verrà automaticamente processata, testata e rilasciata, minimizzando gli interventi manuali di manutenzione.

## Struttura e Contenuto dei File di Configurazione
Il progetto si basa su file di configurazione specifici, ciascuno con un ruolo ben definito all'interno dell'infrastruttura:

### 1. `Jenkinsfile`
Questo script definisce l'intera pipeline di Continuous Integration e Continuous Deployment (CI/CD). Al suo interno è strutturato nelle seguenti fasi:
*   **Build:** Contiene le istruzioni per il download del modello prima della build e la compilazione e la creazione dell'immagine Docker dell'applicazione.
*   **Test:** Avvia l'esecuzione automatizzata degli unit test e dei test di integrazione per validare le previsioni del modello. Sfrutta l'immagine Docker creata nel punto precedente per lanciare pytest in un ambiente isolato.
*   **Deploy:** Contiene i comandi per la pubblicazione del modello su un container (Docker). Prima di avviare il nuovo container, verifica se ne esiste già uno in esecuzione e, in tal caso, lo ferma e lo rimuove. Successivamente, avvia il nuovo container esponendo la porta 8000 per l'accesso all'API REST.
*   **Notifiche:** Gestisce l'invio di avvisi in caso di successo o errore dell'intera pipeline.
*   **Trigger:** Definisce l'attivazione automatica della pipeline a ogni nuovo commit sul repository. Nel file è presente la direttiva `triggers { githubPush() }` che si integra con il webhook di GitHub, facendo partire la build in completa autonomia ad ogni nuovo commit sul repository. *(Nota: Questo sostituisce la necessità di configurare l'opzione "GitHub hook trigger for GITScm polling" manualmente dall'interfaccia web).*

### 2. `prometheus.yml`
È il file di configurazione principale di Prometheus, responsabile della raccolta dei dati. Al suo interno è configurato per:
*   Puntare direttamente all'endpoint `GET /metrics` esposto dalla nostra API REST.
*   Raccogliere periodicamente metriche fondamentali come il tempo di risposta delle richieste e gli eventuali errori di predizione.
*   Registrare le metriche relative all'utilizzo delle risorse hardware, come CPU e memoria.

Riguardo ai parametri specifici:
- La frequenza di raccolta delle metriche è impostata a 5 secondi (parametro `scrape_interval`) per garantire un monitoraggio costante e tempestivo delle prestazioni del sistema.
- Il parametro `job_name` impostato a 'ecommerce-sentiment-analysis-api' assegna un nome identificativo a questa specifica attività di raccolta. Questo sarà utile in Grafana per filtrare e riconoscere i dati provenienti da questa API.
- L'ultimo parametro `targets` 'host.docker.internal:8000' indica l'indirizzo e la porta del container che ospita l'API REST, consentendo a Prometheus di accedere correttamente alle metriche esposte.

### 3. `docker-compose.yml`
Questo file si occupa dell'orchestrazione dei container dell'intero sistema. Il suo scopo principale è quello di avviare e configurare l'infrastruttura di monitoraggio, istanziando i servizi per Prometheus e Grafana.
Nello specifico, il file `docker-compose.yml` contiene le seguenti sezioni principali:

- `services`: blocco principale in cui vengono definiti i container (servizi) che devono essere avviati, in questo caso Prometheus e Grafana.  
- `prometheus`: sezione relativa al container di Prometheus. Questo componente è incaricato di raccogliere costantemente le metriche esposte dall'API (come i tempi di risposta, l'utilizzo di CPU/memoria e gli errori del modello).  
  - `image: prom/prometheus:latest`: Scarica ed esegue l'ultima versione ufficiale dell'ambiente Prometheus.
  - `container_name: prometheus`: Assegna il nome "prometheus" al container.
  - `volumes`: 
    - `./prometheus.yml:/etc/prometheus/prometheus.yml`: Crea un collegamento tra la tua macchina e il container. Prende il file di configurazione locale (./prometheus.yml) e lo inietta nel container, sovrascrivendo quello di default.
  - `ports`: 
    - `"9090:9090"`: Mappa la porta 9090 del container sulla porta 9090 del proprio computer, permettendoti di accedere all'interfaccia web di Prometheus.
  - `extra_hosts`: 
    - `"host.docker.internal:host-gateway"`: È un'impostazione di rete cruciale. Permette al container isolato di comunicare con la macchina host dove sta girando l'API REST, garantendo che Prometheus riesca a interrogare l'endpoint /metrics.
- `grafana`: sezione relativa al container di Grafana. Questo componente si interfaccia con i dati di Prometheus per generare e visualizzare dashboard interattive in tempo reale.  
  - `image: grafana/grafana:latest`: Scarica ed esegue l'ultima immagine ufficiale di Grafana.
  - `container_name: grafana`: Assegna il nome "grafana" al container.
  - `ports`: 
    - `"3000:3000"`: Rende accessibile la piattaforma Grafana dal proprio browser tramite la porta 3000.
  - `environment`: 
    - `GF_SECURITY_ADMIN_PASSWORD=admin`: Inietta una variabile d'ambiente per configurare automaticamente "admin" come password di default per l'amministratore, bypassando il setup iniziale manuale.
  - `depends_on`: 
    - `prometheus`: Definisce una priorità di avvio. Istruisce Docker a lanciare il container di Grafana solo dopo aver avviato con successo quello di Prometheus, poiché il primo ha bisogno del secondo per funzionare correttamente.


### 4. File dell'API - `main.py`
È il codice sorgente (basato su Flask o FastAPI) che serve il modello di Machine Learning. Il codice è strutturato per esporre due endpoint principali:
*   **`POST /predict`**: Contiene la logica per accettare in input una recensione in formato JSON e restituire il sentimento analizzato con il relativo valore di confidenza.
*   **`GET /metrics`**: Contiene l'integrazione necessaria a esporre le metriche del sistema in un formato testuale leggibile da Prometheus.