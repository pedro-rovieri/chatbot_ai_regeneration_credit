# Regeneration Credit AI Assistant — API REST

API REST que expõe o chatbot de IA do Regeneration Credit como serviço, permitindo integração com qualquer frontend (Next.js, React Native, etc.) via HTTP e WebSocket.

## Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Inicialização](#inicialização)
- [Endpoints](#endpoints)
  - [Health Check](#1-health-check)
  - [Criar Sessão](#2-criar-sessão)
  - [Enviar Mensagem (Chat)](#3-enviar-mensagem-chat)
  - [Info da Sessão](#4-info-da-sessão)
  - [Histórico da Sessão](#5-histórico-da-sessão)
  - [Encerrar Sessão](#6-encerrar-sessão)
  - [WebSocket (Chat em Tempo Real)](#7-websocket-chat-em-tempo-real)
- [Fluxo de Integração com o Frontend](#fluxo-de-integração-com-o-frontend)
  - [Exemplo Completo (TypeScript / Next.js)](#exemplo-completo-typescript--nextjs)
  - [Exemplo com WebSocket](#exemplo-com-websocket)
- [Códigos de Erro](#códigos-de-erro)
- [CORS](#cors)
- [Configuração](#configuração)
- [Estrutura de Arquivos](#estrutura-de-arquivos)

---

## Visão Geral

```
Frontend (Next.js)          API (FastAPI/Uvicorn)          Agente IA
┌──────────────┐           ┌───────────────────┐          ┌────────────────┐
│  Widget de   │  HTTP/WS  │  POST /chat       │  Python  │ Claude Haiku   │
│  Chat no     │ ────────► │  POST /sessions   │ ───────► │ + RAG ChromaDB │
│  Website     │ ◄──────── │  GET  /health     │ ◄─────── │ + 120+ docs    │
└──────────────┘   JSON    └───────────────────┘          └────────────────┘
```

**Stack da API:**
- **FastAPI** — framework web async de alta performance
- **Uvicorn** — servidor ASGI
- **WebSocket** — suporte a chat em tempo real (opcional)
- **RegenerationCreditAgent** — agente IA com RAG (LangChain + Claude Haiku + ChromaDB)

---

## Arquitetura

A API gerencia **sessões de chat** independentes. Cada sessão:

- Possui seu próprio agente com **memória conversacional isolada**
- Compartilha o **VectorStore ChromaDB** (base de conhecimento)
- Expira automaticamente após **60 minutos** de inatividade
- É identificada por um **UUID** (`session_id`)

```
Sessão 1 ──► Agente 1 (memória própria) ──┐
Sessão 2 ──► Agente 2 (memória própria) ──┤──► VectorStore ChromaDB (compartilhado)
Sessão N ──► Agente N (memória própria) ──┘    (120+ documentos indexados)
```

---

## Pré-requisitos

- **Python 3.10+** (testado com 3.13)
- **Chave de API da Anthropic** (`ANTHROPIC_API_KEY` no `.env`)
- **VectorStore processado** (executar `python scripts/process_documents.py` na primeira vez)

---

## Instalação

```bash
# 1. Clonar o repositório (se ainda não tiver)
git clone <repo-url>
cd chatbot_ai_regeneration_credit

# 2. Criar e ativar ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1     # Windows PowerShell
# source .venv/bin/activate    # Linux/Mac

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
# Criar arquivo .env na raiz com:
#   ANTHROPIC_API_KEY=sk-ant-...

# 5. Processar documentos (apenas na primeira vez)
python scripts/process_documents.py
```

---

## Inicialização

```bash
# Opção 1: Via script (recomendado)
python run_api.py
python run_api.py --port 8000 --reload    # dev mode com auto-reload

# Opção 2: Via uvicorn diretamente
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Opção 3: Produção (sem reload, logs otimizados)
python run_api.py --port 8000 --log-level warning
```

Após iniciar, a API estará disponível em:
- **API**: `http://localhost:8000/api/v1/`
- **Swagger UI** (documentação interativa): `http://localhost:8000/api/v1/docs`
- **ReDoc** (documentação alternativa): `http://localhost:8000/api/v1/redoc`

---

## Endpoints

Base URL: `http://localhost:8000/api/v1`

### 1. Health Check

Verifica se o serviço está funcionando.

```
GET /api/v1/health
```

**Resposta** `200 OK`:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "active_sessions": 3,
  "vector_store_loaded": true
}
```

---

### 2. Criar Sessão

Cria uma nova sessão de chat. **Deve ser chamado antes de enviar mensagens.**

```
POST /api/v1/sessions
```

**Resposta** `201 Created`:
```json
{
  "session_id": "4faff635-607d-45c8-a23b-c1f23f6f05b0",
  "created_at": "2026-03-25T17:07:24.087292"
}
```

> Guarde o `session_id` — ele é necessário para todos os endpoints de chat e sessão.

---

### 3. Enviar Mensagem (Chat)

Envia uma mensagem ao chatbot e recebe a resposta completa.

```
POST /api/v1/chat
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "4faff635-607d-45c8-a23b-c1f23f6f05b0",
  "message": "O que é o Regeneration Credit?"
}
```

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `session_id` | string | Sim | UUID da sessão ativa |
| `message` | string | Sim | Mensagem do usuário (1–5000 caracteres) |

**Resposta** `200 OK`:
```json
{
  "success": true,
  "session_id": "4faff635-607d-45c8-a23b-c1f23f6f05b0",
  "response": "O Regeneration Credit é um sistema de financiamento peer-to-peer (P2P) criado para resolver um problema fundamental...",
  "timestamp": "2026-03-25T17:07:30.123456",
  "elapsed_seconds": 6.60,
  "tokens": {
    "total": 8251,
    "custo": 0.0104,
    "custo_formatado": "$0.0104",
    "tokens_formatado": "8.2K",
    "por_componente": {}
  },
  "stats": {
    "total_chamadas_llm": 2,
    "chamadas_neste_turno": 2,
    "total_retriever_calls": 1,
    "iterations": 2,
    "tool_calls": 1
  }
}
```

| Campo | Descrição |
|-------|-----------|
| `success` | `true` se a resposta foi gerada com sucesso |
| `response` | Texto da resposta do chatbot (Markdown) |
| `elapsed_seconds` | Tempo total de processamento |
| `tokens.total` | Total de tokens consumidos |
| `tokens.custo_formatado` | Custo estimado da chamada |
| `stats.iterations` | Quantas vezes o agente raciocionou (loop ReAct) |
| `stats.tool_calls` | Quantas ferramentas RAG foram usadas |

---

### 4. Info da Sessão

Retorna metadados de uma sessão ativa.

```
GET /api/v1/sessions/{session_id}
```

**Resposta** `200 OK`:
```json
{
  "session_id": "4faff635-607d-45c8-a23b-c1f23f6f05b0",
  "created_at": "2026-03-25T17:07:24.087292",
  "last_active": "2026-03-25T17:07:30.123456",
  "message_count": 2
}
```

---

### 5. Histórico da Sessão

Retorna todas as mensagens trocadas na sessão.

```
GET /api/v1/sessions/{session_id}/history
```

**Resposta** `200 OK`:
```json
{
  "session_id": "4faff635-607d-45c8-a23b-c1f23f6f05b0",
  "messages": [
    { "role": "user", "content": "O que é o Regeneration Credit?" },
    { "role": "assistant", "content": "O Regeneration Credit é um sistema..." }
  ]
}
```

---

### 6. Encerrar Sessão

Remove a sessão e libera recursos do servidor.

```
DELETE /api/v1/sessions/{session_id}
```

**Resposta** `200 OK`:
```json
{
  "detail": "Sessão encerrada com sucesso"
}
```

---

### 7. WebSocket (Chat em Tempo Real)

Alternativa ao endpoint REST para uma experiência de chat mais fluida.

```
WS ws://localhost:8000/api/v1/ws/chat/{session_id}
```

**Fluxo:**

1. Conectar ao WebSocket com um `session_id` válido
2. Enviar mensagens como **texto puro** (string)
3. Receber respostas como **JSON** (mesmo formato do `ChatResponse`)

**Exemplo JavaScript:**
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/chat/${sessionId}`);

ws.onopen = () => {
  ws.send("O que é o Regeneration Credit?");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.response);
};

ws.onclose = (event) => {
  console.log("Conexão encerrada:", event.reason);
};
```

---

## Fluxo de Integração com o Frontend

O fluxo típico de integração segue estes passos:

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Usuário abre o widget de chat                               │
│     └──► Frontend chama POST /sessions                          │
│          └──► Recebe session_id                                 │
│                                                                 │
│  2. Usuário digita mensagem e envia                             │
│     └──► Frontend chama POST /chat com { session_id, message }  │
│          └──► Exibe "carregando..." enquanto aguarda            │
│          └──► Recebe resposta JSON                              │
│          └──► Renderiza response (Markdown) no chat             │
│                                                                 │
│  3. Repetir passo 2 para cada mensagem                          │
│     (a memória conversacional é mantida no servidor)            │
│                                                                 │
│  4. Usuário fecha o chat ou sai da página                       │
│     └──► Frontend chama DELETE /sessions/{session_id}           │
│          (opcional — sessões expiram sozinhas em 60min)          │
└─────────────────────────────────────────────────────────────────┘
```

### Exemplo Completo (TypeScript / Next.js)

O frontend `regeneration-credit-website` já utiliza **axios** e **React 19**. Abaixo, um exemplo de integração completo:

**`lib/chatbot-api.ts`** — Módulo de comunicação com a API:

```typescript
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_CHATBOT_API_URL || "http://localhost:8000";
const API_V1 = `${API_BASE}/api/v1`;

// Tipos
export interface ChatResponse {
  success: boolean;
  session_id: string;
  response: string;
  timestamp: string;
  elapsed_seconds: number;
  tokens?: {
    total: number;
    custo: number;
    custo_formatado: string;
    tokens_formatado: string;
  };
  stats?: {
    total_chamadas_llm: number;
    iterations: number;
    tool_calls: number;
  };
}

export interface SessionResponse {
  session_id: string;
  created_at: string;
}

export interface HistoryResponse {
  session_id: string;
  messages: Array<{ role: string; content: string }>;
}

// Funções da API

export async function createSession(): Promise<SessionResponse> {
  const { data } = await axios.post<SessionResponse>(`${API_V1}/sessions`);
  return data;
}

export async function sendMessage(
  sessionId: string,
  message: string
): Promise<ChatResponse> {
  const { data } = await axios.post<ChatResponse>(`${API_V1}/chat`, {
    session_id: sessionId,
    message,
  });
  return data;
}

export async function getHistory(sessionId: string): Promise<HistoryResponse> {
  const { data } = await axios.get<HistoryResponse>(
    `${API_V1}/sessions/${sessionId}/history`
  );
  return data;
}

export async function deleteSession(sessionId: string): Promise<void> {
  await axios.delete(`${API_V1}/sessions/${sessionId}`);
}

export async function healthCheck(): Promise<boolean> {
  try {
    const { data } = await axios.get(`${API_V1}/health`);
    return data.status === "healthy";
  } catch {
    return false;
  }
}
```

**`components/ChatWidget.tsx`** — Componente React de exemplo:

```tsx
"use client";

import { useState, useEffect, useRef } from "react";
import { createSession, sendMessage, deleteSession } from "@/lib/chatbot-api";
import { marked } from "marked";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Cria sessão ao abrir o chat
  useEffect(() => {
    if (isOpen && !sessionId) {
      createSession().then((session) => {
        setSessionId(session.session_id);
      });
    }
  }, [isOpen, sessionId]);

  // Scroll automático
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Limpa sessão ao fechar
  useEffect(() => {
    return () => {
      if (sessionId) {
        deleteSession(sessionId).catch(() => {});
      }
    };
  }, [sessionId]);

  const handleSend = async () => {
    if (!input.trim() || !sessionId || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await sendMessage(sessionId, userMessage);

      if (response.success) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: response.response },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Desculpe, não consegui processar sua pergunta. Tente novamente.",
          },
        ]);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Erro de conexão com o assistente. Tente novamente.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-green-600 text-white rounded-full p-4 shadow-lg hover:bg-green-700 transition"
      >
        Assistente IA
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 h-[500px] bg-white rounded-xl shadow-2xl flex flex-col border">
      {/* Header */}
      <div className="bg-green-600 text-white p-4 rounded-t-xl flex justify-between items-center">
        <span className="font-semibold">Assistente Regeneration Credit</span>
        <button onClick={() => setIsOpen(false)} className="text-xl">
          &times;
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg text-sm ${
              msg.role === "user"
                ? "bg-green-50 ml-8 text-right"
                : "bg-gray-100 mr-8"
            }`}
          >
            {msg.role === "assistant" ? (
              <div
                className="prose prose-sm"
                dangerouslySetInnerHTML={{ __html: marked(msg.content) }}
              />
            ) : (
              msg.content
            )}
          </div>
        ))}
        {isLoading && (
          <div className="bg-gray-100 mr-8 p-3 rounded-lg text-sm text-gray-500">
            Pensando...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Digite sua pergunta..."
          className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          disabled={isLoading}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className="bg-green-600 text-white px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 transition"
        >
          Enviar
        </button>
      </div>
    </div>
  );
}
```

**`.env.local`** no projeto Next.js:

```env
NEXT_PUBLIC_CHATBOT_API_URL=http://localhost:8000
```

### Exemplo com WebSocket

Para uma UX sem recarregamento por mensagem:

```typescript
// lib/chatbot-ws.ts
export function createChatWebSocket(
  sessionId: string,
  onMessage: (data: ChatResponse) => void,
  onError?: (error: Event) => void
): WebSocket {
  const wsUrl = process.env.NEXT_PUBLIC_CHATBOT_WS_URL || "ws://localhost:8000";
  const ws = new WebSocket(`${wsUrl}/api/v1/ws/chat/${sessionId}`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  ws.onerror = (error) => {
    onError?.(error);
  };

  return ws;
}
```

---

## Códigos de Erro

| Status | Descrição | Quando ocorre |
|--------|-----------|---------------|
| `200` | Sucesso | Requisição processada com sucesso |
| `201` | Criado | Nova sessão criada |
| `404` | Não encontrado | `session_id` inválido ou sessão expirada |
| `422` | Validação | Campos obrigatórios ausentes ou inválidos |
| `500` | Erro interno | Falha no agente IA ou no servidor |

Todas as respostas de erro seguem o formato:
```json
{
  "detail": "Descrição do erro"
}
```

---

## CORS

A API aceita requisições dos seguintes domínios:

| Origem | Ambiente |
|--------|----------|
| `https://regenerationcredit.org` | Produção |
| `https://www.regenerationcredit.org` | Produção |
| `http://localhost:3000` | Desenvolvimento (Next.js) |
| `http://localhost:3001` | Desenvolvimento (alternativo) |
| `http://127.0.0.1:3000` | Desenvolvimento (alternativo) |

Para adicionar novos domínios, edite `ALLOWED_ORIGINS` em `api/main.py`.

---

## Configuração

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--host` | `0.0.0.0` | Host do servidor |
| `--port` | `8000` | Porta do servidor |
| `--reload` | `false` | Auto-reload em desenvolvimento |
| `--workers` | `1` | Workers do uvicorn (manter 1 — agentes em memória) |
| `--log-level` | `info` | Nível de log (`debug`, `info`, `warning`, `error`) |

**Variáveis de ambiente** (arquivo `.env` na raiz):

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `ANTHROPIC_API_KEY` | Sim | Chave da API Anthropic |
| `LANGCHAIN_API_KEY` | Não | Chave do LangSmith (observabilidade) |
| `LANGCHAIN_PROJECT` | Não | Nome do projeto no LangSmith |

**Limites do AgentManager** (em `api/main.py`):

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `max_sessions` | `100` | Máximo de sessões simultâneas |
| `ttl_minutes` | `60` | Tempo de expiração de sessões inativas |

---

## Estrutura de Arquivos

```
api/
├── __init__.py
├── main.py                     # App FastAPI, CORS, lifespan, routers
├── models/
│   ├── __init__.py
│   └── schemas.py              # Schemas Pydantic (request/response)
├── routers/
│   ├── __init__.py
│   ├── health.py               # GET  /health
│   ├── sessions.py             # POST/GET/DELETE /sessions
│   └── chat.py                 # POST /chat  +  WS /ws/chat
├── services/
│   ├── __init__.py
│   └── agent_manager.py        # Pool de sessões, TTL, thread-safety
└── middleware/
    └── __init__.py              # (reservado para rate limiting futuro)

run_api.py                       # Script de inicialização com argparse
```

---

## Notas Técnicas

- **Concorrência**: O agente é síncrono (chamadas bloqueantes ao LLM). A API usa `asyncio.to_thread()` para delegar cada chamada a uma thread separada, evitando bloquear o event loop do FastAPI.
- **Workers**: Manter `workers=1` porque os agentes vivem em memória. Múltiplos workers criariam pools de sessões separados e incompatíveis.
- **Sessões**: Cada sessão instancia um `RegenerationCreditAgent` completo com memória própria. O VectorStore ChromaDB é compartilhado em modo leitura.
- **TTL**: Sessões inativas por mais de 60 minutos são removidas automaticamente na próxima operação do AgentManager. Não há um timer periódico — a limpeza ocorre de forma lazy.
