# Usiamo un'immagine Python ufficiale e leggera
FROM python:3.10-slim

# Impostiamo la directory di lavoro all'interno del container
WORKDIR /app

# Copiamo il file dei requisiti e li installiamo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia dei sorgenti main + test
COPY main.py .
COPY test_main.py .

# Esponiamo la porta su cui gira FastAPI
EXPOSE 8000

# Comando per avviare l'applicazione
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
