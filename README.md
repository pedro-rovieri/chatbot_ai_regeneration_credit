# 🤖 Regeneration Credit AI Assistant

Chatbot inteligente para responder dúvidas sobre o projeto Regeneration Credit usando IA.

## 🎯 Funcionalidades

- **RAG (Retrieval-Augmented Generation)**: Busca inteligente em contratos, documentação e whitepaper
- **Explicação de Conceitos**: Pools, Rules, Eras, Epochs, Níveis, Tokens
- **Modo Iniciante**: Explicações claras e acessíveis para qualquer nível técnico
- **Interface Amigável**: Chat interativo via Streamlit
- **Histórico de Conversas**: Salve e retome conversas em JSON
- **Multi-fonte**: Contratos Solidity, documentação Markdown, whitepaper PDF

## 🏗️ Arquitetura

```
chatbot-ia/
├── agents/              # Agente principal (ReAct)
├── rag/                 # Sistema RAG (Vector Store + Document Processor)
├── tools/               # Ferramentas RAG (search_general, search_contracts, search_whitepaper)
├── config/              # Configurações e settings
├── data/                # Vector store e conversas salvas
├── scripts/             # Scripts de setup e processamento
└── app.py               # Interface Streamlit
```

## 🚀 Quick Start

### 1. Instalar Dependências

```bash
# Ativar ambiente virtual (recomendado)
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
source .venv/bin/activate      # Linux/Mac

# Instalar dependências
pip install -r chatbot-ia/requirements.txt
```

### 2. Configurar API Key

```bash
# Criar arquivo .env em chatbot-ia/
echo "ANTHROPIC_API_KEY=sua-chave-aqui" > chatbot-ia/.env
```

### 3. Setup Inicial

```bash
# Verificar estrutura e fontes de dados
python chatbot-ia/scripts/setup.py

# Processar documentação e criar vector store
python chatbot-ia/scripts/process_documents.py
```

### 4. Executar Interface Streamlit

```bash
cd chatbot-ia
streamlit run app.py
```

Acesse: **http://localhost:8501**

**Outras opções de teste:**
```bash
# Testar agente sem interface
python chatbot-ia/agents/main_agent.py

# Testar ferramentas RAG
python chatbot-ia/scripts/test_rag_tools.py
```

## 📦 Tecnologias

- **LangChain**: Orquestração de agentes e RAG
- **Claude Sonnet 4.5**: LLM principal
- **ChromaDB**: Vector database
- **Sentence Transformers**: Embeddings
- **Streamlit**: Interface web
- **Python 3.10+**: Linguagem base

## 🎓 Documentação

Ver [docs/](docs/) para documentação completa da arquitetura.



