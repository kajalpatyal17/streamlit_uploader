import boto3
import os
import io
from PyPDF2 import PdfReader
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import qdrant_client
import openai
from qdrant_client.models import PointStruct
from qdrant_client.models import VectorParams, Distance
from langchain.text_splitter import CharacterTextSplitter
import requests
import json

load_dotenv()
OPENAI_API_KEY = st.secrets["openai"]["api_key"]
QDRANT_API_KEY = st.secrets["qdrant"]["api_key"]
QDRANT_URL = st.secrets["qdrant"]["url"]

def find_bucket_key(s3_path):
  
    s3_components = s3_path.split('/')
    bucket = s3_components[0]
    s3_key = ""
    if len(s3_components) > 1:
        s3_key = '/'.join(s3_components[1:])
    return bucket, s3_key


def split_s3_bucket_key(s3_path):
 
    if s3_path.startswith('s3://'):
        s3_path = s3_path[5:]
    return find_bucket_key(s3_path)

def read_file_from_s3(s3,bucket_name, file_name):
    obj = s3.get_object(Bucket=bucket_name, Key=file_name)
    data = obj['Body'].read()
    return data

def get_pdf_text(pdf):
    text = ""
    # print(pdf)
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def create_qdrant_points(result,texts):
    points = [
    PointStruct(
        id=idx,
        vector=data.embedding,
        payload={"text": text},
    )
    for idx, (data, text) in enumerate(zip(result.data, texts))
    ]
    return points

def qdrant_upsert(client,points):
    qcollection_name = "aispoc_collection"
    if client.collection_exists(collection_name=qcollection_name):
        client.delete_collection(collection_name=qcollection_name)

    client.create_collection(
        qcollection_name,
        vectors_config=VectorParams(
            size=1536,
            distance=Distance.COSINE,
        ),
    )
    client.upsert(qcollection_name, points)

def update_embeddings(files_uploaded):
    # s3 = boto3.client('s3')
    s3_client = boto3.client(
        's3',  
        aws_access_key_id=st.secrets["aws"]["access_key_id"],  # Accessing secrets from Streamlit's secrets
        aws_secret_access_key=st.secrets["aws"]["secret_access_key"],
        region_name='us-east-1' 
    )
    openai_client = openai.Client(api_key=OPENAI_API_KEY)
    qclient = qdrant_client.QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=60
    )
    embedding_model = "text-embedding-ada-002"

    for file in files_uploaded:
        bucket_name, file_name = split_s3_bucket_key(file)
        file_data = read_file_from_s3(s3_client,bucket_name,file_name)
        pdf_file = io.BytesIO(file_data)
        # print("\n File Data:\n",file_data,'\n')
        raw_text = get_pdf_text(pdf_file)
        text_chunks = get_text_chunks(raw_text)
        results = openai_client.embeddings.create(input=text_chunks, model=embedding_model)
        embed_points = create_qdrant_points(results,text_chunks)
        qdrant_upsert(qclient,embed_points)
        print(f"File: {file} is uploaded")

def main():
    files_to_upload = list(json.loads(requests.get('http://10.1.208.192:9000/docuements').text)['folders'].values())
    update_embeddings(files_to_upload)



