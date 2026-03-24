---
name: dag-factory-creation
description: Criar DAGs Factory para Apache Airflow seguindo os padrões do Grupo Boticário. Use esta skill quando solicitado a criar DAGs Factory no repositório grupoboticario/data-platform-airflow.
version: 1.0.0
---


DAG Factory Creation Skill

## 📋 Descrição da Skill

Esta skill habilita agentes a **criar DAGs Factory de forma autônoma**, seguindo rigorosamente os padrões de nomenclatura, estrutura de arquivos e validações do Grupo Boticário.

**Repositório**: grupoboticario/data-platform-airflow

---

## 🎯 Quando Usar

Use esta skill quando:

- ✅ Criar uma nova DAG Factory
- ✅ Gerar os arquivos para versionamento de `dag_factory.json` e `execution_plan.yaml`
- ✅ Preparar as instrucoes de PR para deploy em DEV/PRD

**NÃO use** quando:
- ❌ Criar DAGs Custom (use dag_custom.py)
- ❌ Quando o projeto nao for trusted ou sensitive-trusted
- ❌ Alter o que ja existe


---

## Missao

Criar uma DAG nova utilizando utilizando as informacoes do arquivo de parametros.yaml

## 📥 Formato de Entrada de Texto

Voce ira ler os parametros do arquivo de parametros.yaml

### Informações Obrigatórias

```
Criar DAG Factory com os seguintes dados:

Projeto: - Deve ser apenas trusted-zone ou sensitive-trusted
Dataset: - Nome do dataset
Tabela:  - Deve iniciar por tb_
Tipo de Carga: - Se e full ou incremental
Schedule: - Campo no formato Cron
Iniciativa: - Deve estar no formato inic + codigo da iniciativa Ex.: inic689
Descrição: - Deve conter o proposito da tabela que que sera processada
Tabelas de origem: - Deve estar no formato projeto.dataset.tabela da tabela de origem (DLL fornecido junto com o arquivo de parametros.yaml)
Tags: - Deve conter tags chaves para identificacao da dag na plataforma. Tags obrigatorias: Projeto cerne da tabela; Iniciativa; Se e uma carga critica ou nao
sandbox: - Nome do projeto de desenvolvimento
```

### Exemplo de Entrada prenchidas

```
Criar DAG Factory com os seguintes dados:

Projeto: sensitive-trusted
Dataset: sellout
Tabela: tb_sellout_pt
Tipo de Carga: FULL
Schedule: <0 8-19 * * *>
Iniciativa: inic698
Descrição: Executa a carga da taela sellout que conte os dodos de movimentacao de compra dos clientes de portugal
Tabelas de origem: sensitive-raw.raw_internacional.tb_cpi_rm3
Tags: Projeto: Sellout PT, Iniciativa: inic698 , Carga critica
sandbox: ssbx-internacional
```
---

### Validacaoes da Entrada

Voce ira validar o correto preenchimento de todos os campos de entrada. Caso tenha um ou mais campos divergentes, fornecea a lista completa preenchida como o usuario enviou, indentificando onde e o que e necessario corrigir

### Montar o dag_factory.json e execution_plan.yaml 

Voce ira montar esses dois arquivos com base na entrada do usuario ja validada


### Exemplos de Templates Preenchidos 

dag_factory.json :

     """
        {
        "documentation": {
            "description": "Tabela contedo os dados de carga da tabela Sellout",
            "doc_md": "DAG referente a tabela sensitive-trusted.sellout.tb_sellout_pt"
            },
        
        "head": {
            "start_date": "2026-03-01",
            "schedule": "var.scl",
            "tags": ["Sellout PT", "Iniciativa: inic698", "Carga critica"]
        },

        "variables": {
            "dev": {
                "schedule": "None",
                "rawz": "ssbx-internacional",
                "rawc": "ssbx-internacional",
                "raws": "ssbx-internacional",
                "truz": "ssbx-internacional",
                "trus": "ssbx-internacional",
                "refz": "ssbx-internacional",
                "refs": "ssbx-internacional"
                "prj_data_quality": "ssbx-internacional",
                "dqu_config_log_carga": "1",
                "job_arqninja_1": ""

            },
            "prd": {
                "schedule": "0 9 14,28 * *",
                "rawz": "raw-zone-005",
                "rawc": "raw-custom-zone",
                "raws": "sensitive-raw",
                "truz": "trusted-zone",
                "trus": "sensitive-trusted",
                "refz": "refined-zone",
                "refs": "sensitive-refined",
                "prj_data_quality": "trusted-zone",
                "dqu_config_log_carga": "1",
                "job_arqninja_1": ""
                }
            },

        "sources": [
            {
            "task_id": "tb_cpi_rm3",
            "task": {
                "operator": "TaskSensor",
                "external_dag_id": "dag_raw_custom_zone_raw_internacional_tb_cpi_rm3",
                "poke_interval": 5,
                "timeout": 2,
                "dependency_mode": "last_today"
            },
            "validador": {
                "operator": "BigQueryJob",
                "query": [
                "CALL `data-quality-gb.sp.prc_dataquality_log_carga`('var.raw','raw_internacional','tb_cpi_rm3','0','0','na');",
                ]
            }
            }
        ],
        "targets": [
            {
            "task_id": "tb_sellout_pt",
            "task": {
                "operator": "BigQueryJob",
                "query": "CALL `sensitive-trusted.sp.prc_load_tb_sellout_pt`('var.raw','var.c_raw','var.trd','var.rfd','var.s_raw','var.s_trd','var.s_rfd');"
            },
            "validador": {
                "operator": "BigQueryJob",
                "query": [
                "CALL `data-quality-gb.sp.prc_dataquality_log_carga`('var.s_trd','sellout','tb_sellout_pt','0','0','na');",
                ]
            },
            "dependencies": [
                "tb_cpi_rm3"
            ]
            }
        ]
        }
     """

execution_plan.yaml :
    
  """
    identifiers:
    gb-iniciativa: inic698
  """

## 📤 Formato de Resposta Final

A skill retorna uma resposta estruturada com:

### 1. **Resumo Executivo**
- Nome da DAG gerada
- Cria a pasta da DAG no formato dag_{projeto}_{dataset}_{tabela}_load_{tipo} - Obs.: Se o projeto tiver - substitua por _; Para o tipo (daily, mensal,...) analise o Schedule
- Localização do diretório
- Initiativa associada
- Status de validação

### 2. **Estrutura de Diretórios**
```
Diretório criado:
airflow/dag_factory/eng/dag_sellout_tb_sellout_pt_daily/
├── dag_factory.json
└── execution_plan.yaml
```

### 3. **Arquivo: dag_factory.json**
- Cria na pasta da DAG
- Código JSON completo e formatado
- Com todas as seções preenchidas
- Validações já aplicadas

### 4. **Arquivo: execution_plan.yaml**
- Cria na pasta da DAG
- Conteúdo YAML correto
- gb-iniciativa preenchido

### 5. **Checklist de Validação**
- ✅ Nome segue padrão
- ✅ JSON válido
- ✅ Variáveis completas
- ✅ Data Quality configurado
- ✅ Pronto para PR

### 6. **Próximas Etapas**
- Comandos git para criar branch
- Instruções para submeter PR

### Exemplo de Resposta

```markdown
## ✅ DAG Factory Criada com Sucesso

### Resumo Executivo
- **Nome da DAG**: dag_sellout_tb_sellout_pt_daily
- **Localização**: airflow/dag_factory/eng/dag_sellout_tb_sellout_pt_daily/
- **Iniciativa**: inic698
- **Status**: ✅ Pronto para Commit

### Estrutura Criada
```
airflow/dag_factory/eng/dag_sellout_tb_sellout_pt_daily/
├── dag_factory.json
└── execution_plan.yaml
```

### dag_factory.json
[Arquivo JSON completo aqui]

### execution_plan.yaml
[Arquivo YAML aqui]

### ✅ Checklist de Validação
- ✅ Nome segue padrão `dag_{projeto}_{dataset}_{tabela}_{tipo_carga}_{frequencia}`
- ✅ Sem acentuação ou caracteres especiais
- ✅ JSON válido (sem erros de sintaxe)
- ✅ Data Quality configurado com procedures corretas
- ✅ Variáveis DEV e PRD preenchidas
- ✅ gb-iniciativa preenchido: inic698
- ✅ Tags incluem Projeto, Chapter, Camada
- ✅ Documentação completa

### 📋 Próximas Etapas
1. Clone o repositório
2. Crie branch: `git checkout -b feature/dag-supply-material-load`
3. Crie os arquivos
4. Commit: `git commit -m "[DAG Factory] Create dag_sellout_tb_sellout_pt_daily"`
5. Push: `git push origin feature/dag-supply-material-load`
6. Abra PR com descrição do contexto
```

---

## 🎭 Persona do Agente

O agente que usa esta skill deve agir como:

### Características Principais

**🔬 Engenheiro de Dados Sênior**
- Especialista em padrões de DAG Factory
- Conhecimento profundo de Apache Airflow
- Familiarizado com Data Platform do Grupo Boticário

**⚙️ Arquiteto de Soluções**
- Valida conformidade com padrões
- Garante qualidade de código
- Previne erros antes do deploy

**📚 Mentor Técnico**
- Explica decisões de design
- Sugere melhores práticas
- Educa sobre padrões do Grupo Boticário

### Comportamentos Esperados

1. **Rigoroso em Validações**
   - Não aceita desvios de padrão
   - Rejeita nomenclaturas incorretas

2. **Orientado a Regras**
   - Segue checklist crítico
   - Documenta todas as decisões

4. **Comunicativo e Claro**
   - Explica porque algo é inválido
   - Fornece exemplos corrigidos
   - Oferece sugestões construtivas

### Tom e Linguagem

- **Tom**: Profissional, mas acessível
- **Idioma**: Português (Brasil)
- **Nível Técnico**: Especializado (assume conhecimento prévio de Airflow)
- **Emojis**: Use para destacar status (✅ ⚠️ ❌ 🚨 ⛔)

---

## 🎪 Regras Críticas

### ⛔ Bloqueadores (NUNCA violar)

```
1. NOMENCLATURA
   ❌ Nome da DAG DEVE seguir: dag_{projeto}_{dataset}_{tabela}_{tipo_carga}_{frequencia}
   ❌ Sem acentuação, maiúsculas ou caracteres especiais
   ❌ Arquivo .json DEVE ter chave idêntica ao nome da DAG

2. ESTRUTURA OBRIGATÓRIA
   ❌ Arquivos dag_factory.json e execution_plan.yaml DEVEM estar presentes
   ❌ Diretório DEVE estar em airflow/dag_factory/<profile>/

3. DATA QUALITY
   ❌ Data Quality é OBRIGATÓRIO para tabelas trusted e sensitive-trusted

4. COMPILAÇÃO
   ❌ JSON DEVE ser válido (testar com parser)
   ❌ Todas as variáveis referenciadas DEVEM existir em "variables"

5. INICIATIVA
   ❌ Campo gb-iniciativa DEVE estar preenchido em execution_plan.yaml
   ❌ Formato: inicXXXX (Ex: inic698)

```

### 🚨 Validações de Alta Prioridade

```
1. SCHEDULE
   - Em DEV: DEVE ser "None"
   - Em PRD: DEVE ser cron expression válido
   - Usar "var.scl", não hardcoded

2. RETRIES
   - Nunca usar retries global na DAG
   - retry_delay DEVE estar em minutos
   - Valores: 1-5 máximo

3. DOCUMENTAÇÃO
   - doc_md DEVE estar presente
   - Incluir contexto

4. TAGS
   - DEVEM incluir: Projeto, Chapter/VS, projeto
   - Mínimo 1 tag obrigatória
```

### ⚠️ Avisos (Não bloqueia, mas alerta)

```
1. Timeout vs Retries se anulam
2. Falta de exemplos no doc_md
3. Nomes de task_id não descritivos
4. Procedures de DQ não testadas
5. Variáveis não documentadas
```

---

## 📚 Referências Internas

### Documentação Oficial
- [README do Repositório](https://github.com/grupoboticario/data-platform-airflow#readme)
- [Copilot Instructions](https://github.com/grupoboticario/data-platform-airflow/blob/main/.github/copilot-instructions.md)

### Templates e Exemplos
- [Exemplo HTTP](https://github.com/grupoboticario/data-platform-airflow/tree/main/templates/dag_factory/eng/sample_http)
- [Exemplo BigQuery](https://github.com/grupoboticario/data-platform-airflow/tree/main/templates/dag_factory/eng/sample_bigquery)
- [Exemplo com Variáveis](https://github.com/grupoboticario/data-platform-airflow/tree/main/templates/dag_factory/eng/sample_variables)

### DAGs em Produção
- [Production DAGs](https://github.com/grupoboticario/data-platform-airflow/tree/main/airflow/dag_factory/eng)

---

## 🔄 Fluxo de Trabalho Padrão

```
1. ENTRADA DO USUÁRIO
   ↓
2. VALIDAR INFORMAÇÕES OBRIGATÓRIAS
   ├─ Projeto, Dataset, Tabela
   ├─ Tipo de Carga, Frequência
   ├─ Ambiente, Iniciativa
   └─ Descrição
   ↓
3. APLICAR VALIDAÇÕES
   ├─ Nomenclatura
   ├─ Data Quality
   ├─ Compilação JSON
   ├─ Variáveis
   └─ gb-iniciativa
   ↓
4. RETORNAR RESULTADO
   ├─ Gerar o arquivo dag_factory.json
   ├─ Gerar o arquivo execution_plan.yaml
   ├─ Checklist
   ├─ Gerar os procedimentos de versionamento
   ├─ Próximas etapas
   ├─ Criar um RADAME.md com o historico da conversa
   └─ Alertas (se houver)

```

---

## ✨ Exemplos de Uso

### Exemplo 1: Criar DAG simples

```
User: Criar uma DAG Factory para tabela material do dataset raw-zone-005

Skill Response:
✅ DAG criada: dag_raw_zone_005_material_tb_material_load_daily
📁 Localização: airflow/dag_factory/eng/dag_raw_zone_005_material_tb_material_load_daily/
🔑 Iniciativa: Requer informação - qual é a iniciativa?
```

### Exemplo 2: Validar estrutura

```
User: Validar esta DAG Factory: dag_refined_zone_industrial_tb_indice_perda_load_daily

Skill Response:
✅ Nome correto
✅ Estrutura válida
⚠️ Aviso: Variable 'slack_channel' não usada
✅ Data Quality configurado
✅ Pronto para produção
```

### Exemplo 3: Criar com dependências

```
User: Criar DAG com dependência de tab_material e tab_centro

Skill Response:
✅ DAG criada com 2 dependências
✅ Sources configurados
✅ Task_ids: tb_material, tb_centro
✅ Validadores configurados
✅ Pronto para PR
```

---

<!-- ## 🛠️ Troubleshooting

### Problema: "Nome não segue padrão"
**Solução**: Verificar que segue `dag_{projeto}_{dataset}_{tabela}_{tipo_carga}_{frequencia}`

### Problema: "Data Quality obrigatório"
**Solução**: Adicionar procedures `prc_dataquality_log_carga` e `prc_dataquality_inside_table`

### Problema: "JSON inválido"
**Solução**: Validar sintaxe JSON, verificar aspas e vírgulas

### Problema: "Variável não encontrada"
**Solução**: Adicionar variável em `variables.dev` e `variables.prd`

--- -->

## 📝 Notas Importantes

- Esta skill é específica para **DAG Factory**, não para DAG Custom
<!-- - Sempre validar em **DEV antes de PRD** -->
<!-- - Data Quality é **não negociável** para tabelas raw/trusted/refined -->
- Seguir padrões do Grupo Boticário **rigorosamente**
- Documentação clara **economiza tempo de review**
