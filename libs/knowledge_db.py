from openai import OpenAI
import streamlit as st
import os
import pandas as pd
import chromadb
import json


OpenAI.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI()


# load json file
def load_data(json_filename):
    file_path = os.path.join(os.path.dirname(__file__), json_filename)
    df = pd.read_json(file_path)
    guidelines_df = pd.DataFrame(df['guidelines'].explode())
    return guidelines_df


# create embeddings for json file
def create_embeddings(text_list):
    embeddings = []
    for index,row in text_list.iterrows():
        #print(row['guidelines'])
        text = row['guidelines']
        # Generate the embedding for each piece of text
        response = client.embeddings.create(input=text, model="text-embedding-ada-002")
        embeddings.append(response.data[0].embedding)

    return embeddings


# store vector to db
def vector_store(text_list, embeddings):
    chroma_client = chromadb.PersistentClient(path="/Users/maddy/PycharmProjects/green_patent/chromadb")
    ids = [f"id_{i}" for i in range(len(text_list))]
    collection = chroma_client.create_collection(name="knowledge_database",
                                                 metadata={"hnsw:space": "cosine"})
    text_list = text_list['guidelines'].tolist()
    collection.add(documents=text_list, embeddings=embeddings, ids=ids)
    return collection


def create_knowledge_db():
    file_name = 'eco_guidelines.json'
    guidelines = load_data(file_name)
    guidelines_embeddings = create_embeddings(guidelines)
    print(len(guidelines))
    print(len(guidelines_embeddings))
    print(len(guidelines_embeddings[0]))
    knowledge_collection = vector_store(guidelines, guidelines_embeddings)

    return knowledge_collection

