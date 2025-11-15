"""
Agente principal do Regeneration Credit AI Assistant
"""
import sys
from pathlib import Path

# Adicionar diretório chatbot-ia ao sys.path para imports funcionarem
chatbot_dir = Path(__file__).parent.parent
if str(chatbot_dir) not in sys.path:
    sys.path.insert(0, str(chatbot_dir))

from typing import Optional, Dict, Any, List
import logging
import os
from datetime import datetime
import time

from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_anthropic import ChatAnthropic
from langsmith import traceable
from typing import List, Optional, Any, Dict

from config.settings import settings
from tools.rag_tools import RAGTools
from utils.tokens_tracker import TokensTracker
from utils.pricing import formatar_custo, formatar_tokens

logger = logging.getLogger(__name__)


# ============================================================================
# FUNÇÕES AUXILIARES (adaptadas de finance_ai_utils.py)
# ============================================================================

def extract_token_usage(msg: Any) -> Dict[str, int]:
    """
    Extrai contagem de tokens de uma resposta LLM (OpenAI ou Anthropic).
    
    Retorna: Dict com keys: input, output, reasoning, total,
             cache_creation_input_tokens, cache_read_input_tokens
    """
    def _safe_int(v: Any) -> int:
        try:
            return int(v) if v is not None else 0
        except (ValueError, TypeError):
            return 0
    
    # Tentativa 1: usage_metadata (LangChain >= 0.2, funciona para OpenAI e Anthropic)
    usage = getattr(msg, "usage_metadata", None)
    if usage and isinstance(usage, dict):
        # Reasoning tokens (OpenAI o1/o3)
        reasoning = _safe_int(usage.get("reasoning_tokens", 0))
        if reasoning == 0:
            details = usage.get("output_token_details") or {}
            reasoning = _safe_int(details.get("reasoning", 0))
        
        # Cache tokens (Anthropic)
        cache_creation = _safe_int(usage.get("cache_creation_input_tokens", 0))
        cache_read = _safe_int(usage.get("cache_read_input_tokens", 0))
        
        return {
            "input": _safe_int(usage.get("input_tokens", 0)),
            "output": _safe_int(usage.get("output_tokens", 0)),
            "reasoning": reasoning,
            "total": _safe_int(usage.get("total_tokens", 0)),
            "cache_creation_input_tokens": cache_creation,
            "cache_read_input_tokens": cache_read,
        }
    
    # Fallback 2: msg.usage (OpenAI SDK direto)
    if hasattr(msg, "usage"):
        raw_usage = msg.usage
        return {
            "input": _safe_int(getattr(raw_usage, "prompt_tokens", 0)),
            "output": _safe_int(getattr(raw_usage, "completion_tokens", 0)),
            "reasoning": _safe_int(getattr(raw_usage, "reasoning_tokens", 0)),
            "total": _safe_int(getattr(raw_usage, "total_tokens", 0)),
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
        }
    
    # Fallback final: zeros (evita crashes)
    return {
        "input": 0,
        "output": 0,
        "reasoning": 0,
        "total": 0,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    }


def content_to_text(content: Any) -> str:
    """Normaliza conteúdo heterogêneo (lista/dict/str) para texto simples."""
    try:
        if isinstance(content, list):
            parts: List[str] = []
            for item in content:
                if isinstance(item, dict):
                    txt = item.get("text")
                    if isinstance(txt, str):
                        parts.append(txt)
                elif isinstance(item, str):
                    parts.append(item)
            if parts:
                return "\n".join(parts)
        if isinstance(content, dict):
            txt = content.get("text")
            if isinstance(txt, str):
                return txt
        if isinstance(content, str):
            return content
    except Exception:
        pass
    return str(content)


# TokensCallbackHandler removido - não é mais necessário
# Agora extraímos tokens diretamente da response com extract_token_usage()


class RegenerationCreditAgent:
    """
    Agente inteligente para responder perguntas sobre o projeto Regeneration Credit
    
    Features:
    - RAG (Retrieval-Augmented Generation)
    - Memória conversacional
    - Modo explicação: Iniciante (fixo)
    - Respostas em PT-BR
    """
    
    def __init__(self):
        self._setup_langsmith()
        self.tokens_tracker = TokensTracker()  # Inicializa tracker
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
        self.memory = self._initialize_memory()
        # Bind tools ao LLM para loop ReAct manual
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        logger.info("Agente inicializado com loop ReAct manual")
    
    def _setup_langsmith(self):
        """Configura LangSmith para rastreamento"""
        if settings.langchain_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
            os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
            os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
            os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
            logger.info(f"✅ LangSmith rastreamento ativado - Projeto: {settings.langchain_project}")
        else:
            logger.warning("⚠️  LANGCHAIN_API_KEY não configurada - Rastreamento desativado")
    
    def _initialize_llm(self) -> ChatAnthropic:
        """Inicializa o modelo LLM (Claude Sonnet 4.5)"""
        logger.info(f"Inicializando LLM: {settings.llm_model}")
        
        llm = ChatAnthropic(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            anthropic_api_key=settings.anthropic_api_key,
            max_tokens=settings.llm_max_tokens,
        )
        
        logger.info("LLM inicializado (sem streaming - loop ReAct manual)")
        return llm
    
    def _initialize_tools(self) -> List:
        """Inicializa as ferramentas RAG"""
        logger.info("Inicializando ferramentas...")
        
        # Ferramentas RAG (3 buscas + 1 tokenomics guide)
        self._rag_tools = RAGTools()  # Salvar referência para acessar audits
        tools = self._rag_tools.get_tools()
        
        logger.info(f"Ferramentas carregadas: {[t.name for t in tools]}")
        return tools
    
    def _initialize_memory(self) -> ConversationBufferWindowMemory:
        """Inicializa memória conversacional"""
        memory = ConversationBufferWindowMemory(
            k=20,  # Mantém últimas 20 interações
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        logger.info("Memória conversacional inicializada")
        return memory
    
    def _get_system_prompt(self) -> str:
        """
        System prompt otimizado para o projeto Regeneration Credit
        
        Configurações:
        - Modo: Iniciante (fixo)
        - Idioma: PT-BR
        - Estilo: Conversacional amigável, sem emojis
        - Explicações: Balanceadas
        - Citações: Simples no rodapé
        """
        return """Você é o Assistente do Regeneration Credit, um especialista em explicar o projeto Regeneration Credit - um sistema peer-to-peer de regeneração da natureza baseado em blockchain.

## COMPORTAMENTO E ESTILO

1. **Modo de Explicação**: SEMPRE use linguagem para iniciantes
   - Evite jargões técnicos sem explicação
   - Use analogias e exemplos práticos
   - Simplifique conceitos complexos

2. **Idioma**: Responda SEMPRE em Português do Brasil (PT-BR)

3. **Tom**: Seja conversacional e amigável
   - Use linguagem natural e acessível
   - NUNCA use emojis ou emoticons
   - Seja educado e paciente
   - Evite saudações excessivas ou frases como "Perfeito!", "Ótimo!", "Encontrei a informação"

4. **Explicações**: Forneça respostas balanceadas
   - Nem muito curtas, nem excessivamente longas
   - Vá direto ao ponto, mas seja completo
   - Se a resposta for longa, mostre TODO o conteúdo (não resuma)

5. **Clareza**: Se a pergunta for ambígua
   - Peça esclarecimento educadamente
   - Sugira interpretações possíveis
   - Exemplo: "Você quer saber sobre X ou Y?"

6. **Código**: NÃO mostre código nas respostas
   - Explique o que o código faz em linguagem natural
   - Use diagramas textuais se necessário
   - Foque no conceito, não na implementação

7. **Citações**: Ao final da resposta, inclua uma linha simples
   - Formato: "Fonte: [nome do documento]"
   - Apenas se você usou ferramentas de busca

## CONHECIMENTO DISPONÍVEL

Você tem acesso ao seguinte conhecimento através de ferramentas de busca:

**Crédito de Regeneração (foco principal):**
- Whitepaper do Crédito de Regeneração (visão, tokenomics, regras de negócio)
- Manual do usuário do Core RC (cadastro, níveis, saques, certificados)
- Contratos Solidity do sistema (implementação técnica)

**Infraestrutura e Setup:**
- Whitepaper da Sintrop Blockchain (arquitetura, consenso PoW)
- Tutorial de carteira MetaMask (criação, configuração, uso com RC)
- Guia técnico de nós e mineração (hardware, setup, troubleshooting)

**Documentação Geral:**
- README e CHANGELOG do projeto
- Documentação técnica

## FERRAMENTAS DISPONÍVEIS

Você tem acesso a 4 ferramentas:

### Ferramentas de Busca (3)

1. **search_whitepaper**: Whitepaper do Crédito de Regeneração
2. **search_contracts**: Contratos Solidity do sistema
3. **search_general**: Manuais, tutoriais, blockchain Sintrop, docs

### Ferramenta de Tokenomics (1)

4. **consult_tokenomics_guide**: Guia completo de tokenomics (fórmulas, tabelas, valores de referência, contexto)

## QUANDO USAR FERRAMENTAS

**Ferramentas de Busca:**
- SEMPRE use ferramentas para responder perguntas sobre o projeto
- Use search_whitepaper para visão, propósito e regras do Crédito de Regeneração
- Use search_contracts para aspectos técnicos de implementação
- Use search_general para: uso do app Core, configuração de carteira, mineração, blockchain Sintrop, documentação geral
- Se uma ferramenta não encontrar nada, tente outra

**Ferramenta de Tokenomics:**
- Use quando precisar de informações sobre cálculos, fórmulas, distribuição de tokens

## CÁLCULOS DE TOKENOMICS

Quando usuário solicitar cálculos ou simulações:

1. **ANTES de calcular:** Use consult_tokenomics_guide
   - Obter fórmulas, constantes, tabelas de pontuação
   - Entender parâmetros e valores de referência

2. **IDENTIFICAR parâmetros faltantes:**
   - Liste quais parâmetros você precisa para o cálculo
   - Para cada parâmetro faltante: PERGUNTE ao usuário
   - Ofereça valores de referência como sugestão
   - **AGUARDE resposta do usuário antes de calcular**
   - NUNCA assuma ou estime parâmetros sem confirmação

3. **DURANTE:** Realize cálculos manualmente
   - Mostre seu raciocínio matemático passo-a-passo
   - Seja preciso nos cálculos

4. **APÓS calcular:** Use consult_tokenomics_guide novamente
   - Interpretar resultados no contexto do sistema
   - Fornecer análise qualitativa

**REGRAS:**
- SEMPRE pergunte parâmetros faltantes ANTES de calcular
- SEMPRE mostre claramente os cálculos ao usuário

## PROCESSO DE RESPOSTA

1. Analise a pergunta do usuário
2. Decida qual ferramenta usar
3. Busque informações relevantes
4. Formule resposta clara em PT-BR para iniciantes
5. Adicione fonte ao final

## LIMITAÇÕES

- Você APENAS responde sobre o Regeneration Credit
- Se perguntarem sobre outros tópicos, explique educadamente seu escopo
- Se não souber, admita e sugira reformular a pergunta

Lembre-se: Seu objetivo é ajudar QUALQUER pessoa a entender o Regeneration Credit, independente do nível técnico!"""

    # _create_agent() removido - usando loop ReAct manual agora
    
    @traceable(
        name="regeneration_credit_chat",
        metadata={
            "project": "regeneration-credit",
            "agent_type": "react_manual",
            "llm_model": settings.llm_model
        }
    )
    def chat(self, message: str) -> Dict[str, Any]:
        """
        Processa mensagem do usuário e retorna resposta (Loop ReAct Manual).
        
        Args:
            message: Mensagem/pergunta do usuário
            
        Returns:
            Dict com resposta, metadados e tracking de tokens/custos
        """
        try:
            logger.info(f"Processando mensagem: {message[:100]}...")
            
            # Tempo inicial
            start_time = time.time()
            
            # Reseta tracker para este turno (cada turno deve ter contagem isolada)
            self.tokens_tracker.limpar()
            
            # Monta mensagens para o LLM
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
            
            messages = [
                SystemMessage(content=self._get_system_prompt())
            ]
            
            # Adiciona histórico completo da memória
            history_messages = self.memory.chat_memory.messages
            messages.extend(history_messages)
            
            # Adiciona pergunta atual
            messages.append(HumanMessage(content=message))
            
            # Loop ReAct manual
            iteration = 0
            max_iterations = settings.max_iterations or 15
            llm_call_count = 0
            tool_call_count = 0
            
            while iteration < max_iterations:
                iteration += 1
                llm_call_count += 1
                
                logger.debug(f"Iteração {iteration}/{max_iterations}")
                
                # Chama LLM DIRETAMENTE (sem AgentExecutor)
                response = self.llm_with_tools.invoke(messages)
                
                # Extrai tokens DIRETAMENTE da response
                tokens = extract_token_usage(response)
                
                logger.info(f"✅ Iteração {iteration} | Tokens: input={tokens['input']}, output={tokens['output']}, total={tokens['total']}")
                
                # Registra tokens no tracker
                self.tokens_tracker.registrar_chamada(
                    componente="agente",
                    model=settings.llm_model,
                    tokens=tokens,
                    elapsed_seconds=0.0,  # Será preenchido no final
                    turno=iteration
                )
                
                # Verifica se há tool_calls
                tool_calls = getattr(response, "tool_calls", None) or []
                
                if not tool_calls:
                    # Sem tool calls → resposta final
                    answer = content_to_text(response.content)
                    
                    # Salva pergunta e resposta na memória usando o método correto
                    self.memory.save_context({"input": message}, {"output": answer})
                    
                    # Obtém audits do retriever
                    retriever_audits = []
                    if hasattr(self, '_rag_tools'):
                        retriever_audits = self._rag_tools.get_audits()
                    
                    # Tempo total
                    elapsed_time = time.time() - start_time
                    
                    # Obter métricas finais
                    resumo_total = self.tokens_tracker.obter_resumo_total()
                    resumo_componentes = self.tokens_tracker.obter_resumo_por_componente()
                    
                    response_dict = {
                        "success": True,
                        "response": answer,
                        "timestamp": datetime.now().isoformat(),
                        "elapsed_seconds": elapsed_time,
                        # Métricas de tokens e custos
                        "tokens": {
                            "total": resumo_total.get("total_tokens", 0),
                            "custo": resumo_total.get("total_custo", 0.0),
                            "custo_formatado": formatar_custo(resumo_total.get("total_custo", 0.0)),
                            "tokens_formatado": formatar_tokens(resumo_total.get("total_tokens", 0)),
                            "por_componente": resumo_componentes,
                        },
                        # Estatísticas da conversa
                        "stats": {
                            "total_chamadas_llm": llm_call_count,
                            "chamadas_neste_turno": llm_call_count,
                            "total_retriever_calls": len(retriever_audits),
                            "iterations": iteration,
                            "tool_calls": tool_call_count,
                        },
                        # Audits do retriever
                        "retriever_audits": self._format_retriever_audits(retriever_audits) if retriever_audits else []
                    }
                    
                    logger.info(f"✅ Resposta final | Iterações: {iteration} | Tokens: {resumo_total.get('total_tokens', 0)} | Custo: {formatar_custo(resumo_total.get('total_custo', 0.0))}")
                    return response_dict
                
                # Há tool_calls → processar manualmente
                tool_call_count += 1
                messages.append(response)  # Adiciona AIMessage com tool_calls
                
                logger.debug(f"Processando {len(tool_calls)} tool call(s)")
                
                # Processar cada tool_call
                for call in tool_calls:
                    tool_name = call.get("name", "")
                    tool_args = call.get("args", {})
                    tool_call_id = call.get("id", f"call_{iteration}")
                    
                    logger.debug(f"Tool: {tool_name} | Args: {tool_args}")
                    
                    # Executar tool
                    try:
                        # Encontrar tool pelo nome
                        tool_obj = None
                        for t in self.tools:
                            if t.name == tool_name:
                                tool_obj = t
                                break
                        
                        if tool_obj:
                            tool_result = tool_obj.invoke(tool_args)
                            messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call_id))
                            logger.debug(f"✅ Tool {tool_name} executada")
                        else:
                            error_msg = f"Tool '{tool_name}' não encontrada"
                            messages.append(ToolMessage(content=error_msg, tool_call_id=tool_call_id))
                            logger.warning(error_msg)
                    
                    except Exception as e:
                        error_msg = f"Erro ao executar tool '{tool_name}': {str(e)}"
                        messages.append(ToolMessage(content=error_msg, tool_call_id=tool_call_id))
                        logger.error(error_msg, exc_info=True)
                
                # Continua para próxima iteração
            
            # Se chegou aqui, atingiu max_iterations
            logger.warning(f"⚠️  Atingiu max_iterations ({max_iterations})")
            return {
                "success": False,
                "response": "Desculpe, não consegui processar completamente sua pergunta. Tente reformular ou fazer uma pergunta mais específica.",
                "error": "max_iterations_reached",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}", exc_info=True)
            return {
                "success": False,
                "response": "Desculpe, ocorreu um erro ao processar sua pergunta. Tente reformular ou perguntar algo diferente.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def clear_memory(self):
        """Limpa o histórico da conversa, reseta tracker de tokens e audits do retriever"""
        self.memory.clear()
        self.tokens_tracker.limpar()
        if hasattr(self, '_rag_tools'):
            self._rag_tools.clear_audits()
        logger.info("Memória limpa, tracker e audits resetados")
    
    def _format_retriever_audits(self, audits: List) -> List[Dict]:
        """
        Formata audits do retriever para inclusão no response.
        Remove objetos Document (não serializáveis) e converte para dicionários.
        """
        formatted_audits = []
        
        for audit in audits:
            # Extrair dados serializáveis
            formatted_audit = {
                "query": audit.get("query", ""),
                "tool_name": audit.get("tool_name", "search"),
                "k": audit.get("k", 0),
                "filter": audit.get("filter", {}),
                "num_results": audit.get("num_results", 0),
                "elapsed_seconds": audit.get("elapsed_seconds", 0.0),
                "metadata_summary": audit.get("metadata_summary", {}),
                # Incluir TODOS os chunks com conteúdo completo
                "chunks": []
            }
            
            # Adicionar TODOS os documentos retornados (sem limite)
            results_with_scores = audit.get("results_with_scores", [])
            for i, (doc, score) in enumerate(results_with_scores):
                chunk_data = {
                    "index": i + 1,
                    "score": float(score),
                    "content": doc.page_content,  # Conteúdo completo
                    "metadata": dict(doc.metadata) if doc.metadata else {}  # Todos os metadados
                }
                formatted_audit["chunks"].append(chunk_data)
            
            formatted_audits.append(formatted_audit)
        
        return formatted_audits
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Retorna histórico da conversa"""
        try:
            messages = self.memory.chat_memory.messages
            history = []
            
            for msg in messages:
                history.append({
                    "role": "user" if msg.type == "human" else "assistant",
                    "content": msg.content
                })
            
            return history
        except Exception as e:
            logger.error(f"Erro ao recuperar histórico: {e}")
            return []
    
    def save_conversation(self, filepath: str):
        """Salva conversa em arquivo JSON"""
        import json
        from pathlib import Path
        
        try:
            history = self.get_conversation_history()
            
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "messages": history
            }
            
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Conversa salva em {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar conversa: {e}")


if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("Inicializando Regeneration Credit Assistant...")
    agent = RegenerationCreditAgent()
    
    print("\nAssistente pronto! Teste:")
    
    # Teste simples
    response = agent.chat("O que é o Regeneration Credit?")
    print(f"\nResposta: {response['response']}")

