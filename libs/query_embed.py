import chromadb
from openai import OpenAI
import streamlit as st
from libs.knowledge_db import *
from libs.sidebar import *

# openai key
OpenAI.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI()

# collection = create_knowledge_db()
# load the collection
chroma_client = chromadb.PersistentClient(path="./chromadb")
collection = chroma_client.get_collection(name="knowledge_database")


# function for query embedding
def query_embed(question):
    """
        using text-embedding-ada-002 to convert the user-input query into embeddings
    """
    response = client.embeddings.create(
        input=question,
        model="text-embedding-ada-002"
    )
    question_embeddings = response.data[0].embedding
    return question_embeddings


# function for retrieving
def retrieve_from_knowledge_base(question, collection):
    """
    using query to retrieve top k results from knowledge database
    """
    # retrieval content from knowledge db
    question_embeddings = query_embed(question)
    results = collection.query(
        query_embeddings=question_embeddings,
        include=["documents"],
        n_results=3
    )
    return results


# function for generating response
def get_gpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=prompt,
        max_tokens=2000,
        temperature=st.session_state["temperature"],
        top_p=st.session_state["top_p"],
        frequency_penalty=st.session_state["frequency_penalty"],
        presence_penalty=st.session_state["presence_penalty"]
    )
    analysis = response.choices[0].message.content.strip()
    return analysis


# generate response for user query based on retrieved results and chat history
def process_userinput(question, conversation_history):
    # get latest 4 chat history
    recent_history = conversation_history[-4:]

    # using string to represent chat_history
    history_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])

    # retrieve results for user input
    results = retrieve_from_knowledge_base(question, collection)
    print(results)
    text_list = results['documents'][0]
    retrieved_results = "\n".join(text_list)

    chat_prompt = [
        {"role": "system",
         "content": f"""You are an AI assistant expert in green product design. When the user asks about how to design products, answer the user’s question and formulate actionable guidelines for eco-design using the information provided in the {history_context} and {retrieved_results} below.
                        Make sure to connect each guideline to the user's questions, explaining how it addresses or assists in resolving their needs."""
                    f"""--- {history_context} ---"""
                    f"""--- {retrieved_results} --- """
                    f"""Your response should strictly align with the following schema:
                        Guideline: must be each guideline sentence from the {retrieved_results}.
                        Description: Expand on the sentence from {retrieved_results} by detailing intervention timing (WHEN), component actions (WHAT), and methods (HOW). "WHEN" refers to stages of the product lifecycle: pre-manufacturing, manufacturing, usage, and end-of-life. The solutions you generated relate to these stages. Do not mention any of "WHEN", "HOW", "WHAT","ACT" directly in your response.
                        Solutions: List specific solutions for 'How'. These should be presented in bullet points, providing clear and actionable steps.
                        Examples: Illustrate each guideline with 2 or 3 distinct actions derived from real case studies in the business world. Mention the company/manufacturer names explicitly and ensure that these examples are based on publicly available case studies. These examples should help users better understand and apply the guidelines."""
                    f"""If the user's question does not relate to designing products, directly answer the question using the {history_context} provided."""
                    f"""Use clear, concise, and professional language, avoiding colloquialisms and personal pronouns. REMEMBER: If there is nothing in the context relevant to the question at hand, just say "Sorry, I'm not sure" and stop after that. Refuse to answer any question not about the info. Never break character."""
         },
        {"role": "user", "content": f"""Please answer the question: {question}"""}
    ]

    chat_response = get_gpt_response(chat_prompt)

    return chat_response
