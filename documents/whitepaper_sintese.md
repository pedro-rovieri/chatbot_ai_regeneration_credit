# Síntese: Crédito de Regeneração - Guia de Tokenomics

> **Fonte:** Whitepaper "Crédito de Regeneração: Um Sistema Peer-to-Peer de Regeneração da Natureza"  
> **Data:** 3 de outubro de 2025  
> **Uso:** Contexto de tokenomics para cálculos e simulações

---

## 1. VISÃO GERAL DO SISTEMA

O **Crédito de Regeneração (RC)** é um sistema descentralizado (blockchain) que incentiva financeiramente pessoas e comunidades a regenerar ecossistemas terrestres degradados.

**Problema abordado:** Atualmente é mais lucrativo degradar a natureza do que regenerá-la. O RC inverte essa lógica.

**Como funciona:**
- Regeneradores registram áreas (2.500 m² a 1.000.000 m²) e as regeneram
- Inspetores visitam e auditam as áreas, contando árvores e espécies
- O sistema calcula um "Score de Regeneração" baseado nos dados
- Tokens RC são distribuídos proporcionalmente aos scores e níveis acumulados
- Apoiadores compram tokens e os queimam para compensar impacto ambiental

---

## 2. TOKENOMICS ESSENCIAL

### 2.1 Oferta Total Fixa
**1.310.000.000 RC** (1,31 bilhão de tokens) - nunca mais serão criados

### 2.2 Distribuição por Pools

| Pool | Tokens | Percentual |
|------|--------|------------|
| **Regenerador** | 750.000.000 | 57,25% |
| **Inspetor** | 230.000.000 | 17,56% |
| **Ativista** | 40.000.000 | 3,05% |
| **Contribuidor** | 40.000.000 | 3,05% |
| **Pesquisador** | 40.000.000 | 3,05% |
| **Desenvolvedor** | 40.000.000 | 3,05% |

### 2.3 Cronograma de Emissão: Eras e Epochs

**ERA:**
- Duração: ~173 dias (~5,8 meses)
- Definição: 1.152.000 blocos × 13 segundos por bloco
- Tokens são distribuídos ao final de cada Era

**EPOCH:**
- Duração: 12 Eras (~6 anos)
- A cada novo Epoch, emissão de tokens cai pela metade (halving)

**Exemplo (Pool Regeneradores):**
- Epoch 1: 31.250.000 RC por Era
- Epoch 2: 15.625.000 RC por Era (metade)
- Epoch 3: 7.812.500 RC por Era (metade novamente)

**Fórmula:** `tokens_por_era = (total_pool ÷ 2^epoch) ÷ 12`

---

## 3. SCORE DE REGENERAÇÃO

O Score mede o impacto ecológico de uma área regenerada.

### 3.1 Fórmula
```
Score Total = Pontos de Árvores + Pontos de Biodiversidade
(Máximo: 64 pontos = 32 + 32)
```

### 3.2 Tabela de Pontuação: Árvores

| Quantidade de Árvores | Pontos |
|-----------------------|--------|
| ≥ 50.000 | 32 |
| 25.000 - 49.999 | 16 |
| 12.500 - 24.999 | 8 |
| 6.250 - 12.499 | 4 |
| 3.125 - 6.249 | 2 |
| 20 - 3.124 | 1 |
| < 20 | 0 |

### 3.3 Tabela de Pontuação: Biodiversidade (Espécies)

| Número de Espécies | Pontos |
|--------------------|--------|
| ≥ 160 | 32 |
| 80 - 159 | 16 |
| 40 - 79 | 8 |
| 20 - 39 | 4 |
| 10 - 19 | 2 |
| 5 - 9 | 1 |
| < 5 | 0 |

**Exemplo prático:**
- Área com 20.000 árvores = 16 pontos
- Área com 50 espécies diferentes = 8 pontos
- **Score Total = 24 pontos**

---

## 4. TIPOS DE USUÁRIO E NÍVEIS

Cada tipo de usuário acumula "níveis" de formas diferentes. Níveis determinam quanto você recebe.

### 4.1 Regenerador
- **Como ganha níveis:** Score × número de inspeções
- **Mínimo:** 3 inspeções (validação)
- **Máximo:** 6 inspeções (vitalício)
- **Exemplo:** Score 24 × 4 inspeções = 96 níveis

**Regra especial:** Só entra no pool de distribuição após 3ª inspeção.

### 4.2 Inspetor
- **Como ganha níveis:** 1 nível por inspeção válida realizada
- **Exemplo:** 10 inspeções = 10 níveis

### 4.3 Ativista
- **Como ganha níveis:** 1 nível quando convidado completa 3 inspeções
- **Exemplo:** 5 convidados validados = 5 níveis

### 4.4 Contribuidor / Pesquisador / Desenvolvedor
- **Como ganha níveis:** 1 nível por relatório/pesquisa/desenvolvimento publicado
- **Exemplo:** 8 contribuições = 8 níveis

---

## 5. FÓRMULA DE DISTRIBUIÇÃO (COMO OS TOKENS SÃO CALCULADOS)

**Fórmula central do sistema:**

```
Seus tokens = (Seus níveis ÷ Total de níveis na Era) × Tokens disponíveis na Era
```

**Exemplo numérico:**
- Você (Regenerador): 60 níveis
- Todos os Regeneradores juntos nesta Era: 50.000 níveis
- Tokens disponíveis para Regeneradores nesta Era: 31.250.000 RC

Cálculo:
```
Seus tokens = (60 ÷ 50.000) × 31.250.000
            = 0,0012 × 31.250.000
            = 37.500 RC
```

**Implicação importante:** Quanto mais participantes (maior total_níveis), menor sua fatia individual (diluição).

---

## 6. CONCEITOS-CHAVE PARA INTERPRETAÇÃO

### 6.1 Diluição
À medida que mais pessoas entram no sistema, o "total de níveis" aumenta, reduzindo a fatia individual de cada participante.

**Exemplo:**
- Cenário A: 100 participantes, média 50 níveis cada = 5.000 níveis totais
- Cenário B: 200 participantes, média 50 níveis cada = 10.000 níveis totais
- Seu ganho em B será metade do ganho em A (mesmos 50 níveis)

### 6.2 Halving
A cada 12 Eras (~6 anos), tokens emitidos caem pela metade. Isso reduz a oferta ao longo do tempo, mas também reduz ganhos se você entrar mais tarde.

**Primeiros participantes têm vantagem (exemplo: Pool Regenerador):**
- Epoch 1: 31.250.000 RC/era disponíveis
- Epoch 2: 15.625.000 RC/era disponíveis

**Valores por pool no Epoch 1 (tokens/era):**

| Pool | Total Pool | Epoch 1/Era | Cálculo |
|------|-----------|------------|---------|
| Regenerador | 750M RC | 31.250.000 RC | 750M ÷ 2 ÷ 12 |
| Inspetor | 230M RC | 9.583.333 RC | 230M ÷ 2 ÷ 12 |
| Ativista | 40M RC | 1.666.667 RC | 40M ÷ 2 ÷ 12 |
| Contribuidor | 40M RC | 1.666.667 RC | 40M ÷ 2 ÷ 12 |
| Pesquisador | 40M RC | 1.666.667 RC | 40M ÷ 2 ÷ 12 |
| Desenvolvedor | 40M RC | 1.666.667 RC | 40M ÷ 2 ÷ 12 |

**Fórmula geral:** `(total_pool ÷ 2^epoch) ÷ 12`

### 6.3 Cenários (Otimista/Pessimista)
Como o "total de níveis na Era" é imprevisível, simulações usam margens de variação:
- **Pessimista:** +30% participantes (sua fatia cai ~30%)
- **Otimista:** -30% participantes (sua fatia sobe ~30%)

### 6.4 Tempo Real
Eras duram ~173 dias. Logo:
- 1 Era = ~5,8 meses
- 3 Eras = ~1,4 anos
- 12 Eras (1 Epoch) = ~6 anos

---

## 7. VALORES DE REFERÊNCIA (ESTIMATIVAS)

**IMPORTANTE:** Estes valores são **estimativas** para simulação, não regras do protocolo.

### 7.1 Níveis Totais por Era (avg_era_levels)

**Fase Inicial (primeiros anos):**
- Regenerador: 20.000 - 50.000 níveis
- Inspetor: 5.000 - 15.000 níveis
- Outros pools: 2.000 - 8.000 níveis

**Rede Madura (após alguns anos):**
- Regenerador: 100.000 - 500.000 níveis
- Inspetor: 20.000 - 50.000 níveis
- Outros pools: 10.000 - 30.000 níveis

**Por que varia:** Depende de:
- Quantos usuários estão ativos
- Quantas inspeções/contribuições foram feitas na Era
- Crescimento orgânico vs. adoção em massa

### 7.2 Score Típico de Regenerador

**Contexto de interpretação:**
- Score 0-10: Início de regeneração, baixa densidade
- Score 10-20: Regeneração em progresso
- Score 20-30: Regeneração avançada
- Score 30-40: Floresta densa e biodiversa
- Score 40-64: Ecossistema extremamente rico (raro)

---

## 8. LIMITAÇÕES E REGRAS IMPORTANTES

### 8.1 Regenerador
- Área mínima: 2.500 m²
- Área máxima: 1.000.000 m² (100 hectares)
- Máximo de regeneradores ativos simultaneamente: 500.000
- Inspeções: mínimo 3, máximo 6 (vitalício)

### 8.2 Inspetor
- Não pode inspecionar o mesmo Regenerador duas vezes
- Precisa esperar 6.000 blocos entre inspeções consecutivas

### 8.3 Apoiador (Supporter)
- Não ganha tokens, apenas compra e queima
- Queimando tokens = compensando impacto ambiental
- Quem convida apoiador ganha 5% de comissão nos offsets

---

## 9. COMO USAR ESTA INFORMAÇÃO EM CÁLCULOS

### 9.1 Quando Usuário Pedir Cálculo

**Quando faltar parâmetro do usuário:**
1. **PERGUNTE ao usuário** pelo parâmetro faltante
2. Explique o que é o parâmetro e seu impacto no resultado
3. Ofereça valores de referência sugeridos (seção 7.1) como **opções**
4. **AGUARDE confirmação** do usuário antes de calcular
5. Deixe claro que usar sugestão é estimativa, não valor real

**REGRA:** NUNCA calcule com parâmetros assumidos sem perguntar primeiro.

**Exemplo de interação:**
```
Usuário: "Quanto vou ganhar com 15k árvores e 60 espécies?"

Agente: "Para calcular seus ganhos como Regenerador, primeiro vejo que você terá:
- 15.000 árvores = 8 pontos
- 60 espécies = 8 pontos
- Score total = 16 pontos

Para fazer o cálculo, preciso de mais informações:

1. Quantas inspeções você planeja? (mínimo 3, máximo 6)
2. Quantas eras você quer simular?
3. Total de níveis de regeneradores na era (avg_era_levels)?

Para o parâmetro 3, esse é o valor mais incerto. Valores de referência:
- Rede inicial: 20.000 - 50.000 níveis
- Rede média: ~50.000 níveis

Você tem essas informações ou prefere que eu use sugestões?"
```

### 9.2 Ao Interpretar Resultados

**Sempre contextualize:**
- Explique que valores dependem de participação da rede
- Mostre cenários otimista/pessimista (±30%)
- Converta tempo (eras) para meses/anos
- Compare com outros tipos de usuário se relevante

**Exemplo:**
```
"Seus ganhos estimados: 45.000 RC em 3 eras (~1,4 anos)

Isso é baseado em:
- avg_era_levels = 50.000 (rede média)
- Cenário otimista: 58.500 RC (menos participantes)
- Cenário pessimista: 31.500 RC (mais participantes)

Interpretação: Como você tem score 16 (médio-baixo), seus ganhos
são proporcionalmente menores. Aumentar árvores ou biodiversidade
para atingir score 24-32 dobraria/triplicaria seus tokens."
```

---

## 10. GLOSSÁRIO RÁPIDO

- **RC:** Crédito de Regeneração (token)
- **Era:** ~173 dias, período de distribuição
- **Epoch:** 12 eras (~6 anos)
- **Halving:** Redução de 50% na emissão a cada Epoch
- **Score:** Pontuação de regeneração (0-64)
- **Níveis:** Acúmulo de score/contribuições que define sua fatia
- **Pool:** Reserva de tokens para cada tipo de usuário
- **avg_era_levels:** Total de níveis de todos usuários em uma Era
- **Diluição:** Redução de ganhos individuais com mais participantes
- **Offset:** Queimar tokens para compensar impacto ambiental

---

## 11. DETALHAMENTO TÉCNICO POR CONTRATO (VISÃO PARA CÁLCULOS)

Esta seção resume, em linguagem natural, o que os contratos Solidity implementam em termos de **regras, limites e fórmulas** relevantes para cálculos de tokenomics.

### 11.1 `RegenerationCredit.sol` (Token RC)

- **Função:** Contrato ERC‑20 principal do token RC.
- **Papel nos cálculos:**
  - Mantém o **total supply** e registra:
    - `totalLocked_`: quanto está bloqueado em pools (ainda não distribuído aos usuários).
    - `totalCertified_`: quanto já foi queimado como compensação ambiental (offset).
  - Oferece:
    - `addContractPool(address, numTokens)`: envia um lote de tokens para um pool específico e marca como bloqueado.
    - `decreaseLocked(numTokens)`: chamado pelos pools quando liberam tokens para usuários, reduzindo `totalLocked_`.
    - `burnTokens` / `burnFrom`: usados por apoiadores (Supporters) para queimar tokens e gerar certificado (`certificate[address]`).

**Implicação para simulações:**
- Tokens destinados a pools são **pré-alocados** neste contrato e vão sendo liberados ao longo das eras.
- Queimas (offsets) **reduzem oferta circulante**, mas não alteram o total designado aos pools.

### 11.2 `RegenerationIndexRules.sol` (Score de Regeneração)

- **Função:** Converte dados de inspeção (árvores e biodiversidade) em **score 0–64**.
- **Principais pontos:**
  - Duas categorias fixas: **Trees** e **Biodiversity**.
  - Cada categoria tem 7 faixas (6 níveis regenerativos + 1 neutro), com valores de score:
    - 32, 16, 8, 4, 2, 1, 0.
  - A função `calculateScore(treesResult, biodiversityResult)`:
    - Converte o número de árvores em um índice de 1 a 7.
    - Converte o número de espécies em um índice de 1 a 7.
    - Soma os valores de ambas categorias → **Score Total**.

**Relação com a tabela da seção 3:**
- Os thresholds de árvores e biodiversidade da seção 3 são extraídos diretamente deste contrato.
- Score máximo **64 pontos** = 32 (árvores) + 32 (biodiversidade).

### 11.3 `RegeneratorRules.sol` + `RegeneratorPool.sol`

#### Regras de Regenerador (`RegeneratorRules.sol`)

- **Área:**
  - Mínimo: 2.500 m².
  - Máximo: 1.000.000 m².
  - Até 500.000 regeneradores ativos.
- **Inspeções:**
  - `MINIMUM_INSPECTIONS_TO_POOL = 3`.
  - `MAXIMUM_INSPECTIONS = 6`.
  - Score máximo por inspeção: 64.
- **Fluxo de níveis:**
  - Cada inspeção gera um `score` (0–64).
  - Enquanto o usuário tem menos de 3 inspeções:
    - O score é acumulado no perfil, mas **não gera níveis no pool**.
  - Quando atinge a 3ª inspeção:
    - Entra no pool (`onContractPool = true`).
    - Os níveis adicionados ao pool passam a ser o **score total acumulado até então**.
  - Inspeções seguintes:
    - Adicionam ao pool apenas o score da nova inspeção.

#### Pool de Regenerador (`RegeneratorPool.sol`)

- **Constante de pool:**
  - `TOTAL_POOL_TOKENS = 750.000.000 RC` (e18 na implementação).
- **Tempo:**
  - Usa `Blockable` para:
    - `blocksPerEra` (quantos blocos formam uma Era).
    - `halving` (quantas Eras formam um Epoch – 12).
- **Distribuição:**
  - Cada Era:
    - Calcula `tokensPerEra(epoch, halving)` a partir de `TOTAL_POOL_TOKENS`.
  - Em um saque (`withdraw`):
    - Verifica se o usuário pode sacar na Era informada.
    - Calcula `numTokens` com base nos níveis do usuário e níveis totais da Era.
    - Atualiza estados internos (eras já sacadas, níveis etc.).
    - Chama `RegenerationCredit.decreaseLocked(numTokens)` e transfere para o usuário.

**Resumo de regra prática:**
- Níveis de regenerador por Era são a soma dos scores de inspeções válidas (após entrar no pool).
- Tokens recebidos em uma Era seguem a fórmula da seção 5, usando:
  - `tokens_disponíveis_na_era` calculado com o pool de 750M e o halving.

### 11.4 `DeveloperRules.sol` + `DeveloperPool.sol`

#### Regras de Desenvolvedor (`DeveloperRules.sol`)

- **Cadastro:**
  - Máximo de 16.000 desenvolvedores.
  - Requer convite e validação via `CommunityRules`.
- **Relatórios:**
  - Cada relatório de desenvolvimento válido = **1 nível**.
  - Limites de tamanho para texto e hashes (nome, descrição, prova).
  - `timeBetweenWorks`:
    - Número mínimo de blocos entre publicações de relatórios.
  - `securityBlocksToValidation`:
    - Janela final da Era na qual **não é permitido** publicar novos relatórios (tempo reservado para validação).
- **Penalidades:**
  - Relatórios podem ser invalidados via votação (`VoteRules` + `ValidationRules`).
  - Cada relatório invalidado:
    - Remove 1 nível do desenvolvedor.
    - Adiciona uma penalidade.
  - Ao atingir `maxPenalties`, o desenvolvedor é marcado como **denied** e perde os níveis do pool.

#### Pool de Desenvolvedor (`DeveloperPool.sol`)

- **Constante de pool:**
  - `TOTAL_POOL_TOKENS = 40.000.000 RC`.
- **Níveis:**
  - Cada relatório válido aprovado adiciona 1 nível ao pool.
  - `removePoolLevels` pode remover níveis ao invalidar relatórios ou negar o usuário.
- **Distribuição:**
  - Mesmo padrão de RegeneratorPool:
    - `tokens_por_era` baseado em 40M e no Epoch atual.
    - Cálculo de tokens por Era é proporcional aos níveis do desenvolvedor versus total de níveis do pool.

### 11.5 Outros Pools (Inspetor, Ativista, Contribuidor, Pesquisador)

- Todos seguem o mesmo **padrão estrutural**:
  - Um contrato `XRules.sol` define:
    - Como o usuário ganha níveis (geralmente 1 nível por inspeção, convite qualificado ou contribuição aceita).
    - Limites de usuários, texto, frequência de ações, penalidades.
  - Um contrato `XPool.sol` define:
    - `TOTAL_POOL_TOKENS` específico do pool.
    - Lógica de `tokensPerEra`/`tokensPerEpoch`.
    - Como níveis são adicionados e removidos (`addLevel`, `removePoolLevels`).
    - Como o saque é feito (`withdraw`).

**Para cálculos de alto nível:**
- É seguro assumir que:
  - **1 ação válida** (inspeção, convite qualificado, contribuição/reporte aprovado) **≈ 1 nível**.
  - Tokens por Era seguem sempre a fórmula da seção 2.3/6.2, com o `TOTAL_POOL_TOKENS` de cada pool.

### 11.6 `SupporterRules.sol` (Apoiador)

- Apoiadores **não recebem tokens** via pools.
- Principais pontos:
  - Função `offset`:
    - Queima tokens RC em troca de um certificado de compensação.
    - Pode associar a queima a um `CalculatorItem` (pesquisa sobre impacto).
  - Comissão para o convidador:
    - 5% do valor queimado vai para o **inviter**.
    - 95% é efetivamente queimado como offset.
  - Limites:
    - Mínimo de 1 RC para offset.
    - Limites de tamanho para nome, descrição, mensagem.

**Implicação para tokenomics:**
- Apoiadores retiram tokens de circulação (queima), aumentando a escassez.
- Não participam do cálculo de `avg_era_levels` nem dos pools de recompensa.

---

## 12. PASSO A PASSO PARA CÁLCULOS DE TOKENOMICS

Esta seção é um **algoritmo mental** para o agente seguir ao fazer simulações, usando sempre este documento e/ou o whitepaper completo como base.

### 12.1 Identificar o contexto

1. Identifique **tipo de usuário**:
   - Regenerador, Inspetor, Ativista, Contribuidor, Pesquisador, Desenvolvedor ou Apoiador.
2. Pergunte:
   - Em qual **época**/fase a simulação deve considerar (ex.: início de rede = Epoch 1).
   - Quantas **eras** devem ser simuladas.

### 12.2 Calcular tokens disponíveis por Era

1. Escolha o **pool** relevante (seção 2.2).
2. Use a fórmula da seção 2.3 / 6.2:
   - `tokens_por_era = (total_pool ÷ 2^epoch) ÷ 12`.
3. Se precisar de múltiplos Epochs:
   - Para cada Epoch `e`:
     - Calcule `tokens_por_era(e)` com a mesma fórmula.
     - Repita para 12 eras daquele Epoch.

### 12.3 Calcular níveis do usuário

1. **Regenerador:**
   - Calcular score (seção 3 + 11.2).
   - Definir número de inspeções válidas.
   - Considerar regra mínima de 3 inspeções para entrar no pool.
2. **Demais usuários (inspetor, ativista, contribuidor, pesquisador, desenvolvedor):**
   - Estimar quantas ações válidas por Era (inspeções, convites, relatórios etc.).
   - Cada ação válida ≈ 1 nível (salvo regras específicas do contrato).

### 12.4 Estimar `avg_era_levels` (total de níveis na Era)

1. Perguntar ao usuário se ele tem um valor ou estimativa.
2. Se não tiver:
   - Usar as faixas da seção 7.1 (fase inicial vs. rede madura).
3. Em simulações comparativas:
   - Ajustar `avg_era_levels` conforme cenários pessimista/otimista (seção 6.3).

### 12.5 Aplicar fórmula central por Era

Para cada Era simulada:

1. Obter `tokens_por_era` do pool e epoch.
2. Calcular níveis do usuário naquela Era.
3. Aplicar fórmula da seção 5:
   - `Seus tokens = (Seus níveis ÷ Total de níveis na Era) × Tokens disponíveis na Era`.
4. Somar resultados ao longo das Eras simuladas.

### 12.6 Interpretar resultados

Ao final do cálculo:

1. Converter número de Eras em tempo (seção 6.4).
2. Comparar o resultado com:
   - Score do usuário (baixo/médio/alto).
   - Faixas de `avg_era_levels`.
3. Explicar:
   - Se o ganho é proporcionalmente alto ou baixo para o contexto.
   - Como mais níveis, mais tempo ou entrada mais cedo (Epoch 1) afetam o resultado.

---

**NOTA FINAL:** Esta síntese é para contexto interpretativo. Para regras exatas, sempre consulte o whitepaper completo via ferramentas RAG.

