"""log_service.py

Responsabilidade:
    Persistir eventos de observabilidade em ficheiro JSON sem bloquear o fluxo.

Dependencias:
    - datetime
    - config
    - json_store

Contratos de entrada/saida:
    - registrar_evento(...): devolve True se gravou; False em caso de falha.

Funcoes publicas:
    - registrar_evento
"""

from datetime import datetime

from config import CAMINHO_LOG_EVENTOS
from json_store import carregar_json, guardar_json


def normalizar_contexto(contexto):
    """Normaliza o contexto de um evento de log para dicionario.

    Args:
        contexto (dict | None): Contexto opcional do evento.

    Returns:
        dict: Contexto normalizado.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    if contexto is None:
        return {}
    if isinstance(contexto, dict):
        return contexto
    return {"valor": str(contexto)}


def construir_evento(nivel, evento, contexto):
    """Constroi um registo de evento no formato padrao.

    Args:
        nivel (str): Nivel do evento (INFO, WARNING, ERROR).
        evento (str): Nome tecnico do evento.
        contexto (dict | None): Dados associados ao evento.

    Returns:
        dict: Evento pronto para persistencia.

    Raises:
        Nenhum.

    Side Effects:
        Nenhum.
    """
    return {
        "timestamp_iso": datetime.now().isoformat(timespec="seconds"),
        "nivel": str(nivel).strip().upper() or "INFO",
        "evento": str(evento).strip().lower() or "evento_sem_nome",
        "contexto": normalizar_contexto(contexto),
    }


def registrar_evento(nivel, evento, contexto=None, caminho=CAMINHO_LOG_EVENTOS):
    """Regista evento de observabilidade em ficheiro JSON.

    Args:
        nivel (str): Nivel do evento.
        evento (str): Nome tecnico do evento.
        contexto (dict | None): Dados adicionais do evento.
        caminho (str): Caminho do ficheiro de eventos.

    Returns:
        bool: True se o evento foi gravado; False em caso de falha.

    Raises:
        Nenhum.

    Side Effects:
        - Le e escreve o ficheiro de logs JSON.
        - Nunca propaga excecoes para nao interromper a aplicacao.
    """
    try:
        eventos = carregar_json(caminho, [])
        if not isinstance(eventos, list):
            eventos = []
        eventos.append(construir_evento(nivel, evento, contexto))
        guardar_json(caminho, eventos)
        return True
    except Exception:
        return False
