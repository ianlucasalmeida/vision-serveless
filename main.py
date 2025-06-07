# /vision-serveless/main.py
import docker
from app.app import app, ensure_buckets_exist

ESSENTIAL_SERVICES = [
    "vision-serveless_minio",
    "vision-serveless_gateway"
]

def check_docker_services():
    print("Verificando a saúde dos serviços de infraestrutura Docker...")
    try:
        client = docker.from_env()
        running_containers = [c.name for c in client.containers.list()]
        status = {}
        all_ok = True
        for service in ESSENTIAL_SERVICES:
            if any(service in s for s in running_containers):
                status[service.replace('vision-serveless_', '')] = "✅ Online"
            else:
                status[service.replace('vision-serveless_', '')] = "❌ Offline"
                all_ok = False
        return status, all_ok
    except docker.errors.DockerException:
        print("\n❌ ERRO: Não foi possível conectar ao Docker. Ele está rodando?")
        return {service.replace('vision-serveless_', ''): "❌ Erro" for service in ESSENTIAL_SERVICES}, False

def run_orchestrator():
    print("==============================================")
    print("==   Orquestrador Vision-Serveless   ==")
    print("==============================================")
    status, all_services_ok = check_docker_services()
    print("\n--- Status da Infraestrutura ---")
    for service, state in status.items():
        print(f"- {service}: {state}")
    
    if not all_services_ok:
        print("\n❌ Alerta: Um ou mais serviços de infraestrutura não estão online.")
        print("   Por favor, inicie a infraestrutura com 'docker stack deploy ...' e tente novamente.")
    else:
        print("\nInfraestrutura pronta!")

    app.config['SYSTEM_STATUS'] = status

    if all_services_ok:
        ensure_buckets_exist()

    print("\n--- Painel de Gerenciamento ---")
    print("🔗 Console do MinIO: http://localhost:9001")
    print("🔗 Painel do OpenFaaS: http://localhost:8080")
    print("\n---------------------------------------------------------")
    print("Aplicação Flask rodando em: http://localhost:5000")
    print("Para parar a aplicação, pressione CTRL+C neste terminal.")
    print("---------------------------------------------------------")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

if __name__ == '__main__':
    run_orchestrator()