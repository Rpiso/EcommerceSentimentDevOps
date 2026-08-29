# Usiamo un'immagine Python ufficiale e leggera
FROM python:3.10-slim

# Impostiamo la directory di lavoro all'interno del container
WORKDIR /app

# Copiamo il file dei requisiti e li installiamo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamo il modello di machine learning e il codice dell'applicazione
COPY sentiment_analysis_model.pkl .
COPY main.py .

# Esponiamo la porta su cui gira FastAPI
EXPOSE 8000

# Comando per avviare l'applicazione
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]