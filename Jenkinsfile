pipeline {
    agent any

    // Questa istruzione dice a Jenkins di attivare la pipeline in automatico
    // quando riceve la notifica del webhook da GitHub.
    triggers {
        githubPush()
    }

    stages {
        stage('Build') {
            steps {
                echo 'Fase di Build: Creazione dell immagine Docker...'

                // 1. Download del modello prima della build
                sh 'curl -L -o sentiment_analysis_model.pkl "https://github.com/Profession-AI/progetti-devops/raw/refs/heads/main/Deploy%20e%20monitoraggio%20di%20un%20modello%20di%20sentiment%20analysis%20per%20recensioni/sentiment_analysis_model.pkl"'
                
                // Compilazione e creazione dell'immagine Docker con l'applicazione di analisi del sentiment
                sh 'docker build -t sentiment-analysis-api:latest .'
            }
        }

        stage('Test') {
            steps {
                echo 'Fase di Test: Esecuzione dei test automatizzati...'
                // Esecuzione di test automatizzati (unit test e integrazione) per validare le previsioni
                // Sfruttiamo l'immagine Docker appena creata per lanciare pytest in un ambiente isolato
                sh 'docker run --rm sentiment-analysis-api:latest pytest test_main.py'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Fase di Deploy: Pubblicazione del modello sul container...'
                // Deploy del modello su un container Docker
                // 1. Fermiamo e rimuoviamo un eventuale container in esecuzione dalle build precedenti
                sh 'docker rm -f sentiment-api-container || true'

                // 2. Avviamo il nuovo container esponendo la porta 8000
                sh 'docker run -d -p 8000:8000 --name sentiment-api-container sentiment-analysis-api:latest'
            }
        }
    }

    // Notifiche in caso di errore o successo della pipeline
    post {
        success {
            echo 'SUCCESS: La pipeline ha effettuato build, test e deploy senza intervento manuale.'
            mail to: 'roberto.pisoni@fastwebnet.it',
                 subject: "Pipeline SUCCESS: E-commerce Sentiment API",
                 body: "La pipeline di Sentiment Analysis su Jenkins è stata eseguita con successo. Il modello è in produzione."
        }
        failure {
            echo 'FAILED: Errore durante l\'esecuzione della pipeline. Controllare i log!'
            mail to: 'roberto.pisoni@fastwebnet.it',
                 subject: "Pipeline FAILED: E-commerce Sentiment API",
                 body: "La pipeline di Sentiment Analysis su Jenkins ha riscontrato un errore. Controllare i log per ulteriori dettagli!"
        }
    }
}
