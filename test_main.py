import pytest
from fastapi.testclient import TestClient
from main import app, load_model, FILENAME

# Creiamo un client di test per simulare le richieste all'API
client = TestClient(app)

# Test 1: Lettura del file pkl del modello
def test_open_file_ok():
    model_test = load_model(FILENAME)
    assert model_test is not None

# Test 2: Sollevamento eccezione FileNotFoundError se il file non esiste
def test_open_file_ko():
    with pytest.raises(FileNotFoundError):
        load_model("wrong_filename.pkl")

# Test 3: Verifica della risposta API con un testo valido
def test_predict_endpoint_success():
    response = client.post("/predict", json={"review": "This product is amazing! I like it."})
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "confidence" in data

# Test 4: Verifica errore API se il testo è vuoto (Test di Integrazione)
def test_predict_endpoint_empty_text():
    response = client.post("/predict", json={"review": "   "})
    assert response.status_code == 400
    assert response.json()["detail"] == "Input text is empty. Please provide a valid review."