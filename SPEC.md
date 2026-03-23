# SPEC.md - Contrato Funcional do Quiz Python

Data de referencia: 2026-03-23

## Regra de precedencia documental

Em caso de conflito entre documentos:

1. `SPEC.md` (fonte de verdade)
2. `README.md`
3. `PLANIFICACAO.md`

## Invariantes funcionais

- Aplicacao de consola, sem classes.
- Menu principal com 4 opcoes:
  - Jogar
  - Regras / Ajuda
  - Top 10
  - Campeonato
- Cada sessao de jogo usa sempre `10` perguntas.
- Tempo limite por pergunta sempre `20` segundos.
- Pontuacao por dificuldade sempre ativa:
  - `facil = 1`
  - `media = 2`
  - `dificil = 3`
- Comando global de saida em qualquer input: `sair` ou `0`.
- Re-jogar sem reiniciar aplicacao.

## Regras de validacao de perguntas

- O ficheiro `perguntas.json` deve conter uma lista.
- Cada pergunta valida deve ter:
  - `id` nao vazio e unico
  - `pergunta` nao vazia
  - `opcoes` (lista com pelo menos 2 opcoes nao vazias)
  - `resposta` (int ou str coerente com opcoes)
  - `categoria` nao vazia
  - `dificuldade` em `facil|media|dificil`
- Politica tolerante:
  - perguntas invalidas sao ignoradas (skip)
  - app so falha no arranque se perguntas validas < 10

## Contratos de dados persistidos

### `perguntas.json`

- Tipo: `list[dict]`
- Campos por pergunta:
  - obrigatorios: `id`, `pergunta`, `opcoes`, `resposta`, `categoria`, `dificuldade`
  - opcional: `explicacao`

### `pontuacoes.json`

- Tipo: `list[dict]`
- Campos por registo:
  - `nickname`, `data_iso`, `modo`, `pontos`, `certas`, `erradas`, `percentagem`
  - `num_perguntas`, `categoria`, `dificuldade`, `ids_usadas_sessao`
  - `detalhes` (lista com resultado por pergunta)

### `historico_perguntas.json`

- Tipo: `dict`
- Formato:
  - `{"ids_usadas_global": ["p001", "p002", ...]}`

### `logs_eventos.json`

- Tipo: `list[dict]`
- Schema por evento:
  - `timestamp_iso`: datetime ISO
  - `nivel`: `INFO|WARNING|ERROR`
  - `evento`: nome tecnico do evento
  - `contexto`: `dict`
- Falha de logging nunca deve bloquear fluxo da app.

## Fluxo de jogo

1. Jogador escolhe dificuldade (`facil|media|dificil|todas`).
2. Sistema filtra perguntas por dificuldade.
3. Sistema escolhe 10 perguntas aleatorias, sem repeticao na sessao e priorizando nao repetidas globalmente.
4. Cada resposta e validada e avaliada com tempo limite de 20s.
5. App mostra feedback imediato (correta/errada/fora de tempo) e explicacao quando existir.
6. Resultado final e mostrado e guardado em `pontuacoes.json`.
7. IDs da sessao sao guardadas em `historico_perguntas.json`.

## Fluxo campeonato

- Dois jogadores, melhor de 3 rondas.
- Em cada ronda, ambos respondem ao mesmo conjunto de 10 perguntas.
- Vitoria da ronda por maior pontuacao da ronda.
- Desempate final por pontos totais.
