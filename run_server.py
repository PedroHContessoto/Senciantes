#!/usr/bin/env python3
"""
Script de inicialização do servidor backend do projeto Senciantes.
"""

import sys
import os

# Adicionar o diretório atual ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from api_server import app
    
    print("=== Servidor Backend Senciantes ===")
    print("Iniciando servidor na porta 5001...")
    print("Acesse: http://localhost:5001")
    print("Para parar o servidor, pressione Ctrl+C")
    print("=====================================")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\nServidor parado pelo usuário.")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {e}")
        sys.exit(1)

