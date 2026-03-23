# CHANGELOG

## 2026-03-23

### Added

- Novo `docs/SPEC.md` como contrato funcional oficial com regra de precedencia documental.
- Novo `src/infra/log_service.py` para observabilidade em `data/logs_eventos.json`.
- Novo `src/app/app_service.py` para orquestracao de fluxos (bootstrap, menu, jogo e campeonato).
- Novo schema de eventos de log: `timestamp_iso`, `nivel`, `evento`, `contexto`.
- Novo `src/app/jogo_flow.py` para fluxo interativo do modo jogo.
- Novo `src/app/campeonato_flow.py` para fluxo interativo do modo campeonato.

### Changed

- Refatoracao profunda: `main.py` ficou como ponto de entrada minimo.
- Reorganizacao estrutural para `src/ + data/ + docs/` mantendo `python3 main.py`.
- `src/app/app_service.py` foi reduzido a bootstrap + dispatch do menu principal.
- `src/domain/jogo_service.py` passou a dominio puro (avaliacao/agregacao sem I/O direto).
- `src/domain/campeonato_service.py` passou a dominio de campeonato sem impressao direta.
- `src/domain/perguntas_service.py` adotou validacao tolerante com skip de perguntas invalidas.
- `src/infra/json_store.py` passou a usar escrita atomica com `os.replace`.
- `src/ui/ui.py` normalizou transicoes e estilo de mensagens.
- Docstrings padronizadas (module + func) com `Args`, `Returns`, `Raises`, `Side Effects`.
- `src/domain/pontuacoes_service.py` passou a mostrar Top 10 detalhado com fallback para registos antigos.
- `README.md` e `docs/SPEC.md` atualizados com arquitetura final e contrato do Top 10 detalhado.

### Fixed

- Tratamento de casos de JSON vazio/invalido mantendo comportamento seguro.
- Melhoria de robustez em leituras/escritas de historico e pontuacoes.
- Coerencia entre regras do jogo e documentacao operacional.
- Consistencia PT-PT na apresentacao do modo (`relógio`) e dificuldades detalhadas.
