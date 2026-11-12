from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR DE ESTUDIANTES
# =====================================================================
class EstudianteController(CrudBase):

    # TUPLA: campos obligatorios y permitidos son fijos e inmutables,
    # por eso se usa tupla para evitar modificaciones accidentales.
    CAMPOS_OBLIGATORIOS = ("nombre", "apellido", "email", "carnet")
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet", "carrera")

    def __init__(self, archivo="data/estudiantes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = [Estudiante.desde_diccionario(d) for d in self.gestor.leer()]

    def guardar(self):
        self.gestor.guardar([e.a_diccionario() for e in self.lista])

    def validar(self, datos, id_actual=None):
        """Devuelve un mensaje de error, o None si todo es válido."""
        if id_actual is None:
            for campo in self.CAMPOS_OBLIGATORIOS:
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            # CONJUNTO (set): permite comprobar duplicados en tiempo constante O(1)
            emails_usados = {e.email for e in self.lista if e.id != id_actual}
            if email in emails_usados:
                return "Ese email ya está registrado"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()
            if carnet == "":
                return "El carnet no puede estar vacío"
            # CONJUNTO (set): garantiza unicidad del carnet y búsqueda instantánea con 'in'
            carnets_usados = {e.carnet.upper() for e in self.lista if e.id != id_actual}
            if carnet in carnets_usados:
                return f"El carnet '{carnet}' ya está registrado"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for estudiante in self.lista:
            if estudiante.id == id_estudiante:
                return estudiante
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        if texto == "":
            return []
        encontrados = []
        for estudiante in self.lista:
            # Recorre la TUPLA de campos buscables para no repetir condiciones
            if any(texto in str(getattr(estudiante, campo)).lower()
                   for campo in self.CAMPOS_BUSCABLES):
                encontrados.append(estudiante)
        return encontrados

    def siguiente(self):
        mayor = max((e.id for e in self.lista), default=0)
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            # TUPLA (exito, mensaje): empaqueta dos valores de distinto tipo en un retorno fijo
            return False, error

        estudiante = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos["carnet"]).strip().upper(),
            str(datos.get("carrera", "")).strip().title()
        )
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"

        # CONJUNTO (set): diferencia de conjuntos para detectar claves no permitidas
        permitidos = set(self.CAMPOS_BUSCABLES)
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    # --- propio de estudiantes ---
    def carreras(self):
        """CONJUNTO (set): elimina carreras repetidas automáticamente; sorted() devuelve lista ordenada."""
        return sorted({e.carrera for e in self.lista if e.carrera != ""})


# =====================================================================
# CONTROLADOR DE MATERIAS
# =====================================================================
class MateriaController(CrudBase):

    CAMPOS_OBLIGATORIOS = ("nombre", "codigo", "creditos")

    def __init__(self, archivo="data/materias.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = [Materia.desde_diccionario(d) for d in self.gestor.leer()]

    def guardar(self):
        self.gestor.guardar([m.a_diccionario() for m in self.lista])

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in self.CAMPOS_OBLIGATORIOS:
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            if codigo == "":
                return "El código de la materia no puede estar vacío"
            # CONJUNTO (set): validación instantánea de código único de materia
            codigos_usados = {m.codigo.upper() for m in self.lista if m.id != id_actual}
            if codigo in codigos_usados:
                return f"Ya existe una materia con código '{codigo}'"

        if "creditos" in datos:
            try:
                creditos = int(datos["creditos"])
                if not (1 <= creditos <= 10):
                    return "Los créditos deben ser un entero entre 1 y 10"
            except (TypeError, ValueError):
                return "Los créditos deben ser un número entero"

        if "cupos" in datos and str(datos["cupos"]).strip() != "":
            try:
                cupos = int(datos["cupos"])
                if not (0 <= cupos <= Materia.CUPOS_MAXIMOS):
                    return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}"
            except (TypeError, ValueError):
                return "Los cupos deben ser un número entero"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for materia in self.lista:
            if materia.id == id_materia:
                return materia
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        if texto == "":
            return []
        return [
            m for m in self.lista
            if texto in m.nombre.lower() or texto in m.codigo.lower()
        ]

    def siguiente(self):
        return max((m.id for m in self.lista), default=0) + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        cupos_str = str(datos.get("cupos", "")).strip()
        cupos = int(cupos_str) if cupos_str != "" else Materia.CUPOS_MAXIMOS

        materia = Materia(
            self.siguiente(),
            str(datos["nombre"]).strip(),
            str(datos["codigo"]).strip().upper(),
            int(datos["creditos"]),
            cupos
        )
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "codigo", "creditos", "cupos"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip()
        if "codigo" in datos:
            materia.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"

        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    # --- propio de materias ---
    def materias_sin_cupo(self):
        return [m for m in self.lista if not m.hay_cupo()]


# =====================================================================
# CONTROLADOR DE MATRÍCULAS
# =====================================================================
class MatriculaController(CrudBase):

    def __init__(self, estudiantes, materias, archivo="data/matriculas.json"):
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)
        self.lista = [Matricula.desde_diccionario(d) for d in self.gestor.leer()]

    def guardar(self):
        self.gestor.guardar([m.a_diccionario() for m in self.lista])

    def validar(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser números enteros"

        periodo = str(datos.get("periodo", "")).strip()
        if periodo == "":
            return "El periodo académico es obligatorio (ej. 2026-1)"

        # CONJUNTO (set) de IDs registrados para verificar existencia rápida
        ids_estudiantes = {e.id for e in self.estudiantes.leer()}
        if estudiante_id not in ids_estudiantes:
            return f"No existe un estudiante con id {estudiante_id}"

        materia = self.materias.obtener(materia_id)
        if materia is None:
            return f"No existe una materia con id {materia_id}"
        if not materia.hay_cupo():
            return f"La materia {materia.nombre} ({materia.codigo}) no tiene cupos disponibles"

        # CONJUNTO DE TUPLAS (estudiante_id, materia_id, periodo):
        # detecta en O(1) si el estudiante ya está matriculado en esa materia y periodo
        matriculas_existentes = {
            (m.estudiante_id, m.materia_id, m.periodo.upper())
            for m in self.lista
        }
        if (estudiante_id, materia_id, periodo.upper()) in matriculas_existentes:
            return "El estudiante ya está matriculado en esta materia y periodo"

        nota = datos.get("nota", 0)
        if not Materia.es_nota_valida(nota):
            return "La nota debe ser un número entre 0 y 20"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for matricula in self.lista:
            if matricula.id == id_matricula:
                return matricula
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        if texto == "":
            return []
        return [m for m in self.lista if texto in m.periodo.lower()]

    def siguiente(self):
        return max((m.id for m in self.lista), default=0) + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        materia = self.materias.obtener(int(datos["materia_id"]))
        nota = float(datos.get("nota", 0))

        matricula = Matricula(
            self.siguiente(),
            int(datos["estudiante_id"]),
            materia.id,
            str(datos["periodo"]).strip().upper(),
            nota
        )

        materia.ocupar_cupo()
        self.materias.guardar()
        self.lista.append(matricula)
        self.guardar()
        return True, f"Matrícula #{matricula.id} registrada ({materia.codigo})"

    def actualizar(self, id_matricula, datos):
        if "nota" in datos and len(datos) == 1:
            return self.registrar_nota(id_matricula, datos["nota"])
        return False, "Use la opción 'Registrar nota' o retire la matrícula y cree otra"

    def registrar_nota(self, id_matricula, nueva_nota):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula #{id_matricula}"

        if not Materia.es_nota_valida(nueva_nota):
            return False, "Nota inválida: debe estar entre 0 y 20"

        matricula.nota = float(nueva_nota)
        self.guardar()
        return True, f"Nota actualizada a {matricula.nota:.1f} ({matricula.estado()})"

    def eliminar(self, id_matricula):
        """Retirar matrícula: borra el registro y libera un cupo en la materia."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula #{id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matrícula #{id_matricula} retirada y cupo liberado"

    # --- propios de matrículas ---
    def certificado(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return None

        # DICCIONARIO ÍNDICE {id: objeto}: permite acceso directo O(1) por clave
        # sin tener que recorrer las listas de estudiantes ni materias
        indice_estudiantes = {e.id: e for e in self.estudiantes.leer()}
        indice_materias = {m.id: m for m in self.materias.leer()}

        estudiante = indice_estudiantes.get(matricula.estudiante_id)
        materia = indice_materias.get(matricula.materia_id)

        est_txt = f"{estudiante.nombre_completo()}   ({estudiante.carnet})" if estudiante else "Eliminado"
        mat_txt = f"{materia.nombre}   ({materia.codigo}) · {materia.creditos} créditos" if materia else "Eliminada"

        texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
        texto += f"Estudiante: {est_txt}\n"
        texto += f"Materia   : {mat_txt}\n"
        texto += "-" * 42 + "\n"
        texto += f"Nota      : {matricula.nota:.1f}\n"
        texto += f"Estado    : {matricula.estado()}"
        return texto

    def matriculas_por_estudiante(self):
        """DICCIONARIO DE LISTAS {estudiante_id: [matriculas]}: agrupa registros por clave."""
        agrupadas = {}
        for matricula in self.lista:
            agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
        return agrupadas

    def promedio_de_estudiante(self, id_estudiante):
        agrupadas = self.matriculas_por_estudiante()
        mats = agrupadas.get(id_estudiante, [])
        if not mats:
            return None
        return round(sum(m.nota for m in mats) / len(mats), 2)

    def total_aprobadas(self):
        return sum(1 for m in self.lista if m.esta_aprobada())
