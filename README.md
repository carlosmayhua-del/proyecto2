# Damas Chinas

Este módulo reorganiza el juego de damas chinas en un archivo separado con:

- funciones ordenadas por timeline y dependencia.
- persistencia de partidas en `partidas.json`.
- registro tabular de juegos jugados.
- visualización del tablero final de partidas seleccionadas.
- piezas coloreadas usando `colorama`.

## Requisitos

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Uso

```bash
python damas_chinas.py
```

Luego selecciona:

- `1` para jugar una partida local.
- `2` para jugar contra la computadora.
- `3` para ver el registro de partidas.
- `0` para salir.
