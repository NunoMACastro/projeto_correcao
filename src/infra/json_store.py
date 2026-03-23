"""json_store.py

Responsabilidade:
    Ler e escrever ficheiros JSON com defaults seguros e escrita atomica.

Dependencias:
    - json
    - os
    - tempfile

Contratos de entrada/saida:
    - carregar_json(caminho, valor_default): devolve objeto Python desserializado.
    - guardar_json(caminho, dados): persiste JSON de forma atomica.

Funcoes publicas:
    - carregar_json
    - guardar_json
"""

import json
import os
import tempfile


def serializar_json(dados):
    """Serializa uma estrutura Python para string JSON.

    Args:
        dados (object): Estrutura serializavel em JSON.

    Returns:
        str: Conteudo JSON formatado.

    Raises:
        TypeError: Quando os dados nao sao serializaveis.

    Side Effects:
        Nenhum.
    """
    return json.dumps(dados, indent=2, ensure_ascii=False)


def carregar_json(caminho, valor_default):
    """Carrega dados JSON de um ficheiro com fallback seguro.

    Args:
        caminho (str): Caminho do ficheiro JSON.
        valor_default (object): Valor guardado/devolvido se ficheiro faltar ou estiver vazio.

    Returns:
        object: Conteudo JSON carregado.

    Raises:
        ValueError: Quando o ficheiro existe mas contem JSON invalido.

    Side Effects:
        - Pode criar o ficheiro no caminho indicado com o valor default.
        - Pode reescrever o ficheiro se existir vazio.
    """
    if not os.path.exists(caminho):
        guardar_json(caminho, valor_default)
        return valor_default

    with open(caminho, "r", encoding="utf-8") as ficheiro:
        conteudo = ficheiro.read().strip()

    if not conteudo:
        guardar_json(caminho, valor_default)
        return valor_default

    try:
        return json.loads(conteudo)
    except json.JSONDecodeError as erro:
        raise ValueError(f"JSON inválido em '{caminho}'.") from erro


def guardar_json(caminho, dados):
    """Guarda dados em ficheiro JSON com escrita atomica.

    Args:
        caminho (str): Caminho do ficheiro JSON de destino.
        dados (object): Estrutura serializavel para JSON.

    Returns:
        None

    Raises:
        OSError: Quando ocorre falha de escrita/substituicao no sistema de ficheiros.
        TypeError: Quando os dados nao sao serializaveis para JSON.

    Side Effects:
        - Cria diretoria de destino quando necessario.
        - Escreve ficheiro temporario e substitui o destino via os.replace.
    """
    conteudo = serializar_json(dados)
    caminho_absoluto = os.path.abspath(caminho)
    diretorio = os.path.dirname(caminho_absoluto)
    if diretorio:
        os.makedirs(diretorio, exist_ok=True)

    tmp_path = ""
    fd = -1
    try:
        fd, tmp_path = tempfile.mkstemp(
            prefix=".tmp_json_",
            suffix=".json",
            dir=diretorio or None,
            text=True,
        )
        with os.fdopen(fd, "w", encoding="utf-8") as ficheiro_tmp:
            fd = -1
            ficheiro_tmp.write(conteudo)
        os.replace(tmp_path, caminho_absoluto)
    except Exception:
        if fd != -1:
            os.close(fd)
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
