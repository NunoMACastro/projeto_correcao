"""pontuacoes_service.py

Responsabilidade:
    Persistir resultados e apresentar ranking Top 10 detalhado.

Dependencias:
    - datetime
    - config
    - json_store

Contratos de entrada/saida:
    - guardar_resultado(...): persiste registo de sessão.
    - obter_top10(...): devolve ranking ordenado.
    - mostrar_top10(...): imprime ranking detalhado no terminal.

Funcoes publicas:
    - guardar_resultado
    - obter_top10
    - mostrar_top10
"""

from datetime import datetime

from config import CAMINHO_PONTUACOES
from json_store import carregar_json, guardar_json


def _converter_inteiro(valor, padrao=0):
    """Converte valor para inteiro com fallback seguro.

    Args:
        valor (object): Valor bruto.
        padrao (int): Valor devolvido em caso de falha.

    Returns:
        int: Inteiro convertido ou fallback.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    try:
        return int(valor)
    except (TypeError, ValueError):
        return int(padrao)


def _converter_float(valor, padrao=0.0):
    """Converte valor para float com fallback seguro.

    Args:
        valor (object): Valor bruto.
        padrao (float): Valor devolvido em caso de falha.

    Returns:
        float: Float convertido ou fallback.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    try:
        return float(valor)
    except (TypeError, ValueError):
        return float(padrao)


def _formatar_percentagem(percentagem):
    """Formata percentagem com pelo menos uma casa decimal.

    Args:
        percentagem (float): Valor numérico da percentagem.

    Returns:
        str: Texto da percentagem formatada.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    texto = f"{_converter_float(percentagem):.2f}".rstrip("0").rstrip(".")
    if "." not in texto:
        texto += ".0"
    return texto


def _normalizar_data_hora(valor):
    """Normaliza `data_iso` para formato legível `YYYY-MM-DD HH:MM:SS`.

    Args:
        valor (object): Valor original do campo `data_iso`.

    Returns:
        str: Data/hora formatada ou `sem data`.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    data_texto = str(valor or "").strip()
    if not data_texto:
        return "sem data"

    tentativa = data_texto.replace("Z", "+00:00")
    try:
        data = datetime.fromisoformat(tentativa)
    except ValueError:
        return "sem data"
    return data.strftime("%Y-%m-%d %H:%M:%S")


def _normalizar_dificuldade(valor):
    """Normaliza dificuldade para texto de apresentação em PT-PT.

    Args:
        valor (object): Valor original de dificuldade.

    Returns:
        str: Dificuldade normalizada para apresentação.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    texto = str(valor or "").strip().lower()
    tabela = {
        "facil": "fácil",
        "media": "média",
        "dificil": "difícil",
        "todas": "todas",
    }
    return tabela.get(texto, "desconhecida")


def _normalizar_modo(valor):
    """Normaliza modo para texto de apresentação em PT-PT.

    Args:
        valor (object): Valor original de modo.

    Returns:
        str: Modo normalizado para apresentação.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    texto = str(valor or "").strip().lower()
    tabela = {
        "relogio": "relógio",
        "normal": "normal",
    }
    return tabela.get(texto, "desconhecido")


def guardar_resultado(resultado, caminho=CAMINHO_PONTUACOES):
    """Guarda resultado de sessão em histórico JSON.

    Args:
        resultado (dict): Dados finais da sessão.
        caminho (str): Caminho do ficheiro de pontuações.

    Returns:
        None

    Raises:
        ValueError: Quando ficheiro existente contém JSON inválido.
        OSError: Em falhas de escrita do ficheiro.

    Side Effects:
        - Lê e escreve ficheiro de pontuações.
    """
    historico = carregar_json(caminho, [])
    if not isinstance(historico, list):
        historico = []

    registo = dict(resultado)
    registo["data_iso"] = datetime.now().isoformat(timespec="seconds")
    historico.append(registo)
    guardar_json(caminho, historico)


def obter_top10(caminho=CAMINHO_PONTUACOES):
    """Obtém ranking dos 10 melhores resultados.

    Args:
        caminho (str): Caminho do ficheiro de pontuações.

    Returns:
        list[dict]: Top 10 ordenado por pontos, percentagem e data.

    Raises:
        ValueError: Quando ficheiro existente contém JSON inválido.

    Side Effects:
        - Lê ficheiro de pontuações.
    """
    historico = carregar_json(caminho, [])
    if not isinstance(historico, list):
        historico = []

    ordenado = sorted(
        historico,
        key=lambda registo: (
            _converter_inteiro(registo.get("pontos", 0)),
            _converter_float(registo.get("percentagem", 0.0)),
            str(registo.get("data_iso", "")),
        ),
        reverse=True,
    )
    return ordenado[:10]


def mostrar_top10(caminho=CAMINHO_PONTUACOES):
    """Mostra tabela Top 10 detalhada no terminal.

    Args:
        caminho (str): Caminho do ficheiro de pontuações.

    Returns:
        None

    Raises:
        ValueError: Quando ficheiro existente contém JSON inválido.

    Side Effects:
        - Lê ficheiro de pontuações.
        - Escreve no terminal.
    """
    top = obter_top10(caminho)
    print("\nTop 10")
    if not top:
        print("Sem resultados guardados.")
        return

    for posicao, registo in enumerate(top, start=1):
        nome = str(registo.get("nickname", "")).strip() or "anon"
        pontos = _converter_inteiro(registo.get("pontos", 0))
        percentagem = _formatar_percentagem(registo.get("percentagem", 0.0))
        certas = _converter_inteiro(registo.get("certas", 0))
        erradas = _converter_inteiro(registo.get("erradas", 0))
        num_perguntas = _converter_inteiro(registo.get("num_perguntas", 0))
        dificuldade = _normalizar_dificuldade(registo.get("dificuldade", ""))
        modo = _normalizar_modo(registo.get("modo", ""))
        data_hora = _normalizar_data_hora(registo.get("data_iso", ""))

        print(
            f"{posicao:02d}. {nome} | {pontos} pts | {percentagem}% | "
            f"{certas}C/{erradas}E | {num_perguntas} perguntas | "
            f"dificuldade: {dificuldade} | modo: {modo} | {data_hora}"
        )
