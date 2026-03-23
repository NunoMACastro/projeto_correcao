# CHANGELOG

## 2026-03-23

### Added

- Novo `SPEC.md` como contrato funcional oficial com regra de precedencia documental.
- Novo `log_service.py` para observabilidade em `logs_eventos.json`.
- Novo `app_service.py` para orquestracao de fluxos (bootstrap, menu, jogo e campeonato).
- Novo schema de eventos de log: `timestamp_iso`, `nivel`, `evento`, `contexto`.
- Novo `jogo_flow.py` para fluxo interativo do modo jogo.
- Novo `campeonato_flow.py` para fluxo interativo do modo campeonato.

### Changed

- Refatoracao profunda: `main.py` ficou como ponto de entrada minimo.
- `app_service.py` foi reduzido a bootstrap + dispatch do menu principal.
- `jogo_service.py` passou a dominio puro (avaliacao/agregacao sem I/O direto).
- `campeonato_service.py` passou a dominio de campeonato sem impressao direta.
- `perguntas_service.py` adotou validacao tolerante com skip de perguntas invalidas.
- `json_store.py` passou a usar escrita atomica com `os.replace`.
- `ui.py` normalizou transicoes e estilo de mensagens.
- Docstrings padronizadas (module + func) com `Args`, `Returns`, `Raises`, `Side Effects`.
- `pontuacoes_service.py` passou a mostrar Top 10 detalhado com fallback para registos antigos.
- `README.md` e `SPEC.md` atualizados com arquitetura final e contrato do Top 10 detalhado.

### Fixed

- Tratamento de casos de JSON vazio/invalido mantendo comportamento seguro.
- Melhoria de robustez em leituras/escritas de historico e pontuacoes.
- Coerencia entre regras do jogo e documentacao operacional.
- Consistencia PT-PT na apresentacao do modo (`relógio`) e dificuldades detalhadas.
