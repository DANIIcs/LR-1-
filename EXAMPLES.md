## Ejemplos de gramáticas LR(1) para probar el proyecto

Esta app acepta gramáticas en un formato BNF simple, una producción por línea:

- Usa `A -> α | β | ...` con alternativas separadas por `|`.
- El primer símbolo del lado izquierdo de la primera línea es el símbolo inicial.
- Los tokens son sensibles a espacios: en la cadena de entrada separa cada token por un espacio.
- Epsilon se escribe como `ε` (también se aceptan `epsilon` o `EPSILON`). No lo pongas en la cadena de entrada.
- Los terminales pueden ser símbolos como `id`, `+`, `*`, `(`, `)`, `if`, `then`, `else`, `[`, `]`, `,`, etc.
- El marcador de fin `$` se añade automáticamente; no lo escribas en la entrada.

En cada ejemplo incluyo cadenas de prueba esperadas como aceptadas y, cuando es útil, alguna rechazada.

---

### Antes de empezar: por qué pueden “fallar” los ejemplos

Esta app NO tiene analizador léxico; simplemente separa la entrada por espacios. Eso implica:

- Debes poner espacios entre todos los tokens, incluso alrededor de paréntesis, corchetes, comas y operadores: usa `( id )`, `[ id , id ]`, `id ^ id`, `a a b b`. Los textos sin espacios como `id^id`, `[id,id]`, `(id)` o `aabb` serán tokens únicos y no coinciden con la gramática, por eso “fallan”.
- No escribas `ε` en la cadena de entrada; el vacío solo aparece en producciones.
- Las palabras clave son sensibles a espacios y minúsculas: `if`, `then`, `else`.

Si copias las cadenas exactamente como están a continuación, deberían funcionar.

---

### 1) Aritmética clásica con precedencia y paréntesis (LR(1))

Gramática:

```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

Pruebas de entrada (aceptadas):

- `id`
- `id + id`
- `id + id * id`
- `( id + id ) * id`

Pruebas rechazadas:

- `+ id`
- `( id + id * id`  (paréntesis sin cerrar)

---

### 2) If–else (resuelve el dangling else) — LR(1)

Gramática (no ambigua, estándar LR(1)):

```
S -> Stmt
Stmt -> Matched | Unmatched
Matched -> if E then Matched else Matched | id
Unmatched -> if E then Stmt | if E then Matched else Unmatched
E -> id
```

Aceptadas:

- `id`
- `if id then id`
- `if id then id else id`
- `if id then if id then id else id`
- `if id then if id then id`  (la última else puede faltar)

Rechazada:

- `if id id` (falta `then`)

---

### 3) Paréntesis balanceados (no ambigua) — LR(1)

Gramática:

```
S -> ( S ) S | ε
```

Aceptadas:

- `( )`
- `( ) ( )`
- `( ( ) )`
- `( ( ) ( ) )`

Rechazadas:

- `)`
- `( ( )`

Nota: para la cadena vacía, la UI requiere un texto no vacío; usa por ejemplo `( )` para probar aceptación.

---

### 4) Listas entre corchetes con comas — LR(1)

Gramática:

```
S -> [ OptList ]
OptList -> List | ε
List -> List , E | E
E -> id
```

Aceptadas:

- `[ ]`
- `[ id ]`
- `[ id , id ]`
- `[ id , id , id ]`

Rechazadas:

- `[ , ]`
- `[ id , ]`

---

### 5) Potencia asociativa a la derecha — LR(1)

Gramática:

```
E -> F ^ E | F
F -> ( E ) | id
```

Aceptadas:

- `id`
- `id ^ id`
- `id ^ id ^ id`  (asocia como `id ^ ( id ^ id )`)
- `( id ^ id ) ^ id`

Rechazadas:

- `^ id`

---

### 6) Cero o más `a` seguidas de `b` — LR(1)

Gramática:

```
S -> A b
A -> a A | ε
```

Aceptadas:

- `b`
- `a b`
- `a a b`
- `a a a a b`

Rechazadas:

- `a`
- `b a`

---

### 7) Gramática clásica LR(1) (no SLR) para asignaciones

Gramática (típico ejemplo LR(1) que causa conflicto en SLR):

```
S -> L = R | R
L -> * R | id
R -> L
```

Aceptadas:

- `id`
- `* id`
- `id = id`
- `* id = * id`
- `* * id = id`

Rechazadas:

- `=`
- `id =`

---

### 8) `a^n b^n` — LR(1)

Gramática:

```
S -> a S b | ε
```

Aceptadas:

- `a b`
- `a a b b`
- `a a a b b b`

Rechazadas:

- `a a b`
- `b a`

---

## (Opcional) Gramáticas NO LR(1) para probar detección de conflictos

Estas deben reportar conflictos en la tabla ACTION y mostrar que la gramática no es LR(1).

1) Aritmética ambigua:

```
E -> E + E | E * E | id
```

2) Paréntesis balanceados (ambigua):

```
S -> S S | ( S ) | ε
```

---

## Cómo ejecutar la app

1) Instala dependencias (Windows PowerShell):

```powershell
python -m venv .venv ; .venv\Scripts\Activate.ps1 ; pip install -r requirements.txt
```

2) Inicia la app:

```powershell
streamlit run streamlit_app.py
```

3) Abre en el navegador la URL que te indique Streamlit (o usa el deploy del README).

En la UI pega cualquiera de las gramáticas anteriores y escribe la cadena de tokens separada por espacios.
