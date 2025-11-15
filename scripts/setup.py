#!/usr/bin/env python3
"""
Script de setup inicial
"""
import os
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import setup_directories


def main():
    print("Iniciando setup do Regeneration Credit AI Assistant...\n")
    
    # 1. Criar diretórios
    print("[1/4] Criando estrutura de diretórios...")
    setup_directories()
    print("      OK - Diretórios criados\n")
    
    # 2. Verificar .env
    print("[2/4] Verificando arquivo .env...")
    env_file = ROOT_DIR / ".env"
    env_example = ROOT_DIR / ".env.example"
    
    if not env_file.exists():
        print("      AVISO - Arquivo .env não encontrado!")
        print(f"      Copie {env_example} para .env e configure suas chaves\n")
    else:
        print("      OK - Arquivo .env encontrado\n")
    
    # 3. Verificar ANTHROPIC_API_KEY
    print("[3/4] Verificando ANTHROPIC_API_KEY...")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("      AVISO - ANTHROPIC_API_KEY não configurada no .env\n")
    else:
        print("      OK - ANTHROPIC_API_KEY configurada\n")
    
    # 4. Verificar fontes de dados
    print("[4/4] Verificando fontes de dados...")
    
    contracts_dir = ROOT_DIR / "vector_database" / "contracts"
    docs_dir = ROOT_DIR / "vector_database" / "docs-site" / "docs"
    whitepaper = ROOT_DIR / "documents" / "credito-de-regeneracao_docling.md"
    readme = ROOT_DIR / "vector_database" / "README.md"
    changelog = ROOT_DIR / "vector_database" / "CHANGELOG.md"
    
    checks = {
        "Contratos Solidity": contracts_dir.exists(),
        "Documentacao Markdown": docs_dir.exists(),
        "Whitepaper": whitepaper.exists(),
        "README": readme.exists(),
        "CHANGELOG": changelog.exists(),
    }
    
    for source, exists in checks.items():
        status = "OK  " if exists else "FALTA"
        print(f"      [{status}] {source}")
    
    print("\n" + "="*60)
    
    if all(checks.values()):
        print("Setup concluido! Pronto para processar documentos.")
        print("\nProximo passo:")
        print("   python scripts/process_documents.py")
    else:
        print("AVISO - Algumas fontes nao foram encontradas.")
        print("Verifique os caminhos no .env")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

