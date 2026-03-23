# CHANGELOG

## 2026-03-23

### Added

- Novo `SPEC.md` como contrato funcional oficial com regra de precedencia documental.
- Novo `log_service.py` para observabilidade em `logs_eventos.json`.
- Novo `app_service.py` para orquestracao de fluxos (bootstrap, menu, jogo e campeonato).
- Novo schema de eventos de log: `timestamp_iso`, `nivel`, `evento`, `contexto`.

### Changed

- Refatoracao profunda: `main.py` ficou como ponto de entrada minimo.
- `jogo_service.py` passou a dominio puro (avaliacao/agregacao sem I/O direto).
- `campeonato_service.py` passou a dominio de campeonato sem impressao direta.
- `perguntas_service.py` adotou validacao tolerante com skip de perguntas invalidas.
- `json_store.py` passou a usar escrita atomica com `os.replace`.
- `ui.py` normalizou transicoes e estilo de mensagens.
- Docstrings padronizadas (module + func) com `Args`, `Returns`, `Raises`, `Side Effects`.

### Fixed

- Tratamento de casos de JSON vazio/invalido mantendo comportamento seguro.
- Melhoria de robustez em leituras/escritas de historico e pontuacoes.
- Coerencia entre regras do jogo e documentacao operacional.
