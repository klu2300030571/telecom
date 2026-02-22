import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

print("✅ Training started...")

# Load dataset
df = pd.read_csv("complaints.csv")
print(df.head())
print("Rows:", len(df))print("✅ Dataset loaded:", df.shape)

X = df["text"].astype(str).tolist()
y = df["label"].astype(str).tolist()

print("✅ Loading multilingual model...")
embedder = SentenceTransformer("distiluse-base-multilingual-cased-v2")
print("✅ Model loaded")

print("✅ Encoding text to vectors...")
X_vec = embedder.encode(X, show_progress_bar=True)
print("✅ Encoding done")

X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42
)

clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, y_train)

pred = clf.predict(X_test)
acc = accuracy_score(y_test, pred)

print("✅ Accuracy:", acc)

os.makedirs("models", exist_ok=True)
joblib.dump(clf, "models/mbert_lr.pkl")
joblib.dump(embedder, "models/embedder.pkl")

print("✅ Saved models to models/ folder")