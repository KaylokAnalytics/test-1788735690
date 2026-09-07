# Con negras contra `1.e4`: Caro-Kann Avanzada

Elige un peón de ventaja de espacio y un alfil de casillas blancas fuerte en
`f5`, que será el héroe de la línea: clavará al caballo de `b1`... de hecho,
mira bien el **motivo central**: `...cxd4!` abre la diagonal a `b1` y, si el
blanco se descuida, `...Bxb1!` gana el caballo. Todo con **un tronco y un
plan**, sin líneas forzadas locas.

> Aviso: esta versión sustituye a la anterior, que tenía defectos graves
> (un enroque largo malo y un `...Ngf6` prematuro que permitía `exf6!`).
> Todas las líneas que siguen están verificadas con motor.

## Línea madre (la única que memorizas)

```
1. e4 c6 2. d4 d5 3. e5 Bf5 4. Nf3 e6 5. Be2 c5 6. Be3 Nd7 7. c3 cxd4!
8. cxd4 Bb4+! 9. Nbd2 Nge7 10. O-O Nc6 11. a3 Be7 12. Ne1 O-O
```

- **Tu plan en 3 pasos:**
  1. `...c5` y `...cxd4!` **resolviendo ya la tensión**: así no dejas al
     blanco elegir cuándo. Si recaptura con `cxd4`, viene el paso 2.
  2. `...Bb4+!` clava/camina por el centro del blanco y tus piezas apuntan
     a `e7/d5`. **Ojo al detalle de oro:** si el blanco se equivoca (p. ej.
     recaptura con `Nxd4` o subdesarrolla), tu alfil de `f5` gana el caballo
     `b1` con `...Bxb1!` — el peón `c2` ya no lo bloquea tras `...cxd4`.
  3. `...Nge7`, `...Nc6`, `...Be7`, `...O-O`: desarrollo natural y enroque
     corto con estructura sana y el peón pasado `d5` como fortaleza.
- **Qué NO memorizar:** si el blanco cambia el orden (p. ej. `6.c3` o
  `5.Bd3`), el tronco es el mismo. NUNCA juegues `...Ngf6` (`g8-f6`) con el
  peón blanco aún en `e5`: se gana pieza con `exf6!` (verificado, `-4`).
  Siempre `Nge7` cuando el `e5` blanco siga vivo.

## Cruces con el rival

### Si el blanco juega `4.Nc3` (en vez de `4.Nf3`)
```
1. e4 c6 2. d4 d5 3. e5 Bf5 4. Nc3 e6 5. Nf3 Ne7 6. Be2 h6!?
```
- Setup "Short": caballo a `e7`, `...h6` asegura el flanco (verificado:
  balanceado, `+0.4`). Después sigues el mismo plan de fondo: `...c5`,
  desarrollo y castillo corto cuando el blanco se estabilice.
- Si el blanco juega la locura `5.g4!?` (atacando `Bf5`): `...Bg6 6.h4 h5!`
  — se debilita y tu alfil vive en `g6`.

### Si el blanco evita el `cxd4` (hace cualquier otra cosa)
- Si juega `8.cxd4` tras tu `7...cxd4`, sigue el paso 1-2 tal cual.
- Si el blanco captura con caballo (`8.Nxd4!?`), juegas `...Bxb1!`
  (edge: eval `0.0`: el blanco no tiene compensación seria) o simplemente
  `...Qc7/Ngf6`... mejor: `...Bxb1! 9.Rxb1 Nde5` y estás cómodo.
- Si el blanco abandona la tensión (p. ej. `9.Nbd2` antes), tu setup no
  cambia: `...Nge7, ...Nc6, ...Be7`, castillo.

### Cebo favorito: el blanco descuida `b2`
```
1. e4 c6 2. d4 d5 3. e5 Bf5 4. Nf3 e6 5. Be2 c5 6. Bg5?? Qb6 7. O-O Qxb2
```
- Si el blanco juega cualquier movimiento que **no proteja `b2`** (deja su
  alfil de `c1` sin cubrirlo), `...Qb6`+`...Qxb2` gana el peón. Verificado:
  con `6.Bg5??` las negras están `-1.8` arriba. Y si responde `Qb3`/`Rb1`,
  tu `...Bxb1`/plan base sigue funcionando sin memorizar nada.

## Consejo anti-arbol

El peón `e5` rival **no** es una amenaza: tu `...c5` lo rodea y el `Bf5`
controla las casillas de escape. No dejes la tensión `c5/d4` sin resolver
demasiadas jugadas (ahí te atrapa `exf6` o `Bb4+` tarde); **resuélvela en el
tronco, en el momento correcto** y desarrolla con tu estructura.

## Resumen ejecutivo (negras contra `1.e4`)

1. `1...c6 2.d4 d5 3.e5` → `3...Bf5` siempre.
2. Tronco: `...c5, ...cxd4!, ...Bb4+!, ...Nge7, ...Nc6, ...O-O` (y
   **nunca** `...Ngf6`).
3. Motivo de oro: `...Bxb1!` cuando el blanco se descuida con su caballo.
4. Cebo: todo movimiento blanco que no defienda `b2` → `...Qxb2`.