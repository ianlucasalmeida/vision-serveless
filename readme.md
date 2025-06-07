# Vision-Serveless: Conversor de Mídia com FaaS

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Swarm-blue.svg)
![OpenFaaS](https://img.shields.io/badge/OpenFaaS-latest-blue.svg)

O Vision-Serveless é uma prova de conceito de um sistema de processamento de arquivos sob demanda, desenvolvido com uma arquitetura serverless e FaaS. O projeto consiste em uma infraestrutura de backend (MinIO e OpenFaaS) rodando em Docker, e um "Painel de Controle" em Flask que roda localmente, responsável por verificar a saúde do sistema, gerenciar requisições e servir a interface do usuário.

## ✨ Funcionalidades

* **Verificação de Saúde**: O orquestrador `main.py` verifica se os serviços de infraestrutura Docker estão online antes de iniciar.
* **Painel de Controle Web**: Uma interface rica que exibe o status dos serviços e oferece formulários específicos para cada operação.
* **Processamento de Mídia via FaaS**:
    * Conversão de imagens para preto e branco ou outros formatos (PNG, JPG).
    * Extração de frames de vídeos em um tempo específico.
* **Comunicação Baseada em Metadados**: O frontend instrui a função FaaS sobre qual operação realizar através de metadados enviados junto com o arquivo para o MinIO.

## 🚀 Como Executar

O projeto utiliza uma abordagem de dois terminais: um para a infraestrutura Docker e outro para a aplicação web local.

### Pré-requisitos
-   [Docker](https://www.docker.com/products/docker-desktop/)
-   [Python 3.9+](https://www.python.org/downloads/)
-   [CLI do OpenFaaS (faas-cli)](https://docs.openfaas.com/cli/install/)

### Passos para Execução

**No Terminal 1 (Gerenciar a Infraestrutura Docker):**

1.  **Clone o repositório** e entre na pasta do projeto.

2.  **Inicie o Docker Swarm (Apenas uma vez)**:
    ```bash
    docker swarm init
    ```

3.  **Inicie os Serviços de Backend (MinIO e OpenFaaS)**:
    ```bash
    docker stack deploy -c docker-compose.yml vision-serveless
    ```
    *Aguarde um minuto para que todos os serviços subam. Você pode verificar o status com `docker service ls`.*

4.  **Faça o Deploy da Função FaaS**:
    * Obtenha a senha de admin do OpenFaaS: `echo $(docker secret inspect basic-auth-password -f '{{ printf "%s" .Spec.Data }}' | base64 --decode)`
    * Faça login: `faas-cli login --password-stdin` (cole a senha e pressione Enter).
    * Navegue até a pasta da função e faça o deploy:
        ```bash
        cd faas-function/
        faas-cli up -f stack.yml
        cd .. 
        ```

5.  **Configure o Gatilho no MinIO**:
    * Acesse `http://localhost:9001` (login: `minioadmin` / `minioadmin`).
    * Crie os buckets `input-bucket` e `output-bucket`.
    * No `input-bucket`, vá em **Events** e crie um Webhook para o endpoint `http://gateway:8080/async-function/vision-processor`, marcando o evento `put`.

**No Terminal 2 (Gerenciar a Aplicação Web):**

1.  **Navegue até a pasta do projeto.**

2.  **Instale as Dependências Python (Apenas uma vez)**:
    ```bash
    pip install -r app/requirements.txt
    ```

3.  **Inicie o Orquestrador e a Aplicação Web**:
    ```bash
    python main.py
    ```
    *O terminal exibirá o status da infraestrutura e os links de gerenciamento.*

4.  **Acesse o Painel de Controle**: Abra seu navegador em **`http://localhost:5000`**.

### Para Parar a Aplicação

1.  Pressione `CTRL+C` no Terminal 2 para parar a aplicação Flask.
2.  Execute no Terminal 1 para derrubar a infraestrutura Docker:
    ```bash
    docker stack rm vision-serveless
    ```