"""
Gerenciamento do Vector Store (ChromaDB)
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
import time

try:
    # LangChain 1.0+
    from langchain_core.documents import Document
except ImportError:
    # LangChain 0.3.x (fallback)
    from langchain.docstore.document import Document

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import settings, VECTOR_STORE_DIR

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Gerencia o ChromaDB vector store
    - Embeddings: all-MiniLM-L6-v2
    - Busca semântica
    - Filtros por metadados
    """
    
    def __init__(self):
        self.persist_directory = str(VECTOR_STORE_DIR)
        self.embeddings = self._initialize_embeddings()
        self.vector_store: Optional[Chroma] = None
    
    def _initialize_embeddings(self) -> HuggingFaceEmbeddings:
        """Inicializa modelo de embeddings"""
        logger.info(f"Carregando modelo de embeddings: {settings.embedding_model}")
        
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        logger.info("Embeddings carregados")
        return embeddings
    
    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """
        Cria novo vector store e indexa documentos
        """
        logger.info(f"Criando vector store em {self.persist_directory}")
        logger.info(f"Indexando {len(documents)} documentos...")
        
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name="regeneration_credit"
        )
        
        logger.info("Vector store criado e persistido")
        return self.vector_store
    
    def load_vector_store(self) -> Optional[Chroma]:
        """
        Carrega vector store existente
        """
        try:
            logger.info(f"Carregando vector store de {self.persist_directory}")
            
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="regeneration_credit"
            )
            
            logger.info("Vector store carregado")
            return self.vector_store
            
        except Exception as e:
            logger.error(f"Erro ao carregar vector store: {e}")
            return None
    
    def get_or_create_vector_store(self, documents: Optional[List[Document]] = None) -> Chroma:
        """
        Carrega vector store existente ou cria novo
        """
        # Tentar carregar existente
        if Path(self.persist_directory).exists():
            try:
                vs = self.load_vector_store()
                if vs is not None:
                    return vs
            except Exception as e:
                logger.warning(f"Falha ao carregar vector store: {e}")
        
        # Criar novo se não existir ou falhou
        if documents:
            return self.create_vector_store(documents)
        else:
            raise ValueError("Nenhum documento fornecido para criar vector store")
    
    def search(
        self, 
        query: str, 
        k: int = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Busca semântica no vector store
        
        Args:
            query: Consulta em linguagem natural
            k: Número de resultados (padrão: settings.top_k_results)
            filter: Filtros por metadados (ex: {"source_type": "contract"})
        """
        if self.vector_store is None:
            raise ValueError("Vector store não inicializado")
        
        k = k or settings.top_k_results
        
        logger.info(f"Buscando: '{query}' (top_k={k})")
        
        if filter:
            logger.info(f"Filtros aplicados: {filter}")
            results = self.vector_store.similarity_search(
                query,
                k=k,
                filter=filter
            )
        else:
            results = self.vector_store.similarity_search(query, k=k)
        
        logger.info(f"Encontrados {len(results)} resultados")
        return results
    
    def search_with_scores(
        self, 
        query: str, 
        k: int = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Busca com scores de similaridade
        """
        if self.vector_store is None:
            raise ValueError("Vector store não inicializado")
        
        k = k or settings.top_k_results
        
        if filter:
            results = self.vector_store.similarity_search_with_score(
                query,
                k=k,
                filter=filter
            )
        else:
            results = self.vector_store.similarity_search_with_score(query, k=k)
        
        return results
    
    def search_with_audit(
        self,
        query: str,
        k: int = None,
        filter: Optional[Dict[str, Any]] = None,
        tool_name: str = "search"
    ) -> Dict[str, Any]:
        """
        Busca com auditoria completa (query, resultados, tempo, metadados).
        
        Args:
            query: Consulta em linguagem natural
            k: Número de resultados
            filter: Filtros por metadados
            tool_name: Nome da ferramenta que está chamando (para tracking)
        
        Returns:
            {
                "query": str,
                "k": int,
                "filter": dict,
                "tool_name": str,
                "num_results": int,
                "elapsed_seconds": float,
                "results": List[Document],
                "results_with_scores": List[tuple[Document, float]],
                "metadata_summary": dict  # agregação de metadados
            }
        """
        if self.vector_store is None:
            raise ValueError("Vector store não inicializado")
        
        k = k or settings.top_k_results
        
        # Medir tempo
        start_time = time.time()
        
        # Executar busca com scores
        if filter:
            results_with_scores = self.vector_store.similarity_search_with_score(
                query,
                k=k,
                filter=filter
            )
        else:
            results_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
        
        elapsed_seconds = time.time() - start_time
        
        # Extrair documentos
        results = [doc for doc, score in results_with_scores]
        
        # Agregar metadados únicos
        source_types = set()
        sources = set()
        for doc in results:
            if doc.metadata:
                if 'source_type' in doc.metadata:
                    source_types.add(doc.metadata['source_type'])
                if 'source' in doc.metadata:
                    sources.add(doc.metadata['source'])
        
        metadata_summary = {
            "source_types": sorted(source_types),
            "sources": sorted(sources),
            "avg_score": sum(score for _, score in results_with_scores) / len(results_with_scores) if results_with_scores else 0.0,
            "min_score": min(score for _, score in results_with_scores) if results_with_scores else 0.0,
            "max_score": max(score for _, score in results_with_scores) if results_with_scores else 0.0,
        }
        
        audit = {
            "query": query,
            "k": k,
            "filter": filter or {},
            "tool_name": tool_name,
            "num_results": len(results),
            "elapsed_seconds": elapsed_seconds,
            "results": results,
            "results_with_scores": results_with_scores,
            "metadata_summary": metadata_summary,
        }
        
        logger.info(f"Busca auditada: '{query[:50]}...' | {len(results)} resultados | {elapsed_seconds:.3f}s")
        
        return audit
    
    def search_by_type(self, query: str, source_type: str, k: int = None) -> List[Document]:
        """
        Busca filtrada por tipo de fonte
        
        Args:
            source_type: contract, documentation, whitepaper, readme, changelog
        """
        return self.search(
            query=query,
            k=k,
            filter={"source_type": source_type}
        )
    
    def search_contracts(self, query: str, k: int = None) -> List[Document]:
        """Busca específica em contratos"""
        return self.search_by_type(query, "contract", k)
    
    def search_documentation(self, query: str, k: int = None) -> List[Document]:
        """Busca específica em documentação"""
        return self.search_by_type(query, "documentation", k)
    
    def search_whitepaper(self, query: str, k: int = None) -> List[Document]:
        """Busca específica em whitepaper"""
        return self.search_by_type(query, "whitepaper", k)
    
    def get_all_sources(self) -> List[str]:
        """Lista todas as fontes indexadas"""
        if self.vector_store is None:
            return []
        
        # ChromaDB não tem método direto, mas podemos fazer uma busca vazia
        # e coletar metadados únicos
        try:
            all_docs = self.vector_store.similarity_search("", k=1000)
            sources = set(doc.metadata.get("source") for doc in all_docs if "source" in doc.metadata)
            return sorted(sources)
        except Exception as e:
            logger.error(f"Erro ao listar fontes: {e}")
            return []
    
    def delete_vector_store(self):
        """Remove vector store do disco"""
        import shutil
        
        if Path(self.persist_directory).exists():
            shutil.rmtree(self.persist_directory)
            logger.info("Vector store removido")
        
        self.vector_store = None


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    
    # Teste
    manager = VectorStoreManager()
    print("VectorStoreManager inicializado")
    
    # Tentar carregar vector store existente
    try:
        vs = manager.load_vector_store()
        if vs:
            print("\nVector store carregado!")
            
            # Teste de busca
            results = manager.search("O que é um pool contract?", k=3)
            print(f"\nResultados de busca: {len(results)}")
            
            if results:
                print("\nPrimeiro resultado:")
                print(f"Tipo: {results[0].metadata.get('source_type')}")
                print(f"Fonte: {results[0].metadata.get('source')}")
                print(f"Conteudo: {results[0].page_content[:200]}...")
    except Exception as e:
        print(f"Vector store não encontrado ou erro: {e}")
        print("Execute scripts/process_documents.py primeiro")
