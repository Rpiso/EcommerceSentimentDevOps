# Deploy e monitoraggio di un modello di Sentiment Analysis per recensioni

## Progetto finale del modulo di DevOps e Gestione del ciclo di vita del software di Professional AI

## Progetto di Roberto Pisoni

## Panoramica del Progetto
* Questo progetto finale implementa un sistema automatizzato per il deploy e il monitoraggio di un modello di Sentiment Analysis.
* Il sistema analizza le recensioni dei prodotti in lingua inglese per determinare il sentimento (positivo, negativo, neutro) e migliorare il servizio clienti.
* L'infrastruttura garantisce scalabilità e affidabilità automatizzando i processi tramite una pipeline CI/CD

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
* Il sistema è integrato con Prometheus per raccogliere continuamente i dati generati dall'API REST.
* Le metriche monitorate includono il tempo di risposta delle richieste, gli eventuali errori di predizione e l'utilizzo delle risorse fisiche (CPU e memoria).
* Grafana è configurato per leggere questi dati e visualizzare dashboard interattive in tempo reale.
* Questo approccio consente un monitoraggio proattivo, fondamentale per identificare e risolvere rapidamente eventuali problemi.

## Istruzioni di Manutenzione e Configurazione
* **Infrastruttura Locale**: Avvia i container Prometheus e Grafana utilizzando il file `docker-compose.yml` fornito nel repository.
* **Manutenzione Continua**: La pipeline CI/CD assicura che ogni futura modifica al codice o al modello venga testata e distribuita in modo rapido e affidabile.