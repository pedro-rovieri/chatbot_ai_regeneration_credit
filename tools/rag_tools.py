"""
Ferramentas RAG para busca de informações no projeto Regeneration Credit
"""
from typing import List, Optional
try:
    # LangChain 1.0+
    from langchain_core.tools import Tool
except ImportError:
    # LangChain 0.3.x (fallback)
    from langchain.tools import Tool

from pydantic import BaseModel, Field

from rag.vector_store import VectorStoreManager
from config.settings import settings


class RAGTools:
    """Gerenciador de ferramentas RAG para o agente"""
    
    def __init__(self):
        self.vector_store = VectorStoreManager()
        # Carregar vector store existente
        self.vector_store.load_vector_store()
        # Lista para armazenar audits de todas as buscas
        self.audits = []
    
    def _format_results(self, results: List, include_metadata: bool = True) -> str:
        """Formata resultados de busca em texto legível"""
        if not results:
            return "Nenhuma informação encontrada."
        
        formatted = []
        for i, doc in enumerate(results, 1):
            content = doc.page_content.strip()
            
            if include_metadata:
                source = doc.metadata.get('source', 'Desconhecido')
                source_type = doc.metadata.get('source_type', 'unknown')
                
                formatted.append(f"[Resultado {i}]")
                formatted.append(f"Tipo: {source_type}")
                formatted.append(f"Fonte: {source}")
                formatted.append(f"Conteúdo:\n{content}")
                formatted.append("-" * 50)
            else:
                formatted.append(f"[{i}] {content}")
        
        return "\n".join(formatted)
    
    def search_general(self, query: str) -> str:
        """
        Busca geral no conhecimento do projeto Regeneration Credit.
        
        Use esta ferramenta para:
        - Entender conceitos gerais do projeto
        - Buscar informações em documentação, README, CHANGELOG
        - Como usar o aplicativo Core RC (cadastro, níveis, saques, certificados)
        - Como criar e configurar carteira MetaMask
        - Whitepaper e blockchain Sintrop (arquitetura, consenso, mineração, nós)
        - Guias técnicos e tutoriais de setup
        - Responder perguntas amplas sobre infraestrutura e uso
        
        Args:
            query: Pergunta ou termo de busca
            
        Returns:
            Informações relevantes encontradas
        """
        try:
            # Busca com auditoria
            audit = self.vector_store.search_with_audit(
                query=query, 
                k=settings.top_k_results,
                tool_name="search_general"
            )
            self.audits.append(audit)
            
            # Formatar e retornar resultados
            results = audit["results"]
            return self._format_results(results)
        except Exception as e:
            return f"Erro ao buscar informações: {str(e)}"
    
    def search_contracts(self, query: str) -> str:
        """
        Busca específica em contratos Solidity.
        
        Use esta ferramenta para:
        - Entender a implementação técnica de contratos
        - Buscar funções, variáveis e lógica de contratos
        - Explicar como funciona o código Solidity
        
        Args:
            query: Pergunta sobre contratos ou função específica
            
        Returns:
            Código e explicações de contratos relevantes
        """
        try:
            # Busca com auditoria
            audit = self.vector_store.search_with_audit(
                query=query,
                k=settings.top_k_results,
                filter={"source_type": "contract"},
                tool_name="search_contracts"
            )
            self.audits.append(audit)
            
            # Formatar e retornar resultados
            results = audit["results"]
            
            if not results:
                return ("Nenhum contrato encontrado para essa busca. "
                       "Tente reformular a pergunta ou use a busca geral.")
            
            return self._format_results(results)
        except Exception as e:
            return f"Erro ao buscar contratos: {str(e)}"
    
    def search_whitepaper(self, query: str) -> str:
        """
        Busca específica no Whitepaper do projeto.
        
        Use esta ferramenta para:
        - Entender a visão e propósito do projeto
        - Buscar informações sobre tokenomics
        - Explicar regras de negócio e funcionamento do sistema
        - Consultar diagramas e tabelas descritos
        
        Args:
            query: Pergunta sobre visão, propósito ou regras do projeto
            
        Returns:
            Informações do whitepaper
        """
        try:
            # Busca com auditoria
            audit = self.vector_store.search_with_audit(
                query=query,
                k=settings.top_k_results,
                filter={"source_type": "whitepaper"},
                tool_name="search_whitepaper"
            )
            self.audits.append(audit)
            
            # Formatar e retornar resultados
            results = audit["results"]
            
            if not results:
                return ("Nenhuma informação encontrada no whitepaper. "
                       "Tente reformular a pergunta ou use a busca geral.")
            
            return self._format_results(results)
        except Exception as e:
            return f"Erro ao buscar no whitepaper: {str(e)}"
    
    def consult_tokenomics_guide(self, query: str = "") -> str:
        """
        Retorna guia completo de tokenomics para contexto da calculadora.
        
        Esta ferramenta SEMPRE retorna o documento completo (leitura direta do arquivo).
        Use em 2 momentos com calculadora:
        1) ANTES de calculate_scenario: entender parâmetros e valores de referência
        2) APÓS calculate_scenario: interpretar resultados
        
        Args:
            query: Ignorado - sempre retorna documento completo
            
        Returns:
            Guia completo de tokenomics
        """
        import time
        start_time = time.time()
        
        try:
            from pathlib import Path
            
            # Caminho do arquivo
            sintese_path = Path(__file__).parent.parent / "documents" / "whitepaper_sintese.md"
            
            if not sintese_path.exists():
                return ("Guia de tokenomics não encontrado em: " + str(sintese_path))
            
            # Ler conteúdo completo do arquivo
            content = sintese_path.read_text(encoding="utf-8")
            
            # Calcular tempo de execução
            elapsed_seconds = time.time() - start_time
            
            # Audit completo (mesma estrutura das outras ferramentas RAG)
            self.audits.append({
                "tool_name": "consult_tokenomics_guide",
                "query": query if query else "(documento completo - sempre retorna íntegra)",
                "num_results": 1,  # Sempre retorna 1 documento completo
                "elapsed_seconds": elapsed_seconds,
                "filter": {"method": "direct_file_read"},
                "metadata_summary": {
                    "source": ["whitepaper_sintese.md"],
                    "source_type": ["whitepaper_sintese"],
                    "num_lines": [content.count("\n") + 1],
                    "num_chars": [len(content)]
                },
                "chunks": [
                    {
                        "index": 1,
                        "score": 1.0,  # Relevância máxima (documento completo)
                        "content": content,
                        "metadata": {
                            "source": "whitepaper_sintese.md",
                            "source_type": "whitepaper_sintese",
                            "method": "direct_file_read",
                            "num_lines": content.count("\n") + 1,
                            "num_chars": len(content)
                        }
                    }
                ]
            })
            
            return content
            
        except Exception as e:
            return f"Erro ao consultar guia de tokenomics: {str(e)}"
    
    def get_audits(self) -> List:
        """Retorna lista de audits coletados"""
        return self.audits
    
    def clear_audits(self) -> None:
        """Limpa lista de audits"""
        self.audits = []
    
    def get_tools(self) -> List[Tool]:
        """Retorna lista de ferramentas para o agente"""
        
        tools = [
            Tool(
                name="search_general",
                description=(
                    "Busca geral no conhecimento do projeto Regeneration Credit. "
                    "Use para perguntas sobre: documentação, README, CHANGELOG, "
                    "como usar o app Core RC (cadastro, níveis, saques, certificados), "
                    "como criar e configurar carteira MetaMask, "
                    "whitepaper e blockchain Sintrop (arquitetura, consenso, mineração, nós), "
                    "guias técnicos e tutoriais de setup, ou conceitos gerais de infraestrutura. "
                    "Input: pergunta ou termo de busca em português."
                ),
                func=self.search_general
            ),
            Tool(
                name="search_contracts",
                description=(
                    "Busca específica em contratos Solidity. "
                    "Use quando precisar entender implementação técnica, "
                    "buscar funções específicas ou explicar código de contratos. "
                    "Input: pergunta sobre contratos ou função específica."
                ),
                func=self.search_contracts
            ),
            Tool(
                name="search_whitepaper",
                description=(
                    "Busca específica no Whitepaper do Regeneration Credit. "
                    "Use para perguntas sobre visão do projeto, propósito, "
                    "tokenomics, regras de negócio ou informações estratégicas. "
                    "Input: pergunta sobre visão, propósito ou regras."
                ),
                func=self.search_whitepaper
            ),
            Tool(
                name="consult_tokenomics_guide",
                description=(
                    "Consulta guia de tokenomics do Crédito de Regeneração. "
                    "Use em 2 momentos com a calculadora: "
                    "1) ANTES de calculate_scenario: para entender parâmetros (o que é avg_era_levels, árvores, biodiversidade) e buscar valores de referência sugeridos. "
                    "2) APÓS calculate_scenario: para interpretar resultados (o que é bom score, impacto de diluição, contexto de timing). "
                    "Fornece: tabelas de pontuação, fórmulas, valores de referência, contexto interpretativo. "
                    "SEMPRE retorna documento completo. Input pode ser qualquer coisa ou vazio."
                ),
                func=self.consult_tokenomics_guide
            )
        ]
        
        return tools


# Classe para validação de input das ferramentas
class SearchInput(BaseModel):
    """Input schema para ferramentas de busca"""
    query: str = Field(
        description="Pergunta ou termo de busca em português"
    )

