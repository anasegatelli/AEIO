
================================================================================
SKILL - PROCEDURE CREATION PARA TRUSTED-ZONE E SENSITIVE-TRUSTED
================================================================================

Versão: 1.0.0
Repositório: grupoboticario/data-platform-bigquery
Mantido por: Engenharia de Dados

DEPENDÊNCIA: Esta skill deve ser executada APÓS a criação da DDL (tb_*.sql)

================================================================================
DESCRIÇÃO DA SKILL
================================================================================

Esta skill habilita agentes a CRIAR Procedures de Carga de forma autônoma para 
as camadas TRUSTED-ZONE e SENSITIVE-TRUSTED, realizando tipificação e 
transformação de dados vindos da camada Raw.

OBJETIVO: Padronizar a criação de procedures SQL em BigQuery que extraem dados 
brutos (Raw), aplicam lógica de negócio e carregam em tabelas tipificadas nas 
camadas Trusted.

================================================================================
QUANDO USAR
================================================================================

Use esta skill quando:

✅ Criar nova Procedure de carga para tabela em Trusted Zone (trusted-zone)
✅ Criar nova Procedure de carga para tabela em Sensitive-Trusted (sensitive-trusted)
✅ Implementar tipificação e transformação de dados Raw
✅ Gerar arquivos: prc_load_{tabela}.sql, execution_plan.yaml
✅ Preparar estrutura completa com tabelas temporárias e tratamento de erros
✅ Implementar transaction blocks para robustez

NÃO use quando:

❌ Criar procedures para camadas Raw ou Refined
❌ Modificar procedures já existentes sem justificativa
❌ Criar procedures sem especificação clara de origem/destino de dados
❌ Trabalhar com dados que não seguem padrão de tipificação
❌ Projeto diferente de trusted-zone ou sensitive-trusted

================================================================================
VALIDAÇÃO DE ENTRADA - CAMPOS OBRIGATÓRIOS
================================================================================

A Procedure deve ser criada com base nos seguintes 12 campos:

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

4. TIPO DE CARGA
   Validação: Exatamente "FULL" ou "INCREMENTAL"
   Exemplo Válido: FULL
   Exemplo Inválido: full ou FULL_LOAD

5. FREQUÊNCIA
   Validação: Um de: DIARIO, SEMANAL, MENSAL, SOB_DEMANDA
   Exemplo Válido: DIARIO
   Exemplo Inválido: daily ou Diário

6. CAMPO DELTA
   Validação: Se FULL: "null" | Se INCREMENTAL: campo válido
   Exemplo Válido FULL: null
   Exemplo Válido INCREMENTAL: dt_hr_atualizacao
   Exemplo Inválido: data atualizacao

7. FAIXA DELTA
   Validação: Se FULL: "null" | Se INCREMENTAL: informar a quantida de dias
   Exemplo Válido FULL: null
   Exemplo Válido INCREMENTAL: 7 -> vai de 0 a -7
   Exemplo Inválido: -1

8. INICIATIVA
   Validação: Formato "inicXXXX" (4 dígitos)
   Exemplo Válido: inic1234
   Exemplo Inválido: iniciativa1234 ou inic12

9. ORIGEM DOS DADOS (Tabela de Origem)
   Validação: "{dataset}.{tabela}" válidos
   Exemplo Válido: raw_linx.ljv_terminal
   Exemplo Inválido: raw-linx.ljv_terminal

10. DESCRIÇÃO
    Validação: Mínimo 10 palavras, sem caracteres especiais
    Exemplo Válido: "Tabela que centraliza dados de terminais..."
    Exemplo Inválido: "Dados"

11. SQUAD/TIME
    Validação: Um de: eng, dataops, arq, ml, bi, plat
    Exemplo Válido: eng
    Exemplo Inválido: engineering ou engenharia

12. SANDBOX DEV
    Validação: Projeto sandbox válido, minúsculas
    Exemplo Válido: sandbox-casa-magalhaes
    Exemplo Inválido: Sandbox-Casa-Magalhaes

================================================================================
REGRA DE CONSISTÊNCIA: FULL vs INCREMENTAL
================================================================================

Se Tipo de Carga = FULL:
   ✅ Campo Delta DEVE ser: null
   ✅ Faixa Delta DEVE ser: null
   ❌ Caso contrário: INVÁLIDO

Se Tipo de Carga = INCREMENTAL:
   ✅ Campo Delta NÃO PODE ser: null
   ✅ Faixa Delta NÃO PODE ser: null
   ✅ Faixa Delta DEVE ser: a quantidade de dias. Ex.: 7 (Com isso sera criada a logica, nesse cado -7 a 0)
   ❌ Caso contrário: INVÁLIDO

================================================================================
ESTRUTURA DE DIRETÓRIOS - PROCEDURE
================================================================================

Padrão Geral:

bigquery/
└── procedure/
    └── eng/
        └── {projeto}/
            └── prc_load_tb_{nome_tabela}/
                ├── prc_load_tb_{nome_tabela}.sql
                └── execution_plan.yaml

Exemplo - Trusted Zone:

bigquery/
├── procedure/
│   └── eng/
│       └── trusted-zone/
│           └── prc_load_tb_terminal/
│               ├── prc_load_tb_terminal.sql
│               └── execution_plan.yaml

Exemplo - Sensitive-Trusted:

bigquery/
├── procedure/
│   └── eng/
│       └── sensitive-trusted/
│           └── prc_load_tb_lead_optin/
│               ├── prc_load_tb_lead_optin.sql
│               └── execution_plan.yaml

================================================================================
ARQUIVO 1: PROCEDURE SQL - prc_load_tb_{nome_tabela}.sql
================================================================================

TEMPLATE - Carga FULL:

-- ========================================================================
-- Objeto......: prc_load_tb_{nome_tabela}
-- Camada......: {projeto}
-- Version.....: 0.0.1
-- Squad.......: {squad_time}
-- Data Criacao: {data_criacao}
-- Descricao...: {descricao}
-- ========================================================================

CREATE OR REPLACE PROCEDURE `sp.prc_load_tb_{nome_tabela}`(
    VAR_PRJ_RAW STRING,
    VAR_PRJ_RAW_CUSTOM STRING,
    VAR_PRJ_TRUSTED STRING,
    VAR_PRJ_REFINED STRING,
    VAR_PRJ_SENSITIVE_RAW STRING,
    VAR_PRJ_SENSITIVE_TRUSTED STRING,
    VAR_PRJ_SENSITIVE_REFINED STRING
)
BEGIN

    -- Parametros usados para tabela de controle e log
    DECLARE VAR_PROCEDURE  DEFAULT 'prc_load_tb_{nome_tabela}';
    DECLARE VAR_DELTA_INI  DATE;
    DECLARE VAR_DELTA_FIM  DATE;
    DECLARE VAR_TABELA     STRING;
    DECLARE VAR_DTH_INICIO TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

    -- Inicio do bloco de TRY/CATCH (tratamento de erros)
    BEGIN

        -- Recupera parametros da TB_AUX_CONFIG_CARGA_BUS
        CALL sp.prc_get_params(VAR_PROCEDURE, VAR_DELTA_INI, VAR_DELTA_FIM, VAR_TABELA);

        BEGIN TRANSACTION;

            -- Criação da tabela temporária com dados da RAW
            EXECUTE IMMEDIATE """
                CREATE TEMP TABLE temp_tb_{nome_tabela} AS
                SELECT
                    campo_1,
                    campo_2,
                    campo_3,
                    CURRENT_TIMESTAMP AS dt_carga
                FROM `""" || VAR_PRJ_RAW || """.{dataset_origem}.{tabela_origem}`
                WHERE
                    -- Condições de filtro conforme necessário
                    campo_1 IS NOT NULL
            """;

            -- TRUNCATE na tabela final (FULL LOAD)
            EXECUTE IMMEDIATE """
                TRUNCATE TABLE `""" || {var_projeto} || """.""" || VAR_TABELA || """`
            """;

            -- INSERT dos dados da temp para tabela final
            EXECUTE IMMEDIATE """
                INSERT INTO `""" || {var_projeto} || """.""" || VAR_TABELA || """` (
                    campo_1,
                    campo_2,
                    campo_3,
                    dt_carga
                )
                SELECT
                    campo_1,
                    campo_2,
                    campo_3,
                    dt_carga
                FROM temp_tb_{nome_tabela}
            """;

            -- Log de sucesso
            CALL sp.prc_log_exec_transaction(VAR_TABELA, VAR_DTH_INICIO, @@row_count, VAR_PROCEDURE, @@error.message, {var_projeto});
            COMMIT TRANSACTION;

    EXCEPTION WHEN ERROR THEN
        ROLLBACK TRANSACTION;
        CALL sp.prc_log_exec_transaction(VAR_TABELA, VAR_DTH_INICIO, @@row_count, VAR_PROCEDURE, @@error.message, {var_projeto});
        RAISE USING MESSAGE = @@error.message;

    END;

END;

VARIÁVEIS DE SUBSTITUIÇÃO:

{var_projeto}: VAR_PRJ_TRUSTED para trusted-zone | VAR_PRJ_SENSITIVE_TRUSTED para sensitive-trusted
{squad_time}: Valor do campo Squad/Time
{data_criacao}: Data atual (YYYY-MM-DD)
{descricao}: Valor do campo Descrição
{dataset_origem}: Extraído de "Origem dos Dados" (primeira parte antes do ponto)
{tabela_origem}: Extraído de "Origem dos Dados" (segunda parte após o ponto)

---

TEMPLATE - Carga INCREMENTAL:

-- ========================================================================
-- Objeto......: prc_load_tb_{nome_tabela}
-- Camada......: {projeto}
-- Version.....: 0.0.1
-- Squad.......: {squad_time}
-- Data Criacao: {data_criacao}
-- Descricao...: {descricao}
-- ========================================================================

CREATE OR REPLACE PROCEDURE `sp.prc_load_tb_{nome_tabela}`(
    VAR_PRJ_RAW STRING,
    VAR_PRJ_RAW_CUSTOM STRING,
    VAR_PRJ_TRUSTED STRING,
    VAR_PRJ_REFINED STRING,
    VAR_PRJ_SENSITIVE_RAW STRING,
    VAR_PRJ_SENSITIVE_TRUSTED STRING,
    VAR_PRJ_SENSITIVE_REFINED STRING
)
BEGIN

    -- Parametros usados para tabela de controle e log
    DECLARE VAR_PROCEDURE  DEFAULT 'prc_load_tb_{nome_tabela}';
    DECLARE VAR_DELTA_INI  DATE;
    DECLARE VAR_DELTA_FIM  DATE;
    DECLARE VAR_TABELA     STRING;
    DECLARE VAR_DTH_INICIO TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

    -- Inicio do bloco de TRY/CATCH (tratamento de erros)
    BEGIN

        -- Recupera parametros da TB_AUX_CONFIG_CARGA_BUS
        CALL sp.prc_get_params(VAR_PROCEDURE, VAR_DELTA_INI, VAR_DELTA_FIM, VAR_TABELA);

        BEGIN TRANSACTION;

            -- Criação da tabela temporária com dados da RAW do período
            EXECUTE IMMEDIATE """
                CREATE TEMP TABLE temp_tb_{nome_tabela} AS
                SELECT
                    id_chave_primaria,
                    campo_1,
                    campo_2,
                    campo_3,
                    CAST(""" || VAR_DELTA_FIM || """ AS DATE) AS dt_carga
                FROM `""" || VAR_PRJ_RAW || """.{dataset_origem}.{tabela_origem}`
                WHERE
                    -- Filtro por data delta
                    DATE({campo_delta}) BETWEEN """ || VAR_DELTA_INI || """ AND """ || VAR_DELTA_FIM || """
                    AND id_chave_primaria IS NOT NULL
            """;

            -- DELETE dos registros do período (idempotência)
            EXECUTE IMMEDIATE """
                DELETE FROM `""" || {var_projeto} || """.""" || VAR_TABELA || """` target
                WHERE
                    DATE(target.{campo_delta}) BETWEEN """ || VAR_DELTA_INI || """ AND """ || VAR_DELTA_FIM || """
            """;

            -- INSERT dos dados novos/atualizados
            EXECUTE IMMEDIATE """
                INSERT INTO `""" || {var_projeto} || """.""" || VAR_TABELA || """` (
                    id_chave_primaria,
                    campo_1,
                    campo_2,
                    campo_3,
                    dt_carga
                )
                SELECT
                    id_chave_primaria,
                    campo_1,
                    campo_2,
                    campo_3,
                    dt_carga
                FROM temp_tb_{nome_tabela}
            """;

            -- Log de sucesso
            CALL sp.prc_log_exec_transaction(VAR_TABELA, VAR_DTH_INICIO, @@row_count, VAR_PROCEDURE, @@error.message, {var_projeto});
            COMMIT TRANSACTION;

    EXCEPTION WHEN ERROR THEN
        ROLLBACK TRANSACTION;
        CALL sp.prc_log_exec_transaction(VAR_TABELA, VAR_DTH_INICIO, @@row_count, VAR_PROCEDURE, @@error.message, {var_projeto});
        RAISE USING MESSAGE = @@error.message;

    END;

END;

VARIÁVEIS ADICIONAIS PARA INCREMENTAL:

{campo_delta}: Valor do campo "Campo Delta"
{faixa_delta_ini}: Primeiro número de "Faixa Delta" (ex: -1)
{faixa_delta_fim}: Segundo número de "Faixa Delta" (ex: 0)

================================================================================
CHECKLIST - CÓDIGO SQL DA PROCEDURE
================================================================================

- ✅ Nome procedure: prc_load_tb_{nome_tabela} (exato)
- ✅ Declaração: CREATE OR REPLACE PROCEDURE
- ✅ Sem projeto fixo no código (usar variáveis)
- ✅ VAR_PROCEDURE com nome correto
- ✅ BEGIN TRANSACTION presente
- ✅ COMMIT TRANSACTION presente
- ✅ EXCEPTION WHEN ERROR com ROLLBACK
- ✅ Tabela temporária: temp_tb_{nome_tabela}
- ✅ TRUNCATE/DELETE antes de INSERT
- ✅ Comentários em cada EXECUTE IMMEDIATE
- ✅ Log com prc_log_exec_transaction
- ✅ Converter todos os campos usando CAST
- ❌ Nao pode usar conversoes com SAFE_CAST

================================================================================
ARQUIVO 2: PLANO DE EXECUÇÃO - execution_plan.yaml
================================================================================

TEMPLATE - Carga FULL:

# ========================================================================
# Objeto......: execution_plan.yaml
# Tabela......: tb_{nome_tabela}
# Camada......: {projeto}
# Version.....: 0.0.1
# Criacao.....: {data_criacao}
# ========================================================================

identifiers:
  gb-iniciativa: {iniciativa}

resource:
  dev:
    project_id: {sandbox_dev}
    dataset_id: sp
    config:
      des_processo: prc_load_tb_{nome_tabela}
      des_dataset: {dataset}
      des_tabela_destino: tb_{nome_tabela}
      des_frequencia: {frequencia}
      des_tipo_delta: FULL
      des_campo_delta: null
      vlr_faixa_delta_inicio: null
      vlr_faixa_delta_fim: null
    params:
      raw_zone: {sandbox_dev}
      raw_custom_zone: {sandbox_dev}
      trusted_zone: {sandbox_dev}
      refined_zone: {sandbox_dev}
      sensitive_raw: {sandbox_dev}
      sensitive_trusted: {sandbox_dev}
      sensitive_refined: {sandbox_dev}

  prd:
    project_id: {projeto}
    dataset_id: sp
    config:
      des_processo: prc_load_tb_{nome_tabela}
      des_dataset: {dataset}
      des_tabela_destino: tb_{nome_tabela}
      des_frequencia: {frequencia}
      des_tipo_delta: FULL
      des_campo_delta: null
      vlr_faixa_delta_inicio: null
      vlr_faixa_delta_fim: null
    params:
      raw_zone: raw-zone-005
      raw_custom_zone: raw-custom-zone
      trusted_zone: trusted-zone
      refined_zone: refined-zone
      sensitive_raw: sensitive-raw
      sensitive_trusted: sensitive-trusted
      sensitive_refined: sensitive-refined

---

TEMPLATE - Carga INCREMENTAL:

# ========================================================================
# Objeto......: execution_plan.yaml
# Tabela......: tb_{nome_tabela}
# Camada......: {projeto}
# Version.....: 0.0.1
# Criacao.....: {data_criacao}
# ========================================================================

identifiers:
  gb-iniciativa: {iniciativa}

resource:
  dev:
    project_id: {sandbox_dev}
    dataset_id: sp
    config:
      des_processo: prc_load_tb_{nome_tabela}
      des_dataset: {dataset}
      des_tabela_destino: tb_{nome_tabela}
      des_frequencia: {frequencia}
      des_tipo_delta: MERGE
      des_campo_delta: {campo_delta}
      vlr_faixa_delta_inicio: {faixa_delta_ini}
      vlr_faixa_delta_fim: {faixa_delta_fim}
    params:
      raw_zone: {sandbox_dev}
      raw_custom_zone: {sandbox_dev}
      trusted_zone: {sandbox_dev}
      refined_zone: {sandbox_dev}
      sensitive_raw: {sandbox_dev}
      sensitive_trusted: {sandbox_dev}
      sensitive_refined: {sandbox_dev}

  prd:
    project_id: {projeto}
    dataset_id: sp
    config:
      des_processo: prc_load_tb_{nome_tabela}
      des_dataset: {dataset}
      des_tabela_destino: tb_{nome_tabela}
      des_frequencia: {frequencia}
      des_tipo_delta: MERGE
      des_campo_delta: {campo_delta}
      vlr_faixa_delta_inicio: {faixa_delta_ini}
      vlr_faixa_delta_fim: {faixa_delta_fim}
    params:
      raw_zone: raw-zone-005
      raw_custom_zone: raw-custom-zone
      trusted_zone: trusted-zone
      refined_zone: refined-zone
      sensitive_raw: sensitive-raw
      sensitive_trusted: sensitive-trusted
      sensitive_refined: sensitive-refined

================================================================================
CHECKLIST - EXECUTION PLAN YAML
================================================================================

- ✅ gb-iniciativa preenchido no formato inicXXXX
- ✅ Dois ambientes: dev e prd
- ✅ project_id correto para ambiente
- ✅ des_processo = nome da procedure
- ✅ des_dataset = nome do dataset
- ✅ des_tabela_destino = nome da tabela
- ✅ des_tipo_delta = FULL ou MERGE
- ✅ Se MERGE, campos delta preenchidos
- ✅ Todos os params preenchidos
- ✅ Valor null para campos não aplicáveis

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
   ❌ Rejeitar se não tiver prefixo

3. TIPO DE CARGA
   ❌ DEVE ser "FULL" ou "INCREMENTAL"
   ❌ Rejeitar outros valores

4. CAMPO DELTA
   ❌ Se FULL: DEVE ser "null"
   ❌ Se INCREMENTAL: NÃO PODE ser "null"

5. FAIXA DELTA
   ❌ Se FULL: DEVE ser "null"
   ❌ Se INCREMENTAL: formato "-N a 0"

6. INICIATIVA
   ❌ Formato obrigatório: "inicXXXX"
   ❌ Exatamente 4 dígitos

7. SQUAD/TIME
   ❌ Apenas: eng, dataops, arq, ml, bi, plat

SE QUALQUER BLOQUEADOR FALHAR:

NUNCA prossiga com a geração da Procedure.

Retorne:

❌ VALIDAÇÃO FALHOU - GERAÇÃO NÃO POSSÍVEL

[Lista clara dos campos inválidos com valores esperados]

[Solicitação para corrigir antes de prosseguir]

================================================================================
EXEMPLOS COMPLETOS
================================================================================

EXEMPLO 1: Trusted Zone - FULL Load - prc_load_tb_terminal

Entrada do Usuário (12 campos obrigatórios):

Projeto: trusted-zone
Dataset: casa_magalhaes
Tabela: tb_terminal
Tipo de Carga: FULL
Frequência: DIARIO
Campo Delta: null
Faixa Delta: null
Iniciativa: inic1234
Origem dos Dados: raw_linx.ljv_terminal
Descrição: Tabela que centraliza dados de terminais de ponto de venda com 
informações técnicas de suporte e integração de sistemas
Squad/Time: eng
Sandbox Dev: sandbox-casa-magalhaes

Validação: ✅ TODOS OS CAMPOS VÁLIDOS

Arquivos Gerados:

1. prc_load_tb_terminal.sql
2. execution_plan.yaml

---

EXEMPLO 2: Sensitive-Trusted - INCREMENTAL Load - prc_load_tb_lead_optin

Entrada do Usuário (12 campos obrigatórios):

Projeto: sensitive-trusted
Dataset: saloes
Tabela: tb_lead_optin
Tipo de Carga: INCREMENTAL
Frequência: DIARIO
Campo Delta: dt_hr_atualizacao
Faixa Delta: 1
Iniciativa: inic1028
Origem dos Dados: sensitive-raw.raw_saloes.tbl_lead_optin
Descrição: Tabela com dados de leads e seu status de opt-in para comunicações, 
contendo informações sensíveis de contato
Squad/Time: dataops
Sandbox Dev: ssbx-saloes-profissinaisblz

Validação: ✅ TODOS OS CAMPOS VÁLIDOS

Arquivos Gerados:

1. prc_load_tb_lead_optin.sql
2. execution_plan.yaml

---

EXEMPLO 3: Validação Falha - Projeto Inválido

Entrada do Usuário:

Projeto: refined-zone
Dataset: casa_magalhaes
Tabela: tb_terminal
Tipo de Carga: FULL
Frequência: DIARIO
Campo Delta: null
Faixa Delta: null
Iniciativa: inic1234
Origem dos Dados: raw_linx.ljv_terminal
Descrição: Tabela que centraliza dados de terminais
Squad/Time: eng
Sandbox Dev: sandbox-casa-magalhaes

Resultado:

❌ VALIDAÇÃO FALHOU - GERAÇÃO NÃO POSSÍVEL

| # | Campo | ❌ Fornecido | ✅ Esperado | 📝 Ação |
|---|-------|-------------|-----------|---------|
| 1 | Projeto | refined-zone | trusted-zone ou sensitive-trusted | Projeto não permitido para esta skill |

⚠️ Resumo:
- Status: ❌ NÃO POSSÍVEL GERAR
- Motivo: Projeto "refined-zone" não é válido para criação de Procedure
- Projetos aceitos: trusted-zone, sensitive-trusted

================================================================================
FORMATO DE RESPOSTA FINAL - PROCEDURE
================================================================================

Quando validação é ✅ APROVADA:

RESPOSTA ESTRUTURADA:

## ✅ Validação Aprovada - Gerando Procedure

### Resumo da Entrada
| Campo | Valor |
|-------|-------|
| Projeto | trusted-zone |
| Dataset | casa_magalhaes |
| Tabela | tb_terminal |
| Tipo de Carga | FULL |
| Frequência | DIARIO |
| Iniciativa | inic1234 |
| Squad/Time | eng |

**Status**: ✅ PRONTO PARA GERAÇÃO

### Estrutura de Diretórios a Criar

bigquery/
└── procedure/
    └── eng/
        └── trusted-zone/
            └── prc_load_tb_terminal/
                ├── prc_load_tb_terminal.sql
                └── execution_plan.yaml

### Arquivo 1: prc_load_tb_terminal.sql

[Código SQL completo aqui]

### Arquivo 2: execution_plan.yaml

[YAML completo aqui]

### ✅ Checklist - Código SQL
- ✅ Nome: prc_load_tb_terminal
- ✅ Camada: trusted-zone
- ✅ BEGIN/COMMIT TRANSACTION presente
- ✅ EXCEPTION WHEN ERROR com ROLLBACK
- ✅ Temp table: temp_tb_terminal
- ✅ TRUNCATE before INSERT (FULL Load)

### ✅ Checklist - Execution Plan
- ✅ gb-iniciativa: inic1234
- ✅ Ambientes: dev e prd
- ✅ des_tipo_delta: FULL
- ✅ Todos os params preenchidos
- ✅ YAML válido

### 📋 Próximas Etapas para Deploy

1. Clone o Repositório
   git clone https://github.com/grupoboticario/data-platform-bigquery.git
   cd data-platform-bigquery

2. Crie a Branch
   git checkout -b feature/prc-load-tb-terminal

3. Crie os Diretórios
   mkdir -p bigquery/procedure/eng/trusted-zone/prc_load_tb_terminal

4. Copie os Arquivos
   cp prc_load_tb_terminal.sql bigquery/procedure/eng/trusted-zone/prc_load_tb_terminal/
   cp execution_plan.yaml bigquery/procedure/eng/trusted-zone/prc_load_tb_terminal/

5. Commit e Push
   git add .
   git commit -m "[PROC] Add prc_load_tb_terminal for casa_magalhaes
   
   - Type: FULL Load
   - Frequency: Daily
   - Initiative: inic1234
   - Source: raw_linx.ljv_terminal
   "
   git push origin feature/prc-load-tb-terminal

6. Abra Pull Request
   - Descrição: Inclua contexto de negócio
   - Labels: procedure, trusted-zone, load

================================================================================
FLUXO COMPLETO: DDL → PROCEDURE
================================================================================

ORDEM DE EXECUÇÃO OBRIGATÓRIA:

1️⃣  CRIAR DDL (tb_*.sql)
    - Valida 5 campos principais
    - Gera arquivo da tabela
    - Pronto para criação de estrutura no BigQuery

2️⃣  CRIAR PROCEDURE (prc_load_tb_*.sql + execution_plan.yaml)
    - Valida 12 campos completos
    - Depende da DDL já criada
    - Gera dois arquivos: procedure SQL + plano de execução

EXEMPLO COMPLETO DE FLUXO:

Passo 1: Gerar DDL para tb_terminal
├─ Entrada: Projeto, Dataset, Tabela, Squad, Descrição
├─ Saída: bigquery/table/eng/trusted-zone/casa_magalhaes/tb_terminal/tb_terminal.sql
└─ Status: ✅ DDL Criada

Passo 2: Gerar Procedure para prc_load_tb_terminal
├─ Entrada: Todos os 12 campos (incluindo referência à DDL criada)
├─ Saída: 
│   ├─ bigquery/procedure/eng/trusted-zone/prc_load_tb_terminal/prc_load_tb_terminal.sql
│   └─ bigquery/procedure/eng/trusted-zone/prc_load_tb_terminal/execution_plan.yaml
└─ Status: ✅ Procedure Criada

Passo 3: Deploy no Git
├─ Criar branch para feature
├─ Commitar ambos os arquivos (DDL + Procedure)
├─ Abrir Pull Request com documentação
└─ Status: ✅ Pronto para Merge

================================================================================
FIM DO DOCUMENTO - PROCEDURE CREATION SKILL
================================================================================
