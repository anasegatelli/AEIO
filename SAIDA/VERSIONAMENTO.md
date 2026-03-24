# Versionamento dos Artefatos - Data Platform Grupo Boticário

Este arquivo contém os comandos necessários para versionar (git add, commit e push) todos os artefatos gerados neste fluxo.

## Estrutura dos Artefatos

```
airflow/dag_factory/eng/dag_sensitive_trusted_sellout_tb_fato_categoria_full_monthly/dag_factory.json
airflow/dag_factory/eng/dag_sensitive_trusted_sellout_tb_fato_categoria_full_monthly/execution_plan.yaml
bigquery/procedure/eng/sensitive-trusted/prc_load_tb_fato_categoria/prc_load_tb_fato_categoria.sql
bigquery/procedure/eng/sensitive-trusted/prc_load_tb_fato_categoria/execution_plan.yaml
bigquery/table/eng/sensitive-trusted/sellout/tb_fato_categoria/tb_fato_categoria.sql
bigquery/table/eng/sensitive-trusted/sellout/tb_fato_categoria/execution_plan.yaml
validador_dados/eng/sensitive-trusted/sellout/tb_fato_categoria/tb_fato_categoria.yaml
validador_dados/eng/sensitive-trusted/sellout/tb_fato_categoria/README.md
```

## Comandos para Versionamento

### 1. Inicialize o repositório (se necessário)
```sh
git init
```

### 2. Adicione todos os arquivos gerados
```sh
git add airflow/dag_factory/eng/dag_sensitive_trusted_sellout_tb_fato_categoria_full_monthly/dag_factory.json
git add airflow/dag_factory/eng/dag_sensitive_trusted_sellout_tb_fato_categoria_full_monthly/execution_plan.yaml
git add bigquery/procedure/eng/sensitive-trusted/prc_load_tb_fato_categoria/prc_load_tb_fato_categoria.sql
git add bigquery/procedure/eng/sensitive-trusted/prc_load_tb_fato_categoria/execution_plan.yaml
git add bigquery/table/eng/sensitive-trusted/sellout/tb_fato_categoria/tb_fato_categoria.sql
git add bigquery/table/eng/sensitive-trusted/sellout/tb_fato_categoria/execution_plan.yaml
git add validador_dados/eng/sensitive-trusted/sellout/tb_fato_categoria/tb_fato_categoria.yaml
git add validador_dados/eng/sensitive-trusted/sellout/tb_fato_categoria/README.md
```

### 3. Crie uma branch para a feature (ajuste o nome conforme sua convenção)
```sh
git checkout -b feature/sensitive-trusted-sellout-tb-fato-categoria
```

### 4. Commit com mensagem detalhada
```sh
git commit -m "[PLATAFORMA-DADOS] Criação dos artefatos tb_fato_categoria

- DDL e execution_plan.yaml
- Procedure de carga e execution_plan.yaml
- DAG Factory (dag_factory.json e execution_plan.yaml)
- Validador YAML
- Contexto: Sensitive-Trusted/Sellout/tb_fato_categoria
"
```

### 5. Push para o repositório remoto
```sh
git push origin feature/sensitive-trusted-sellout-tb-fato-categoria
```

### 6. Abra um Pull Request
- Descrição: Detalhe o contexto de negócio, origem dos dados, time responsável e iniciativa (inic).
- Labels: table, procedure, dag, validador, sensitive-trusted, sellout

---

**Checklist Final**
- [ ] Todos os arquivos adicionados
- [ ] Branch criada corretamente
- [ ] Mensagem de commit clara e padronizada
- [ ] Push realizado
- [ ] Pull Request aberto
