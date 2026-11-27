# Istruzioni permanenti

## Regola universale di brevità (ordine del proprietario, 24/11/2026)
- Rispondi con il MINIMO di parole, in chat e in ogni agente (anche quelli dei plugin ECC): massimo 15 righe di rapporto, dettagli in file. Prima riga = esito o problema.
- Plugin ECC e raea sono abilitati da `.claude/settings.json` (hook ECC in profilo minimal, GateGuard spento). Usa solo agenti/skill ECC utili (review, build-fix, sicurezza), mai in automatico dopo ogni modifica.

## Regole anti-spreco token e agenti (ordine del proprietario, 27/11/2026, dopo Roma)
- **Prima di lanciare un agente su una città, controlla TUTTI i branch** (`git branch -r | grep -i <città>`, `git log --all --grep`) e Nodum. Il lavoro può essere su `yb/<città>` o `yb/integ`, non su main. Mai ricreare `story.json`, QA o regia già esistenti.
- **Il proprietario dice "finiamo X" = si finisce X.** Non cercare cronologie né chiedere conferme sulla scelta.
- **Un agente alla volta** (massimo 2 solo se indipendenti), modello esplicito, lavoro intero, UN solo rapporto finale (max 12 righe).
- **Agenti: nessun processo in background lasciato attivo** alla chiusura (rendering, pip, script). Se serve un lavoro lungo, aspettare che finisca e poi riportare. Altrimenti riportano più volte lo stesso rapporto.
- **Rapporto duplicato di un agente: non rispondere**, nessun commento al proprietario.
- Non tentare merge di branch grandi (es. `yb/integ`) sul branch di lavoro: usa un `git worktree` separato.
