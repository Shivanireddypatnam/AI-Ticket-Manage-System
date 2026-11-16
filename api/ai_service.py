
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


# Training examples
training_data = [
    # PAYMENT complaints
    ("payment deducted twice", "PAYMENT"),
    ("money deducted from bank account", "PAYMENT"),
    ("refund not received", "PAYMENT"),
    ("unable to complete payment", "PAYMENT"),
    ("wrong amount charged", "PAYMENT"),
    ("payment transaction failed", "PAYMENT"),
    ("duplicate payment", "PAYMENT"),
    ("invoice billing problem", "PAYMENT"),

    # TECHNICAL complaints
    ("application is not working", "TECHNICAL"),
    ("website keeps crashing", "TECHNICAL"),
    ("unable to login to application", "TECHNICAL"),
    ("page is loading slowly", "TECHNICAL"),
    ("getting server error", "TECHNICAL"),
    ("application shows an error", "TECHNICAL"),
    ("password reset page not working", "TECHNICAL"),
    ("website is not opening", "TECHNICAL"),

    # ACCOUNT complaints
    ("change my email address", "ACCOUNT"),
    ("update my phone number", "ACCOUNT"),
    ("delete my account", "ACCOUNT"),
    ("change account details", "ACCOUNT"),
    ("unable to update profile", "ACCOUNT"),
    ("account information is incorrect", "ACCOUNT"),
    ("update my personal details", "ACCOUNT"),
    ("account settings problem", "ACCOUNT"),

    # OTHER complaints
    ("need help with my order", "OTHER"),
    ("delivery has been delayed", "OTHER"),
    ("product not delivered", "OTHER"),
    ("need general assistance", "OTHER"),
    ("want to provide feedback", "OTHER"),
    ("service quality is poor", "OTHER"),
    ("need information about services", "OTHER"),
    ("general customer support request", "OTHER"),
]


# Separate complaint text and categories
X = [item[0] for item in training_data]
y = [item[1] for item in training_data]


# Create Machine Learning pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("classifier", MultinomialNB())
])


# Train the model
model.fit(X, y)


def classify_complaint(subject, description):

    complaint_text = subject + " " + description

    predicted_category = model.predict([complaint_text])[0]

    return predicted_category

import re


def summarize_complaint(subject, description):

    text = subject + ". " + description

    sentences = re.split(r'(?<=[.!?])\s+', text)

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    if len(sentences) <= 2:
        return text

    summary = " ".join(sentences[:2])

    return summary