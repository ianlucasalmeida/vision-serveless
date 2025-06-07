#!/bin/bash

# Define as variáveis
LAMBDA_FUNCTION_NAME="vision-processor"
LAMBDA_ROLE_NAME="lambda-s3-role"
INPUT_BUCKET="input-bucket"
OUTPUT_BUCKET="output-bucket"
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="000000000000" # ID padrão para o LocalStack

echo "--- Criando Role IAM para a Lambda ---"
ROLE_ARN=$(awslocal iam create-role \
  --role-name ${LAMBDA_ROLE_NAME} \
  --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}' \
  --query 'Role.Arn' --output text)

awslocal iam attach-role-policy \
  --role-name ${LAMBDA_ROLE_NAME} \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

echo "Role ARN: ${ROLE_ARN}"
# Pequena pausa para garantir que a role se propague
sleep 5

echo "--- Criando Buckets S3 ---"
awslocal s3api create-bucket --bucket ${INPUT_BUCKET}
awslocal s3api create-bucket --bucket ${OUTPUT_BUCKET}
# Inicializa o arquivo de estatísticas
echo '{"operations": {}}' > stats.json
awslocal s3 cp stats.json s3://${OUTPUT_BUCKET}/stats.json
rm stats.json

echo "--- Empacotando a Função Lambda ---"
cd faas-function
pip install -r requirements.txt -t ./package
cp handler.py ./package/
cp -r processors ./package/
cd package
zip -r ../lambda_package.zip .
cd ..
rm -rf package
cd ..

echo "--- Criando/Atualizando a Função Lambda ---"
awslocal lambda create-function \
  --function-name ${LAMBDA_FUNCTION_NAME} \
  --runtime python3.9 \
  --handler handler.handler \
  --memory-size 256 \
  --timeout 60 \
  --role ${ROLE_ARN} \
  --zip-file fileb://faas-function/lambda_package.zip \
  --region ${AWS_REGION} > /dev/null 2>&1 || \
awslocal lambda update-function-code \
  --function-name ${LAMBDA_FUNCTION_NAME} \
  --zip-file fileb://faas-function/lambda_package.zip > /dev/null 2>&1

echo "--- Configurando o Gatilho S3 -> Lambda ---"
LAMBDA_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:function:${LAMBDA_FUNCTION_NAME}"
awslocal lambda add-permission --function-name ${LAMBDA_FUNCTION_NAME} --statement-id "s3-invoke-permission" --action "lambda:InvokeFunction" --principal s3.amazonaws.com --source-arn arn:aws:s3:::${INPUT_BUCKET}
awslocal s3api put-bucket-notification-configuration --bucket ${INPUT_BUCKET} --notification-configuration '{ "LambdaFunctionConfigurations": [{ "LambdaFunctionArn": "'${LAMBDA_ARN}'", "Events": ["s3:ObjectCreated:*"] }] }'

echo "--- Setup concluído! ---"