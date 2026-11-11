# 10 · Suporte: checklist e perguntas ao cliente

## Checklist por horário

### Até 08h40 (leitura)
- [x] Banco restaurado e contagem conferida (10.000 / 2.000).
- [x] Token do bureau recebido e salvo em `.env`; `/health` respondendo.
- [x] Bureau dos 2.000 novos baixado e carregado (`dados/bureau_novos.csv`).
- [x] Política atual reproduzida e base de comparação gerada (`saida/politica_atual.csv`).
- [ ] Papéis divididos: dados, IA, painel, pitch.
- [ ] Marcar janela de 15 min com o cliente no canal.

### Manhã (08h40–12h00)
- [ ] Primeiros padrões no formato do painel (`/padrao`).
- [ ] Decidido como tratar contratos em andamento (`09-insights.md`).

### 13h00–14h15
- [ ] Primeira versão do CSV gerada pelo código.
- [ ] `/validar-csv` passou.
- [ ] **Até 14h15**: CSV mandado no canal para o checkpoint.
- [ ] Perguntas preparadas para os 10 min com o mentor.

### 14h15–15h30
- [ ] Ajustes pós-checkpoint anotados (o pitch precisa dizer o que mudou).
- [ ] Painel com Parte 1 (padrões) e Parte 2 (política em passos).
- [ ] Validação oficial pedida de novo no canal com a versão final.
- [ ] **Até 15h30**: `<time>_final.csv` + zip/link do código com README na pasta do time. Mandar com folga (15h15).

### 15h30–15h45
- [ ] Roteiro do pitch: IA no fluxo → padrões → política → mudanças pós-checkpoint → validação pelo analista.
- [ ] Demo: consultar 2–3 pedidos ao vivo e explicar a decisão.
- [ ] Respostas prontas: uso de variáveis sensíveis, pedidos sem bureau, como o analista aprova a política.

## Perguntas para o cliente (janela de 15 min)

Priorizar as que mudam a política ou a leitura dos dados:

1. Na pontuação dos novos, "pagou com atraso" inclui atraso de qualquer tamanho abaixo de 90 dias? E "não pagou" é o mesmo critério de 90 dias do `inadimplente`?
2. Para aprender no histórico, como a Fortuna trata `em_dia` e `em_atraso` (contratos em andamento)? Considera bom, ruim ou exclui?
3. O piloto aprovou com quais critérios? Existe alguma diferença de perfil intencional entre quem caiu no piloto e na atual?
4. Confirmar: a política atual reduz o valor até a parcela caber em 30% da renda, em vez de negar? (O histórico mostra isso em 100% dos casos; ver `09-insights.md`.) A pontuação da "política atual" nos novos usa essa mesma regra de valor?
5. A política atual usa `>` ou `≥` nos limites (score 600, renda R$ 2.000)?
6. Existe restrição de negócio para usar gênero, estado civil, idade ou CEP na decisão?
7. Há preferência entre negar e reduzir valor (ex.: experiência do cliente, volume mínimo de aprovações)?
8. `renda_declarada` é verificada de alguma forma, ou a Fortuna confia mais em `entradas_salario`?
9. Pedido novo sem resposta do bureau: negar, aprovar com teto baixo, ou outra regra?

## Para a conversa com o mentor (14h15)

- Leve o relatório do checkpoint e a diferença para a política atual (quantos pedidos mudaram e em que direção).
- Pergunte sobre a explicação dos padrões (25% da nota vem disso), não só do modelo.
