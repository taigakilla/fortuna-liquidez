---
name: padrao
description: Revisa ou escreve um padrão encontrado nos dados para a Parte 1 do painel do hackathon Fortuna, no formato "Clientes com X têm inadimplência de N%, contra M% da média. Afeta K clientes.", conferindo se a explicação está correta. Use quando pedirem para revisar, escrever, formatar ou checar um padrão, achado ou insight.
---

# Padrão para o painel

A banca dá 25% da nota para padrões **e só conta o padrão se a explicação estiver correta**. O leitor é o analista de risco.

## Formato obrigatório

> Clientes com [característica] têm inadimplência de [N]%, contra [M]% da média. Afeta [K] clientes.

## Checagem (responder item a item, curto)

1. **Característica** em linguagem de negócio, sem nome de coluna nem jargão de modelo ("usaram cheque especial em 4 ou mais dos últimos 12 meses", não `dias_cheque_especial>0 count>=4`).
2. **Inadimplência** com definição clara e igual no grupo e na média: numerador (`inadimplente`? inclui `em_atraso`?) e denominador (todos os aprovados? só contratos com tempo suficiente?). Se usar a taxa bruta, avisar que contratos em andamento deixam o número otimista (`docs/09-insights.md`).
3. **Média** calculada no mesmo universo do grupo (ex.: aprovados do histórico), não na base toda.
4. **Afeta K clientes**: K do histórico, e se possível quantos dos 2.000 novos têm a característica.
5. **Tamanho do grupo**: abaixo de ~50 aprovados, avisar que o número é frágil.
6. **Causalidade**: não dizer "causa"; é associação. Se o grupo só existe via piloto, dizer isso.
7. **Ligação com a política**: qual passo da política proposta usa esse padrão (o painel tem que fechar padrões → política).
8. **Variável sensível** (gênero, estado civil, idade, CEP): sinalizar e sugerir como defender ou trocar.

Se houver banco no ar, conferir os números com o molde 5 de `sql/consultas.md` antes de aprovar o texto. Não subir o banco por conta própria.

Entregar no fim a frase final pronta para colar no painel.
