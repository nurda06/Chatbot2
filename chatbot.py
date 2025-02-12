import streamlit as st
import ollama
from pymongo import MongoClient

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["chatbot"]
collection = db["chat_history"]
documents = db["documents"]

# Установка заголовка
st.title("Chatbot with Ollama and MongoDB")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Функция для загрузки файлов
def save_uploaded_files(uploaded_files):
    for uploaded_file in uploaded_files:
        file_content = uploaded_file.read().decode("utf-8")
        documents.insert_one({"filename": uploaded_file.name, "content": file_content})
        st.success(f"Файл {uploaded_file.name} загружен!")

# Загрузка файлов
uploaded_files = st.file_uploader("Загрузите файлы", accept_multiple_files=True, type=["txt"])
if uploaded_files:
    save_uploaded_files(uploaded_files)

# Получение содержимого всех загруженных документов
def get_documents_content():
    return "\n".join([doc["content"] for doc in documents.find()])

# Пользовательский ввод
user_input = st.text_input("You:", "", key="user_input")

if user_input:
    docs_content = get_documents_content()
    
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": "Используй следующие документы как контекст: " + docs_content},
            {"role": "user", "content": user_input}
        ]
    )
    bot_response = response["message"]["content"]
    
    # Сохранение в MongoDB
    collection.insert_one({"role": "user", "content": user_input})
    collection.insert_one({"role": "bot", "content": bot_response})
    
    # Обновление чата
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Bot", bot_response))

# Отображение истории чата
for role, text in st.session_state.chat_history:
    st.text(f"{role}: {text}")
