"""
Processamento de documentos para o sistema RAG
Implementa estratégias específicas de chunking por tipo de fonte
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import re
import logging

from langchain_core.documents import Document

from config.settings import (
    settings, 
    BASE_DIR,
    CONTRACTS_DIR, 
    DOCS_DIR, 
    README_PATH,
    CHANGELOG_PATH,
    WHITEPAPER_PATH,
    MANUAL_CORE_PATH,
    TUTORIAL_WALLET_PATH,
    GUIA_MINERACAO_PATH,
    WHITEPAPER_SINTROP_PATH
)

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Processa documentos com estratégias específicas por tipo:
    - Contratos Solidity: 1 arquivo = 1 chunk
    - Markdown docs: Por seções H2
    - README: Chunk único prioritário
    - CHANGELOG: Por versão
    - Whitepaper RC: Por seções H2
    - Manual Core: Por seções H2
    - Tutorial Wallet: Por seções H2
    - Guia Mineração: Por seções H2
    - Whitepaper Sintrop: Por seções H2
    """
    
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    def process_all_documents(self) -> List[Document]:
        """Processa todos os documentos do projeto"""
        logger.info("Iniciando processamento de documentos...")
        
        all_documents = []
        
        # README (prioridade alta)
        logger.info("[1/9] Processando README...")
        all_documents.extend(self._process_readme())
        
        # Contratos Solidity
        logger.info("[2/9] Processando contratos Solidity...")
        all_documents.extend(self._process_contracts())
        
        # Documentação Markdown
        logger.info("[3/9] Processando documentação...")
        all_documents.extend(self._process_documentation())
        
        # CHANGELOG
        logger.info("[4/9] Processando CHANGELOG...")
        all_documents.extend(self._process_changelog())
        
        # Whitepaper RC (prioridade alta)
        logger.info("[5/9] Processando Whitepaper RC...")
        all_documents.extend(self._process_whitepaper())
        
        # Manual Core
        logger.info("[6/9] Processando Manual Core...")
        all_documents.extend(self._process_manual_core())
        
        # Tutorial Wallet
        logger.info("[7/9] Processando Tutorial Wallet...")
        all_documents.extend(self._process_tutorial_wallet())
        
        # Guia Mineração
        logger.info("[8/9] Processando Guia Mineração...")
        all_documents.extend(self._process_guia_mineracao())
        
        # Whitepaper Sintrop
        logger.info("[9/9] Processando Whitepaper Sintrop...")
        all_documents.extend(self._process_whitepaper_sintrop())
        
        logger.info(f"Total de chunks criados: {len(all_documents)}")
        return all_documents
    
    def _process_readme(self) -> List[Document]:
        """
        README: Chunk único prioritário
        """
        try:
            if not README_PATH.exists():
                logger.warning(f"README não encontrado: {README_PATH}")
                return []
            
            content = README_PATH.read_text(encoding="utf-8")
            
            doc = Document(
                page_content=content,
                metadata={
                    "source": str(README_PATH),
                    "file_name": README_PATH.name,
                    "source_type": "readme",
                    "priority": "high",
                    "chunk_strategy": "single_document",
                    "language": "pt-br"
                }
            )
            
            logger.info("README processado como chunk único")
            return [doc]
            
        except Exception as e:
            logger.error(f"Erro ao processar README: {e}")
            return []
    
    def _process_contracts(self) -> List[Document]:
        """
        Contratos Solidity: 1 arquivo = 1 chunk
        Nenhum contrato excede 7000 tokens
        """
        documents = []
        
        try:
            if not CONTRACTS_DIR.exists():
                logger.warning(f"Diretório de contratos não encontrado: {CONTRACTS_DIR}")
                return []
            
            sol_files = list(CONTRACTS_DIR.rglob("*.sol"))
            logger.info(f"Encontrados {len(sol_files)} contratos")
            
            for sol_file in sol_files:
                try:
                    content = sol_file.read_text(encoding="utf-8")
                    
                    # Extrair informações do contrato
                    contract_name = self._extract_contract_name(content)
                    contract_type = self._classify_contract(sol_file.name, content)
                    
                    # Caminho relativo para melhor legibilidade
                    relative_path = sol_file.relative_to(CONTRACTS_DIR.parent)
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(relative_path),
                            "file_name": sol_file.name,
                            "source_type": "contract",
                            "contract_type": contract_type,
                            "contract_name": contract_name,
                            "language": "solidity",
                            "chunk_strategy": "single_file",
                            "priority": "high" if contract_type in ["token", "pool", "rules"] else "medium"
                        }
                    )
                    
                    documents.append(doc)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar {sol_file}: {e}")
            
            logger.info(f"Contratos processados: {len(documents)}")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao processar contratos: {e}")
            return []
    
    def _process_documentation(self) -> List[Document]:
        """
        Documentação Markdown: Chunking por seções H2
        """
        documents = []
        
        try:
            if not DOCS_DIR.exists():
                logger.warning(f"Diretório de docs não encontrado: {DOCS_DIR}")
                return []
            
            md_files = list(DOCS_DIR.rglob("*.md"))
            logger.info(f"Encontrados {len(md_files)} arquivos de documentação")
            
            for md_file in md_files:
                try:
                    content = md_file.read_text(encoding="utf-8")
                    sections = self._split_by_h2(content)
                    
                    relative_path = md_file.relative_to(CONTRACTS_DIR.parent)
                    
                    for idx, (title, section_content) in enumerate(sections):
                        doc = Document(
                            page_content=section_content,
                            metadata={
                                "source": str(relative_path),
                                "file_name": md_file.name,
                                "source_type": "documentation",
                                "section_title": title,
                                "chunk_index": idx,
                                "chunk_strategy": "h2_sections",
                                "language": "pt-br",
                                "priority": "medium"
                            }
                        )
                        documents.append(doc)
                        
                except Exception as e:
                    logger.error(f"Erro ao processar {md_file}: {e}")
            
            logger.info(f"Documentação processada: {len(documents)} seções")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao processar documentação: {e}")
            return []
    
    def _process_changelog(self) -> List[Document]:
        """
        CHANGELOG: Chunk por versão (indexar todas)
        """
        try:
            if not CHANGELOG_PATH.exists():
                logger.warning(f"CHANGELOG não encontrado: {CHANGELOG_PATH}")
                return []
            
            content = CHANGELOG_PATH.read_text(encoding="utf-8")
            versions = self._split_changelog_by_version(content)
            
            documents = []
            relative_path = CHANGELOG_PATH.relative_to(CONTRACTS_DIR.parent)
            
            for idx, (version, version_content) in enumerate(versions):
                doc = Document(
                    page_content=version_content,
                    metadata={
                        "source": str(relative_path),
                        "file_name": CHANGELOG_PATH.name,
                        "source_type": "changelog",
                        "version": version,
                        "chunk_index": idx,
                        "chunk_strategy": "by_version",
                        "language": "pt-br",
                        "priority": "medium"
                    }
                )
                documents.append(doc)
            
            logger.info(f"CHANGELOG processado: {len(documents)} versões")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao processar CHANGELOG: {e}")
            return []
    
    def _process_whitepaper(self) -> List[Document]:
        """
        Whitepaper RC: Chunking por seções H2
        Usa arquivo .md já processado pelo Docling
        """
        try:
            if not WHITEPAPER_PATH.exists():
                logger.warning(f"Whitepaper RC não encontrado: {WHITEPAPER_PATH}")
                return []
            
            content = WHITEPAPER_PATH.read_text(encoding="utf-8")
            sections = self._split_by_h2(content)
            
            documents = []
            relative_path = WHITEPAPER_PATH.relative_to(BASE_DIR)
            
            for idx, (title, section_content) in enumerate(sections):
                doc = Document(
                    page_content=section_content,
                    metadata={
                        "source": str(relative_path),
                        "file_name": WHITEPAPER_PATH.name,
                        "source_type": "whitepaper",
                        "section_title": title,
                        "chunk_index": idx,
                        "chunk_strategy": "h2_sections",
                        "language": "pt-br",
                        "priority": "high"
                    }
                )
                documents.append(doc)
            
            logger.info(f"Whitepaper RC processado: {len(documents)} seções")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao processar Whitepaper RC: {e}")
            return []
    
    def _process_manual_core(self) -> List[Document]:
        """
        Manual Core RC: Chunking por seções H2
        Manual do usuário do aplicativo Core
        """
        try:
            if not MANUAL_CORE_PATH.exists():
                logger.warning(f"Manual Core não encontrado: {MANUAL_CORE_PATH}")
                return []
            
            content = MANUAL_CORE_PATH.read_text(encoding="utf-8")
            sections = self._split_by_h2(content)
            
            documents = []
            relative_path = MANUAL_CORE_PATH.relative_to(BASE_DIR)
            
            for idx, (title, section_content) in enumerate(sections):
                doc = Document(
                    page_content=section_content,
                    metadata={
                        "source": str(relative_path),
                        "file_name": MANUAL_CORE_PATH.name,
                        "source_type": "manual_user",
                        "section_title": title,
                        "chunk_index": idx,
                        "chunk_strategy": "h2_sections",
                        "language": "pt-br",
                        "priority": "medium"
                    }
                )
                documents.append(doc)
            
            logger.info(f"Manual Core processado: {len(documents)} seções")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao processar Manual Core: {e}")
            return []
    
    def _process_tutorial_wallet(self) -> List[Document]:
        """
        Tutorial Wallet: Chunking por seções H2
        Tutorial de criação e configuração de carteira MetaMask
        """
        try:
            if not TUTORIAL_WALLET_PATH.exists():
                logger.warning(f"Tutorial Wallet não encontrado: {TUTORIAL_WALLET_PATH}")
                return []
            
            content = TUTORIAL_WALLET_PATH.read_text(encoding="utf-8")
            sections = self._split_by_h2(content)
            
            documents = []
            relative_path = TUTORIAL_WALLET_PATH.relative_to(BASE_DIR)
            
            for idx, (title, section_content) in enumerate(sections):
                doc = Document(
                    page_content=section_content,
                    metadata={
                        "source": str(relative_path),
                        "file_name": TUTORIAL_WALLET_PATH.name,
                        "source_type": "tutorial",
                        "section_title": title,
                        "chunk_index": idx,
                        "chunk_strategy": "h2_sections",
                        "language": "pt-br",
                        "priority": "medium"
                    }
                )
                documents.append(doc)
            
            logger.info(f"Tutorial Wallet processado: {len(documents)} seções")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao processar Tutorial Wallet: {e}")
            return []
    
    def _process_guia_mineracao(self) -> List[Document]:
        """
        Guia Mineração: Chunking por seções H2
        Guia técnico de configuração de nós e mineração Sintrop
        """
        try:
            if not GUIA_MINERACAO_PATH.exists():
                logger.warning(f"Guia Mineração não encontrado: {GUIA_MINERACAO_PATH}")
                return []
            
            content = GUIA_MINERACAO_PATH.read_text(encoding="utf-8")
            sections = self._split_by_h2(content)
            
            documents = []
            relative_path = GUIA_MINERACAO_PATH.relative_to(BASE_DIR)
            
            for idx, (title, section_content) in enumerate(sections):
                doc = Document(
                    page_content=section_content,
                    metadata={
                        "source": str(relative_path),
                        "file_name": GUIA_MINERACAO_PATH.name,
                        "source_type": "manual_technical",
                        "section_title": title,
                        "chunk_index": idx,
                        "chunk_strategy": "h2_sections",
                        "language": "pt-br",
                        "priority": "medium"
                    }
                )
                documents.append(doc)
            
            logger.info(f"Guia Mineração processado: {len(documents)} seções")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao processar Guia Mineração: {e}")
            return []
    
    def _process_whitepaper_sintrop(self) -> List[Document]:
        """
        Whitepaper Sintrop: Chunking por seções H2
        Whitepaper da blockchain Sintrop (infraestrutura)
        """
        try:
            if not WHITEPAPER_SINTROP_PATH.exists():
                logger.warning(f"Whitepaper Sintrop não encontrado: {WHITEPAPER_SINTROP_PATH}")
                return []
            
            content = WHITEPAPER_SINTROP_PATH.read_text(encoding="utf-8")
            sections = self._split_by_h2(content)
            
            documents = []
            relative_path = WHITEPAPER_SINTROP_PATH.relative_to(BASE_DIR)
            
            for idx, (title, section_content) in enumerate(sections):
                doc = Document(
                    page_content=section_content,
                    metadata={
                        "source": str(relative_path),
                        "file_name": WHITEPAPER_SINTROP_PATH.name,
                        "source_type": "whitepaper_sintrop",
                        "section_title": title,
                        "chunk_index": idx,
                        "chunk_strategy": "h2_sections",
                        "language": "pt-br",
                        "priority": "medium"
                    }
                )
                documents.append(doc)
            
            logger.info(f"Whitepaper Sintrop processado: {len(documents)} seções")
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao processar Whitepaper Sintrop: {e}")
            return []
    
    # Funções auxiliares
    
    def _extract_contract_name(self, content: str) -> str:
        """Extrai nome do contrato do código Solidity"""
        match = re.search(r"contract\s+(\w+)", content)
        return match.group(1) if match else "Unknown"
    
    def _classify_contract(self, filename: str, content: str) -> str:
        """Classifica tipo do contrato"""
        if "Pool" in filename:
            return "pool"
        elif "Rules" in filename:
            return "rules"
        elif "RegenerationCredit.sol" == filename:
            return "token"
        elif "Impact" in filename:
            return "impact"
        elif "shared" in filename.lower():
            return "shared"
        else:
            return "other"
    
    def _split_by_h2(self, content: str) -> List[Tuple[str, str]]:
        """
        Divide conteúdo Markdown por seções H2
        Retorna lista de (título, conteúdo)
        """
        sections = []
        
        # Regex para capturar H2 e seu conteúdo até o próximo H2 ou fim
        pattern = r"^##\s+(.+?)$"
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        
        if not matches:
            # Se não houver H2, retornar documento inteiro
            return [("Document", content)]
        
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            start = match.start()
            
            # Encontrar fim da seção (próximo H2 ou fim do documento)
            if i < len(matches) - 1:
                end = matches[i + 1].start()
            else:
                end = len(content)
            
            section_content = content[start:end].strip()
            sections.append((title, section_content))
        
        return sections
    
    def _split_changelog_by_version(self, content: str) -> List[Tuple[str, str]]:
        """
        Divide CHANGELOG por versões
        Retorna lista de (versão, conteúdo)
        """
        versions = []
        
        # Regex para capturar versões no formato ## [X.Y.Z] ou ## vX.Y.Z ou ## X.Y.Z
        pattern = r"^##\s+\[?v?(\d+\.\d+\.\d+)\]?"
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        
        if not matches:
            # Se não houver versões, retornar documento inteiro
            return [("all", content)]
        
        for i, match in enumerate(matches):
            version = match.group(1)
            start = match.start()
            
            # Encontrar fim da versão
            if i < len(matches) - 1:
                end = matches[i + 1].start()
            else:
                end = len(content)
            
            version_content = content[start:end].strip()
            versions.append((version, version_content))
        
        return versions


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    
    # Teste
    processor = DocumentProcessor()
    chunks = processor.process_all_documents()
    
    print(f"\nTotal: {len(chunks)} chunks")
    
    # Exemplo de chunk
    if chunks:
        print("\nExemplo de chunk:")
        print(f"Tipo: {chunks[0].metadata.get('source_type')}")
        print(f"Fonte: {chunks[0].metadata.get('source')}")
        print(f"Conteudo (primeiros 200 chars): {chunks[0].page_content[:200]}...")
