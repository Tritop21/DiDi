from flask import Flask, redirect, url_for, session, jsonify
from flask import request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import json

from googleapiclient.http import MediaFileUpload
from regex import regex

import ai

app = Flask(__name__)

app.secret_key = 'your_secret_key'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Path to your service account key file
SERVICE_ACCOUNT_FILE = "service.json"

# Scopes for Google Docs API
SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/drive.readonly',
          'https://www.googleapis.com/auth/drive.file']

@app.route('/')
def index():
    # Load credentials from the service account file
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Build the Drive service
    service = build('drive', 'v3', credentials=creds)

    # The ID of the file you want to open
    file_id = '1XU4yBtiBIonSsxa4FO6uN_mo_NZbPsEx36Wk2HMiq2U'

    # Get the file metadata
    file = service.files().get(fileId=file_id).execute()

    return f"File Name: {file['name']}"

@app.route('/checkid/<docid>/<contextid>')
def checkid(docid, contextid):
    # Load credentials from the service account file
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Build the Docs and Drive services
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # Get the document content
    document = docs_service.documents().get(documentId=docid).execute()
    content = document.get('body').get('content')

    # Extract paragraphs
    paragraphs = []
    for element in content:
        if 'paragraph' in element:
            for text_run in element['paragraph']['elements']:
                if 'textRun' in text_run:
                    paragraphs.append(text_run['textRun']['content'])

    # Convert paragraphs to Markdown
    markdown_content = '\n\n'.join(paragraphs)
    markdown_file_path = 'currentfile.md'

    with open(markdown_file_path, 'w') as markdown_file:
        markdown_file.write(markdown_content)

    # Upload the Markdown file to Google Drive
    file_metadata = {
        'name': 'currentfile.md',
        'mimeType': 'application/vnd.google-apps.document'
    }
    media = MediaFileUpload(markdown_file_path, mimetype='text/markdown')
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    response = ai.triggerAI(docid, contextid)
    jsonres = str2json(response)
    print(jsonres)

    return jsonres

def str2json(input):
    pattern = regex.compile(r'\{(?:[^{}]|(?R))*\}')
    return json.loads("".join(pattern.findall(input)))

if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)