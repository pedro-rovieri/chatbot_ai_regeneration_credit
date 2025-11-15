# 🤖 Regeneration Credit AI Assistant

Chatbot inteligente para responder dúvidas sobre o projeto Regeneration Credit usando IA com sistema RAG avançado.

## 🎯 Funcionalidades

### Core Features
- **RAG (Retrieval-Augmented Generation)**: Busca inteligente em 9 fontes de dados diferentes
- **4 Ferramentas RAG Especializadas**: Busca geral, contratos, whitepaper e guia de tokenomics
- **Modo Iniciante**: Explicações claras e acessíveis para qualquer nível técnico
- **Loop ReAct Manual**: Raciocínio iterativo com controle total sobre chamadas de ferramentas
- **Claude Haiku 4.5**: LLM rápido e econômico

### Interface Avançada (Streamlit)
- **Aba Chat**: Interface principal de conversação
- **Aba Prompts**: Visualização e download do system prompt
- **Aba Retriever Debug**: Histórico detalhado de todas as buscas no vector store
- **Aba Tokens & Custos**: Rastreamento completo de uso e custos por turno com exportação CSV

### Tracking & Analytics
- **Tokens Tracker**: Contabilização precisa de tokens (input, output, cache)
- **Pricing Calculator**: Custos em tempo real por componente
- **Retriever Audits**: Métricas completas de cada busca (tempo, scores, metadados)
- **Conversas Enriquecidas**: Salva mensagens + tokens + audits + analytics

## 🏗️ Arquitetura

```
chatbot_ai_regeneration_credit/
├── agents/                    # Agente principal (ReAct manual)
│   └── main_agent.py         # RegenerationCreditAgent
├── rag/                       # Sistema RAG
│   ├── document_processor.py # Processamento de 9 fontes
│   └── vector_store.py       # ChromaDB + Audits
├── tools/                     # Ferramentas RAG
│   └── rag_tools.py          # 4 ferramentas especializadas
├── utils/                     # Utilitários
│   ├── tokens_tracker.py     # Rastreamento de tokens
│   └── pricing.py            # Cálculo de custos
├── config/                    # Configurações
│   └── settings.py           # Settings centralizados
├── data/                      # Dados gerados
│   ├── vector_store/         # ChromaDB
│   └── conversations/        # Conversas salvas (JSON)
├── documents/                 # Documentos fontes
│   ├── credito-de-regeneracao_docling.md
│   ├── manual_core_credito_regeneracao_docling.md
│   ├── how_to_create_a_wallet_on_the_blockchain_docling.md
│   ├── sintrop_node_e_guia_de_mineracao_docling.md
│   ├── Whitepaper_Sintrop_*_docling.md
│   └── whitepaper_sintese.md  # Guia de tokenomics
├── vector_database/           # Fontes RAG (57 contratos + 66 docs)
│   ├── contracts/            # Contratos Solidity
│   ├── docs-site/docs/       # Documentação Markdown
│   ├── README.md             # README do projeto principal
│   └── CHANGELOG.md          # Histórico de mudanças
├── scripts/                   # Scripts auxiliares
│   ├── setup.py              # Verificação de setup
│   ├── process_documents.py  # Processamento e indexação
│   └── test_*.py             # Scripts de teste
└── app_completo.py           # Interface Streamlit completa
```

## 🚀 Quick Start

### 1. Instalar Dependências

```bash
# Ativar ambiente virtual (recomendado)
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
source .venv/bin/activate      # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar API Keys

Crie um arquivo `.env` na raiz do projeto:

```bash
# API Key da Anthropic (obrigatória)
ANTHROPIC_API_KEY=sua-chave-anthropic-aqui

# LangSmith (opcional - para rastreamento e observabilidade)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=sua-chave-langsmith-aqui
LANGCHAIN_PROJECT=regeneration-credit-chatbot
```

### 3. Setup Inicial

```bash
# Verificar estrutura e fontes de dados
python scripts/setup.py

# Processar documentação e criar vector store (primeira vez)
python scripts/process_documents.py
```

**Saída esperada:**
- ✅ 57 contratos Solidity processados
- ✅ 66 arquivos Markdown processados  
- ✅ 5 documentos principais processados
- ✅ Vector store criado com sucesso

### 4. Executar Interface Streamlit

```bash
streamlit run app_completo.py
```

Acesse: **http://localhost:8501**

### 5. Usar o Chatbot

1. **Aba Chat**: Faça perguntas sobre o projeto
   - Ex: "O que é o Regeneration Credit?"
   - Ex: "Como funcionam os pool contracts?"
   - Ex: "Explique o sistema de eras e epochs"

2. **Aba Prompts**: Veja o system prompt do assistente

3. **Aba Retriever Debug**: Analise as buscas realizadas
   - Queries enviadas
   - Documentos retornados
   - Scores de similaridade
   - Tempos de execução

4. **Aba Tokens & Custos**: Monitore uso e custos
   - Tokens por turno
   - Custos em USD
   - Breakdown por componente
   - Exportação para CSV

## 🧪 Testes e Scripts

```bash
# Testar agente diretamente (sem interface)
python scripts/test_agent.py

# Testar ferramentas RAG
python scripts/test_rag_tools.py

# Testar sistema de memória
python scripts/test_memory.py

# Testar cálculos de pricing
python scripts/test_pricing.py

# Testar loop ReAct manual
python scripts/test_react_manual.py
```

## 📦 Tecnologias

### Core
- **Python 3.10+**: Linguagem base
- **LangChain 0.3+**: Orquestração de agentes e RAG
- **Claude Haiku 4.5**: LLM principal (rápido e econômico)
- **ChromaDB**: Vector database para RAG
- **Sentence Transformers**: Embeddings (all-MiniLM-L6-v2)

### Interface & Tracking
- **Streamlit**: Interface web interativa
- **Pandas**: Exportação de dados
- **LangSmith**: Observabilidade e rastreamento (opcional)

### Processamento
- **Docling**: Conversão de PDFs para Markdown
- **LangChain Document Loaders**: Processamento de documentos
- **Pydantic Settings**: Gerenciamento de configurações

## 📊 Fontes de Dados (9 tipos)

O chatbot processa e indexa 9 fontes diferentes:

1. **Contratos Solidity** (57 arquivos): Pools, Rules, Tokens, Types
2. **Documentação MD** (66 arquivos): Docs técnica gerada do código
3. **README.md**: Visão geral do projeto
4. **CHANGELOG.md**: Histórico de mudanças
5. **Whitepaper RC**: Visão, tokenomics, regras de negócio
6. **Manual Core**: Guia do usuário do app Core RC
7. **Tutorial Wallet**: Como criar carteira MetaMask
8. **Guia Mineração**: Setup de nós e mineração Sintrop
9. **Whitepaper Sintrop**: Arquitetura da blockchain

## 🛠️ Ferramentas RAG (4)

1. **`search_general`**: Busca ampla em todas as fontes
   - Documentação, README, CHANGELOG
   - Manuais de usuário e tutoriais
   - Whitepapers e guias técnicos

2. **`search_contracts`**: Busca específica em contratos Solidity
   - Implementação técnica
   - Funções e variáveis
   - Lógica de contratos

3. **`search_whitepaper`**: Busca no Whitepaper RC
   - Visão e propósito
   - Tokenomics
   - Regras de negócio

4. **`consult_tokenomics_guide`**: Guia completo de tokenomics
   - Fórmulas e tabelas
   - Valores de referência
   - Contexto interpretativo

## 🎓 Documentação Adicional

- **CHANGELOG_UI.md**: Histórico completo das mudanças na interface
- **vector_database/**: Código fonte original (contratos + docs)
- **LangSmith**: Dashboard online (se configurado)



