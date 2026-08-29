from fastapi import FastAPI, HTTPException
import pickle
import uvicorn
from pydantic import BaseModel, Field
import logging
from typing import Tuple
from prometheus_fastapi_instrumentator import Instrumentator

# Definizione del nome del file pkl contenente il modello di sentiment analysis richiesto
FILENAME = "sentiment_analysis_model.pkl"

#Contenuto del log: livello del log (levelname), nome del modulo (name), timestamp (asctime) e messaggio effettivo del log (message)
#Il formato del timestamp nel log: anno-mese-giorno ore:minuti:secondi.
#Il livello minimo di log è impostato a INFO quindi i messaggi di livello INFO e superiore (WARNING, ERROR, CRITICAL) verranno registrati.
LOG_FORMAT = "[%(levelname)s]%(name)s: %(asctime)s - %(message)s"
DATE_LOG_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_LOG_FORMAT)
logger = logging.getLogger(__name__)

EMPTY_TEXT_ERROR_MESSAGE = "Input text is empty. Please provide a valid review."
PREDICTION_ERROR_MESSAGE = "Sentiment not identified due to an internal error."

#Request dell'API: review di input per la quale fare sentiment analysis
class ReviewRequest(BaseModel):
    model_config = { "extra": "forbid" }
    review: str = Field(..., description='Review text for sentiment analysis', examples=['This product is amazing! I love it.']) #

# Response dell'API: sentiment e confidence di output
class SentimentResponse(BaseModel):
    sentiment: str = Field(..., description="Sentiment identified (positive, negative, neutral)", examples=["positive"]) #[cite: 1]
    confidence: float = Field(..., description="Confidence score", examples=[0.95]) #[cite: 1]

#Lettura del file pkl del modello. Modalità di accesso: sola lettura (rb)
#Viene sollevata una eccezione FileNotFoundError se il file non esiste.
def load_model(pathfile=FILENAME):
    model_out = None
    try:
        with open(pathfile, "rb") as file:
            model_out = pickle.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File {FILENAME} not found")
    return model_out

# Caricamento del modello
model = load_model(FILENAME)

app = FastAPI(title="Sentiment Analysis API")

# Integrazione con Prometheus per l'endpoint GET /metrics richiesto dal progetto
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

def predict_sentiment(text: str, model_to_use) -> Tuple[str, float]:
    try:
        predicted_class = model_to_use.predict([text])[0]

        # Gestione della confidence
        try:
            prediction_proba = model_to_use.predict_proba([text])[0]
            confidence = max(prediction_proba)
        except AttributeError:
            confidence = 1.0  # Fallback se il modello non espone predict_proba

        return str(predicted_class), float(confidence)
    except Exception as e:
        logger.error(f"{PREDICTION_ERROR_MESSAGE}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=PREDICTION_ERROR_MESSAGE)


# Nuovo endpoint POST /predict come da specifiche
@app.post("/predict", description="Predict sentiment of a review", response_model=SentimentResponse)  # [cite: 1]
def analyze_review(request: ReviewRequest) -> SentimentResponse:
    logger.info(f"Request received: {request.review}")

    if len(request.review.strip()) == 0:
        logger.error(EMPTY_TEXT_ERROR_MESSAGE)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EMPTY_TEXT_ERROR_MESSAGE)

    sentiment, confidence = predict_sentiment(request.review, model)

    return SentimentResponse(sentiment=sentiment, confidence=round(confidence, 2))

#Questo blocco di codice serve per avviare un server web usando Uvicorn quando lo script Python è eseguito direttamente.
if __name__ == "__main__":
    uvicorn.run("main:app")
