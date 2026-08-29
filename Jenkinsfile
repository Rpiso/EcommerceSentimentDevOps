pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Fase di Build: Creazione dell immagine Docker...'
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
    }

    // Notifiche in caso di errore o successo della pipeline
    post {
        success {
            echo 'SUCCESS: La pipeline ha effettuato build, test e deploy senza intervento manuale.'
        }
        failure {
            echo 'FAILED: Errore durante l\'esecuzione della pipeline. Controllare i log!'
        }
    }
}
