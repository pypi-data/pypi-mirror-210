from langchain.document_loaders import PyPDFLoader

loader = PyPDFLoader("/Users/kevinfortier/Downloads/information_compression.pdf")
pages = loader.load_and_split()
print(pages[0])

import nltk

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def preprocess_text(text):
    # Tokenize and lowercase the text
    tokens = word_tokenize(text.lower())

    # Remove non-alphabetic characters
    words = [word for word in tokens ]#if word.isalpha()]

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]

    # Lemmatize the words
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]

    # Join the words back into a preprocessed text
    preprocessed_text = ' '.join(lemmatized_words)

    return preprocessed_text

loader = PyPDFLoader("/Users/kevinfortier/Downloads/information_compression.pdf")
pages = loader.load_and_split()
print(pages[0])

preprocessed_pages_text = []
for page in pages:
    # Example usage

    preprocessed_text = preprocess_text(page.page_content)
    print(preprocessed_text)
    preprocessed_pages_text.append(preprocessed_text)
print(preprocessed_pages_text[0])