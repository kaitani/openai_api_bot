from openai import AsyncOpenAI
from openai import OpenAI
import os
from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from enum import Enum
import requests

import os  # OpenAI ChatCompletionのAPIキー
# from openai import AsyncOpenAI
import streamlit as st


# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key
client = OpenAI(api_key=OPENAI_API_KEY)

from pathlib import Path
from llama_index import download_loader

PDFReader = download_loader("PDFReader")

loader = PDFReader()
documents = loader.load_data(file=Path("/Users/kaiya/Library/CloudStorage/Dropbox/0python/py開発用/chatGPT_LINEbot_GCP/コンプライアンスのすべて.pdf"))

from llama_index import ServiceContext, LLMPredictor, VectorStoreIndex
from langchain.chat_models import ChatOpenAI

service_context = ServiceContext.from_defaults(
    llm_predictor=LLMPredictor(
        llm=ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
    )
)

# indexを作成
index = VectorStoreIndex.from_documents(documents, service_context=service_context)
index.storage_context.persist(persist_dir="./storage/")
query_engine = index.as_query_engine()





# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "あなたは優秀なアシスタントAIです。"}
        ]

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = query_engine.query(
    messages=messages
    )

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄を消去


# ユーザーインターフェイスの構築
st.title("My AI Assistant")
st.write("ChatGPT APIを使ったチャットボットです。")

user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    messages = st.session_state["messages"]

    for message in reversed(messages[1:]):  # 直近のメッセージを上に
        speaker = "🙂"
        if message["role"]=="assistant":
            speaker="🤖"

        st.write(speaker + ": " + message["content"])
