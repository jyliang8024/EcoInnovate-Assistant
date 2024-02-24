from openai import OpenAI
from libs.main_layout import *
import streamlit as st

OpenAI.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI()


# prompt generator
def prompt_generator(question, chat_response):
    input_text = question + " " + chat_response
    prompt_text = [
        {"role": "system",
         "content": f"""I want you act as a professional prompt generator to generate concise prompts for DALLE3 to create images to illustrate sustainable aspects of the products based on the provided text. 
                Each prompt will be under 50 words, tailored to user's query about the products, and ensure the images are product design sketches/blueprinting, focusing on the product's structure, texture, and engineering details, in response to user inquiries."""
         },
        {"role": "user", "content": f"""{input_text}"""}
    ]

    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=prompt_text,
        max_tokens=200,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\n\n"]  # Stopping point to generate concise prompts
    )

    generated_prompts = response.choices[0].message.content.strip()
    return generated_prompts


# img generator
def img_generator(question, chat_response):
    img_prompt = prompt_generator(question, chat_response)
    response = client.images.generate(
        model="dall-e-3",
        prompt=img_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url

