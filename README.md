# Compilador Clite con Generación de Código LLVM IR

Este proyecto consiste en el desarrollo de un compilador completo para el lenguaje Clite (un subconjunto del lenguaje C) extendido con llamadas a funciones, múltiples parámetros/argumentos, conversiones implícitas de tipos y estructuras de control avanzadas. El compilador analiza el código fuente, valida su estructura sintáctica/semántica construyendo un Árbol de Sintaxis Abstracta (AST) y genera código intermedio de bajo nivel optimizado en formato LLVM IR.

Desarrollado como parte de la materia de Desarrollo de aplicaciones avanzadas de ciencias computacionales (Gpo 502) en el Tecnológico de Monterrey.

## Características del Compilador

- **Análisis Léxico y Sintáctico (Bottom-Up LALR(1))**: Construido utilizando la biblioteca PLY (Python Lex-Yacc), permitiendo recursión por la izquierda eficiente para el procesamiento de listas de declaraciones y sentencias.
- **Manejo de Memoria Real en la Pila**: Genera código intermedio utilizando almacenamiento físico local en la pila de LLVM mediante la combinación de `alloca`, `store` y `load`, garantizando la mutabilidad de variables y parámetros locales.
- **Estructuras de Control Completas**:
  - **Condicionales**: IF / ELSE.
  - **Ciclos**: WHILE, FOR (con inicialización, condición e incremento secuenciales) y DO / WHILE (optimizados a dos bloques básicos).
  - **Selección Múltiple**: SWITCH mediante una tabla de saltos indexada nativa de LLVM (`switch_inst`), con comportamiento cerrado por defecto para evitar problemas de fall-through.
- **Funciones y Recursividad**: Soporte nativo para definición de funciones con múltiples parámetros y llamadas con múltiples argumentos, permitiendo recursión simple y doble en tiempo de ejecución.
- **Conversión Implícita de Tipos**: Resolución semántica automática entre variables de tipo `int` y `float` mediante la emisión selectiva de instrucciones de promoción/degradación de bits (`sitofp` y `fptosi`).
- **Entrada y Salida con libc**: Enlace directo con la función externa variádica `printf` de la biblioteca estándar de C utilizando casteo de direcciones a nivel de bits con `bitcast`.

## Estructura del Proyecto

```text
├── analisis.py          # Lexer, Parser, IRGenerator y configuración del módulo LLVM
├── arbol.py             # Jerarquía de clases de los nodos del AST (patrón Visitor)
├── verificar_pruebas.py # Script automatizado que ejecuta el lote de pruebas
├── README.md            # Documentación general del compilador (este archivo)
└── pruebas/             # Carpeta con los códigos fuente de prueba en C-like
    ├── programa1_factorial.c
    ├── programa2_fibonacci.c
    ├── programa3_potencia.c
    ├── programa4_ciclo_for.c
    └── programa5_conversion_tipos.c
```

## Instalación y Requisitos

### Prerrequisitos

El compilador requiere de un entorno con Python 3.8 o superior instalado.

### Clonar el Repositorio

```bash
git clone https://github.com/danyflores7/Actividad-3.2.-Analizador.git
cd Actividad-3.2.-Analizador
```

### Crear y Activar Entorno Virtual (Opcional pero Recomendado)

**En macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**En Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Instalar Dependencias

Instala los analizadores y las herramientas de enlace de LLVM:

```bash
pip install ply llvmlite
```

## Instrucciones de Ejecución

El proyecto incluye dos formas principales de interacción y prueba:

### 1. Compilación del Archivo Base

Para ejecutar el analizador con el código de prueba estático configurado en el archivo base (el cual demuestra el uso de la estructura SWITCH):

```bash
python analisis.py
```

Este comando imprimirá en consola:
- La dirección del nodo raíz del AST.
- El estado de la pila semántica de LLVM.
- El código intermedio de LLVM IR generado completo.

### 2. Ejecutar la Suite de Pruebas Automatizada

Para verificar que los 5 programas de validación (incluyendo los recursivos y las conversiones de tipo) compilan perfectamente sin errores:

```bash
python verificar_pruebas.py
```

El script leerá dinámicamente cada archivo de la carpeta `pruebas/`, los procesará y emitirá un reporte con marcas visuales de éxito (✅) junto con su código intermedio correspondiente.

## Catálogo de Casos de Prueba Incluidos

- **`pruebas/programa1_factorial.c`**: Implementa el cálculo del factorial de $5$ de forma recursiva. Demuestra bifurcación condicional, ámbitos locales de parámetros en pila y retornos de llamada simples.
- **`pruebas/programa2_fibonacci.c`**: Calcula el sexto término de la serie de Fibonacci empleando recursión múltiple. Valida la integridad de la pila semántica al resolver expresiones complejas con múltiples llamadas.
- **`pruebas/programa3_potencia.c`**: Algoritmo recursivo que calcula $2^4$ empleando una firma de función de múltiples parámetros y llamada con múltiples argumentos.
- **`pruebas/programa4_ciclo_for.c`**: Acumula una suma iterativa utilizando un ciclo FOR y comprueba la inicialización, la evaluación y el incremento tardío dentro del bloque del cuerpo.
- **`pruebas/programa5_conversion_tipos.c`**: Realiza una asignación heterogénea entre una variable float y un literal de tipo int, forzando al backend a emitir una promoción aritmética con `sitofp` en LLVM IR.

## Autor

**Daniel Flores Rojas** (Matrícula: A01737719)

Tecnológico de Monterrey
