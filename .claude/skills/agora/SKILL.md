---
name: agora
description: Diz o que o suporte do time deve fazer agora no hackathon Fortuna, pelo horário atual — próximo marco (checkpoint 14h15, code freeze 15h30, pitch 15h45), tempo restante e itens pendentes do checklist. Use quando perguntarem "o que falta", "o que faço agora", "quanto tempo temos" ou pedirem status do dia.
---

# O que fazer agora

1. Pegar a hora: `date +%H:%M`.
2. Ler `docs/02-agenda.md` e `docs/10-suporte.md`.
3. Responder em até 8 linhas:
   - hora atual e **próximo marco** com o tempo que falta (destacar 14h15 e 15h30);
   - os itens do checklist do bloco atual que ainda estão abertos (`- [ ]`);
   - um alerta se faltar menos de 30 min para 15h30: parar de mexer na política, gerar o CSV final, validar (`/validar-csv`) e mandar.
4. Se o usuário disser que um item foi feito, marcar `- [x]` em `docs/10-suporte.md`.
