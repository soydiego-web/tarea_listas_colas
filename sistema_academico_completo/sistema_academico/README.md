# Sistema Académico — CRUD en Python con MVC, POO y Colecciones

Aplicación de consola desarrollada en Python 3 que implementa la gestión de **Estudiantes**, **Materias** y **Matrículas** aplicando el patrón arquitectónico **MVC**, Programación Orientada a Objetos (**Herencia, Polimorfismo, Clases Abstractas, Métodos de Clase y Estáticos**), persistencia en **JSON** y uso estratégico de las **cuatro colecciones nativas de Python**.

---

## 1. Estructura del Proyecto

```text
sistema_academico/
├── main.py                  # VISTA: menús interactivos, entrada/salida por consola
├── views.py                 # CONTROLADOR: lógica de negocio, validaciones y CRUD
├── models.py                # MODELO: jerarquía de clases y reglas de dominio
├── README.md                # Documentación completa del sistema
├── shared/                  # HERRAMIENTAS REUTILIZABLES
│   ├── __init__.py          # Define el paquete importable
│   ├── herramientas.py      # Utilidades de formato en consola y validación de email
│   └── json_manager.py      # Persistencia en archivos JSON (lectura/escritura)
└── data/                    # ALMACENAMIENTO (se genera automáticamente al ejecutar)
    ├── estudiantes.json
    ├── materias.json
    └── matriculas.json
```

---

## 2. Arquitectura MVC y Flujo de Datos

El sistema separa las responsabilidades en tres capas independientes para evitar acoplamiento:

1. **Vista (`main.py`):** Única capa autorizada para usar `input()` y `print()`. Captura los datos del usuario, los empaqueta en diccionarios y muestra los resultados devueltos por los controladores. No accede a archivos ni contiene reglas de negocio.
2. **Controlador (`views.py`):** Contiene `CrudBase` (clase abstracta) y los controladores `EstudianteController`, `MateriaController` y `MatriculaController`. Valida reglas de negocio, gestiona las colecciones en memoria y devuelve tuplas `(exito, mensaje)` o listas de objetos. No contiene ningún `print()` ni `input()`.
3. **Modelo (`models.py`):** Define las entidades del dominio (`ModeloBase`, `Persona`, `Estudiante`, `Materia`, `Matricula`), sus atributos y transformaciones (`a_diccionario()` y `desde_diccionario()`).
4. **Apoyo (`shared/`):** `GestorJSON` es el único componente que lee y escribe archivos en disco dentro de `data/`.

---

## 3. Conceptos de POO Implementados

### Herencia (`super()`)
* **`ModeloBase`:** Clase padre de todo el sistema. Administra el `id` entero y define `a_diccionario()`, `etiqueta()` y `__str__()`.
* **`Persona(ModeloBase)`:** Extiende `ModeloBase` incorporando `nombre`, `apellido`, `email` y el método `nombre_completo()`.
* **`Estudiante(Persona)`:** Hereda de `Persona` mediante `super().__init__(...)` y agrega `carnet` y `carrera`. Reutiliza `super().a_diccionario()` y `super().etiqueta()`.
* **`Materia(ModeloBase)` y `Matricula(ModeloBase)`:** Heredan directamente de `ModeloBase`.

### Polimorfismo
* Cada modelo sobrescribe el método `etiqueta()` con su propio formato visual (`Estudiante`, `Materia` con alerta de cupo, `Matricula` con estado calculado).
* Gracias a `ModeloBase.__str__()`, la función `mostrar_lista()` en `main.py` imprime cualquier colección de objetos con una sola línea (`print(f"  {objeto}")`) sin usar condicionales `if/elif` por tipo de entidad.

### Métodos de Clase y Estáticos
* **`@classmethod` (`ModeloBase.desde_diccionario(cls, datos)`):** Único método de clase del proyecto. Se escribe una sola vez en el padre y usa `cls(id_registro, **datos)` para instanciar dinámicamente objetos `Estudiante`, `Materia` o `Matricula` al leer los JSON.
* **Atributos y Métodos `@staticmethod` en `Materia`:**
  * `CUPOS_MAXIMOS = 30` y `NOTA_APROBACION = 14`: constantes de negocio compartidas a nivel de clase.
  * `Materia.es_nota_valida(valor)`: método estático que valida si una calificación es un número entre `0` y `20` sin requerir una instancia previa.

### Datos Calculados vs. Almacenados
* El estado de aprobación (`Aprobado` / `Reprobado`) **no se guarda** en `matriculas.json`; se calcula dinámicamente con `matricula.esta_aprobada()` y `matricula.estado()` para evitar desincronizaciones si se actualiza la nota.

---

## 4. Uso Estratégico de las 4 Colecciones de Python

| Colección | Dónde se usa | Propósito y justificación |
| :--- | :--- | :--- |
| **`list`** | `self.lista` en cada controlador | Mantiene la secuencia ordenada y mutable de objetos en memoria. |
| **`tuple`** | `CAMPOS_OBLIGATORIOS`, `CAMPOS_BUSCABLES` y retornos `(exito, mensaje)` | Protege configuraciones fijas contra modificaciones accidentales y empaqueta múltiples valores de retorno. |
| **`set`** | Validación de `email`, `carnet`, `codigo`, `carreras()` y tuplas `(estudiante_id, materia_id, periodo)` | Garantiza unicidad sin duplicados y permite verificar pertenencia (`in`) en tiempo constante $O(1)$. |
| **`dict`** | Registros JSON, menús `MENU_*`, índices `{id: objeto}` en `certificado()` y `matriculas_por_estudiante()` | Permite acceso instantáneo por clave $O(1)$ para cruzar datos y agrupar listas con `setdefault()`. |

---

## 5. Funcionalidades y Reglas de Negocio

* **Estudiantes:** CRUD completo + búsqueda multi-campo. Valida campos obligatorios, formato de email, email único y **carnet único**. Calcula el promedio general del estudiante al consultar por ID.
* **Materias:** CRUD completo + búsqueda por nombre o código. Valida **código único**, créditos (`1` a `10`) y cupos (`0` a `30`). Reporta materias sin cupo.
* **Matrículas:**
  * Verifica existencia de estudiante y materia, disponibilidad de cupos y que el estudiante **no esté matriculado dos veces** en la misma materia y periodo.
  * Descuenta automáticamente `1` cupo en `materias.json` al registrar la matrícula.
  * Permite registrar o actualizar la nota (`0` a `20`).
  * Genera un **Certificado** cruzando datos con diccionarios índice.
  * Al **retirar una matrícula**, elimina el registro y **libera automáticamente** el cupo en la materia.
* **Resumen Académico:** Muestra conteo total de estudiantes, carreras distintas ordenadas, materias sin cupo, total de matrículas y total de aprobadas.

---

## 6. Cómo Ejecutar el Proyecto

1. Asegúrate de tener **Python 3.8 o superior** instalado.
2. Abre una terminal dentro de la carpeta `sistema_academico/`:
   ```bash
   cd sistema_academico
   ```
3. Ejecuta el archivo principal:
   ```bash
   python main.py
   ```
   *(En macOS o Linux utiliza `python3 main.py`)*
