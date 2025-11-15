#!/usr/bin/env python3
"""
Script para testar o agente principal
"""
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import logging
from agents.main_agent import RegenerationCreditAgent


def test_agent():
    """Testa o agente com algumas perguntas"""
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    print("="*70)
    print("TESTE DO AGENTE REGENERATION CREDIT")
    print("="*70 + "\n")
    
    # Inicializar agente
    print("Inicializando agente...")
    agent = RegenerationCreditAgent()
    print("[OK] Agente inicializado\n")
    
    # Perguntas de teste
    test_questions = [
        "O que e o Regeneration Credit?",
        "Quais sao os tipos de usuario no sistema?",
        "Como funciona o sistema de eras e epochs?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print("-"*70)
        print(f"PERGUNTA {i}: {question}")
        print("-"*70)
        
        try:
            response = agent.chat(question)
            
            if response["success"]:
                print("\nResposta:")
                print(response["response"])
                print("\n[OK] Resposta gerada com sucesso\n")
            else:
                print(f"\n[ERRO] Falha ao gerar resposta: {response.get('error', 'Desconhecido')}\n")
                
        except Exception as e:
            print(f"\n[ERRO] Excecao durante teste: {e}\n")
    
    # Testar histórico
    print("="*70)
    print("HISTORICO DA CONVERSA")
    print("="*70)
    
    history = agent.get_conversation_history()
    print(f"\nTotal de mensagens: {len(history)}")
    
    for i, msg in enumerate(history, 1):
        role = "Usuario" if msg["role"] == "user" else "Assistente"
        content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
        print(f"{i}. [{role}] {content_preview}")
    
    print("\n" + "="*70)
    print("TESTE CONCLUIDO")
    print("="*70)


if __name__ == "__main__":
    test_agent()



