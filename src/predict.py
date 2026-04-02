import pickle
import os
from .preprocessing import clean_text

model = pickle.load(open(os.path.join(os.path.dirname(__file__), "..", "Models", "model.pkl"),"rb"))
vectorizer = pickle.load(open(os.path.join(os.path.dirname(__file__), "..", "Vectorizers", "tfidf.pkl"),"rb"))

def predict_job(text):
    
    cleaned = clean_text(text)

    X = vectorizer.transform([cleaned])

    prediction = model.predict(X)

    if prediction[0] == 1:
        return "Fake Job"
    else:
        return "Real Job"