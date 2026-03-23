# Quiz em Python (Projeto Final)

Aplicacao de consola para jogo de perguntas/respostas, sem classes.

## Contrato oficial

- A fonte de verdade funcional do projeto e o [`SPEC.md`](./SPEC.md).
- Em caso de conflito entre docs: `SPEC.md` > `README.md` > `PLANIFICACAO.md`.

## Requisitos

- Python 3.x
- Sem bibliotecas externas (apenas standard library)

## Como executar

```bash
python3 main.py
```

## Verificacao tecnica

```bash
python3 -m py_compile *.py
```

## Arquitetura funcional

- `main.py`: ponto de entrada mínimo.
- `app_service.py`: bootstrap da aplicação e dispatch do menu principal.
- `jogo_flow.py`: fluxo interativo do modo jogo.
- `campeonato_flow.py`: fluxo interativo do modo campeonato.
- `jogo_service.py`: regras de domínio de avaliação/pontuação de sessão.
- `campeonato_service.py`: regras de domínio de rondas e vencedor.
- `perguntas_service.py`: carga, validação, filtros e seleção de perguntas.
- `pontuacoes_service.py`: persistência e apresentação do Top 10 detalhado.
- `json_store.py`: infraestrutura JSON com escrita atómica.
- `log_service.py`: observabilidade em ficheiro JSON.
- `ui.py`, `menu.py`, `validacao.py`: camada de interação de consola.

## Ficheiros de dados

- `perguntas.json`: base de perguntas do quiz.
- `pontuacoes.json`: historico de resultados.
- `historico_perguntas.json`: IDs usadas entre sessoes.
- `logs_eventos.json`: eventos de observabilidade.

## Funcionalidades implementadas

### MVP

- Carregamento e validacao de `perguntas.json`.
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
- Persistencia de resultados em `pontuacoes.json`.
- Top 10 detalhado no menu principal.
- Mostrar explicacao quando disponivel.

### Nivel 3

- Contra-relogio fixo (20s por pergunta).
- Pontuacao por dificuldade sempre ativa (1/2/3).
- Modo campeonato (2 jogadores, melhor de 3 rondas).

## Validacao tolerante de perguntas

- Perguntas invalidas sao ignoradas (skip) com registo em `logs_eventos.json`.
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

- Eventos importantes sao registados em `logs_eventos.json`.
- Logging e resiliente: falha de log nao bloqueia o jogo.
