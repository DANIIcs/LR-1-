# Parser LR(1) en Python con interfaz (Tkinter)

Este proyecto implementa un generador y ejecutor de parser LR(1) en Python, junto con una interfaz gráfica simple usando Tkinter. Se puede construir el autómata LR(1), ver las tablas ACTION/GOTO, y analizar cadenas paso a paso.

- Lenguaje: Python 3.11 (sin dependencias externas)
- Interfaz: Tkinter (incluido en Python)
- Inspiración y lectura recomendada:
  - https://compiler-slr-parser.netlify.app/
  - https://jsmachines.sourceforge.net/machines/lr1.html
  - https://light0x00.github.io/parser-generator/

## Estructura

- `grammar.py`: Representación de gramática y cálculo de FIRST. Parser BNF simple.
- `lr1.py`: Construcción de ítems LR(1), cierre/goto, colección canónica y tablas ACTION/GOTO.
- `parser.py`: Intérprete del parser (shift/reduce/accept) con traza de pasos.
- `lexer.py`: Tokenizador sencillo para expresiones (mapeando identificadores y números a `id`).
- `app_tk.py`: Interfaz gráfica.
- `examples/`: Gramáticas y entradas de ejemplo.
- `tests/`: Prueba unitaria mínima.

## Formato de gramática (BNF simple)

Cada producción se escribe como:

```
A -> X Y Z | W
```

- Símbolos separados por espacios.
- Terminales pueden ir entre comillas simples o dobles (por ejemplo: `'+'`, `"id"`) o sin comillas si no son no terminales.
- Epsilon: `ε` o `epsilon`.
- Comentarios con `#` y líneas vacías se ignoran.

Ejemplo (expresiones aritméticas):

```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

## Cómo ejecutar la app

1. Asegura que estás usando el intérprete de Python del proyecto (se creó un `.venv`).
2. Ejecuta la app:

```
# PowerShell
D:/Principal/compiladores/puntosextra/.venv/Scripts/python.exe -m lr1_py.app_tk
```

### Alternativa: Frontend Web (Flask)

También añadimos una app web minimalista para visualizar la gramática, las tablas ACTION/GOTO y los pasos de análisis, además de una tabla de derivación aproximada:

```
# PowerShell
D:/Principal/compiladores/puntosextra/.venv/Scripts/python.exe -m webapp.app
```

Luego abre en el navegador: http://127.0.0.1:5000

En la página:
- Pega/edita la gramática (BNF simple).
- Escribe la cadena de entrada y el modo de tokenización.
- Pulsa “Construir y Analizar” para ver tablas y la traza.

En la ventana:
- Pega/edita la gramática.
- Escribe la cadena de entrada (por ejemplo: `id + id * id`).
- Elige tokenización (léxico o tokens separados por espacios).
- Haz clic en “Construir parser” y luego en “Analizar”.

## Ejecutar pruebas

```
D:/Principal/compiladores/puntosextra/.venv/Scripts/python.exe -m unittest lr1_py.tests.test_lr1_basic -v
```

## Reporte (resumen técnico)

- Algoritmo: Se implementa LR(1) canónico con ítems `[A → α • β, a]`. La clausura añade ítems para no terminales después del punto con lookaheads `FIRST(βa)` (si `ε ∈ FIRST(β)`, se incluye `a`). Se genera la colección canónica de conjuntos de ítems con `goto` por símbolo, y de ahí las tablas ACTION (shift/reduce/accept) y GOTO.
- Detección de conflictos: Al poblar ACTION se registra si aparece `shift/reduce` o `reduce/reduce`. Para la gramática de expresiones de ejemplo no deben aparecer conflictos.
- Parser: Implementa la clásica pila de estados y símbolos. Acciones: `s` (shift), `r` (reduce), `acc` (accept). Se generan pasos detallados para depuración.
- Interfaz: Permite construir las tablas y visualizar el procesamiento. Admite dos modos de entrada: tokenización léxica básica para expresiones o secuencia de tokens separados por espacios.
- Limitaciones: No se implementa construcción de árbol sintáctico ni acciones semánticas; el foco es el análisis LR(1). El formato BNF es intencionalmente sencillo.

## Próximos pasos sugeridos
- Exportar tablas a JSON y cargar desde archivo.
- Mostrar los conjuntos de ítems por estado en la interfaz.
- Construir árbol de derivación y visualizarlo.
- Soportar definiciones de tokens (regex) desde la interfaz.
