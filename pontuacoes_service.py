"""pontuacoes_service.py

Responsabilidade:
    Persistir resultados e apresentar ranking Top 10.

Dependencias:
    - datetime
    - config
    - json_store

Contratos de entrada/saida:
    - guardar_resultado(...): persiste registo de sessao.
    - obter_top10(...): devolve ranking ordenado.
    - mostrar_top10(...): imprime ranking no terminal.

Funcoes publicas:
    - guardar_resultado
    - obter_top10
    - mostrar_top10
"""

from datetime import datetime

from config import CAMINHO_PONTUACOES
from json_store import carregar_json, guardar_json


def guardar_resultado(resultado, caminho=CAMINHO_PONTUACOES):
    """Guarda resultado de sessao em historico JSON.

    Args:
        resultado (dict): Dados finais da sessao.
        caminho (str): Caminho do ficheiro de pontuacoes.

    Returns:
        None

    Raises:
        ValueError: Quando ficheiro existente contem JSON invalido.
        OSError: Em falhas de escrita do ficheiro.

    Side Effects:
        - Le e escreve ficheiro de pontuacoes.
    """
    historico = carregar_json(caminho, [])
    if not isinstance(historico, list):
        historico = []

    registo = dict(resultado)
    registo["data_iso"] = datetime.now().isoformat(timespec="seconds")
    historico.append(registo)
    guardar_json(caminho, historico)


def obter_top10(caminho=CAMINHO_PONTUACOES):
    """Obtem ranking dos 10 melhores resultados.

    Args:
        caminho (str): Caminho do ficheiro de pontuacoes.

    Returns:
        list[dict]: Top 10 ordenado por pontos, percentagem e data.

    Raises:
        ValueError: Quando ficheiro existente contem JSON invalido.

    Side Effects:
        - Le ficheiro de pontuacoes.
    """
    historico = carregar_json(caminho, [])
    if not isinstance(historico, list):
        historico = []

    ordenado = sorted(
        historico,
        key=lambda r: (
            int(r.get("pontos", 0)),
            float(r.get("percentagem", 0.0)),
            str(r.get("data_iso", "")),
        ),
        reverse=True,
    )
    return ordenado[:10]


def mostrar_top10(caminho=CAMINHO_PONTUACOES):
    """Mostra tabela Top 10 no terminal.

    Args:
        caminho (str): Caminho do ficheiro de pontuacoes.

    Returns:
        None

    Raises:
        ValueError: Quando ficheiro existente contem JSON invalido.

    Side Effects:
        - Le ficheiro de pontuacoes.
        - Escreve no terminal.
    """
    top = obter_top10(caminho)
    print("\nTop 10")
    if not top:
        print("Sem resultados guardados.")
        return

    for posicao, registo in enumerate(top, start=1):
        nome = registo.get("nickname", "anon")
        pontos = registo.get("pontos", 0)
        percentagem = registo.get("percentagem", 0.0)
        print(f"{posicao:02d}. {nome} - {pontos} pts ({percentagem}%)")
