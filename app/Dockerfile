# /vision-serveless/app/Dockerfile

# 1. Imagem Base
# Começamos com uma imagem oficial do Python. A versão 'slim' é mais leve.
FROM python:3.9-slim

# 2. Diretório de Trabalho
# Define o diretório de trabalho dentro do contêiner.
WORKDIR /usr/src/app

# 3. Copiar e Instalar as Dependências
# Copiamos primeiro o arquivo de requisitos para aproveitar o cache do Docker.
# Se este arquivo não mudar, o Docker não reinstalará as dependências.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar o Código da Aplicação
# Copia todo o conteúdo da pasta 'app' local para o diretório de trabalho no contêiner.
COPY . .

# 5. Expor a Porta
# Informa ao Docker que o contêiner escuta na porta 5000.
EXPOSE 5000

# 6. Comando de Execução
# O comando para iniciar a aplicação quando o contêiner for executado.
# O host '0.0.0.0' é necessário para que o servidor seja acessível de fora do contêiner.
CMD ["python", "app.py"]