# Reporte: Parser LR(1) con interfaz en Python

Autor: (tu nombre)
Fecha: 21/oct/2025

## Objetivo
Implementar un parser LR(1) canónico en Python y una interfaz gráfica simple para construir las tablas y analizar cadenas, reutilizando conceptos de los ejercicios previos de análisis sintáctico.

## Metodología
- Representación de la gramática en un formato BNF simple (`A -> α | β`).
- Cálculo de conjuntos FIRST para símbolos y secuencias.
- Construcción de ítems LR(1) `[A → α • β, a]`.
- Algoritmos de `closure` y `goto` para formar la colección canónica.
- Generación de tablas ACTION/GOTO:
  - `shift` cuando el punto antecede a un terminal.
  - `reduce` cuando el punto está al final (`A→α`), sobre el lookahead del ítem.
  - `accept` en el estado que contiene `S' → S •, $`.
- Ejecutor shift-reduce con traza de pasos.
- Interfaz en Tkinter para edición de gramática, construcción de tablas y análisis de cadenas.

## Referencias consultadas
- https://compiler-slr-parser.netlify.app/
- https://jsmachines.sourceforge.net/machines/lr1.html
- https://light0x00.github.io/parser-generator/

## Uso resumido
- Ejecutar: `python -m lr1_py.app_tk`
- Ingresar la gramática (ej. expresiones aritméticas) y la cadena (`id + id * id`).
- Construir el parser y luego analizar.
- Visualizar ACTION/GOTO y los pasos del análisis.

## Resultados
- Para la gramática de expresiones: se construyen correctamente las tablas sin conflictos.
- Cadenas típicas como `id + id * id` son aceptadas; se observa la precedencia de `*` sobre `+` implícita en la gramática.

## Limitaciones y trabajo futuro
- No se genera el árbol sintáctico.
- El lector BNF es básico; no maneja prioridades ni alias.
- Se podría añadir: exportación/importación de tablas, visualización de conjuntos de ítems, y construcción del árbol de derivación.
