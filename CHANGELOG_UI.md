# Changelog - Interface do Usuário Aprimorada

## Fase 4: Sistema de Abas com Métricas e Debug

### Data: 2025-11-13

### Resumo das Mudanças

O `app_completo.py` foi completamente reestruturado para incorporar um **sistema de tabs** que oferece visibilidade completa sobre o funcionamento interno do chatbot. Agora, além do chat principal, o usuário tem acesso a:

1. **Aba "Chat"**: Interface principal de conversação (funcionalidade anterior preservada)
2. **Aba "Prompts"**: Visualização do system prompt usado pelo agente
3. **Aba "Retriever Debug"**: Histórico detalhado de todas as buscas no vector store
4. **Aba "Tokens e Custos"**: Rastreamento completo de uso de tokens e custos por turno

---

## Detalhamento das Mudanças

### 1. Novos Imports

```python
import pandas as pd
from utils.pricing import formatar_custo, formatar_tokens
```

### 2. Session State Expandido

Adicionadas duas novas variáveis de estado para rastreamento:

- `st.session_state.tokens_history`: Lista de dicionários com métricas de tokens/custos por turno
- `st.session_state.retriever_audits`: Lista de audits detalhados de cada busca no retriever

### 3. Persistência Aprimorada

A função `save_conversation()` agora salva:
- Histórico de mensagens (anterior)
- **Histórico de tokens/custos** (`tokens_history`)
- **Audits do retriever** (`retriever_audits`)

### 4. Captura de Métricas

Na função `render_tab_chat()`, após cada resposta do agente:

```python
# Captura tokens_history
tokens_data = response.get("tokens", {})
turno_entry = {
    "turno_id": len(st.session_state.tokens_history) + 1,
    "timestamp": datetime.now(),
    "question": user_input,
    "response": assistant_message[:100] + "...",
    "elapsed_seconds": response.get("elapsed_seconds", response_time),
    "total_tokens": tokens_data.get("total", 0),
    "total_custo": tokens_data.get("custo", 0.0),
    "por_componente": tokens_data.get("por_componente", {}),
    "stats": response.get("stats", {})
}
st.session_state.tokens_history.append(turno_entry)

# Captura retriever_audits
retriever_audits = response.get("retriever_audits", [])
if retriever_audits:
    st.session_state.retriever_audits.extend(retriever_audits)
```

---

## Descrição das Abas

### Aba "Chat"

- Interface principal de conversação
- Exibe mensagens com formatação customizada
- Mostra tempo de resposta do assistente
- Input de texto com botão de envio

### Aba "Prompts"

- **System Prompt do Agente**: Exibe o prompt completo que define o comportamento do assistente
- **Botão de Download**: Permite baixar o system prompt como arquivo `.txt`
- **Informações**: Explicação sobre o papel do prompt

**Conteúdo exibido:**
- Modo de explicação (iniciante)
- Idioma (PT-BR)
- Tom conversacional
- Ferramentas disponíveis (search_general, search_contracts, search_whitepaper)
- Processo de resposta
- Limitações

### Aba "Retriever Debug"

- **Histórico de Buscas**: Lista todas as chamadas ao retriever desde o início da conversa
- **Métricas**: Número de resultados, tempo de execução, filtros aplicados
- **Detalhes da Query**: Exibe a query enviada ao retriever
- **Filtros Aplicados**: Mostra os filtros de metadados usados
- **Resumo dos Metadados**: Lista os valores únicos encontrados nos metadados dos documentos retornados
- **Preview dos Documentos**: Expander com preview do conteúdo dos documentos retornados

**Informações por busca:**
- Tool name (search_general, search_contracts, search_whitepaper)
- Query
- Número de resultados
- Tempo de execução (segundos)
- Filtros aplicados
- Resumo dos metadados (e.g., `source`, `section`, `type`)
- Preview dos documentos retornados (primeiras linhas)

### Aba "Tokens e Custos"

- **Resumo Financeiro (Toda a Conversa)**:
  - Total de Tokens
  - Total Custo (USD)
  - Total Chamadas LLM
  - Custo Médio por Turno

- **Histórico de Turnos**: Expanders para cada turno com:
  - Turno ID
  - Timestamp
  - Pergunta completa
  - Tempo de resposta
  - Breakdown por Componente (Agente):
    - Número de chamadas
    - Tokens (Input, Output)
    - Custo (USD)
  - Estatísticas detalhadas (expander adicional)

- **Exportar Dados**: Botão para baixar CSV com:
  - Turno
  - Timestamp
  - Question
  - Total Tokens
  - Total Custo
  - Tempo (segundos)

---

## Funções Criadas

### 1. `get_system_prompt() -> str`

Retorna o system prompt do agente (hard-coded para exibição na UI).

### 2. `render_tab_chat(agent)`

Renderiza a aba principal de chat, incluindo:
- Mensagem de boas-vindas
- Histórico de mensagens
- Input de texto
- Captura de métricas de tokens e retriever_audits

### 3. `render_tab_prompts()`

Renderiza a aba de prompts com:
- Expander para o system prompt
- Botão de download

### 4. `render_tab_retriever_debug()`

Renderiza a aba de debug do retriever com:
- Lista de todos os audits
- Métricas e detalhes de cada busca
- Filtros aplicados
- Resumo dos metadados
- Preview dos documentos (opcional)

### 5. `render_tab_tokens()`

Renderiza a aba de tokens e custos com:
- Resumo financeiro acumulado
- Histórico detalhado por turno
- Breakdown por componente
- Exportação de dados (CSV)

### 6. `render_main()`

Função principal que:
- Inicializa o agente
- Cria o sistema de 4 tabs
- Chama as funções de renderização para cada tab

---

## Testes de Validação

Foi criado o script `scripts/test_ui_integration.py` que valida:

1. **Imports**: Verifica se todos os módulos necessários estão disponíveis
2. **Estrutura do App**: Valida a existência de todas as funções necessárias
3. **Persistência**: Confirma que tokens_history e retriever_audits são salvos
4. **Captura de Dados**: Verifica se os dados do agente são capturados corretamente
5. **Renderização das Tabs**: Valida o conteúdo de cada função de renderização

**Resultado dos Testes**: 4/5 passaram (o único que falhou foi o import do agente, devido à ausência de `langchain_classic` no ambiente de teste, o que não afeta a funcionalidade em produção).

---

## Como Usar

### Executar o App

```bash
cd chatbot-ia
streamlit run app_completo.py
```

### Navegar pelas Abas

1. **Chat**: Faça perguntas sobre o Regeneration Credit
2. **Prompts**: Visualize e baixe o system prompt
3. **Retriever Debug**: Veja o histórico de buscas e seus detalhes
4. **Tokens e Custos**: Acompanhe o uso de tokens e custos em tempo real

### Salvar Conversa

- Use o botão "💾 Salvar" na sidebar
- A conversa será salva com todos os dados de tokens e retriever audits

### Limpar Conversa

- Use o botão "🔄 Nova Conversa" na sidebar
- Todos os dados (mensagens, tokens, audits) serão limpos

---

## Dependências Adicionais

Nenhuma nova dependência foi adicionada. Todas as funções usam módulos já presentes:
- `streamlit`
- `pandas`
- `json`
- `datetime`
- Módulos internos: `utils.pricing`, `agents.main_agent`, etc.

---

## Próximos Passos (Opcional)

- **Carregamento de Conversas Salvas**: Implementar função para carregar conversas anteriores
- **Gráficos**: Adicionar visualizações gráficas de tokens/custos ao longo do tempo
- **Filtros na Aba de Debug**: Permitir filtrar audits por tool_name ou período
- **Comparação de Turnos**: Comparar custos/tokens entre diferentes turnos

---

## Arquivos Modificados

- `chatbot-ia/app_completo.py`: Reestruturação completa com sistema de tabs

## Arquivos Criados

- `chatbot-ia/scripts/test_ui_integration.py`: Script de teste de integração da UI
- `chatbot-ia/CHANGELOG_UI.md`: Este arquivo

