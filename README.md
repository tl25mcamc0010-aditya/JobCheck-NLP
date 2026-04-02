# Fake Job Detector

A Python script that uses machine learning to detect fake job postings by processing a dataset.

## Features

- Loads job postings dataset from the Data folder
- Uses machine learning model to predict fake/real job descriptions
- Compares predictions with actual labels (if available)
- Outputs accuracy and saves predictions to a CSV file
- Processes the entire dataset in batch

## Project Structure

```
.
├── app.py                 # Main script to process dataset and predict
├── main.py                # (Empty)
├── Data/
│   ├── fake_job_postings.csv  # Input dataset
│   └── predictions.csv        # Output predictions (generated)
├── Models/
│   └── model.pkl              # Trained ML model
├── src/
│   ├── __init__.py
│   ├── feature_engineering.py # TF-IDF vectorization
│   ├── predict.py             # Prediction logic
│   ├── preprocessing.py       # Text cleaning
│   └── train_model.py         # Model training script
├── templates/                 # (No longer used)
│   └── index.html
└── Vectorizers/
    └── tfidf.pkl              # TF-IDF vectorizer
```

## Setup and Installation

1. **Clone or download the project**

2. **Install dependencies**
   ```bash
   pip install pandas scikit-learn nltk
   ```

3. **Download NLTK data** (optional, done automatically)
   ```python
   import nltk
   nltk.download('stopwords')
   nltk.download('wordnet')
   ```

4. **Train the model**
   ```bash
   python -m src.train_model
   ```
   This will create `Models/model.pkl` and `Vectorizers/tfidf.pkl`

5. **Run the prediction script**
   ```bash
   python app.py
   ```

## Usage

Run the script to process the entire dataset:

```bash
python app.py
```

The script will:
- Load the dataset from `Data/fake_job_postings.csv`
- Predict fake/real for each job description
- Calculate and display accuracy (if labels are present)
- Save results to `Data/predictions.csv`
- Show sample predictions

## Dataset

The script processes the "Fake Job Postings" dataset, which contains job postings with descriptions and fraudulent labels.

## Model Details

- **Algorithm**: Logistic Regression
- **Features**: TF-IDF vectorization of cleaned job descriptions
- **Training Accuracy**: ~96.8% on test set

## Output

- **Console Output**: Accuracy score and sample predictions
- **File Output**: `Data/predictions.csv` with original data plus `predicted_fraudulent` column

## Technologies Used

- Python
- Scikit-learn
- NLTK
- Pandas

## Notes

- Ensure the model files exist before running the prediction script
- The script handles missing or invalid descriptions gracefully</content>
<parameter name="filePath">c:\Users\adity\OneDrive\Desktop\Infosys\Milestone2\README.md