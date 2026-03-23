"""json_store.py

Responsabilidade:
    Ler e escrever ficheiros JSON com defaults seguros.

Dependencias:
    - json
    - os

Funcoes publicas:
    - carregar_json
    - guardar_json
"""

import json
import os


def carregar_json(caminho, valor_default):
    """Carrega dados JSON de um ficheiro.

    Args:
        caminho (str): Caminho do ficheiro JSON.
        valor_default (object): Valor a devolver/guardar se o ficheiro nao existir.

    Returns:
        object: Conteudo JSON carregado.

    Raises:
        ValueError: Quando o ficheiro existe mas contem JSON invalido.
    """
    if not os.path.exists(caminho):
        guardar_json(caminho, valor_default)
        return valor_default

    with open(caminho, "r", encoding="utf-8") as ficheiro:
        conteudo = ficheiro.read().strip()
        if not conteudo:
            guardar_json(caminho, valor_default)
            return valor_default

    with open(caminho, "r", encoding="utf-8") as ficheiro:
        try:
            return json.load(ficheiro)
        except json.JSONDecodeError as erro:
            raise ValueError(f"JSON invalido em '{caminho}'.") from erro


def guardar_json(caminho, dados):
    """Guarda dados em ficheiro JSON.

    Args:
        caminho (str): Caminho do ficheiro JSON.
        dados (object): Estrutura serializavel para JSON.

    Returns:
        None
    """
    with open(caminho, "w", encoding="utf-8") as ficheiro:
        json.dump(dados, ficheiro, indent=2, ensure_ascii=False)

