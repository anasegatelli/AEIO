
================================================================================
SKILL - DDL TABLE CREATION PARA TRUSTED-ZONE E SENSITIVE-TRUSTED
================================================================================

Versão: 1.0.0
Repositório: grupoboticario/data-platform-bigquery
Mantido por: Engenharia de Dados

================================================================================
DESCRIÇÃO DA SKILL
================================================================================

Esta skill habilita agentes a CRIAR tabelas DDL de forma autônoma para as 
camadas TRUSTED-ZONE e SENSITIVE-TRUSTED, seguindo padrões de nomeação, 
estrutura e metadados do Grupo Boticário.

OBJETIVO: Padronizar a criação de tabelas SQL em BigQuery tipificadas nas 
camadas Trusted Zone e Sensitive-Trusted, gerando 2 arquivos:
  1. tb_{tabela}.sql (DDL da tabela)
  2. execution_plan.yaml (plano de execução e metadados)

================================================================================
QUANDO USAR
================================================================================

Use esta skill quando:

✅ Criar nova tabela em Trusted Zone (trusted-zone)
✅ Criar nova tabela em Sensitive-Trusted (sensitive-trusted)
✅ Implementar tipificação e estrutura de dados
✅ Gerar arquivos: tb_{tabela}.sql E execution_plan.yaml
✅ Adicionar metadados, particionamento e clustering
✅ Seguir nomenclatura e padrão de campos

NÃO use quando:

❌ Criar tabelas para camadas Raw ou Refined
❌ Modificar tabelas já existentes sem justificativa
❌ Criar tabelas sem especificação clara de origem/destino
❌ Trabalhar com dados que não seguem padrão de tipificação
❌ Projeto diferente de trusted-zone ou sensitive-trusted

================================================================================
VALIDAÇÃO DE ENTRADA - CAMPOS OBRIGATÓRIOS (5 CAMPOS)
================================================================================

A DDL deve ser criada com base nos seguintes campos:

1. PROJETO
   Validação: Exatamente "trusted-zone" ou "sensitive-trusted"
   Exemplo Válido: trusted-zone
   Exemplo Inválido: trusted ou TRUSTED-ZONE

2. DATASET
   Validação: Minúsculas, sem espaços, sem underscore duplo
   Exemplo Válido: casa_magalhaes
   Exemplo Inválido: Casa Magalhães ou casa__magalhaes

3. TABELA
   Validação: Deve iniciar com "tb_", minúsculas
   Exemplo Válido: tb_terminal
   Exemplo Inválido: terminal ou Tb_Terminal

4. SQUAD/TIME
   Validação: Um de: eng, dataops, arq, ml, bi, plat
   Exemplo Válido: eng
   Exemplo Inválido: none

5. DESCRIÇÃO
   Validação: Mínimo 10 palavras maximo 20, sem caracteres especiais. Resuma caso necessario e corrija os erros de gramatica
   Exemplo Válido: "Tabela que centraliza dados de terminais..."
   Exemplo Inválido: "Dados"

================================================================================
ESTRUTURA DE DIRETÓRIOS - DDL
================================================================================

Padrão Geral:

bigquery/
└── table/
    └── eng/
        └── {projeto}/
            └── {dataset}/
                └── tb_{nome_tabela}/
                    ├── tb_{nome_tabela}.sql
                    └── execution_plan.yaml

Exemplo - Trusted Zone:

bigquery/
└── table/
    └── eng/
        └── trusted-zone/
            └── casa_magalhaes/
                └── tb_terminal/
                    ├── tb_terminal.sql
                    └── execution_plan.yaml

Exemplo - Sensitive-Trusted:

bigquery/
└── table/
    └── eng/
        └── sensitive-trusted/
            └── saloes/
                └── tb_lead_optin/
                    ├── tb_lead_optin.sql
                    └── execution_plan.yaml

================================================================================
ARQUIVO 1: tb_{nome_tabela}.sql
================================================================================

TEMPLATE DDL:

CREATE TABLE IF NOT EXISTS {dataset}.tb_{nome_tabela} (
    -- Identificadores
    id_chave_primaria       INT64           OPTIONS(description="Chave primária da tabela"),
    
    -- Dados de negócio
    campo_1                 STRING          OPTIONS(description="Descrição do campo 1"),
    campo_2                 STRING          OPTIONS(description="Descrição do campo 2"),
    campo_3                 NUMERIC         OPTIONS(description="Descrição do campo 3"),
    
    -- Flags e controle
    flg_ativo               BOOL            OPTIONS(description="Flag ativo/inativo"),
    
    -- Data de carga
    dt_carga                TIMESTAMP       OPTIONS(description="Data e hora da carga na tabela")
)

PARTITION BY DATE(dt_carga)
CLUSTER BY id_chave_primaria

OPTIONS(
    description="{descricao}",
    labels=[("projeto", "{projeto}"), ("dataset", "{dataset}"), ("squad", "{squad_time}")]
)
;

VARIÁVEIS DE SUBSTITUIÇÃO:

{projeto}: Valor do campo Projeto (trusted-zone ou sensitive-trusted)
{dataset}: Valor do campo Dataset
{squad_time}: Valor do campo Squad/Time
{data_criacao}: Data atual (YYYY-MM-DD)
{descricao}: Valor do campo Descrição (truncado se necessário)
{nome_tabela}: Extraído do campo Tabela (sem prefixo tb_)

================================================================================
ARQUIVO 2: execution_plan.yaml - TABELA
================================================================================

Este arquivo é gerado junto com a DDL e contém metadados de execução e 
informações sobre a tabela.

TEMPLATE:

# ========================================================================
# Objeto......: execution_plan.yaml
# Tabela......: tb_{nome_tabela}
# Camada......: {projeto}
# Version.....: 0.0.1
# Criacao.....: {data_criacao}
# Proposito...: Metadados e plano de execução da tabela
# ========================================================================

identifiers:
  gb-iniciativa: {iniciativa}

resource:
  table:
    project_id: {projeto}
    dataset_id: {dataset}
    table_id: tb_{nome_tabela}

    metadata:
      description: "{descricao}"
      squad: "{squad_time}"
      layer: "{projeto}"
      version: "0.0.1"
      created_at: "{data_criacao}"

    schema:
      fields:
        - name: "{campo}"
          type: "{tipo}"
          mode: "NULLABLE"
          description: "{descricao_campo}"
        # repetir para cada campo da tabela

    partitioning:
      type: "TIME"
      field: "dt_carga"

    clustering:
      fields:
        - "{campo_cluster_1}"
        # adicionar demais campos de clustering

    options:
      labels:
        projeto: "{projeto}"
        dataset: "{dataset}"
        squad: "{squad_time}"

  dev:
    project_id: {sandbox}
  prd:
    project_id: {projeto}


VARIÁVEIS DE SUBSTITUIÇÃO:

{projeto}: trusted-zone ou sensitive-trusted
{sandbox}: Projeto do ambiente de desenvolvimento
{dataset}: Nome do dataset
{nome_tabela}: Nome da tabela sem prefixo tb_
{iniciativa}: Código da iniciativa (ex: inic1500)
{descricao}: Descrição da tabela
{squad_time}: Squad responsável
{data_criacao}: Data atual no formato YYYY-MM-DD

================================================================================
NOMES DE CAMPOS - PADRÃO DE NOMENCLATURA
================================================================================

IDENTIFICADORES:
  id_{entidade}
  id_chave_primaria
  id_mudanca
  Exemplo: id_terminal, id_cliente

DADOS DE NEGÓCIO:
  {prefixo}_{descricao}
  ds_: descrições textuais
  vl_: valores monetários
  qt_: quantidades
  Exemplo: ds_nome_terminal, vl_velocidade_ecf, qt_quantidade

FLAGS E CONTROLES:
  flg_{descricao}
  Exemplo: flg_ativo, flg_sincronizado

DATAS E TIMESTAMPS:
  dt_{descricao}: para datas
  dt_hr_{descricao}: para timestamps
  Exemplo: dt_criacao, dt_hr_atualizacao, dt_carga

VALORES NUMÉRICOS:
  vl_{descricao} ou qt_{descricao}
  Exemplo: vl_preco, qt_quantidade

PERCENTUAIS:
  pct_{descricao}
  Exemplo: pct_desconto

TIPOS DE DADOS RECOMENDADOS:

STRING: Textos, descrições, IDs textuais
INT64: Números inteiros, IDs numéricas
NUMERIC: Valores monetários, percentuais com precisão
FLOAT64: Valores decimais científicos
BOOL: Flags, verdadeiro/falso
DATE: Datas (YYYY-MM-DD)
TIMESTAMP: Data e hora (YYYY-MM-DD HH:MM:SS)
ARRAY: Listas de valores
STRUCT: Estruturas aninhadas
JSON: Dados semi-estruturados

================================================================================
ESTRUTURA RECOMENDADA DE CAMPOS NA DDL
================================================================================

Ordem típica de campos:

1. IDENTIFICADORES (IDs, chaves primárias)
2. DADOS DE NEGÓCIO (campos de domínio)
3. FLAGS E CONTROLE (indicadores booleanos)
4. DATAS E TIMESTAMPS (datas de criação, atualização, carga)

Exemplo completo:

CREATE TABLE IF NOT EXISTS casa_magalhaes.tb_terminal (
    -- Identificadores
    id_terminal             INT64           OPTIONS(description="ID único do terminal"),
    id_ponto_venda          INT64           OPTIONS(description="ID do ponto de venda"),
    
    -- Dados de negócio
    ds_hostname             STRING          OPTIONS(description="Hostname do terminal"),
    ds_endereco_ip          STRING          OPTIONS(description="Endereço IP do terminal"),
    vl_velocidade_ecf       INT64           OPTIONS(description="Velocidade do ECF em kbps"),
    ds_versao_tif           STRING          OPTIONS(description="Versão do software TIF"),
    
    -- Flags e controle
    flg_ativo               BOOL            OPTIONS(description="Indica se terminal está ativo"),
    flg_sincronizado        BOOL            OPTIONS(description="Indica sincronização com servidor"),
    
    -- Datas e timestamps
    dt_hr_atualizacao       TIMESTAMP       OPTIONS(description="Data/hora da última atualização"),
    dt_carga                TIMESTAMP       OPTIONS(description="Data/hora da carga na tabela")
)

PARTITION BY DATE(dt_carga)
CLUSTER BY id_ponto_venda, id_terminal

OPTIONS(
    description="Tabela que centraliza dados de terminais de ponto de venda com informações técnicas",
    labels=[("projeto", "trusted-zone"), ("dataset", "casa_magalhaes"), ("squad", "eng")]
)
;

================================================================================
CHECKLIST - DDL E EXECUTION_PLAN
================================================================================

CHECKLIST DDL (tb_*.sql):

- ✅ Nome tabela: tb_{nome_tabela} (com prefixo)
- ✅ Dataset correto
- ✅ CREATE TABLE IF NOT EXISTS
- ✅ Nome e formato dos campos seguindo padrão de nomenclatura
- ✅ Todos os campos com OPTIONS(description=...)
- ✅ PARTITION BY com campo de data
- ✅ CLUSTER BY com campo mais consultado
- ✅ Tipos de dados corretos
- ✅ OPTIONS com labels (projeto, dataset, squad)

CHECKLIST EXECUTION_PLAN (YAML):

- ✅ table.project_id = projeto correto
- ✅ table.dataset_id = dataset correto
- ✅ table.table_id = tb_{nome_tabela}
- ✅ metadata.description preenchida
- ✅ metadata.squad preenchido
- ✅ schema.fields com todos os campos
- ✅ Cada field com name, type, mode, description
- ✅ partitioning.type = TIME
- ✅ partitioning.field = dt_carga
- ✅ clustering.fields preenchido
- ✅ labels: projeto, dataset, squad
- ✅ YAML válido (indentação correta)

================================================================================
VALIDAÇÃO E REGRAS CRÍTICAS
================================================================================

BLOQUEADORES ABSOLUTOS:

1. PROJETO
   ❌ SEMPRE validar: apenas "trusted-zone" ou "sensitive-trusted"
   ❌ Rejeitar se divergir
   ❌ Qualquer outro projeto deve resultar em "NÃO POSSÍVEL GERAR"

2. TABELA
   ❌ DEVE iniciar com "tb_"
   ��� Rejeitar se não tiver prefixo

3. DATASET
   ❌ Deve estar em minúsculas
   ❌ Sem espaços ou underscores duplos

SE QUALQUER BLOQUEADOR FALHAR:

NUNCA prossiga com a geração da DDL e YAML.

Retorne:

❌ VALIDAÇÃO FALHOU - GERAÇÃO NÃO POSSÍVEL

[Lista clara dos campos inválidos com valores esperados]

[Solicitação para corrigir antes de prosseguir]

================================================================================
EXEMPLOS COMPLETOS
================================================================================

EXEMPLO 1: Trusted Zone - tb_terminal

Entrada do Usuário (5 campos):

Projeto: trusted-zone
Dataset: casa_magalhaes
Tabela: tb_terminal
Squad/Time: eng
Descrição: Tabela que centraliza dados de terminais de ponto de venda com 
informações técnicas de suporte e integração de sistemas

Validação: ✅ TODOS OS CAMPOS VÁLIDOS

Estrutura de Diretórios Criada:

bigquery/
└── table/
    └── eng/
        └── trusted-zone/
            └── casa_magalhaes/
                └── tb_terminal/
                    ├── tb_terminal.sql
                    └── execution_plan.yaml

---

Arquivo 1: tb_terminal.sql

-- ========================================================================
-- Objeto......: create_tb_terminal
-- Camada......: trusted-zone
-- Version.....: 0.0.1
-- Data Criacao: 2026-03-22
-- Data Update.: 2026-03-22
-- Squad.......: eng
-- Descricao...: DDL da tabela tb_terminal
-- ========================================================================

CREATE TABLE IF NOT EXISTS casa_magalhaes.tb_terminal (
    -- Identificadores
    id_terminal             INT64           OPTIONS(description="ID único do terminal"),
    id_ponto_venda          INT64           OPTIONS(description="ID do ponto de venda"),
    
    -- Dados de negócio
    ds_hostname             STRING          OPTIONS(description="Hostname do terminal"),
    ds_endereco_ip          STRING          OPTIONS(description="Endereço IP do terminal"),
    vl_velocidade_ecf       INT64           OPTIONS(description="Velocidade do ECF em kbps"),
    ds_versao_tif           STRING          OPTIONS(description="Versão do software TIF"),
    
    -- Flags e controle
    flg_ativo               BOOL            OPTIONS(description="Indica se terminal está ativo"),
    flg_sincronizado        BOOL            OPTIONS(description="Indica sincronização com servidor"),
    
    -- Datas e timestamps
    dt_hr_atualizacao       TIMESTAMP       OPTIONS(description="Data/hora da última atualização"),
    dt_carga                TIMESTAMP       OPTIONS(description="Data/hora da carga na tabela")
)

PARTITION BY DATE(dt_carga)
CLUSTER BY id_ponto_venda, id_terminal

OPTIONS(
    description="Tabela que centraliza dados de terminais de ponto de venda com informações técnicas de suporte e integração de sistemas",
    labels=[("projeto", "trusted-zone"), ("dataset", "casa_magalhaes"), ("squad", "eng")]
)
;

---

Arquivo 2: execution_plan.yaml

# ========================================================================
# Objeto......: execution_plan.yaml
# Tabela......: tb_terminal
# Camada......: trusted-zone
# Version.....: 0.0.1
# Criacao.....: 2026-03-22
# Proposito...: Metadados e plano de execução da tabela
# ========================================================================

resource:
  table:
    project_id: trusted-zone
    dataset_id: casa_magalhaes
    table_id: tb_terminal
    
    metadata:
      description: "Tabela que centraliza dados de terminais de ponto de venda com informações técnicas de suporte e integração de sistemas"
      squad: "eng"
      layer: "trusted-zone"
      version: "0.0.1"
      created_at: "2026-03-22"
      
    schema:
      fields:
        - name: "id_terminal"
          type: "INT64"
          mode: "NULLABLE"
          description: "ID único do terminal"
          
        - name: "id_ponto_venda"
          type: "INT64"
          mode: "NULLABLE"
          description: "ID do ponto de venda"
          
        - name: "ds_hostname"
          type: "STRING"
          mode: "NULLABLE"
          description: "Hostname do terminal"
          
        - name: "ds_endereco_ip"
          type: "STRING"
          mode: "NULLABLE"
          description: "Endereço IP do terminal"
          
        - name: "vl_velocidade_ecf"
          type: "INT64"
          mode: "NULLABLE"
          description: "Velocidade do ECF em kbps"
          
        - name: "ds_versao_tif"
          type: "STRING"
          mode: "NULLABLE"
          description: "Versão do software TIF"
          
        - name: "flg_ativo"
          type: "BOOL"
          mode: "NULLABLE"
          description: "Indica se terminal está ativo"
          
        - name: "flg_sincronizado"
          type: "BOOL"
          mode: "NULLABLE"
          description: "Indica sincronização com servidor"
          
        - name: "dt_hr_atualizacao"
          type: "TIMESTAMP"
          mode: "NULLABLE"
          description: "Data/hora da última atualização"
          
        - name: "dt_carga"
          type: "TIMESTAMP"
          mode: "NULLABLE"
          description: "Data/hora da carga na tabela"
    
    partitioning:
      type: "TIME"
      field: "dt_carga"
      
    clustering:
      fields:
        - "id_ponto_venda"
        - "id_terminal"
    
    options:
      labels:
        projeto: "trusted-zone"
        dataset: "casa_magalhaes"
        squad: "eng"

---

EXEMPLO 2: Sensitive-Trusted - tb_lead_optin

Entrada do Usuário (5 campos):

Projeto: sensitive-trusted
Dataset: saloes
Tabela: tb_lead_optin
Squad/Time: dataops
Descrição: Tabela com dados de leads e seu status de opt-in para comunicações, 
contendo informações sensíveis de contato

Validação: ✅ TODOS OS CAMPOS VÁLIDOS

Estrutura de Diretórios Criada:

bigquery/
└── table/
    └── eng/
        └── sensitive-trusted/
            └── saloes/
                └── tb_lead_optin/
                    ├── tb_lead_optin.sql
                    └── execution_plan.yaml

================================================================================
FORMATO DE RESPOSTA FINAL - DDL
================================================================================

Quando validação é ✅ APROVADA:

RESPOSTA ESTRUTURADA:

## ✅ Validação Aprovada - Gerando DDL e Execution Plan

### Resumo da Entrada
| Campo | Valor |
|-------|-------|
| Projeto | trusted-zone |
| Dataset | casa_magalhaes |
| Tabela | tb_terminal |
| Squad/Time | eng |

**Status**: ✅ PRONTO PARA GERAÇÃO

### Estrutura de Diretórios a Criar

bigquery/
└── table/
    └── eng/
        └── trusted-zone/
            └── casa_magalhaes/
                └── tb_terminal/
                    ├── tb_terminal.sql
                    └── execution_plan.yaml

### Arquivo 1 Gerado: tb_terminal.sql

[Código DDL completo aqui]

### Arquivo 2 Gerado: execution_plan.yaml

[YAML completo aqui]

### ✅ Checklist - DDL
- ✅ Nome: tb_terminal
- ✅ Dataset: casa_magalhaes
- ✅ Projeto: trusted-zone
- ✅ PARTITION BY: DATE(dt_carga)
- ✅ CLUSTER BY: id_ponto_venda, id_terminal
- ✅ Descrição em OPTIONS
- ✅ Labels configurados (projeto, dataset, squad)
- ✅ Todos os campos com OPTIONS(description=...)

### ✅ Checklist - Execution Plan
- ✅ project_id: trusted-zone
- ✅ dataset_id: casa_magalhaes
- ✅ table_id: tb_terminal
- ✅ metadata.squad: eng
- ✅ schema.fields: 10 campos
- ✅ partitioning.field: dt_carga
- ✅ clustering.fields: id_ponto_venda, id_terminal
- ✅ labels: projeto, dataset, squad
- ✅ YAML válido

### 📋 Próximas Etapas para Deploy

1. Clone o Repositório
   git clone https://github.com/grupoboticario/data-platform-bigquery.git
   cd data-platform-bigquery

2. Crie a Branch
   git checkout -b feature/tb-terminal

3. Crie os Diretórios
   mkdir -p bigquery/table/eng/trusted-zone/casa_magalhaes/tb_terminal

4. Copie os Arquivos
   cp tb_terminal.sql bigquery/table/eng/trusted-zone/casa_magalhaes/tb_terminal/
   cp execution_plan.yaml bigquery/table/eng/trusted-zone/casa_magalhaes/tb_terminal/

5. Commit e Push
   git add .
   git commit -m "[TABLE] Add tb_terminal for casa_magalhaes
   
   - Projeto: trusted-zone
   - Dataset: casa_magalhaes
   - Squad: eng
   - Particionada por dt_carga
   - Clusterizada por id_ponto_venda, id_terminal
   "
   git push origin feature/tb-terminal

6. Abra Pull Request
   - Descrição: Inclua contexto de negócio
   - Labels: table, trusted-zone, casa_magalhaes

================================================================================
FIM DO DOCUMENTO - DDL TABLE CREATION SKILL COM EXECUTION_PLAN.YAML
================================================================================
