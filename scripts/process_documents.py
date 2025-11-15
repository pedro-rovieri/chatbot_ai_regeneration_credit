#!/usr/bin/env python3
"""
Script para processar e indexar todos os documentos no vector store
"""
import sys
from pathlib import Path
import logging

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from rag.document_processor import DocumentProcessor
from rag.vector_store import VectorStoreManager
from config.settings import setup_directories


def main():
    """Processa todos os documentos e cria/atualiza o vector store"""
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    logger = logging.getLogger(__name__)
    
    print("="*60)
    print("REGENERATION CREDIT - PROCESSAMENTO DE DOCUMENTOS")
    print("="*60 + "\n")
    
    # Setup de diretórios
    logger.info("Criando diretórios necessários...")
    setup_directories()
    
    # Processar documentos
    logger.info("Iniciando processamento de documentos...")
    processor = DocumentProcessor()
    
    try:
        documents = processor.process_all_documents()
        
        if not documents:
            logger.error("Nenhum documento foi processado!")
            sys.exit(1)
        
        logger.info(f"Total de chunks criados: {len(documents)}")
        
        # Estatísticas por tipo
        stats = {}
        for doc in documents:
            source_type = doc.metadata.get("source_type", "unknown")
            stats[source_type] = stats.get(source_type, 0) + 1
        
        print("\nEstatisticas por tipo:")
        for source_type, count in sorted(stats.items()):
            print(f"  {source_type.ljust(15)}: {count} chunks")
        
        # Criar/atualizar vector store
        print("\n" + "-"*60)
        logger.info("Criando vector store...")
        
        vector_store_manager = VectorStoreManager()
        vector_store = vector_store_manager.create_vector_store(documents)
        
        logger.info("Vector store criado e persistido com sucesso!")
        
        # Teste de busca
        print("\n" + "-"*60)
        logger.info("Testando busca no vector store...")
        
        test_queries = [
            "O que é Regeneration Credit?",
            "Como funcionam os pool contracts?",
            "Quais são os tipos de usuário?"
        ]
        
        print("\nTeste de buscas:")
        for query in test_queries:
            results = vector_store_manager.search(query, k=2)
            print(f"\n  Query: '{query}'")
            print(f"  Resultados: {len(results)}")
            if results:
                print(f"  Tipo: {results[0].metadata.get('source_type')}")
                print(f"  Fonte: {results[0].metadata.get('source')}")
        
        print("\n" + "="*60)
        print("PROCESSAMENTO CONCLUIDO COM SUCESSO!")
        print("="*60)
        print("\nProximo passo:")
        print("  python ui/app.py")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Erro durante processamento: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()





