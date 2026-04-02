import pandas as pd
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from imblearn.over_sampling import SMOTE

from preprocessing import clean_text
from feature_engineering import create_tfidf

from sklearn.metrics import classification_report


df = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "Data", "fake_job_postings.csv"))

df["text"] = (
    df["title"].fillna("") + " " +
    df["company_profile"].fillna("") + " " +
    df["description"].fillna("") + " " +
    df["requirements"].fillna("") + " " +
    df["benefits"].fillna("")
)

df["clean_text"] = df["text"].apply(clean_text)


X, vectorizer = create_tfidf(df["clean_text"])

y = df["fraudulent"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

smote = SMOTE()
X_train, y_train = smote.fit_resample(X_train, y_train) # pyright: ignore[reportAssignmentType]

model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=["Real Job", "Fake Job"]))


pickle.dump(model, open(os.path.join(os.path.dirname(__file__), "..", "Models", "model.pkl"),"wb"))
pickle.dump(vectorizer, open(os.path.join(os.path.dirname(__file__), "..", "Vectorizers", "tfidf.pkl"),"wb"))