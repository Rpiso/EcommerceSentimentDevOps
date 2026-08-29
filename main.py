from fastapi import FastAPI, status, HTTPException
import pickle
import pytest
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

#Funzione che esegue la predizione della lingua del testo presente nella request.
#Con il metodo predict viene restituita la classe più probabile (lingua identificata).
#Con il metodo predict_proba vengono restituite le probabilità per ogni classe cioè le probabilità per ogni lingua presente nel dataset.
#Tramite la funzione index è recuperato l'indice della lingua identificata: questo servirà poi per recuperare la probabilità associata ad essa
#Qualora il testo non sia identificato viene lanciata un eccezione HttpException che avvisa di questa casistica
#La probabilità è arrotondata alla seconda cifra decimale
def predict_language(text: str, model_to_use) -> Tuple[str, float]:
    predicted_class = model_to_use.predict([text])
    prediction_proba = model_to_use.predict_proba([text])
    if len(predicted_class) == 0 or len(prediction_proba) == 0:
        logger.error(LANGUAGE_UNDEFINED_ERROR_MESSAGE)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=LANGUAGE_UNDEFINED_ERROR_MESSAGE)

    index_predicted_class = model_classes.index(predicted_class)
    confidence_score = float(prediction_proba[0][index_predicted_class])
    return predicted_class[0], round(confidence_score, 2)

#Caricamento modello salvato nel file FILENAME
model = load_model(FILENAME)
#Recupero delle classi previste dal modello. Questa lista  sarà utile per restituire la confidence
model_classes = list(model.classes_)

app = FastAPI()

#Definizione dell'endpoint
#Se il testo da identificare non è presente (lunghezza pari a zero) viene lanciata un eccezione HTTPException con stato 500
#che informa della mancanza del testo da identificare.
#Il testo da identificare viene passato alla funzione predict_language assieme al modello per la predizione.
#Il risultato della predizione è salvato nella classe PredictionTextResult valorizzando la lingua rilevata e la confidence
#Nel metodo vengono tracciati nel log la request ricevuta e la response
@app.post("/identify-language", description="Post endpoint to identify input json text language",
          response_description="Language code identified and confidence score")
def identify_language(text_to_identify: TextToIdentify) -> PredictionTextResult:
    logger.info(f"Request: {text_to_identify}")
    if len(text_to_identify.text) == 0:
        logger.error(EMPTY_TEXT_ERROR_MESSAGE)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EMPTY_TEXT_ERROR_MESSAGE)

    language_code, confidence_score = predict_language(text_to_identify.text, model)
    prediction_text_result = PredictionTextResult(language_code=language_code, confidence=confidence_score)
    logger.info(f"Response: {prediction_text_result}")
    return prediction_text_result

#Test lettura del file pkl del modello
def test_open_file_ok():
    model_test = load_model(FILENAME)
    assert model_test is not None

#Test sollevamento eccezione FileNotFoundError se il file non esiste
def test_open_file_ko():
    with pytest.raises(FileNotFoundError):
        load_model("wrong_filename.pkl")

#Test sollevamento eccezione HttpException se il testo nella request è vuoto
def test_input_missing():
    with pytest.raises(HTTPException):
        identify_language(TextToIdentify(text=""))

#Questo blocco di codice serve per avviare un server web usando Uvicorn quando lo script Python è eseguito direttamente.
#MuseumLangMain è il nome del modulo Python mentre app è l'applicazione da eseguire definita all'interno del modulo MuseumLangMain
if __name__ == "__main__":
    uvicorn.run("MuseumLangMain:app")
