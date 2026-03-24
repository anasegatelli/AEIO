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
skill_dir = Path("AEIO_ddl_dag_proc/skills").expanduser().resolve()
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
        f"Coloque o DDL da tabela de origem e edite 'parametros.yaml'."
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
    Ex.: create_tabela.sql, parametros.yaml
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
    Salva um arquivo dentro de uma subpasta da pasta Saida.
    A subpasta é definida pela skill.
    """

    subpasta_limpa = subpasta.strip().replace("\\", "/").strip("/")

    if not subpasta_limpa:
        return "Erro: a subpasta não pode estar vazia."

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

def texto_limpo(resposta) -> str:
    if isinstance(resposta, dict) and "messages" in resposta and resposta["messages"]:
        ultima = resposta["messages"][-1]

        if hasattr(ultima, "content"):
            return ultima.content

        if isinstance(ultima, dict):
            return ultima.get("content", str(ultima))

        return str(ultima)

    return str(resposta)

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
        2. Pedir que o usuário coloque o DDL na pasta Entrada e edite o arquivo Entrada/parametros.yaml.
        3. Quando os arquivos existirem, ler ambos.
        4. Analisar o DDL (Somente fonte de conhecimento para gerar o DDL da nova tabela trusted-zone ou sensitive-trusted) e os parâmetros.
        5. Fluxo de execucao: Gerar DAG da nova tabela -> DDL da nova tabela -> Procedure de carga da nova tabela com base no novo DDL da nova tabela criada (Converta todos os campos necessarios) -> Validador da tabela alvo. Nao esqueça os arquivos .yaml de cada artefato. Todos em suas respectivas subpastas. Seguir todos os padroes de nomeclatura.
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
                    "Prepare a estrutura de entrada para eu colocar o DDL e editar os parâmetros."
                    "Liste todas as skills disponivies e de um breve resumo do que cada uma faz (Uma frase de no maximo 10 palavras para cada skill)."
                            ),
            }
          ]
        }
    )
    print(texto_limpo(resposta1))

    input("\nDepois de colocar o DDL da RAW na pasta Entrada e editar o arquivo parametros.yaml, pressione ENTER.\n")

    print("="*5," Etapa 2 - Gerando os artefatos ","="*5)
   # resposta2 = agent.invoke(
    resposta2 = invoke_com_retry(
        agent,
        {
         "messages": [
            {
              "role": "user",
              "content": ( 
                      "Leia os arquivos da pasta Entrada e com base neles, gere a DAG Factory, o DDL da nova tabela (com todos os nomes de campos seguindo a padronizacao correta), a Procedure de carga da nova tabela e o Validador da tabela alvo. No final valide todas as pastas e arquivos criados garantindo que estejam corretos e completos. Se algo estiver faltando ou fora do padrão, corrija usando as skills disponíveis. Gere também os comandos para versionamento no Git, como mensagens de commit e comandos de push. Informe quais skills foram utilizadas. Caso o parametro 'Projeto' nao seja trusted-zone ou sensitive-trusted, interrompa na hora a execucao e solicite que seja revisado o processo"
                      "Nao deixe de gerar nenhum dos arquivos solicitados e siga rigorosamente os padrões de nomeclatura. Use as skills disponíveis para isso. Para o validador, use obrigatoriamente a skill create-validador.md e gere o bloco/arquivo conforme as regras da skill. Salve obrigatoriamente o validador usando salvar_arquivo_saida em SAIDA/validador_dados/eng/{projeto}/{dataset}/{tabela}/, incluindo o YAML e o README.md. Se não tiver como gerar algum dos artefatos, informe que não tem como ajudar. Nao replique o DDL original na pasta de saida, apenas consulte na pasta entrada"
                      "Crie um README.md com os comandos nencessarios para versionamento no github para cada artefato criado, incluindo o validador."
                 "So volte a responder quando todo o processo for finalizado"
                   ),
             }
          ]
        }
    )
    print(texto_limpo(resposta2))

    if not existe_validador_em_saida():
        print("\nValidador não encontrado em SAIDA. Executando geração complementar do artefato faltante...\n")
        resposta3 = invoke_com_retry(
            agent,
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "O validador nao foi salvo na SAIDA. Leia novamente ENTRADA/parametros.yaml e gere apenas o artefato faltante. "
                            "Use obrigatoriamente a skill create-validador.md e a tool salvar_arquivo_saida. "
                            "Salve em SAIDA/validador_dados/eng/{projeto}/{dataset}/{tabela}/ os arquivos de validador (YAML e README.md). "
                            "Ao final, use a tool listar_arquivos_saida e confirme os caminhos salvos."
                        ),
                    }
                ]
            }
        )
        print(texto_limpo(resposta3))

if __name__ == "__main__":
    main()