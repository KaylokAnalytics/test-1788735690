# Repertorio de ajedrez — fácil de aprender, con estilo

Repertorio pensado para un jugador práctico que quiere:
- **Ganar partidas reales contra rivales sub-2000** (no memorizar teoría inútil).
- **Poco estudio**: aprender *planes*, no kilómetros de variantes.
- **Estilo**: posiciones desequilibradas, ataques y trampas concretas.

> **Aviso honesto:** ningún repertorio "garantiza" la victoria. Esto lo que
> garantiza es que *siempre* juegas posiciones sanas y jugables, y que el
> rival sub-2000 tendrá que resolver problemas reales cada partida.

## La idea central

El árbol se reduce con esta regla de oro:

> **Si la respuesta del rival desemboca en una posición parecida a tu
> estructura principal, no la memorizas: la juegas con tu plan.**

Un repertorio "de sistema" no necesita 500 variantes. Necesita:
1. Un **tronco** de 12-15 jugadas.
2. Un **plan** claro que se repite en casi todas las variantes.
3. **2-3 respuestas del rival** a conocer en cada cruce.
4. **1-2 trampas/cebos** por línea (oro puro contra sub-2000).

## Aperturas elegidas

| Color | Apertura | Archivo |
|---|---|---|
| Blancas | **Gambito de Dama** (si el rival juega `...d5`) | `blancas.md` |
| Blancas | **Sistema Londres** (si el rival juega `...Nf6`) | `blancas.md` |
| Negras vs `1.e4` | **Caro-Kann Avanzada** (`...c6 ...Bf5`) | `negras-e4.md` |
| Negras vs `1.d4` | **Gambito de Dama Rehusado** (`...e6 ...Nf6`) | `negras-d4.md` |
| Cualquier color | **Remates y conversión** | `remates.md` |

## El método de 4 niveles

- **Nivel 1 — Tronco:** las jugadas principales. Es lo único "obligatorio".
- **Nivel 2 — Plan:** qué hacer cuando el rival no sigue el tronco. Se aplica
  casi siempre el mismo plan → no memorizar.
- **Nivel 3 — Cruces críticos:** top 3 respuestas razonables del rival por
  posición clave.
- **Nivel 4 — Cebos:** 1-2 trucos por apertura para coleccionar colgadas.

## Qué NO estudiar (regla anti-árbol)

- Líneas que el rival sub-2000 jamás jugará (los "mails de la teoría").
- Refutaciones a gambitos raros: con el plan base basta.
- Variantes donde la posición resultante te gusta aunque la "teoría" diga
  `=`. Si el resultado te da un juego cómodo, esa línea ya es tuya.

## Archivos

- `blancas.md` — GQ clásico + Sistema Londres, con planes y trampas.
- `negras-e4.md` — Caro-Kann Avanzada.
- `negras-d4.md` — QGD contra todo el mundo de `1.d4` y laterales.
- `remates.md` — convertir la ventaja (donde más puntos se pierden).
- `cheatsheet.md` — 1 página imprimible: troncos, disparadores, cebos.
- `pgn/blancas.pgn`, `pgn/negras.pgn` — importables a Lichess/Chessable.