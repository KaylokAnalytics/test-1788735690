# Con negras contra `1.d4`: Gambito de Dama Rehusado + setup universal

Una sola idea lo cubre todo: **`...d5, ...e6, ...Nf6, ...Be7, ...0-0`** con la
ruptura liberadora **`...Nd5` (o `...dxc4` + `...c5`)**. Contra `1.Nf3`,
`1.c4` y `1.g3`, transpón al mismo setup con `...d5`. Un solo plan para toda
la familia `1.d4`.

## Línea madre (QGD clásico)

```
1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. Bg5 Be7 5. e3 O-O 6. Nf3 Nbd7 7. Rc1 c6
8. Bd3 dxc4 9. Bxc4 Nd5 10. Bxe7 Qxe7
```

- Esta es la famosa **"liberación capablanca"**: cambio `...dxc4`, caballo a
  `d5`, alfil contra alfil. La posición queda **igualada y sin debilidades**.
- **Plan después de `10...Qxe7`:** `11.0-0` y juegas **`...b6`, `...Bb7`,
  `...Rac8`** (lo que prefiere el motor, `+0.3` igualado), o el clásico
  `...Nxc3 12.Rxc3 e5` — en ambos casos el centro liberado. Si el blanco no
  acepta el cambio en `d5`, igualas con `...e5` o preparas `...c5`.
- **Qué NO memorizar:** cualquier transposición del blanco al mismo sistema
  (cambie el orden de `Nc3/Nf3/Bg5`) juegas **el tronco tal cual**.

## Cruces con el rival

### El blanco juega `4.Nf3` (Catalan / fianchetto)
```
1. d4 d5 2. c4 e6 3. Nf3 Nf6 4. g3 Be7 5. Bg2 O-O 6. O-O c6
```
- `6...c6` mantiene el centro peón-sólido (estructura tipo Eslava);
  plan: `...Nbd7, ...b6, ...Bb7, ...Rc8`, ruptura `...c5` o `...dxc4`
  seguido de `...c5`. Nada agresivo del blanco te asusta; es un final
  central equilibrado.
- Si el blanco en su lugar hace `4.Bg5` pasando al QGD de la madre: tronco.

### El blanco juega `2.Bf4` (Londres)
```
1. d4 d5 2. Bf4 Nf6 3. e3 c5 4. c3 Nc6 5. Nd2 e6 6. Ngf3 Bd6 7. Bg3 O-O
```
- Tu setup: `...c5` inmediato, alfil activo a `d6` (atacando `h2`), y el
  plan `...0-0` + `...Re8` + ruptura `...e5` (con `...cxd4` primero si el
  blanco aprieta). Igualdad cómoda sin teoría.
- **Cebo contra el Londres (verificado con motor):** si el blanco se descuida
  con `8.h3?` (o suelta el control de `e5`/`g3`), juega **`...Bxg3!` primero**:
  `8...Bxg3! 9.fxg3` y su flanco de rey queda roto con `...cxd4` + `...e5`
  listos detrás (eval `-2`: claramente mejor para ti). No dejes pasar ese
  alfil sin castigo.
- Si el blanco juega `Qb3` (su forma de provocar/evitar `...Qb6`): si tienes
  tu dama en `b6`, **cambia damas sin miedo** — el final es igualado y tu
  estructura queda intacta. Después, el plan base. No hay variante nueva.

### El blanco juega `2.Nf3` (Colle / sistemas de desarrollo)
```
1. d4 d5 2. Nf3 Nf6 3. e3 e6 4. Bd3 c5 5. c3 Nc6 6. O-O Bd6
```
- Mismo setup: `...c5`, `...Bd6`, `...0-0`, `...Re8`, `...e5`. El rival
  pierde el tiempo si no juega `c4`; tu igualdad llega sola.

### El blanco evita `c4` del todo (`1.Nf3`, `1.c4`, `1.g3`)
- **Universo:** responde con `...d5` (y `...e6`) y el mismo desarrollo:
  `1.Nf3 d5 2.c4 e6 3.d4 Nf6` → QGD tronco.
  `1.c4 e6 2.Nc3 d5 3.d4 Nf6` → QGD tronco.
  `1.g3 d5 2.Bg2 e6 3.Nf3 Nf6 4.d4 Be7 5.O-O O-O` → plan Catalan negro.
- Nunca necesitas "otras" aperturas para los flancos; siempre el mismo plan.

## Motivo táctico que debes ver siempre

El **cambio central en `d5`**: cuando tu caballo llega a `d5` (tras
`...dxc4`), ataca el caballo/blanco rival y libera la diagonal de tu dama a
`e7`/`c7`. Todos tus rivales sub-2000 reaccionan mal a `...Nd5`: no saben si
cambiar, retirar o avanzar. Tú decides tras ver su reacción, no antes.

## Resumen ejecutivo (negras contra `1.d4`)

1. Setup universal: `...d5, ...e6, ...Nf6, ...Be7, ...0-0`.
2. Tronco madre: `...Nbd7, ...c6, ...dxc4, ...Nd5` (liberación Capablanca).
3. Contra Londres/Colle: `...c5` + alfil `...Bd6` + ruptura `...e5`.
4. Contra flancos (`Nf3/c4/g3`): transpón con `...d5` y `...e6`.