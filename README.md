# Quiz em Python (Projeto Final)

Aplicacao de consola para jogo de perguntas/respostas, sem classes.

## Contrato oficial

- A fonte de verdade funcional do projeto e o [`docs/SPEC.md`](./docs/SPEC.md).
- Em caso de conflito entre docs: `docs/SPEC.md` > `README.md` > `docs/PLANIFICACAO.md`.

## Requisitos

- Python 3.x
- Sem bibliotecas externas (apenas standard library)

## Como executar

```bash
python3 main.py
```

## Verificacao tecnica

```bash
python3 -m py_compile main.py src/app/*.py src/domain/*.py src/infra/*.py src/ui/*.py
```

## Arquitetura funcional

- `main.py`: ponto de entrada mínimo.
- `src/app`: bootstrap/menu e fluxos interativos (`app_service.py`, `jogo_flow.py`, `campeonato_flow.py`).
- `src/domain`: regras de domínio (`jogo_service.py`, `campeonato_service.py`, `perguntas_service.py`, `pontuacoes_service.py`).
- `src/infra`: infraestrutura (`config.py`, `json_store.py`, `log_service.py`).
- `src/ui`: consola e validação (`ui.py`, `menu.py`, `validacao.py`).

## Ficheiros de dados

- `data/perguntas.json`: base de perguntas do quiz.
- `data/pontuacoes.json`: histórico de resultados.
- `data/historico_perguntas.json`: IDs usadas entre sessões.
- `data/logs_eventos.json`: eventos de observabilidade.

## Funcionalidades implementadas

### MVP

- Carregamento e validacao de `data/perguntas.json`.
- Menu principal com `Jogar`, `Regras / Ajuda`, `Top 10`, `Campeonato`.
- Jogo com 10 perguntas aleatorias por partida.
- Tempo fixo de 20 segundos por pergunta.
- Validacao robusta de input.
- Feedback por pergunta e resumo final.
- Re-jogar sem reiniciar aplicacao.

### Nível 2

- Filtro por dificuldade (`facil`, `media`, `dificil`, `todas`).
- Sem repeticao na mesma sessao.
- Anti-repeticao entre sessoes enquanto houver novas perguntas.
- Nickname por jogador.
- Persistencia de resultados em `data/pontuacoes.json`.
- Top 10 detalhado no menu principal.
- Mostrar explicacao quando disponivel.

### Nivel 3

- Contra-relogio fixo (20s por pergunta).
- Pontuacao por dificuldade sempre ativa (1/2/3).
- Modo campeonato (2 jogadores, melhor de 3 rondas).

## Validacao tolerante de perguntas

- Perguntas invalidas sao ignoradas (skip) com registo em `data/logs_eventos.json`.
- A app so arranca se existirem pelo menos 10 perguntas validas.

## Top 10 detalhado

- A vista `Top 10` mostra: posição, nome, pontos, percentagem, certas/erradas,
  número de perguntas, dificuldade, modo e data/hora.
- Fallbacks de compatibilidade para registos antigos/incompletos:
  - `nickname` vazio -> `anon`
  - `modo` ausente -> `desconhecido`
  - `dificuldade` ausente -> `desconhecida`
  - `data_iso` inválida/ausente -> `sem data`
  - campos numéricos ausentes -> `0`

## Observabilidade

- Eventos importantes sao registados em `data/logs_eventos.json`.
- Logging e resiliente: falha de log nao bloqueia o jogo.
