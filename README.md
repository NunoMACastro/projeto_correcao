# Quiz em Python (Projeto Final)

Aplicacao de consola para jogo de perguntas/respostas, implementada sem classes.

## Requisitos

- Python 3.x
- Sem bibliotecas externas (apenas standard library)

## Como executar

1. Abre o terminal na pasta do projeto.
2. Executa:

```bash
python3 main.py
```

## Ficheiros de dados

- `perguntas.json`: base de perguntas do quiz
- `pontuacoes.json`: historico de resultados
- `historico_perguntas.json`: IDs de perguntas usadas entre sessoes

## Funcionalidades implementadas

### MVP

- Carregamento e validacao de `perguntas.json`
- Menu principal com:
  - Jogar
  - Regras / Ajuda
  - Sair
- Jogo com 10 perguntas aleatorias por partida
- Validacao robusta de input
- Feedback de acerto/erro por pergunta
- Atualizacao de pontuacao
- Resumo final com pontos, certas/erradas e percentagem
- Re-jogar sem reiniciar a aplicacao

### Nivel 2

- Filtro por dificuldade (`facil`, `media`, `dificil`)
- Opcao `todas` no filtro de dificuldade
- Sem repeticao de perguntas na mesma sessao
- Anti-repeticao entre sessoes enquanto houver perguntas novas
- Nickname por jogador
- Guardar resultados em `pontuacoes.json`
- Top 10 no menu principal
- Mostrar explicacao da pergunta quando disponivel

### Nivel 3

- Modo contra-relogio por pergunta
- Pontuacao por dificuldade:
  - facil = 1
  - media = 2
  - dificil = 3
- Modo campeonato (2 jogadores, melhor de 3 rondas)

## Notas

- O contra-relogio esta implementado em modo funcional: resposta acima do tempo limite conta como errada.
- Podes escrever `sair` ou `0` em qualquer input para terminar a app de imediato.
