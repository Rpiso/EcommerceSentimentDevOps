# Deploy e monitoraggio di un modello di Sentiment Analysis per recensioni

## Progetto finale del modulo di DevOps e Gestione del ciclo di vita del software di Professional AI

### Progetto di Roberto Pisoni

## Sommario
- [Panoramica del Progetto](#panoramica-del-progetto)
- [Repository Git](#repository-git)
- [Architettura CI/CD (Jenkins)](#architettura-cicd-jenkins)
- [Utilizzo dell'API REST](#utilizzo-dellapi-rest)
  - [Predizione del Sentimento](#predizione-del-sentimento)
  - [Esportazione delle Metriche](#esportazione-delle-metriche)
- [Infrastruttura di Monitoraggio](#infrastruttura-di-monitoraggio)
- [Istruzioni per la Manutenzione](#istruzioni-per-la-manutenzione)
- [Struttura e Contenuto dei File di Configurazione](#struttura-e-contenuto-dei-file-di-configurazione)
  - [1. Jenkinsfile](#1-jenkinsfile)
  - [2. prometheus.yml](#2-prometheusyml)
  - [3. docker-compose.yml](#3-docker-composeyml)
  - [4. Dockerfile](#4-dockerfile)
  - [5. main.py](#5-mainpy)
  - [6. test_main.py](#6-test_mainpy)
  - [7. sentiment_analysis_model.pkl](#7-sentiment_analysis_modelpkl)
  - [8. requirements.txt](#8-requirementstxt)
  - [9. grafana/provisioning/datasource/datasource.yml](#9-grafanaprovisioningdatasourcedatasourceyml)
  - [10. grafana/provisioning/dashboard/dashboard_provider.yml](#10-grafanaprovisioningdashboarddashboard_provideryml)
  - [11. grafana/dashboard/dashboard.json](#11-grafanadashboarddashboardjson)
  - [12. .gitignore](#12-gitignore)

## Panoramica del Progetto
Questo progetto finale implementa un sistema automatizzato per il deploy e il monitoraggio di un modello di Sentiment Analysis destinato a una piattaforma di e-commerce.
Il sistema analizza le recensioni dei prodotti in lingua inglese per determinare il sentimento (positivo, negativo, neutro) in modo da supportare le decisioni aziendali per migliorare i prodotti e il servizio clienti.
L'infrastruttura garantisce scalabilità e affidabilità automatizzando i processi tramite una pipeline CI/CD.

## Repository Git
Il codice sorgente, la pipeline e l'intera documentazione sono gestiti e versionati su Git, come richiesto dagli obiettivi del progetto. 
Puoi consultare e clonare il repository completo al seguente [link](https://github.com/Rpiso/EcommerceSentimentDevOps)


## Architettura CI/CD (Jenkins)
La pipeline CI/CD è gestita tramite uno script `Jenkinsfile` che si avvia in automatico (trigger automatico) a ogni nuovo commit sul repository. 
La pipeline esegue le seguenti fasi in sequenza, senza alcun intervento manuale:
* **Build**: Effettua la compilazione del modello e crea l'immagine Docker dell'applicazione.
* **Test**: Esegue test automatizzati, sia unit test che test di integrazione, per validare le previsioni.
* **Deploy**: Gestisce la pubblicazione del modello su un container Docker.
* **Notifiche**: Il sistema è predisposto per inviare notifiche via mail in caso di errore o successo della pipeline.

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
* **Grafana:** Si interfaccia con i dati raccolti da Prometheus per visualizzare in tempo reale le prestazioni dell'intero sistema tramite dashboard interattive. Questa dashboard mostra:
  * se l’API fallisce
  * quanto è lenta
  * quanta RAM usa
  * quanta CPU sta consumando

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

* Nota: La configurazione del server di posta (server, porta, credenziali di accesso, protocollo di sicurezza) deve essere impostata tramite interfaccia grafica di Jenkins.

### 2. `prometheus.yml`
È il file di configurazione principale di Prometheus, responsabile della raccolta dei dati. Al suo interno troviamo queste sezioni:
-  **`global: scrape_interval: 5s:`** Impostazione globale che definisce il ritmo di lavoro di Prometheus. scrape_interval indica che Prometheus effettuerà lo "scraping" (cioè la lettura e raccolta dei dati) ogni 5 secondi.
-  **`scrape_configs`**: Definisce le configurazioni per la raccolta delle metriche. In questo caso, è presente un solo job denominato 'ecommerce-sentiment-analysis-api'.
- **`job_name: 'ecommerce-sentiment-analysis-api'`**: Assegna un nome identificativo a questa specifica attività di raccolta. Utile in Grafana per filtrare e riconoscere i dati provenienti da questa API.
- **`targets: ['host.docker.internal:8000']`**: Indica l'indirizzo e la porta del container che ospita l'API REST creata con FastAPI, consentendo a Prometheus di accedere correttamente alle metriche esposte.
Prometheus aggiungerà automaticamente /metrics alla fine di questo indirizzo, andando così a interrogare l'endpoint GET /metrics che espone le metriche del sistema.

### 3. `docker-compose.yml`
Questo file si occupa dell'orchestrazione dei container dell'intero sistema. Il suo scopo principale è quello di avviare e configurare l'infrastruttura di monitoraggio, istanziando i servizi per Prometheus e Grafana.
Nello specifico, il file `docker-compose.yml` contiene le seguenti sezioni principali:

- `services`: blocco principale in cui vengono definiti i container (servizi) che devono essere avviati, in questo caso Prometheus e Grafana.  
- `prometheus`: sezione relativa al container di Prometheus. Questo componente è incaricato di raccogliere costantemente le metriche esposte dall'API (come i tempi di risposta, l'utilizzo di CPU/memoria e gli errori del modello).  
  - `image: prom/prometheus:latest`: Scarica ed esegue l'ultima versione ufficiale dell'ambiente Prometheus.
  - `container_name: prometheus`: Assegna il nome "prometheus" al container.
  - `volumes`: 
    - `./prometheus.yml:/etc/prometheus/prometheus.yml`: Prende il file di configurazione locale (./prometheus.yml) e lo monta nel container Docker, sovrascrivendo quello di default e usando quindi tale configurazione.
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
  -  `volumes`: 
    - `./grafana/provisioning/datasource/datasource.yml:/etc/grafana/provisioning/datasources/datasource.yml`: monta nel container Docker il file di configurazione del datasource di Grafana.
    - `./grafana/provisioning/dashboard/dashboard_provider.yml:/etc/grafana/provisioning/dashboards/dashboard_provider.yml`: monta nel container Docker il file di configurazione del provider delle dashboard di Grafana.
    - `./grafana/dashboard:/etc/grafana/provisioning/dashboards/json_files`: monta nel container Docker la cartella che conterrà i file JSON dei grafici di Grafana.

### 4. `Dockerfile`
Questo file definisce le istruzioni per costruire l'immagine dell'applicazione, operazione che rappresenta il passaggio centrale della fase di Build nella pipeline CI/CD. 
Il file contiene queste istruzioni:

*   **`FROM python:3.10-slim`**: Specifica l'immagine di base da utilizzare per il container; ho scelto Python 3.10 slim per avere un ambiente Python isolato e leggero.
*   **`WORKDIR /app`**: Imposta la cartella di lavoro principale all'interno del container. Tutti i comandi successivi verranno eseguiti in questo percorso.
*   **`COPY requirements.txt .`** e **`RUN pip install --no-cache-dir -r requirements.txt`**: Trasferisce l'elenco delle dipendenze nel container e installa le librerie necessarie (come FastAPI) per esporre i servizi REST.
*   **`COPY main.py .`** e **`COPY test_main.py .`**: Copia il codice sorgente dell'applicazione e gli script per l'esecuzione automatizzata dei test.
*   **`COPY sentiment_analysis_model.pkl .`**: Copia all'interno del container il file fisico del modello pre-addestrato necessario per elaborare il testo e fornire le previsioni.
*   **`EXPOSE 8000`**: Dichiarazione esplicita della porta di rete su cui l'applicazione rimarrà in ascolto per ricevere il traffico in ingresso.
*   **`CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`**: Comando di avvio finale per il server web tramite Uvicorn. Questa istruzione mantiene attiva l'API REST per servire gli endpoint di predizione e per esporre le metriche di monitoraggio del sistema.

### 5 `main.py`
È il codice sorgente (basato su Flask o FastAPI) che serve il modello di Machine Learning. Il codice è strutturato per esporre due endpoint principali:
*   **`POST /predict`**: Contiene la logica per accettare in input una recensione in formato JSON e restituire il sentimento analizzato con il relativo valore di confidenza.
*   **`GET /metrics`**: Contiene l'integrazione necessaria a esporre le metriche del sistema in un formato testuale leggibile da Prometheus.

### 6. `test_main.py`
Contiene gli unit test e i test di integrazione per validare le previsioni del modello. Questi test vengono eseguiti automaticamente durante la fase di Test della pipeline CI/CD
I test includono casi di test per sentimenti positivi, negativi e neutri, nonché test per gestire input non validi o mancanti.

### 7. `sentiment_analysis_model.pkl`
Contiene il modello di Sentiment Analysis pre-addestrato, salvato in formato pickle. Link al modello: [sentiment_analysis_model.pkl](https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentiment_analysis_model.pkl)

### 8. `requirements.txt`
Contiene l'elenco delle dipendenze Python necessarie per eseguire l'applicazione, inclusi framework come FastAPI, librerie per il machine learning e strumenti per il testing.
La versione di scikit-learn specificata in questo file è la 1.6.0, stessa versione del modello pickle evitando così l'emissione di un InconsistentVersionWarning durante la fase di buid ma soprattutto evitando predizioni potenzialmente sbagliate.

### 9. `grafana/provisioning/datasource/datasource.yml`
Contiene la configurazione del datasource di Grafana, permettendogli di connettersi a Prometheus per leggere le metriche raccolte dall'API REST. 

* **`datasources:`**: Sezione che definisce i datasource disponibili in Grafana.
* **`name: Prometheus`**: Identificativo datasource
* **`type: prometheus`**: Tipo di datasource, in questo caso Prometheus.
* * **`access: proxy`**: Imposta il metodo di accesso al datasource. In questo caso, Grafana agirà come un proxy per inoltrare le richieste a Prometheus.
* **`url: http://prometheus:9090`**: URL di Prometheus a cui Grafana deve connettersi per recuperare le metriche. L'URL fa riferimento al container di Prometheus definito nel file `docker-compose.yml`.
* **`isDefault: true`**: Imposta questo datasource come predefinito per le query di Grafana.
* **`editable: true`**: Permette di modificare la configurazione del datasource direttamente dall'interfaccia da Grafana

### 10. `grafana/provisioning/dashboard/dashboard_provider.yml`
Contiene la configurazione del provider delle dashboards di Grafana, che permette di caricare automaticamente le dashboard predefinite all'avvio del container.

* **`name: 'default'`**: Nome del provider di dashboard.
* **`orgId: 1`**: Identificativo dell'organizzazione in Grafana (defualt=1).
* **`type: file`**: Tipo di provider, in questo caso un file.
* **`disableDeletion: false`**: Impostazione che consente la cancellazione di dashboard esistenti e non più presenti nel file di configurazione.
* **`updateIntervalSeconds: 10`**: Grafana controllerà ogni 10 secondi se ci sono nuove dashboard da caricare o aggiornare.
* **`options/path:`**: percorso nel container dove Grafana cercherà i file JSON delle dashboard da caricare.

### 11. `grafana/dashboard/dashboard.json`
Contiene la definizione della dashboards di Grafana che visualizzano in tempo reale le metriche raccolte da Prometheus.
I tag nel json sono autoesplicativi e descrivono le caratteristiche principali della dashboard:
* **`title`**: nome della dashboard ("Sentiment Analysis API - Monitoraggio")
* **`tags`**: etichette per trovare facilmente la dashboard
* **`refresh: "5s"`**: il grafico si aggiorna ogni 5 secondi
* **`time:`**: la dashboard mostra gli ultimi 5 minuti (now-5m)
* **`panels:`**: qua vengono definiti i grafici da mostrare, ogni blocco è un grafico. In 4 grafici implementati, ognuno con un titolo e una query PromQL per estrarre i dati da Prometheus, sono i seguenti: 

  - 1] Grafico Errore di Predizione (HTTP 4xx / 5xx): mostra quante richieste di predizione hanno fallito nel tempo, con status code 4xx o 5xx. La query PromQL utilizzata è:
  `sum(rate(http_requests_total{status=~\"[45].*\"}[5m]))` dove rate(...) misura il numero di richieste fallite per secondo e sum(...) è la somma totale.
  
  - 2] Grafico Tempo di Risposta (Latenza Media): calcola il tempo medio di risposta del backend. La query utilizzata è:
  `sum(rate(http_request_duration_seconds_sum[5m])) / sum(rate(http_request_duration_seconds_count[5m]))` dove viene fatta la divisione tra due metriche:
    - `http_request_duration_seconds_sum` = tempo totale impiegato
    - `http_request_duration_seconds_count` = numero di richieste

  - 3] Grafico Utilizzo Memoria: mostra quanta memoria RAM sta utilizzando il processo usando la query predefinita `process_resident_memory_bytes`
  L'unità di misura è "bytes" - fa vedere il valore in byte

  - 4] Grafico Utilizzo CPU: mostra il consumo di CPU del processo usando la query predefinita `process_cpu_seconds_total`
  La funzione rate(...) calcola il tasso di utilizzo nel tempo.

### 12. `.gitignore`
Contiene l'elenco dei file e delle cartelle che Git deve ignorare durante il versionamento. Questo è utile per evitare di includere file temporanei, di log o di configurazione locale che non sono rilevanti per il progetto condiviso.