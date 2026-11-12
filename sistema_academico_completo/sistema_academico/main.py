from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import EstudianteController, MateriaController, MatriculaController

# Instancia única de cada controlador compartida entre menús
estudiantes = EstudianteController()
materias = MateriaController()
matriculas = MatriculaController(estudiantes, materias)


# =====================================================================
# AYUDAS DE PANTALLA
# =====================================================================

def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    """Polimorfismo en acción: sirve para Estudiante, Materia y Matricula sin if de tipo."""
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


# =====================================================================
# MENÚ DE ESTUDIANTES
# =====================================================================

def crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet (ej. EST2026001): "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*estudiantes.crear(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("ESTUDIANTES")
    mostrar_lista(estudiantes.leer(), "Todavía no hay estudiantes.")
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email, carnet o carrera: ")
    encontrados = estudiantes.buscar(termino)
    mostrar_lista(encontrados, f"Ningún estudiante coincide con '{termino}'.")
    pausa()


def ver_estudiante():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    estudiante = estudiantes.obtener(pedir_entero("Id: "))
    if estudiante is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(estudiante)
        prom = matriculas.promedio_de_estudiante(estudiante.id)
        if prom is not None:
            imprimir_info(f"Promedio general: {prom:.2f}")
    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_est = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_est)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {estudiante.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*estudiantes.actualizar(id_est, cambios))
    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_est = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_est)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminará: {estudiante.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*estudiantes.eliminar(id_est))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ DE MATERIAS
# =====================================================================

def crear_materia():
    imprimir_titulo("CREAR MATERIA")
    datos = {
        "nombre": input("Nombre: "),
        "codigo": input("Código (ej. MAT101): "),
        "creditos": input("Créditos (1-10): "),
        "cupos": input("Cupos iniciales (Enter = 30): "),
    }
    mostrar_resultado(*materias.crear(datos))
    pausa()


def listar_materias():
    imprimir_titulo("MATERIAS")
    mostrar_lista(materias.leer(), "Todavía no hay materias.")
    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o código: ")
    mostrar_lista(materias.buscar(termino), "Sin coincidencias.")
    pausa()


def ver_materia():
    imprimir_titulo("VER MATERIA POR ID")
    materia = materias.obtener(pedir_entero("Id: "))
    if materia is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(materia)
    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_mat = pedir_entero("Id: ")
    materia = materias.obtener(id_mat)
    if materia is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {materia.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "codigo", "creditos", "cupos"):
        actual = getattr(materia, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*materias.actualizar(id_mat, cambios))
    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    id_mat = pedir_entero("Id: ")
    materia = materias.obtener(id_mat)
    if materia is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminará: {materia.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*materias.eliminar(id_mat))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ DE MATRÍCULAS
# =====================================================================

def matricular_estudiante():
    imprimir_titulo("MATRICULAR ESTUDIANTE")
    imprimir_info("Estudiantes:")
    mostrar_lista(estudiantes.leer())
    imprimir_info("Materias:")
    mostrar_lista(materias.leer())

    est_id = pedir_entero("\nId del estudiante: ")
    mat_id = pedir_entero("Id de la materia: ")
    periodo = input("Periodo (ej. 2026-1): ").strip()
    nota_txt = input("Nota inicial (0-20, Enter = 0): ").strip()

    if est_id is None or mat_id is None:
        imprimir_error("Los IDs deben ser números enteros")
        return pausa()

    datos = {
        "estudiante_id": est_id,
        "materia_id": mat_id,
        "periodo": periodo,
        "nota": nota_txt if nota_txt != "" else 0,
    }
    mostrar_resultado(*matriculas.crear(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("MATRÍCULAS")
    mostrar_lista(matriculas.leer(), "Todavía no hay matrículas.")
    pausa()


def registrar_nota():
    imprimir_titulo("REGISTRAR NOTA")
    id_mat = pedir_entero("Id de la matrícula: ")
    matricula = matriculas.obtener(id_mat)
    if matricula is None:
        imprimir_error("No existe esa matrícula")
        return pausa()

    imprimir_info(f"Actual: {matricula.etiqueta()}")
    nota = input("Nueva nota (0 - 20): ").strip()
    mostrar_resultado(*matriculas.registrar_nota(id_mat, nota))
    pausa()


def ver_certificado():
    imprimir_titulo("CERTIFICADO DE MATRÍCULA")
    texto = matriculas.certificado(pedir_entero("Id de la matrícula: "))
    if texto is None:
        imprimir_error("No existe esa matrícula")
    else:
        print(texto)
    pausa()


def retirar_matricula():
    imprimir_titulo("RETIRAR MATRÍCULA")
    id_mat = pedir_entero("Id de la matrícula: ")
    if id_mat and confirmar("Se liberará el cupo en la materia. ¿Confirma?"):
        mostrar_resultado(*matriculas.eliminar(id_mat))
    else:
        imprimir_info("Operación cancelada")
    pausa()


def resumen():
    imprimir_titulo("RESUMEN ACADÉMICO")
    print(f"  Estudiantes         : {len(estudiantes.leer())}")
    print(f"  Carreras            : {', '.join(estudiantes.carreras()) or '-'}")
    print(f"  Materias            : {len(materias.leer())}")
    sin_cupo = materias.materias_sin_cupo()
    print(f"  Materias sin cupo   : {', '.join(m.nombre for m in sin_cupo) or 'ninguna'}")
    print(f"  Matrículas totales  : {len(matriculas.leer())}")
    print(f"  Matrículas aprobadas: {matriculas.total_aprobadas()}")
    pausa()


# =====================================================================
# MENÚS: DICCIONARIOS tecla -> (texto, función)
# =====================================================================

MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", crear_estudiante),
    "2": ("Ver todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por id", ver_estudiante),
    "5": ("Actualizar", actualizar_estudiante),
    "6": ("Eliminar", eliminar_estudiante),
    "0": ("Volver", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Ver todas", listar_materias),
    "3": ("Buscar", buscar_materia),
    "4": ("Ver por id", ver_materia),
    "5": ("Actualizar", actualizar_materia),
    "6": ("Eliminar", eliminar_materia),
    "0": ("Volver", None),
}

MENU_MATRICULAS = {
    "1": ("Matricular", matricular_estudiante),
    "2": ("Ver todas", listar_matriculas),
    "3": ("Registrar nota", registrar_nota),
    "4": ("Ver certificado", ver_certificado),
    "5": ("Retirar matrícula", retirar_matricula),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Opción: ").strip()
        if tecla not in opciones:
            imprimir_error("Opción no válida")
            pausa()
            continue

        _texto, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA ACADÉMICO")
        print("  1. Estudiantes")
        print("  2. Materias")
        print("  3. Matrículas")
        print("  4. Resumen")
        print("  0. Salir\n")

        tecla = input("Opción: ").strip()
        if tecla == "1":
            ejecutar_menu("ESTUDIANTES", MENU_ESTUDIANTES)
        elif tecla == "2":
            ejecutar_menu("MATERIAS", MENU_MATERIAS)
        elif tecla == "3":
            ejecutar_menu("MATRÍCULAS", MENU_MATRICULAS)
        elif tecla == "4":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego! 👋")
            break
        else:
            imprimir_error("Opción no válida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
