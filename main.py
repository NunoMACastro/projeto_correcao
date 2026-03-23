"""main.py

Responsabilidade:
    Ponto de entrada da aplicacao.

Dependencias:
    - app_service

Contratos de entrada/saida:
    - iniciar_aplicacao(): delega bootstrap para a camada de aplicacao.

Funcoes publicas:
    - iniciar_aplicacao
"""

from app_service import executar_aplicacao


def iniciar_aplicacao():
    """Inicia aplicacao e delega fluxo completo para `app_service`.

    Args:
        Nenhum.

    Returns:
        None

    Raises:
        SystemExit: Quando utilizador pede saida durante a execucao.

    Side Effects:
        - Executa fluxos de consola e persistencia atraves da camada de aplicacao.
    """
    executar_aplicacao()


if __name__ == "__main__":
    iniciar_aplicacao()
