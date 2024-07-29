import os
import google.generativeai as genai
import io
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema.runnable import RunnableMap
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_chroma import Chroma

os.environ["GOOGLE_API_KEY"] = "AIzaSyA3B9r7L0cQDb7rEXIDcU0oaWVllo88W_I"

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def download_file_content(file_id, creds):
    drive_service = build('drive', 'v3', credentials=creds)

    request = drive_service.files().export_media(fileId=file_id, mimeType='text/plain')
    file_buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(file_buffer, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    file_buffer.seek(0)
    return file_buffer.read().decode('utf-8')


def triggerAI(current_file_id, context_file_id):
    SERVICE_ACCOUNT_FILE = "service.json"  # GO TO GOOGLE AND CREATE YOUR SERVICE TOKEN SAVE AS "service.json" AND
    # PUT IN FOLDER
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/drive.readonly',
              'https://www.googleapis.com/auth/drive.file']

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    current_file_content = download_file_content(current_file_id, creds)
    context_content = download_file_content(context_file_id, creds)

    print("Current File Content:", current_file_content)
    print("Context Content:", context_content)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0)
    current_file_splits = text_splitter.split_text(current_file_content)
    context_splits = text_splitter.split_text(context_content)

    current_file_docs = [Document(page_content=chunk, metadata={"source": "current_file"}) for chunk in
                         current_file_splits]
    context_docs = [Document(page_content=chunk, metadata={"source": "context"}) for chunk in context_splits]

    all_docs = current_file_docs + context_docs

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma.from_documents(documents=all_docs, embedding=embeddings)

    template = """provided below is data you can use to check on my work:
    {context}

    based on the data check if 'My Work' is correct

    Highlight my mistakes and differences and also give me the sentences inside My Work that I need to replace in a 
    json format with the schema below:
    
    also in the suggestion, put 1 sentence that I can replace my sentence with, do not say why, just the sentence to
    replace
    {{Response1: "response",
    Response2: "response",
    Response3: "response",
    Response4: "response",
    Suggestion1: "response",
    Suggestion2: "response",
    Sentence1: "response",
    Sentence2: "response",
    Source: "https://docs.google.com/document/d/1I66eo7dhGk_kcYNaDanTlPhJfl2vtFkuIaAd_iqIH8M/edit"
    }}
    My Work:
    {currentFile}

    No need to provide more output beyond this.
    """

    prompt = ChatPromptTemplate.from_template(template)
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-001", temperature=0.7)
    output_parser = StrOutputParser()

    chain = RunnableMap({
        "context": lambda x: context_content,
        "currentFile": lambda y: current_file_content
    }) | prompt | model | output_parser

    response = chain.invoke({"currentFile": current_file_content, "context": context_content})

    return response
