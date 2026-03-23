# PLANIFICACAO.md - Projeto Final Quiz (Python)

## 1) Objetivo e abordagem

Implementar um quiz de consola em Python com arquitetura modular, sem classes, usando apenas:

- estruturas de controlo
- listas
- dicionários
- ficheiros JSON
- funções
- módulos

Meta deste plano: cobrir os requisitos funcionais do enunciado, com foco em:

- MVP completo
- Nível 2: dificuldade, anti-repetição, pontuações e explicações
- Nível 3: A, B e C

---

## 2) Requisitos funcionais (checklist completo)

### 2.1 MVP (obrigatório)

- [x] Carregar `data/perguntas.json`
- [x] Validar: ficheiro existe, não vazio, campos mínimos (`pergunta`, `opcoes`)
- [x] Menu principal com opções obrigatórias:
  - [x] (1) Jogar
  - [x] (2) Regras / Ajuda
  - [x] (3) Top 10
  - [x] (4) Campeonato
  - [x] Saída por comando de prompt (`sair`/`0`)
- [x] Modo de jogo:
  - [x] Escolher 10 perguntas aleatórias
  - [x] Mostrar pergunta e opções numeradas
  - [x] Pedir e validar resposta (letras, vazio, fora de intervalo)
  - [x] Informar acerto/erro
  - [x] Atualizar pontuação
- [x] Resumo final:
  - [x] Pontuação total
  - [x] Nº certas/erradas
  - [x] Percentagem
- [x] Re-jogar sem reiniciar a aplicação

### 2.2 Nível 2 (implementação final)

- [x] A) Filtro por dificuldade (`facil`, `media`, `dificil`)
- [x] A) Opção "todas"
- [x] B) Não repetir perguntas na sessão
- [x] B extra) Evitar repetição entre sessões enquanto existirem novas
- [x] C) Pedir nickname
- [x] C) Guardar resultado em `data/pontuacoes.json`
- [x] C) Mostrar Top 10 no menu
- [x] D) Mostrar `explicacao` (quando existir)

### 2.3 Nível 3 (todos os opcionais implementados)

- [x] A) Modo contra-relógio (20 segundos fixos por pergunta)
- [x] B) Pontos por dificuldade (1/2/3)
- [x] C) Modo campeonato (2 jogadores, melhor de 3 rondas)

---

## 3) Decisões técnicas importantes

- Sem classes; estado do jogo será guardado em dicionários.
- Persistência em JSON:
    - `data/perguntas.json`
    - `data/pontuacoes.json`
    - `data/historico_perguntas.json` (extra para evitar repetição entre sessões)
- Compatibilidade com `resposta` em formato:
    - índice numérico
    - texto da opção correta
- Validação defensiva em todas as entradas do utilizador.

---

## 4) Modelo de dados (com exemplos)

### 4.1 Pergunta em memória (`dict`)

```python
{
    "id": "p001",
    "pergunta": "Qual e a capital de Portugal?",
    "opcoes": ["Porto", "Lisboa", "Faro", "Braga"],
    "resposta": "Lisboa",
    "categoria": "geografia",
    "dificuldade": "facil",
    "explicacao": "Lisboa e a capital oficial de Portugal desde 1255."
}
```

### 4.2 Estado de uma sessão de jogo (`dict`)

```python
{
    "nickname": "nuno",
    "modo": "relogio",  # modo atual da sessao de jogo
    "config": {
        "num_perguntas": 10,
        "categoria": "todas",
        "dificuldade": "todas",
        "tempo_limite": 20,
        "pontuacao_por_dificuldade": True,
        "mostrar_explicacao": "apos_resposta"
    },
    "ids_usadas_sessao": ["p001", "p004"],
    "resultado": {
        "pontos": 3,
        "certas": 3,
        "erradas": 2,
        "percentagem": 60.0,
        "tempo_total_seg": 42
    }
}
```

### 4.3 Registo de pontuação persistida (`data/pontuacoes.json`)

```python
[
    {
        "nickname": "nuno",
        "data_iso": "2026-03-23T15:00:00",
        "modo": "relogio",
        "pontos": 8,
        "certas": 4,
        "erradas": 1,
        "percentagem": 80.0,
        "num_perguntas": 10,
        "categoria": "todas",
        "dificuldade": "media"
    }
]
```

### 4.4 Histórico de IDs usados entre sessões (`data/historico_perguntas.json`)

```python
{
    "ids_usadas_global": ["p001", "p002", "p003"]
}
```

Regras:

- Se todas as perguntas elegíveis já tiverem sido usadas globalmente, limpa histórico para esse universo e volta a começar.

---

## 5) Entradas / Processamento / Saídas

| Entradas                      | Processamento                         | Saídas                                        |
| ----------------------------- | ------------------------------------- | --------------------------------------------- |
| `data/perguntas.json`              | leitura + validação de schema mínimo  | lista de perguntas válidas em memória         |
| escolha do menu               | validação de opção                    | navegação entre fluxos                        |
| `10` perguntas por sessão     | seleção fixa por dificuldade          | seleção aleatória sem repetição               |
| resposta do jogador           | normalização e comparação com correta | feedback acerto/erro + atualização de pontos  |
| filtro dificuldade            | filtrar lista base por dificuldade    | conjunto elegível para sessão                 |
| nickname                      | validação (não vazio, tamanho limite) | identificador para ranking                    |
| resultado final               | serializar e guardar em JSON          | histórico persistente                         |
| pedido Top 10                 | ordenar por pontos/percentagem/data   | tabela Top 10 no terminal                     |
| tempo limite por pergunta     | medir tempo decorrido                 | resposta válida ou marcada como fora de tempo |
| modo campeonato               | repetir rondas por jogador            | vencedor por ronda e vencedor final           |

---

## 6) Estrutura de ficheiros / módulos

```text
.
├── main.py
├── README.md
├── 11_projeto_final_python.md
├── src/
│   ├── app/
│   │   ├── app_service.py
│   │   ├── jogo_flow.py
│   │   └── campeonato_flow.py
│   ├── domain/
│   │   ├── jogo_service.py
│   │   ├── campeonato_service.py
│   │   ├── perguntas_service.py
│   │   └── pontuacoes_service.py
│   ├── infra/
│   │   ├── config.py
│   │   ├── json_store.py
│   │   └── log_service.py
│   └── ui/
│       ├── ui.py
│       ├── menu.py
│       └── validacao.py
├── data/
│   ├── perguntas.json
│   ├── pontuacoes.json
│   ├── historico_perguntas.json
│   └── logs_eventos.json
└── docs/
    ├── SPEC.md
    ├── PLANIFICACAO.md
    └── CHANGELOG.md
```

### Responsabilidade por módulo

- `main.py`: ponto de entrada único (`python3 main.py`).
- `src/app`: bootstrap/menu e fluxos interativos.
- `src/domain`: regras de negócio de jogo, perguntas, pontuações e campeonato.
- `src/infra`: constantes, JSON store e logging.
- `src/ui`: apresentação e validação de input.
- `data/`: persistência de perguntas, histórico, pontuações e logs.
- `docs/`: documentação técnica de suporte.

---

## 7) Documentação em Python

### 7.1 Padrão para cada ficheiro (`module docstring`)

Cada ficheiro começa com docstring com objetivo, responsabilidades, dependências e funções públicas.

Exemplo:

```python
"""jogo_service.py

Responsabilidade:
    Executar uma sessão de jogo com contra-relogio fixo, processando
    perguntas, respostas e pontuacao.

Dependencias:
    - perguntas_service
    - validacao
    - time

Funcoes publicas:
    - jogar_sessao
    - calcular_resumo
"""
```

### 7.2 Padrão para cada função (`function docstring`)

Formato recomendado (estilo Google/ReST simples):

```python
def carregar_perguntas(caminho):
    """Carrega perguntas de um ficheiro JSON.

    Args:
        caminho (str): Caminho do ficheiro de perguntas.

    Returns:
        list[dict]: Lista de perguntas validadas.

    Raises:
        FileNotFoundError: Quando o ficheiro nao existe.
        ValueError: Quando o conteudo JSON e invalido.
    """
```

Regra de projeto:

- Todas as funções públicas e internas terão docstring.
- Sem exceções para funções "pequenas".

---

## 8) Lista de funções (sem classes)

| Função                                                      | Módulo                  | Descrição                                                  |
| ----------------------------------------------------------- | ----------------------- | ---------------------------------------------------------- |
| `iniciar_aplicacao()`                                       | `main.py`               | Arranca app, carrega dados base, entra no loop principal.  |
| `ciclo_menu_principal()`                                    | `main.py`               | Mostra menu e encaminha ações até sair.                    |
| `mostrar_menu_principal()`                                  | `menu.py`               | Mostra opções obrigatórias e extras.                       |
| `ler_opcao_menu(min_opcao, max_opcao)`                      | `menu.py`               | Lê e valida opção numérica.                                |
| `mostrar_regras()`                                          | `ui.py`                 | Mostra ajuda/regras do jogo.                               |
| `mostrar_mensagem_erro(texto)`                              | `ui.py`                 | Output uniforme para erros.                                |
| `mostrar_resumo(resultado)`                                 | `ui.py`                 | Exibe resumo final formatado.                              |
| `carregar_json(caminho, valor_default)`                     | `json_store.py`         | Lê JSON; cria default se não existir.                      |
| `guardar_json(caminho, dados)`                              | `json_store.py`         | Guarda dados em JSON com indentação.                       |
| `carregar_perguntas(caminho)`                               | `perguntas_service.py`  | Carrega e valida perguntas do ficheiro.                    |
| `validar_lista_perguntas(perguntas)`                        | `perguntas_service.py`  | Valida estrutura global da lista.                          |
| `validar_pergunta(pergunta)`                                | `perguntas_service.py`  | Valida campos mínimos e coerência por pergunta.            |
| `normalizar_indice_resposta(pergunta)`                      | `perguntas_service.py`  | Converte resposta correta em índice de opção.              |
| `listar_categorias(perguntas)`                              | `perguntas_service.py`  | Extrai categorias únicas.                                  |
| `filtrar_perguntas(perguntas, categoria, dificuldade)`      | `perguntas_service.py`  | Filtra por critérios ou "todas".                           |
| `selecionar_perguntas_aleatorias(perguntas, n, ids_evitar)` | `perguntas_service.py`  | Seleciona N sem repetição.                                 |
| `atualizar_historico_global(ids_novas)`                     | `perguntas_service.py`  | Guarda IDs usados entre sessões.                           |
| `obter_ids_historico_global()`                              | `perguntas_service.py`  | Carrega IDs usados globalmente.                            |
| `reiniciar_historico_se_necessario(ids_elegiveis)`          | `perguntas_service.py`  | Reseta histórico quando esgota universo elegível.          |
| `pedir_nickname()`                                          | `validacao.py`          | Lê nickname válido.                                        |
| `pedir_inteiro_intervalo(prompt, minimo, maximo)`           | `validacao.py`          | Input numérico robusto.                                    |
| `pedir_confirmacao(prompt)`                                 | `validacao.py`          | Lê confirmação sim/não.                                    |
| `pontuar_resposta(correta, dificuldade, usar_pesos)`        | `jogo_service.py`       | Calcula pontos ganhos numa pergunta.                       |
| `fazer_pergunta(pergunta, config)`                          | `jogo_service.py`       | Mostra pergunta, lê resposta e devolve resultado unitário. |
| `fazer_pergunta_relogio(pergunta, config)`                  | `jogo_service.py`       | Variante com limite temporal.                              |
| `jogar_sessao(perguntas, config, nickname)`                 | `jogo_service.py`       | Executa sessão completa e devolve resultado final.         |
| `calcular_percentagem(certas, total)`                       | `jogo_service.py`       | Percentagem de acertos.                                    |
| `guardar_resultado(resultado)`                              | `pontuacoes_service.py` | Persiste resultado no histórico.                           |
| `obter_top10()`                                             | `pontuacoes_service.py` | Ordena e devolve 10 melhores resultados.                   |
| `mostrar_top10()`                                           | `pontuacoes_service.py` | Imprime ranking no terminal.                               |
| `jogar_campeonato(perguntas, config_base, jogador_1, jogador_2)` | `campeonato_service.py` | Coordena melhor de 3 rondas para 2 jogadores.         |
| `jogar_ronda_campeonato(jogador, perguntas_ronda, config)`  | `campeonato_service.py` | Executa uma ronda para um jogador.                         |
| `determinar_vencedor_campeonato(placar)`                    | `campeonato_service.py` | Decide vencedor final.                                     |

---

## 9) Fluxo do programa (detalhado)

1. `main.py` arranca aplicação.
2. Carrega perguntas com validação.
3. Mostra menu principal:
    - 1 Jogar
    - 2 Regras/Ajuda
    - 3 Top 10
    - 4 Modo Campeonato
4. Se escolha inválida, mostrar erro e repetir.
5. Em "Jogar":
    - pedir nickname
    - pedir dificuldade (ou "todas")
    - usar 10 perguntas fixas
    - montar conjunto elegível
    - aplicar regra anti-repetição (sessão + global)
    - iniciar sessão com contra-relógio fixo (20s por pergunta)
6. Para cada pergunta:
    - mostrar enunciado/opções
    - ler resposta com validação
    - verificar tempo (se modo relógio)
    - verificar acerto
    - atribuir pontos por dificuldade (1/2/3)
    - mostrar explicação, se existir
7. No final da sessão:
    - calcular resumo
    - mostrar resultados
    - guardar pontuação
    - atualizar histórico de perguntas usadas
    - perguntar se quer re-jogar
8. Em "Top 10": carregar, ordenar e mostrar ranking.
9. Em "Campeonato":
    - pedir dois nicknames
    - jogar 3 rondas
    - cada ronda: dois jogadores respondem ao mesmo conjunto de perguntas
    - atualizar placar de rondas e pontos totais
    - declarar vencedor
10. Em qualquer input: escrever `sair` ou `0` para terminar app sem crash.

---

## 10) Estratégia para requisitos opcionais difíceis

### 10.1 Contra-relógio (Nível 3-A)

Implementação base (portável):

- medir `inicio = time.time()` antes do input
- medir `fim` após input
- se `fim - inicio > limite`, resposta conta como errada

Observação:

- esta abordagem é simples, sem threads e sem classes, e cumpre a regra funcional de tempo limite.

### 10.2 Evitar repetição entre sessões (Nível 2-B extra)

- Guardar IDs em `data/historico_perguntas.json`.
- Filtrar universo elegível removendo IDs já usados.
- Se não houver suficientes perguntas novas:
    - resetar histórico para o universo atual
    - continuar seleção normalmente.

### 10.3 `resposta` como int ou str

- Se for `int`: converter para índice válido (aceitar 0-based e 1-based, se coerente).
- Se for `str`: procurar opção com texto equivalente (normalização por trim/lower).

---

## 11) Plano de implementação por fases

### Fase A - Fundação (Dia 1)

- Criar estrutura de módulos e constantes.
- Implementar utilitários JSON e validação de input.
- Implementar carga/validação de perguntas.
- Entregável: app abre, lê JSON, mostra menu funcional.

### Fase B - MVP completo (Dias 2-3)

- Implementar sessão de jogo base.
- Implementar resumo final e re-jogar.
- Tratar inputs inválidos em todos os pontos críticos.
- Entregável: requisitos 5.1 concluídos.

### Fase C - Nível 2 completo (Dias 4-5)

- Filtro por dificuldade.
- Não repetição sessão + global.
- Persistência de pontuações + Top 10.
- Mostrar explicações.
- Entregável: requisitos 5.2 A/B/C/D + extra concluídos.

### Fase D - Nível 3 completo (Dias 6-7)

- Modo contra-relógio fixo (20s).
- Pontuação por dificuldade sempre ativa.
- Campeonato melhor de 3.
- Entregável: requisitos 5.3 A/B/C concluídos.

### Fase E - Qualidade e entrega (Dia 8)

- Testes manuais completos.
- Correções finais.
- README e revisão de docstrings.

---

## 12) Plano de testes manuais (min 7, aqui: 17)

1. Menu: inserir letra (`a`) e confirmar que repete sem crash.
2. Menu: inserir número fora do intervalo e repetir pedido.
3. `data/perguntas.json` em falta: mostrar erro claro e encerrar com segurança.
4. `data/perguntas.json` vazio: impedir jogo e informar problema.
5. Pergunta sem `opcoes`: detetar inválida e não usar.
6. Resposta com campo `resposta` textual: avaliação correta.
7. Resposta com campo `resposta` numérica: avaliação correta.
8. Verificar que a sessão usa 10 perguntas fixas.
9. Garantir não repetição na mesma sessão.
10. Garantir não repetição entre sessões enquanto houver novas perguntas.
11. Top 10: guardar múltiplos resultados e confirmar ordenação correta.
12. Filtro dificuldade: escolher `media` e receber apenas `media`.
13. Opção `todas` no filtro: incluir universo completo.
14. Explicação: mostrar quando campo existe; omitir sem crash quando não existe.
15. Contra-relógio: validar limite fixo de 20s e contagem como errada fora do tempo.
16. Pontuação por dificuldade: verificar valores 1/2/3 sempre ativos.
17. Campeonato: simular 3 rondas e confirmar vencedor correto.

---

## 13) Critérios de pronto (Definition of Done)

- Todos os itens do checklist da secção 2 marcados como concluídos.
- Nenhum fluxo principal crasha com input inválido.
- Todos os módulos e funções têm docstrings completas.
- Projeto executa com `python main.py`.
- `README.md` descreve execução e funcionalidades.

---

## 14) Riscos e mitigação

- Risco: inconsistências no formato de `resposta`.
    - Mitigação: normalização centralizada (`normalizar_indice_resposta`).

- Risco: poucos dados para uma dificuldade específica.
    - Mitigação: mensagens claras e possibilidade de escolher "todas".

- Risco: histórico global bloquear novas sessões.
    - Mitigação: reset automático quando universo elegível esgotar.

- Risco: complexidade do modo campeonato.
    - Mitigação: reutilizar `jogar_sessao` por ronda, só variando config.

---

## 15) Resumo final do plano

Este plano implementa o quiz completo com arquitetura modular, sem classes, com persistência JSON e documentação equivalente a JSDoc em Python (docstrings de módulo e função), cobrindo integralmente:

- MVP
- Nível 2 (com dificuldade, anti-repetição, pontuações e explicações)
- Nível 3 inteiro (todos os opcionais)
