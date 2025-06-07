# /vision-serveless/faas-function/handler.py
import os
import boto3
import json
from urllib.parse import unquote_plus
from processors import image_processor, video_processor

S3_ENDPOINT_URL = f"http://{os.environ.get('LOCALSTACK_HOSTNAME')}:{os.environ.get('EDGE_PORT')}"
INPUT_BUCKET = "input-bucket"
OUTPUT_BUCKET = "output-bucket"
STATS_FILE_KEY = "stats.json"
TEMP_DIR = "/tmp"

s3_client = boto3.client("s3", endpoint_url=S3_ENDPOINT_URL)

def update_stats(operation):
    try:
        # Baixa o arquivo de estatísticas atual
        stats_obj = s3_client.get_object(Bucket=OUTPUT_BUCKET, Key=STATS_FILE_KEY)
        stats_data = json.loads(stats_obj['Body'].read().decode('utf-8'))
        
        # Incrementa o contador da operação
        current_count = stats_data.get("operations", {}).get(operation, 0)
        stats_data["operations"][operation] = current_count + 1
        
        # Faz o upload do arquivo atualizado
        s3_client.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=STATS_FILE_KEY,
            Body=json.dumps(stats_data),
            ContentType='application/json'
        )
        print(f"Estatísticas para '{operation}' atualizadas.")
    except Exception as e:
        print(f"Erro ao atualizar estatísticas: {e}")


def handler(event, context):
    try:
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        # Busca os metadados para saber qual operação executar
        head_object = s3_client.head_object(Bucket=bucket, Key=key)
        metadata = head_object.get('Metadata', {})
        operation = metadata.get('operation')
        params = metadata.get('params', '')

        local_path = os.path.join(TEMP_DIR, os.path.basename(key))
        s3_client.download_file(bucket, key, local_path)

        output_path = None
        if operation == 'img_to_bw':
            output_path = image_processor.convert_to_bw(local_path)
        elif operation == 'img_change_format':
            output_path = image_processor.change_format(local_path, params)
        elif operation == 'extract_frame':
            second = int(params) if params.isdigit() else None
            output_path = video_processor.extract_frame(local_path, second)
        else:
            raise ValueError(f"Operação desconhecida: {operation}")

        if output_path:
            output_key = f"processed-{os.path.basename(output_path)}"
            s3_client.upload_file(output_path, OUTPUT_BUCKET, output_key)
            # Se deu tudo certo, atualiza as estatísticas
            update_stats(operation)
            return {"status": "success", "output_key": output_key}
        
        return {"status": "error", "message": "Nenhum arquivo de saída foi gerado."}

    except Exception as e:
        print(f"Erro no handler: {e}")
        raise e