# Con blancas: `1.d4`

Doble sistema según la respuesta de las negras:

- Si juegan `1...d5` → **Gambito de Dama clásico** (`2.c4`).
- Si juegan `1...Nf6` (la mayoría) → **Sistema Londres** (`2.Bf4`, `3.e3`, `4.c3`).

Este cambio es deliberado: contra `...Nf6` evitas toda la teoría de India de
Rey, Grünfeld y Nimzo que exigiría `2.c4`. Contra `...d5` usas tu Gambito de
Dama que ya conoces.

---

## PARTE A — Gambito de Dama (si las negras juegan `1...d5 2.c4`)

### A1. Línea madre: QGD ortodoxa (`2...e6`)

```
1. d4 d5 2. c4 e6 3. Nf3 Nf6 4. Bg5 Be7 5. e3 O-O 6. Nc3 Nbd7 7. Rc1 c6
8. Bd3 dxc4 9. Bxc4 Nd5 10. Bxe7 Qxe7
```

- **Plan:** tras `10...Qxe7`, juega `11.0-0` y luego la **minoría** `b2-b4-b5`
  para crear debilidades en `c6`, o el avance central `e3-e4` con `Qd3/Qc2`
  y `Ne5`. La columna `c` es tuya.
- **Qué NO memorizar:** si las negras no juegan `...dxc4` y retrasan el
  alivio, juegas el plan de siempre (castillo, `Rc1`, `Qc2`, `e3-e4`).
- **Tema a explotar:** si en cualquier momento las negras expulsan el alfil
  de `c4` con `...b5`, **no retrocedas pasivamente a `Bd3`**: juega `Bb3!`
  y prepara `a2-a4`. El peón `b5` queda débil para siempre y la columna `a`
  abre sola. Es una debilidad que los sub-2000 no saben cuidar.

### A2. Contra la Eslava (`2...c6`)

```
1. d4 d5 2. c4 c6 3. Nf3 Nf6 4. Nc3 dxc4 5. a4 Bf5 6. e3 e6 7. Bxc4 Bb4
8. O-O O-O
```

- **Plan:** `8...O-O 9.Qe2` (protege `e3`) y luego `e3-e4` expulsando el
  alfil de `f5` (`Ne5` o `e4`) para ganar espacio. El centro y la ventaja de
  desarrollo presionan casi solos.
- Alternativa tranquila de las negras: `7...e6 8.O-O Nbd7 9.Qe2` — mismo plan.

### A3. Contra el Gambito de Dama Aceptado (`2...dxc4`)

```
1. d4 d5 2. c4 dxc4 3. Nf3 Nf6 4. e3 e6 5. Bxc4 c5 6. O-O a6 7. Qe2 b5?!
8. Bb3 Bb7 9. Rd1 Nbd7 10. Nc3
```

- **Plan:** no premio a las negras. Si `7...b5?! 8.Bb3`, el peón de `b5`
  queda flojo con `a2-a4` a la vista; si no avanzan `b5`, juegas eso mismo
  con peón `d4-d5` o `e3-e4` ganando centro.
- **Cebo:** si las negras se apresuran a jugar `...a6`+`...b5` **antes de
  desarrollar** (`3...e6 4.e3 a6? 5.Bxc4 b5 6.Bb3`), `a2-a4` deja su flanco
  de dama bajo presión eterna: el `b4`/`b5` se vuelve un peón flojo de por
  vida en cuanto `axb5` obliga a recapturar con pieza.

---

## PARTE B — Sistema Londres (si las negras juegan `1...Nf6`)

Un *sistema* puro: mismo setup contra casi cualquier cosa, con plan claro
posicional **y** opción de ataque. Es el reemplazo sólido del antiguo
"Jobava", que tenía un fallo táctico grave (la dama se ganaba en una variante
de enroques opuestos). Esto está verificado jugada a jugada con motor.

### B1. Línea madre (Londres vs `...Nf6 ...d5`)

```
1. d4 Nf6 2. Bf4 d5 3. e3 c5 4. c3 Nc6 5. Nd2 e6 6. Ngf3 Bd6 7. Bg3 O-O
8. Bd3 b6 9. O-O
```

- **Plan A (posicional):** desarrollo completo, `Qe2/Qc2`, `Rad1`; avance
  central `e3-e4` (con `Ne5` previo) cuando las negras claven su `...d5`.
- **Plan B (ataque):** `Ne5!` (con `h3` antes si el alfil negro pasea),
  paraguas `f2-f4` y presión sobre `g7/h7`. Es la forma estándar del Londres
  de jugar con estilo sin arriesgar nada.
- **Qué NO memorizar:** cualquier desarrollo razonable del rival se responde
  con el mismo setup. Si las negras no juegan `...c5` (p. ej. `2...d5 3.e3
  Bf5/6`), haces lo mismo: `Nd2-Nf3`, `Bd3`, `0-0`, y luego el plan A o B.
- **Tu tema táctico de seguridad (IMPORTANTE):** las negras suelen probar
  `...Qb6` atacando `b2`. **Nunca** juegues tu siguiente jugada sin defender
  `b2`: responde `Qb3!` (cambio de damas, final igualado y sin riesgo) o
  `Rb1`. Si te descuidas, `...Qxb2` es un peón gratis para ellas (verificado:
  ganan la partida con `-1.8`). Es el mismo motivo que encontramos en la Caro.

### B2. Contra el ala `...g6` (Moderno / India de Rey)

```
1. d4 Nf6 2. Bf4 g6 3. e3 Bg7 4. Nf3 O-O 5. Be2 d6 6. O-O
```

- **Plan:** como el rival no controla `e5` con un peón, el alfil de `f4`
  apunta directo a `e5`/`h6`. Desarrollo natural y luego `c2-c4` (o `b2-b4`)
  en el flanco de dama; o el plan de ataque `Ne5-f4`. Nada que memorizar:
  es el mismo Londres, con `Be2` en vez de `Bd3`.
- **No** te tiente perseguir la columna `h` con caballos a la antigua: el
  plan por el centro y el flanco de dama es el correcto (balanceado en el
  motor).

---

## Resumen ejecutivo (blancas)

1. `1.d4`: si `...d5` → Gambito de Dama; si `...Nf6` → **Sistema Londres**.
2. Londres: `2.Bf4 3.e3 4.c3 5.Nd2 6.Ngf3 7.Bg3 8.Bd3` y `0-0`; luego Plan A
   (centro) o Plan B (ataque `Ne5-f4`).
3. Regla de oro: **si el rival juega `...Qb6`, defiende `b2` con `Qb3` o
   `Rb1` — nunca desarrolles sin eso.**
4. Tu objetivo real de partida: el enroque del rival o la columna `c` abierta.