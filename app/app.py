# /vision-serveless/app/app.py
import logging
import boto3
import json
from botocore.client import Config
from botocore.exceptions import ClientError
from flask import Flask, render_template, request, jsonify
import uuid

app = Flask(__name__)
logging.basicConfig(filename='system.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

S3_ENDPOINT_URL = "http://localhost:4566"
OUTPUT_BUCKET = "output-bucket"
INPUT_BUCKET = "input-bucket"
STATS_FILE_KEY = "stats.json"

s3_client = boto3.client(
    "s3", endpoint_url=S3_ENDPOINT_URL, aws_access_key_id="test",
    aws_secret_access_key="test", region_name="us-east-1",
    config=Config(signature_version='s3v4')
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or not request.form.get('operation'):
        return jsonify({"error": "Requisição incompleta (arquivo ou operação faltando)."}), 400

    file = request.files['file']
    operation = request.form.get('operation')
    params = request.form.get('params', '')
    
    metadata = {"operation": operation, "params": params}
    unique_filename = f"{uuid.uuid4()}-{file.filename}"

    try:
        s3_client.upload_fileobj(
            file, INPUT_BUCKET, unique_filename,
            ExtraArgs={"Metadata": metadata}
        )
        logging.info(f"Arquivo '{unique_filename}' com operação '{operation}' enviado.")
        return jsonify({"success": f"Arquivo enviado. Operação '{operation}' iniciada."})
    except ClientError as e:
        logging.error(f"Erro no upload para o S3: {e}")
        return jsonify({"error": "Falha ao enviar o arquivo."}), 500

@app.route('/logs')
def get_logs():
    try:
        with open('system.log', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""

@app.route('/stats')
def get_stats():
    try:
        stats_obj = s3_client.get_object(Bucket=OUTPUT_BUCKET, Key=STATS_FILE_KEY)
        stats_data = json.loads(stats_obj['Body'].read().decode('utf-8'))
        return jsonify(stats_data.get("operations", {}))
    except ClientError:
        return jsonify({"error": "Arquivo de estatísticas não encontrado."})