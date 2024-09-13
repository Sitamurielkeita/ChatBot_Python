# -*- coding: utf-8 -*-
"""Chatbot_python.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IVG5JB8VMk1-dyimQ9A2vcsQHevKYvxU
"""

# Insallation des librairies
!pip install requests
!pip install beautifulsoup4
!pip install transformers faiss-cpu sentence-transformers
!pip install gradio

# Importation des librairies
import requests # scraper l'article
from bs4 import BeautifulSoup # scraper l'article
import faiss
import numpy as np
import pandas as pd
import re
from transformers import pipeline# Modèle RAG
from gradio import Interface # Interface web
from sentence_transformers import SentenceTransformer # Modèle RAG

# URL du site web
url = 'https://www.agenceecofin.com/gestion-publique/0109-121155-le-niger-et-le-nigeria-annoncent-un-front-commun-contre-le-terrorisme'

# Obtenir le contenu de la page
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# On cherche l'élément contenant le texte de l'article
article = soup.find_all('p', class_="texte textearticle")

# Extraire le texte de l'article
if article: # Check to make sure article is not None
    article_text = ' '.join([p.text.strip() for p in article]) # Extract the text from each paragraph and join them
    print(article_text)
else:
    print("Article not found.")

# l'enregistrer dans un fichier:
with open('article.txt', 'w', encoding='utf-8') as f:
    f.write(article_text)

data=[article_text]

# Préparer l'article
sentences = article_text.split('.') # Access the string within the list

# Charger les modèles
model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)
generator = pipeline("text-generation", model="gpt2")

# Encoder les phrases et créer l'index
sentence_embeddings = model.encode(sentences)
dimension = sentence_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(sentence_embeddings)

# Fonction pour générer une réponse
def generate_response(question):
    # Encoder la question
    query_embedding = model.encode(question)

    # Rechercher les k plus proches voisins
    k = 5  # Nombre de phrases à retourner
    distances, indices = index.search(query_embedding, k)

    # Récupérer les phrases les plus similaires
    most_similar_sentences = [sentences[i] for i in indices[0]]

    # Construire le prompt
    prompt = f"Question: {question}\nContexte: {'. '.join(most_similar_sentences)}\nRéponse:"

    # Générer la réponse
    generated_text = generator(prompt=prompt, max_length=100)[0]['generated_text']

    return generated_text

# Interface Gradio
demo = Interface(
    fn=generate_response,
    inputs=["text"],  # Question et article
    outputs="text"
)
demo.launch()