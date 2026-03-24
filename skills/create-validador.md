---
name: dag-factory-validador-creation
description: Criar arquivos de validador em YAML para Data Quality seguindo padrão owner + production_table + sandbox_table + checks.
version: 1.1.0
---


DAG Factory Validador Creation Skill

## 📋 Descrição da Skill

Esta skill habilita agentes a **criar validadores em YAML de forma autônoma**, seguindo o padrão de saída com `owner`, `production_table`, `sandbox_table` e lista de `checks`.

**Contexto**: geração de arquivo de regras de validação para tabela de produção e sandbox, com rastreabilidade por iniciativa.

---

## 🎯 Quando Usar

Use esta skill quando:

- ✅ Criar um arquivo de validador novo
- ✅ Padronizar checks de qualidade com `rule_name` e `payload`
- ✅ Gerar saída final em YAML para versionamento
- ✅ Validar consistência entre tabela de produção e sandbox

**NÃO use** quando:
- ❌ Criar DAG Factory (use skill de DAG)
- ❌ Criar DDL ou Procedure
- ❌ Alterar validadores já existentes sem solicitação explícita

---

## Missão

Criar um arquivo de validador em YAML utilizando informações do `parametros.yaml` e/ou entrada textual do usuário, no formato padrão:

- `owner`
- `production_table`
- `sandbox_table`
- `checks`

---

## 📥 Formato de Entrada de Texto

Você irá ler os parâmetros do arquivo `parametros.yaml` ou da solicitação do usuário.

### Informações Obrigatórias

```
Criar Validador com os seguintes dados:

Owner: - E-mail corporativo válido
Sandbox Table: - Deve estar no formato projeto.dataset.tabela
Iniciativa: - Deve estar no formato inic + código. Ex.: inic717
Checks: - Não deve ser informado pelo usuário; deve ser gerado automaticamente

Production Table: - Não deve ser solicitada ao usuário; deve ser derivada automaticamente da tabela criada pelo agente no artefato de DDL

O agente deve gerar automaticamente o bloco checks com a regra emptyTable:
   __info__: Validade - se a tabela está vazia
   rule_name: emptyTable
   payload: {}
   initiative_id: deve repetir a iniciativa
```

### Exemplo de Entrada Preenchida

```
Owner: ana.segatelli@grupoboticario.com.br
Sandbox Table: ssbx-multib.b2b.tb_teste
Iniciativa: inic1500
Checks: (não informar - será gerado automaticamente)
        
```

---

## ✅ Validações da Entrada

Você irá validar o correto preenchimento de todos os campos de entrada. Caso exista um ou mais campos divergentes, retorne a lista completa preenchida pelo usuário com as correções necessárias.

### Regras Obrigatórias

1. `owner`
   - Deve ser e-mail corporativo válido
   - Formato mínimo: `nome.sobrenome@grupoboticario.com.br`

2. `production_table`
   - Não deve ser solicitado ao usuário
   - Deve ser derivado automaticamente a partir da tabela criada no DDL gerado pelo agente
   - Formato obrigatório: `projeto.dataset.tabela`
   - `tabela` deve iniciar com `tb_`

3. `sandbox_table`
   - Formato obrigatório: `projeto.dataset.tabela`
   - `tabela` deve iniciar com `tb_`
   - Deve ser a mesma tabela lógica da `production_table`

4. `checks`
   - Não deve ser solicitado ao usuário
   - Deve ser gerado automaticamente pelo agente
   - Deve conter ao menos 1 item
   - Cada item deve conter: `__info__`, `rule_name`, `payload`, `initiative_id`

5. `initiative_id`
   - Formato obrigatório: `inicXXXX`
   - Deve ser idêntico em todos os checks

6. Regras com payload obrigatório
   - `emptyTable` deve usar `payload: {}`
   - `checks` deve ser montado automaticamente sem depender de entrada manual

### Geração automática de production_table

Para qualquer geração de validador, o agente deve montar `production_table` automaticamente com base no DDL gerado no fluxo atual.

Regra:
- usar o projeto e dataset de produção do contexto (trusted/sensitive-refined)
- usar exatamente o nome da tabela criada no DDL
- não solicitar este campo ao usuário

### Geração automática de checks

Para qualquer geração de validador, o agente deve sempre montar este bloco:

```yaml
checks:
  - __info__: Validade - se a tabela está vazia
    payload: {}
    rule_name: emptyTable
    initiative_id: <iniciativa informada>
```

---

## 🧱 Formato de Saída Obrigatório

O YAML final **deve seguir exatamente esta estrutura**:

```yaml
owner: ana.segatelli@grupoboticario.com.br
production_table: sensitive-refined.b2b.tb_tabela_teste
sandbox_table: ssbx-multib.b2b.tb_tabela_teste
checks:
  - __info__: Validade - se a tabela está vazia
    payload: {}
    rule_name: emptyTable
    initiative_id: inic1500

```

---

## 📤 Formato de Resposta Final

A skill retorna uma resposta estruturada com:

### 1. **Resumo Executivo**
- Nome do arquivo do validador
- Tabela de produção
- Tabela de sandbox
- Iniciativa
- Status de validação

### 2. **Estrutura de Diretórios**
```
Diretório criado:
validador_dados/eng/{projeto}/{dataset}/{tabela}/
├── {tabela}.yaml
└── README.md
```

### 3. **Arquivo YAML do Validador**
- Conteúdo YAML completo e formatado
- Com todos os checks validados

### 4. **Checklist de Validação**
- ✅ owner válido
- ✅ production_table válida
- ✅ sandbox_table válida
- ✅ checks preenchidos
- ✅ rule_name + payload consistentes
- ✅ initiative_id no padrão `inicXXXX`

### 5. **Próximas Etapas**
- Comandos git para branch/commit/push
- Orientação para PR

---

## 🎪 Regras Críticas

### ⛔ Bloqueadores (NUNCA violar)

```
1. ESTRUTURA YAML
   ❌ Não omitir owner, production_table, sandbox_table ou checks

2. FORMATO DE TABELA
   ❌ Não aceitar tabela fora do padrão projeto.dataset.tabela

3. INICIATIVA
   ❌ initiative_id deve estar em todos os checks
   ❌ Formato: inicXXXX

4. CHECKS
   ❌ Não gerar checks sem rule_name
   ❌ Não gerar checks com regras diferentes de emptyTable
   ❌ Não solicitar o bloco checks na entrada do usuário

5. PRODUCTION_TABLE
   ❌ Não solicitar production_table na entrada do usuário
   ❌ Não usar valor manual quando já existir DDL gerado no fluxo
```

### 🚨 Validações de Alta Prioridade

```
1. Consistência entre produção e sandbox
2. Tabela iniciando com tb_
3. owner com domínio corporativo
4. Pelo menos 1 check válido
5. YAML válido e bem formatado
6. rule_name deve ser apenas emptyTable
```

---

## 🔄 Fluxo de Trabalho Padrão

```
1. ENTRADA DO USUÁRIO
   ↓
2. VALIDAR CAMPOS OBRIGATÓRIOS
   ├─ owner
   ├─ sandbox_table
   └─ initiative_id
   ↓
3. DERIVAR PRODUCTION_TABLE DO DDL
   ↓
4. VALIDAR REGRAS POR CHECK
   └─ emptyTable
   ↓
5. GERAR YAML FINAL
   ├─ Conteúdo do arquivo
   ├─ Caminho de saída
   └─ Checklist
```

---

## 📝 Notas Importantes

- Esta skill é específica para **geração de YAML de validador**
- O agente deve priorizar simplicidade e consistência do formato
- Não misturar este artefato com bloco de `dag_factory.json`
- Sempre manter rastreabilidade por `initiative_id`