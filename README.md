# 🤖 AEIO - Agente Gerador de Artefatos de Engenharia de Dados

**AEIO** é um agente inteligente de IA que automatiza a geração de artefatos para pipelines de engenharia de dados, utilizando LLMs (Large Language Models) para criar DAGs, DDLs, procedures, validadores e documentação de forma inteligente e padronizada.

## 📋 Índice

- [Características](#características)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Uso](#uso)
- [Configuração](#configuração)
- [Artefatos Gerados](#artefatos-gerados)
- [Exemplo de Uso](#exemplo-de-uso)
- [Dependências Principais](#dependências-principais)

## ✨ Características

- **Geração de DAGs** - Cria automaticamente DAGs (Directed Acyclic Graphs) para orquestração de pipelines
- **Geração de DDLs** - Produz SQL DDL (Data Definition Language) otimizado para suas tabelas
- **Geração de Procedures** - Cria stored procedures para operações complexas no banco de dados
- **Validação de Dados** - Gera validadores automáticos para garantir qualidade dos dados
- **Padronização** - Aplica padrões de nomenclatura consistentes em todo o projeto
- **Integração com IA** - Utiliza OpenAI, Google Genai e modelos do Azure para geração inteligente
- **Suporte a Cloud** - Integração com Google Cloud (BigQuery, Secret Manager, Storage)

## 🔧 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- Conta na Azure OpenAI ou Google Cloud
- Variáveis de ambiente configuradas (.env)

## 📦 Instalação

1. **Clone o repositório**
   ```bash
   git clone <seu-repositorio>
   cd AEIO
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   ```

## 📁 Estrutura do Projeto

```
AEIO/
├── main.py                    # Script principal do agente
├── requirements.txt           # Dependências do projeto
├── README.md                  # Este arquivo
├── ENTRADA/                   # Diretório de entrada
│   ├── parametros.yaml        # Arquivo de configuração dos parâmetros
│   └── create_fact_category_ds_gc.sql  # Exemplo de SQL de entrada
├── SAIDA/                     # Diretório de saída (artefatos gerados)
│   └── [arquivos gerados pelo agente]
└── skills/                    # Instruções e padrões para IA
    ├── create-dag.md          # Skill para geração de DAGs
    ├── create-ddl.md          # Skill para geração de DDLs
    ├── create-procedure.md    # Skill para geração de Procedures
    ├── create-validador.md    # Skill para geração de Validadores
    └── padra-nomenclatura-tabela.md  # Padrões de nomenclatura
```

## 🚀 Uso

### 1. Configure os parâmetros de entrada

Edite o arquivo `ENTRADA/parametros.yaml` com as informações do seu projeto:

```yaml
Projeto: sensitive-trusted
Dataset: sellout
Tabela: tb_fato_categoria
Tipo de Carga: FULL
Schedule: "0 5 21 * *"
Campo Delta: 
Faixa Delta: 
Iniciativa: inic1500
Descrição: Executa a carga da tabela fato mercado
Tabela de origem: sensitive-raw.raw_iqvia.fact_category_ds_gc
Squad/Time: eng
Tags: Projeto:Sellout,Iqvia Iniciativa:inic1500
sandbox: ssbx-mulitb
owner: email@example.com
```

### 2. Adicione o SQL de entrada

Coloque seu arquivo SQL na pasta `ENTRADA/`:
```bash
ENTRADA/create_fato_tabela.sql
```

### 3. Execute o agente

```bash
python main.py
```

### 4. Recupere os artefatos gerados

Os arquivos gerados estarão na pasta `SAIDA/`:
```
SAIDA/
├── dag_tb_fato_categoria.py
├── ddl_tb_fato_categoria.sql
├── procedure_tb_fato_categoria.sql
├── validador_tb_fato_categoria.py
└── documentacao.md
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=sua-chave-api
AZURE_OPENAI_ENDPOINT=https://seu-recurso.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=seu-deployment

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=caminho/para/credenciais.json

# Configurações opcionais
LOG_LEVEL=INFO
DEBUG=False
```

## 📊 Artefatos Gerados

### DAG (Directed Acyclic Graph)
Arquivo Python com definição de pipeline no Airflow/Prefect com:
- Definição de tarefas
- Dependências entre tarefas
- Agendamento
- Tratamento de erros

### DDL (Data Definition Language)
Comando SQL com:
- Criação de tabelas
- Índices
- Partições
- Constraints
- Comentários

### Procedure (Stored Procedure)
Procedure SQL com:
- Lógica de transformação
- Tratamento de erros
- Logs de execução
- Validações

### Validador
Script Python com:
- Validações de qualidade de dados
- Verificação de integridade
- Alertas e relatórios
- Testes unitários

## 💡 Exemplo de Uso

```bash
# 1. Preparar estrutura inicial
python main.py

# 2. Editar parametros.yaml com seus dados
# ENTRADA/parametros.yaml

# 3. Executar geração automática
# O agente processará os parâmetros e SQL
# e gerará todos os artefatos

# 4. Revisar arquivos em SAIDA/
# Fazer ajustes conforme necessário
```

## 📚 Dependências Principais

| Biblioteca | Versão | Uso |
|-----------|--------|-----|
| `langchain` | - | Orquestração e chains de IA |
| `langchain-openai` | - | Integração com Azure OpenAI |
| `google-cloud-bigquery` | 3.31.0 | Acesso ao BigQuery |
| `google-cloud-storage` | 3.1.0 | Acesso ao Cloud Storage |
| `deepagents` | 0.4.12 | Framework de agentes IA |
| `python-dotenv` | 0.9.9 | Gerenciamento de variáveis de ambiente |
| `anthropic` | 0.86.0 | Integração com Claude |

Para a lista completa, consulte [requirements.txt](requirements.txt).

## 🔐 Segurança

- Não compartilhe suas chaves de API
- Use variáveis de ambiente para credenciais
- Revise sempre os artefatos gerados antes de usar em produção
- Mantenha as credenciais seguras no arquivo .env (adicione à .gitignore)

## 📝 Licença

[Adicione sua licença aqui]

## 👥 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## 📧 Contato

Para questões e sugestões, entre em contato através de [seu-email@example.com]

---

**Desenvolvido com ❤️ para automação de engenharia de dados**
