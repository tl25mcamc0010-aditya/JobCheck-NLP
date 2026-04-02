from sklearn.feature_extraction.text import TfidfVectorizer

def create_tfidf(text):

    vectorizer = TfidfVectorizer(
    max_features=20000,
    ngram_range=(1,2),
    min_df=5,
    max_df=0.9
    )

    X = vectorizer.fit_transform(text)

    return X, vectorizer

from sklearn.feature_selection import SelectKBest, chi2

def select_features(X, y):

    selector = SelectKBest(chi2, k=2000)

    X_new = selector.fit_transform(X, y)

    return X_new, selector