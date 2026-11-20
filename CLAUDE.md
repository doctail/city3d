# Year Built — regole obbligatorie (token e velocità)

Valgono per la chat principale e per TUTTI gli agenti (yb-*).

## Risposte veloci
- Risposte brevi: prima il risultato, poi al massimo 5-10 righe. Niente preamboli, niente riassunti di ciò che hai appena fatto.
- Un report di agente: max 30 righe, nessun log grezzo, nessun dump di file. Solo percorsi e numeri.
- Leggi solo ciò che serve (offset/limit, grep mirato). Non rileggere file già letti né file appena modificati.
- Mai incollare output lunghi: `| head`, `| tail`, `grep -c`. Log completi su file, in chat solo l'estratto.
- Chiamate indipendenti in parallelo, nello stesso turno.

## Modelli e agenti
- La chat gira su Sonnet. Agenti con modello esplicito: yb-scout haiku; yb-historian/yb-modeler/yb-qa sonnet. Max 2-3 in parallelo.
- Non lanciare agenti per cose che si fanno con 1-2 tool call. Gli agenti fanno il lavoro misurabile; la chat non improvvisa.
- Nessun agente scrive codice fuori dal suo step, né tocca altri branch, né avvia un pod.

## Costi
- Tutto ciò che è misurabile si misura in locale prima del pod. Pod acceso solo su GO scritto del proprietario.
- Crediti vidIQ: dichiara il costo prima di spendere, registra nel LEDGER.
- Prima di dare un'informazione verificala con uno strumento; tag [Certain]/[Likely]/[Guessing].

## Riferimenti
`kit/AVVIO_NUOVA_CITTA.md` (leggi il POST-MORTEM LYON), `kit/ATLANTE_DATI.md`, `kit/STORY_SCHEMA.md`.
