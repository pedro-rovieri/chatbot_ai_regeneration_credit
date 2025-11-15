# Persistência de Conversas no Streamlit Cloud

## 🚨 Problema

No Streamlit Cloud, o filesystem é **efêmero**:
- Arquivos salvos em `data/conversations/` são perdidos ao reiniciar
- Não é possível acessar conversas de outros usuários
- Histórico não persiste entre deploys

## ✅ Solução 1: LangSmith (JÁ CONFIGURADO!)

O LangSmith **já está salvando** todas as conversas automaticamente!

### Acessar conversas:
1. https://smith.langchain.com/
2. Login
3. Projects → `regeneration-credit-chatbot`
4. Veja: conversas, tokens, custos, traces

### Exportar dados:
- Interface web: exportar CSV/JSON
- API do LangSmith: consultas programáticas

**Plano gratuito:** 5.000 traces/mês

---

## ✅ Solução 2: Supabase (Banco PostgreSQL Gratuito)

Para ter controle total dos dados.

### Passo 1: Criar conta Supabase
1. https://supabase.com/
2. Criar novo projeto
3. Anotar: `SUPABASE_URL` e `SUPABASE_KEY`

### Passo 2: Criar tabela
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  session_id TEXT,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  messages JSONB NOT NULL,
  tokens_history JSONB,
  retriever_audits JSONB,
  analytics JSONB,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_conversation_id ON conversations(conversation_id);
CREATE INDEX idx_user_id ON conversations(user_id);
CREATE INDEX idx_timestamp ON conversations(timestamp);
```

### Passo 3: Adicionar variáveis ao Streamlit Cloud

No campo "Secrets" (Advanced Settings), adicionar:

```toml
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_KEY = "sua-chave-aqui"
```

### Passo 4: Instalar dependências

Adicionar ao `requirements.txt`:
```
supabase==2.0.3
```

### Passo 5: Criar módulo de persistência

Arquivo: `utils/database.py`

```python
import os
from supabase import create_client, Client
from datetime import datetime
import json

class ConversationDB:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.client: Client = create_client(url, key)
    
    def save_conversation(self, conversation_data: dict):
        """Salva conversa no Supabase"""
        try:
            response = self.client.table('conversations').insert(conversation_data).execute()
            return response.data
        except Exception as e:
            print(f"Erro ao salvar conversa: {e}")
            return None
    
    def get_conversations_by_user(self, user_id: str):
        """Busca conversas de um usuário"""
        try:
            response = self.client.table('conversations')\
                .select("*")\
                .eq('user_id', user_id)\
                .order('timestamp', desc=True)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Erro ao buscar conversas: {e}")
            return []
    
    def get_conversation(self, conversation_id: str):
        """Busca conversa específica"""
        try:
            response = self.client.table('conversations')\
                .select("*")\
                .eq('conversation_id', conversation_id)\
                .single()\
                .execute()
            return response.data
        except Exception as e:
            print(f"Erro ao buscar conversa: {e}")
            return None
```

### Passo 6: Modificar `app_completo.py`

```python
# No início do arquivo
from utils.database import ConversationDB

# Inicializar na função save_conversation()
def save_conversation():
    """Salva conversa em Supabase"""
    try:
        # ... código existente para preparar conversation_data ...
        
        # Salvar no Supabase em vez de arquivo local
        db = ConversationDB()
        result = db.save_conversation(conversation_data)
        
        if result:
            logger.info(f"✅ Conversa salva no Supabase: {conversation_id}")
        
        return result
    except Exception as e:
        logger.error(f"❌ Erro ao salvar conversa: {e}")
        return None
```

---

## ✅ Solução 3: Google Sheets (Simples e Gratuito)

Para analytics simples sem banco de dados.

### Instalar:
```bash
pip install gspread oauth2client
```

### Configurar Google Service Account:
1. https://console.cloud.google.com/
2. Criar projeto
3. Ativar Google Sheets API
4. Criar Service Account
5. Baixar JSON de credenciais
6. Compartilhar planilha com email do service account

### Adicionar ao Secrets:
```toml
GOOGLE_SHEETS_CREDENTIALS = '''
{
  "type": "service_account",
  "project_id": "xxx",
  "private_key_id": "xxx",
  ...
}
'''
```

---

## 📊 Comparação

| Solução | Facilidade | Custo | Dados | Analytics |
|---------|-----------|-------|-------|-----------|
| **LangSmith** | ⭐⭐⭐⭐⭐ | Grátis (5k traces) | Traces completos | ⭐⭐⭐⭐⭐ |
| **Supabase** | ⭐⭐⭐ | Grátis (500MB) | Controle total | ⭐⭐⭐ |
| **Google Sheets** | ⭐⭐⭐⭐ | Grátis | Básico | ⭐⭐ |

## 🎯 Recomendação

**Para começar:** Use o **LangSmith** que já está configurado!

**Para produção:** Adicione **Supabase** para ter controle total e backup dos dados.

**Para analytics simples:** Google Sheets pode ser suficiente.

---

## 🔍 Acessar Dados do LangSmith via API

```python
from langsmith import Client

client = Client()

# Listar runs do projeto
runs = client.list_runs(
    project_name="regeneration-credit-chatbot",
    start_time=datetime(2024, 11, 1)
)

# Exportar para CSV
for run in runs:
    print(f"Run ID: {run.id}")
    print(f"Tokens: {run.total_tokens}")
    print(f"Custo: {run.total_cost}")
```

Documentação: https://docs.smith.langchain.com/


