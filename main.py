# /vision-serveless/main.py
from app.app import app

if __name__ == '__main__':
    print("==============================================")
    print("==   Orquestrador Vision-Serveless (LocalStack)   ==")
    print("==============================================")
    print("\n--- Painel de Gerenciamento ---")
    print("🔗 Dashboard do LocalStack: http://localhost:8080")
    print("\n---------------------------------------------------------")
    print("Aplicação Flask rodando em: http://localhost:5000")
    print("Para parar a aplicação, pressione CTRL+C neste terminal.")
    print("---------------------------------------------------------")
    
    app.run(host='0.0.0.0', port=5000, debug=True)