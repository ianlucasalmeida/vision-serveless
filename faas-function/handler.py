# /vision-serveless/faas-function/handler.py
import os
from minio import Minio
from urllib.parse import unquote_plus
from processors import image_processor, video_processor, slideshow_creator

MINIO_URL = os.environ.get("MINIO_URL")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
minio_client = Minio(MINIO_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
INPUT_BUCKET = "input-bucket"
OUTPUT_BUCKET = "output-bucket"
TEMP_DIR = "/tmp"

def handle(req):
    try:
        event = req.get_json()
        record = event['Records'][0]
        metadata = record['s3']['object'].get('userMetadata', {})
        operation = metadata.get('x-amz-meta-operation')
        params_str = metadata.get('x-amz-meta-params', '')
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        local_path = os.path.join(TEMP_DIR, os.path.basename(key))
        
        print(f"Evento recebido. Operação: '{operation}', Arquivo: '{key}'")
        minio_client.fget_object(bucket, key, local_path)
        output_path = None
        
        if operation == 'img_to_bw':
            output_path = image_processor.convert_to_bw(local_path)
        elif operation == 'img_change_format':
            output_path = image_processor.change_format(local_path, params_str)
        elif operation == 'extract_frame':
            second = int(params_str) if params_str and params_str.isdigit() else None
            output_path = video_processor.extract_frame(local_path, second)
        else:
            print(f"Operação desconhecida ou não especificada: '{operation}'")
            return {"status": "error", "message": "Operação desconhecida"}, 400

        if output_path and os.path.exists(output_path):
            output_key = f"processed-{os.path.basename(output_path)}"
            minio_client.fput_object(OUTPUT_BUCKET, output_key, output_path)
            print(f"Resultado salvo como '{output_key}'")
            os.remove(output_path)
        
        os.remove(local_path)
        return {"status": "success", "operation": operation}, 200

    except Exception as e:
        print(f"Erro no handler: {e}")
        return {"status": "error", "message": str(e)}, 500