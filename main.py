from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from deepagents import create_deep_agent
import random
import time

load_dotenv()

BASE_DIR = Path.cwd()
ENTRADA = BASE_DIR / "ENTRADA"
SAIDA = BASE_DIR / "SAIDA"

ENTRADA.mkdir(exist_ok=True)
SAIDA.mkdir(exist_ok=True)

dir_path = os.path.dirname(os.path.realpath(__file__))
skills_path = os.path.join(dir_path, "skills")

#skill_dir = Path("~/Documents/GenIA - TRILHA/AEIO_ddl_dag_proc/skills").expanduser().resolve()
skill_dir = Path("AEIO/skills").expanduser().resolve()
def load_skills(path: str) -> str:
    with open(path, "r") as f:
        return f.read()

l_skills = [
        load_skills("skills/create-dag.md"),
        load_skills("skills/create-procedure.md"),
        load_skills("skills/create-ddl.md"),
        load_skills("skills/padrao-nomeclatura-tabela.md"),
        load_skills("skills/create-validador.md")        
        ]

@tool
def preparar_entrada() -> str:
    """
    Cria a estrutura inicial de entrada e um arquivo parametros.yaml base.
    """
    arquivo_parametros = ENTRADA / "parametros.yaml"

    if not arquivo_parametros.exists():
        conteudo = """# Edite este arquivo
            Projeto:
            Dataset:
            Tabela:
            Tipo de Carga:
            Schedule:
            Campo Delta:
            Faixa Delta:
            Iniciativa:
            Descrição:
            Tabela de origem:
            Squad/Time:
            Tags:
            sandbox:
            """

        arquivo_parametros.write_text(conteudo, encoding="utf-8")

    return (
        f"Estrutura preparada com sucesso.\n"
        f"Pasta de entrada: {ENTRADA.resolve()}\n"
        f"Adicione o script .sql de origem e edite o arquivo 'parametros.yaml'."
    )

@tool
def listar_arquivos_entrada() -> str:
    """
    Lista os arquivos da pasta Entrada.
    """
    arquivos = [p.name for p in ENTRADA.iterdir() if p.is_file()]
    if not arquivos:
        return "Nenhum arquivo encontrado na pasta Entrada."
    return "\n".join(arquivos)


@tool
def ler_arquivo_entrada(nome_arquivo: str) -> str:
    """
    Lê um arquivo de texto da pasta Entrada.
    Ex.: qualquer_arquivo.sql, parametros.yaml
    """
    arquivo = (ENTRADA / nome_arquivo).resolve()

    if not str(arquivo).startswith(str(ENTRADA.resolve())):
        return "Acesso negado."

    if not arquivo.exists():
        return f"Arquivo não encontrado: {arquivo.name}"

    try:
        return arquivo.read_text(encoding="utf-8")
    except Exception as e:
        return f"Erro ao ler arquivo: {e}"

@tool
def salvar_arquivo_saida(subpasta: str, nome_arquivo: str, conteudo: str) -> str:
    """
    Salva um arquivo dentro de uma subpasta da pasta SAIDA.
    A subpasta deve ser relativa à raiz SAIDA (sem prefixo "SAIDA/").
    Para salvar na raiz de SAIDA, use subpasta=".".
    """

    subpasta_limpa = subpasta.strip().replace("\\", "/").strip("/")

    if subpasta_limpa.lower().startswith("saida/"):
        subpasta_limpa = subpasta_limpa[6:]
    elif subpasta_limpa.lower() == "saida":
        subpasta_limpa = ""

    if subpasta_limpa in ("", "."):
        pasta_destino = SAIDA.resolve()
    else:
        pasta_destino = (SAIDA / subpasta_limpa).resolve()

    if not str(pasta_destino).startswith(str(SAIDA.resolve())):
        return "Acesso negado."

    pasta_destino.mkdir(parents=True, exist_ok=True)

    arquivo = (pasta_destino / nome_arquivo).resolve()

    if not str(arquivo).startswith(str(SAIDA.resolve())):
        return "Acesso negado."

    try:
        arquivo.write_text(conteudo, encoding="utf-8")
        return f"Arquivo salvo com sucesso em: {arquivo}"
    except Exception as e:
        return f"Erro ao salvar arquivo: {e}"

@tool
def listar_arquivos_saida() -> str:
    """
    Lista os arquivos gerados na pasta SAIDA com caminho relativo.
    """
    if not SAIDA.exists():
        return "Pasta SAIDA não encontrada."

    arquivos = [p.relative_to(SAIDA).as_posix() for p in SAIDA.rglob("*") if p.is_file()]
    if not arquivos:
        return "Nenhum arquivo encontrado na pasta SAIDA."
    return "\n".join(sorted(arquivos))

def existe_validador_em_saida() -> bool:
    if not SAIDA.exists():
        return False
    for arquivo in SAIDA.rglob("*.yaml"):
        caminho = arquivo.as_posix().lower()
        if "validador" in caminho:
            return True
    return False

def existe_dag_em_saida() -> bool:
    if not SAIDA.exists():
        return False
    for arquivo in SAIDA.rglob("*"):
        caminho = arquivo.as_posix().lower()
        if "dag" in caminho and arquivo.is_file():
            return True
    return False

def existe_ddl_em_saida() -> bool:
    if not SAIDA.exists():
        return False
    for arquivo in SAIDA.rglob("*.sql"):
        caminho = arquivo.as_posix().lower()
        if "ddl" in caminho or ("create" in caminho and "table" in arquivo.read_text().lower()):
            return True
    return False

def existe_procedure_em_saida() -> bool:
    if not SAIDA.exists():
        return False
    for arquivo in SAIDA.rglob("*.sql"):
        caminho = arquivo.as_posix().lower()
        if "procedure" in caminho or "proc" in caminho:
            return True
    return False

def texto_limpo(resposta) -> str:
    if isinstance(resposta, dict) and "messages" in resposta and resposta["messages"]:
        ultima = resposta["messages"][-1]

        if hasattr(ultima, "content"):
            return ultima.content

        if isinstance(ultima, dict):
            return ultima.get("content", str(ultima))

        return str(ultima)

    return str(resposta)

def extrair_campo_yaml(texto: str, campo: str) -> str:
    for linha in texto.splitlines():
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            if chave.strip().lower() == campo.strip().lower():
                return valor.strip()
    return ""

def contar_campos_sql(sql_texto: str) -> int:
    total = 0
    for linha in sql_texto.splitlines():
        trecho = linha.strip().rstrip(",")
        if not trecho:
            continue
        if trecho.startswith("CREATE TABLE") or trecho.startswith("CLUSTER BY") or trecho.startswith("OPTIONS"):
            continue
        if trecho.startswith("(") or trecho.startswith(")"):
            continue
        if " OPTIONS(" in trecho and " " in trecho:
            total += 1
    return total

def invoke_com_retry(agent, payload: dict, max_tentativas: int = 6, espera_inicial: float = 3.0):
    espera = espera_inicial

    for tentativa in range(1, max_tentativas + 1):
        try:
            return agent.invoke(payload)
        except Exception as e:
            erro = str(e)
            erro_rate_limit = (
                "RateLimitError" in erro
                or "RateLimitReached" in erro
                or "Error code: 429" in erro
                or "429" in erro
            )

            if (not erro_rate_limit) or tentativa == max_tentativas:
                raise

            pausa = espera + random.uniform(0, 1)
            print(
                f"Rate limit detectado (tentativa {tentativa}/{max_tentativas}). "
                f"Aguardando {pausa:.1f}s antes de tentar novamente..."
            )
            time.sleep(pausa)
            espera = min(espera * 2, 30)

def main():
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("endpoint"),
        api_key=os.getenv("api_key"),
        api_version=os.getenv("api_version"),
        azure_deployment=os.getenv("model_name"),
        temperature=0.4,
    )

    instrucoes_principais="""
        Você é um agente que trabalha com arquivos locais.

        Fluxo esperado:
        1. Preparar a pasta Entrada com o arquivo parametros.yaml se necessário.
        2. Pedir que o usuário coloque o script .sql na pasta Entrada e edite o arquivo Entrada/parametros.yaml.
        3. Ler os parâmetros de Entrada/parametros.yaml e ler o script .sql da pasta Entrada.
        4. Usar o SQL de Entrada como fonte obrigatória dos campos e os parâmetros como fonte oficial de projeto/dataset/tabela.
        4.1. Nunca exigir nome fixo de SQL (ex.: create_tabela.sql). Qualquer arquivo com extensão .sql em ENTRADA é válido.
        5. Fluxo de execucao: Gerar DAG da nova tabela -> DDL da nova tabela -> Procedure de carga da nova tabela com base no novo DDL da nova tabela criada (considerar 100% dos campos do SQL de entrada, sem omissoes; na procedure usar CAST e nunca SAFE_CAST) -> Validador da tabela alvo. Nao esqueça os arquivos .yaml de cada artefato. Todos em suas respectivas subpastas. Seguir todos os padroes de nomeclatura.
        6. Sempre usar as tools e skills disponíveis para ler e salvar arquivos e criar os arquivos. Para CADA artefato gerado, usar obrigatoriamente a tool salvar_arquivo_saida e confirmar o caminho final. Informe quais skills foram utilizadas. Nao inventar nada que nao esteja nas skills disponiveis. Se nao tiver como montar o artefato solicitado, informe que nao tem como ajudar.
        7. Validar a estrutura de todas as pastas e arquivos criados, garantindo que estejam corretos e completos. Se algo estiver faltando ou fora do padrão, corrija usando as skills disponíveis.
        8. Gere os comandos para versionamento no Git, como mensagens de commit e comandos de push.
        9. No final faca um cheklist de validacao para cada artefato criado e sua estrutura de pasta.
      """
   


    agent = create_deep_agent(
        model=llm,
        tools=[
            preparar_entrada,
            listar_arquivos_entrada,
            ler_arquivo_entrada,
            salvar_arquivo_saida,
            listar_arquivos_saida,
        ],
        skills=l_skills,
        system_prompt=instrucoes_principais
    )

    print("="*5," Etapa 1 - Preparando a Estrutura de entrada de dados","="*5)
   # resposta1 = agent.invoke(
    resposta1 = invoke_com_retry(
        agent,
        {
         "messages": [
            {
                "role": "user",
                "content": (
                            "Prepare a estrutura de entrada para eu colocar um arquivo .sql (qualquer nome) e editar os parâmetros."
                    "Liste todas as skills disponivies e de um breve resumo do que cada uma faz (Uma frase de no maximo 10 palavras para cada skill)."
                            ),
            }
          ]
        }
    )
    print(texto_limpo(resposta1))

    input("\nDepois de colocar o script .sql na pasta ENTRADA e editar o arquivo parametros.yaml, pressione ENTER.\n")

    print("="*5," Etapa 2 - Gerando os artefatos (fluxo rápido)","="*5)

    parametros_path = ENTRADA / "parametros.yaml"
    if not parametros_path.exists():
        raise FileNotFoundError("Arquivo ENTRADA/parametros.yaml não encontrado.")

    parametros_texto = parametros_path.read_text(encoding="utf-8")

    sql_entrada = sorted(ENTRADA.glob("*.sql"))
    if not sql_entrada:
        raise FileNotFoundError("Nenhum arquivo .sql encontrado em ENTRADA.")

    sql_origem_path = sql_entrada[0]
    sql_origem_nome = sql_origem_path.name
    sql_origem_texto = sql_origem_path.read_text(encoding="utf-8")
    qtd_campos_origem = contar_campos_sql(sql_origem_texto)

    projeto = extrair_campo_yaml(parametros_texto, "Projeto")
    dataset = extrair_campo_yaml(parametros_texto, "Dataset")
    tabela = extrair_campo_yaml(parametros_texto, "Tabela")

    if projeto not in ("trusted-zone", "sensitive-trusted"):
        raise ValueError(
            f"Projeto inválido: {projeto}. Use trusted-zone ou sensitive-trusted."
        )

    if not tabela:
        raise ValueError("Campo 'Tabela' não encontrado em ENTRADA/parametros.yaml")

    prompt_geracao_unica = f"""
Gere TODOS os artefatos em uma única execução:
1) DAG
2) DDL da nova tabela
3) Procedure de carga
4) Validador (YAML e README.md)

⚠️  INSTRUÇÃO CRÍTICA - NOME DA TABELA:
Use OBRIGATORIAMENTE: {tabela}
Este é o nome definido no campo "Tabela" do PARAMETROS_YAML.

Regras:
- Use as skills apropriadas.
- Use obrigatoriamente salvar_arquivo_saida para cada arquivo.
- Em salvar_arquivo_saida, use subpasta relativa à SAIDA (não incluir prefixo "SAIDA/").
- Não bloquear por nome fixo de SQL (NUNCA exigir create_tabela.sql).
- Use o arquivo SQL identificado automaticamente: {sql_origem_nome}
- O SQL de ENTRADA é fonte obrigatória de campos para DDL e Procedure.
- O novo DDL trusted/sensitive-trusted deve conter 100% dos campos do SQL de ENTRADA (sem omissões).
- Aplique padronização de nomenclatura de campos no novo DDL conforme as skills.
- A Procedure deve considerar todos os campos definidos no novo DDL gerado.
- Na Procedure: usar CAST quando necessário e NUNCA usar SAFE_CAST.
- A DAG deve usar: dataset={dataset}, tabela={tabela}
- O DDL deve criar tabela: {tabela}
- A Procedure de carga deve trabalhar com: dataset={dataset}, tabela={tabela}
- O validador deve usar: tabela={tabela}
- O validador deve ficar em: validador_dados/eng/{projeto}/{dataset}/{tabela}/
- Antes de finalizar, validar que o total de campos do DDL gerado é igual ao SQL de ENTRADA.
- Se houver divergência de campos, corrigir e regenerar antes da resposta final.
- Siga padrão de nomenclatura.
- No final, use listar_arquivos_saida e confirme os caminhos.

RESUMO OBRIGATÓRIO:
  Projeto: {projeto}
  Dataset: {dataset}
  Tabela: {tabela}
    Campos no SQL de entrada: {qtd_campos_origem}

PARAMETROS_YAML:
{parametros_texto}

SQL_ENTRADA (FONTE DOS CAMPOS):
{sql_origem_texto}
"""

    resposta2 = invoke_com_retry(
        agent,
        {"messages": [{"role": "user", "content": prompt_geracao_unica}]},
        max_tentativas=4,
        espera_inicial=1.5,
    )
    print(texto_limpo(resposta2))

    artefatos_faltantes = []
    if not existe_dag_em_saida():
        artefatos_faltantes.append("DAG")
    if not existe_ddl_em_saida():
        artefatos_faltantes.append("DDL")
    if not existe_procedure_em_saida():
        artefatos_faltantes.append("Procedure")
    if not existe_validador_em_saida():
        artefatos_faltantes.append("Validador")

    if artefatos_faltantes:
        print(f"\n⚠️  Artefatos faltantes: {', '.join(artefatos_faltantes)}")

        prompt_regeneracao_unica = (
            "Regenerar apenas estes artefatos faltantes: "
            f"{', '.join(artefatos_faltantes)}. "
            f"⚠️  CRÍTICO: Use OBRIGATORIAMENTE a tabela = {tabela} (definida no PARAMETROS_YAML). "
            f"⚠️  CRÍTICO: Considerar o SQL de entrada identificado: {sql_origem_nome}. Não exigir create_tabela.sql. "
            "⚠️  CRÍTICO: Para DDL/Procedure, considerar 100% dos campos do SQL de ENTRADA e aplicar padrão de nomenclatura no novo DDL. "
            "⚠️  CRÍTICO: Na Procedure é proibido SAFE_CAST; usar CAST quando necessário. "
            "Use salvar_arquivo_saida e confirme caminhos finais. "
            "Depois use listar_arquivos_saida."
        )

        resposta_faltantes = invoke_com_retry(
            agent,
            {"messages": [{"role": "user", "content": prompt_regeneracao_unica}]},
            max_tentativas=3,
            espera_inicial=1.0,
        )
        print(texto_limpo(resposta_faltantes))
    else:
        print("\n✅ Todos os artefatos foram gerados com sucesso!")

    print("\n" + "="*5," Etapa 4 - Preparando Versionamento ","="*5)
    resposta_git = invoke_com_retry(
        agent,
        {
         "messages": [
            {
              "role": "user",
              "content": ( 
                      "Crie um arquivo README.md de versionamento na raiz da SAIDA com os comandos necessários para fazer git add, git commit e git push de cada artefato. "
                      "Use a tool salvar_arquivo_saida com subpasta='.' para salvar este README com nome 'VERSIONAMENTO.md'. Informe o caminho final."
                      ),
             }
          ]
        }
    )
    print(texto_limpo(resposta_git))

if __name__ == "__main__":
    main()