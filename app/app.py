# /vision-serveless/app/app.py
import logging
from flask import Flask, render_template, request, jsonify
from minio import Minio
from minio.error import S3Error
import uuid

logging.basicConfig(filename='system.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)

MINIO_URL = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
minio_client = Minio(MINIO_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
INPUT_BUCKET = "input-bucket"
OUTPUT_BUCKET = "output-bucket"

def ensure_buckets_exist():
    try:
        if not minio_client.bucket_exists(INPUT_BUCKET):
            minio_client.make_bucket(INPUT_BUCKET)
        if not minio_client.bucket_exists(OUTPUT_BUCKET):
            minio_client.make_bucket(OUTPUT_BUCKET)
    except S3Error as e:
        print(f"ERRO: Não foi possível conectar ao MinIO em '{MINIO_URL}'. Verifique se os serviços Docker estão rodando. Detalhe: {e}")

@app.route('/')
def index():
    system_status = app.config.get('SYSTEM_STATUS', {})
    return render_template('index.html', system_status=system_status)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files['file']
    operation = request.form.get('operation')
    params = request.form.get('params', '')
    metadata = {"X-Amz-Meta-Operation": operation, "X-Amz-Meta-Params": params}
    
    try:
        if file.filename == '':
            return jsonify({"error": "Nome de arquivo vazio."}), 400
        
        unique_filename = f"{uuid.uuid4()}-{file.filename}"
        minio_client.put_object(
            INPUT_BUCKET, unique_filename, file, length=-1,
            part_size=10*1024*1024, content_type=file.content_type, metadata=metadata
        )
        logging.info(f"Arquivo '{unique_filename}' com operação '{operation}' enviado.")
        return jsonify({"success": f"Requisição de '{operation}' enviada para o arquivo '{file.filename}'."})
    except S3Error as e:
        logging.error(f"Erro no upload para o MinIO: {e}")
        return jsonify({"error": "Falha ao enviar o arquivo para o armazenamento."}), 500

@app.route('/logs')
def get_logs():
    try:
        with open('system.log', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Arquivo de log ainda não foi criado."