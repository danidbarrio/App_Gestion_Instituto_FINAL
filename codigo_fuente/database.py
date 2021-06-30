import sqlite3
from tkinter import messagebox

# Clase de la base de datos
class DataBase:
    def __init__(self):
        # Creación y conexión a la base de datos
        self.con = sqlite3.connect('prestamos.db')

        # Cursor para recorrer la base de datos
        self.cur = self.con.cursor()

        # Creación de las tablas
        self.cur.execute("""CREATE TABLE if NOT EXISTS departamentos(
                            id INTEGER PRIMARY KEY,
                            nombre text NOT NULL);""")

        self.cur.execute("""CREATE TABLE if NOT EXISTS permisos(
                            id INTEGER PRIMARY KEY,
                            nombre text NOT NULL);""")

        self.cur.execute("""CREATE TABLE if NOT EXISTS profesores(
                            id INTEGER PRIMARY KEY,
                            user text NOT NULL,
                            password text NOT NULL,
                            nombre text NOT NULL,
                            ape1 text NOT NULL,
                            ape2 text,
                            id_permisos INTEGER NOT NULL,
                            FOREIGN KEY(id_permisos) REFERENCES permisos(id));""")

        self.cur.execute("""CREATE TABLE if NOT EXISTS profesores_departamentos(
                            id_profesor INTEGER NOT NULL,
                            id_depart INTEGER NOT NULL,
                            FOREIGN KEY(id_profesor) REFERENCES profesores(id),
                            FOREIGN KEY(id_depart) REFERENCES departmentos(id));""")

        self.cur.execute("""CREATE TABLE if NOT EXISTS estado(
                            id INTEGER PRIMARY KEY,
                            nombre text NOT NULL);""")

        self.cur.execute("""CREATE TABLE if NOT EXISTS material(
                            id INTEGER PRIMARY KEY,
                            nombre text NOT NULL,
                            codigo text NOT NULL,
                            id_estado INTEGER NOT NULL,
                            FOREIGN KEY(id_estado) REFERENCES estado(id));""")

        self.cur.execute("""CREATE TABLE if NOT EXISTS prestamos(
                            id INTEGER PRIMARY KEY,
                            id_material INTEGER NOT NULL,
                            id_profesor INTEGER NOT NULL,
                            dia_ini text NOT NULL,
                            mes_ini text NOT NULL,
                            ano_ini text NOT NULL,
                            dia_fin text,
                            mes_fin text,
                            ano_fin text,
                            FOREIGN KEY(id_material) REFERENCES material(id),
                            FOREIGN KEY(id_profesor) REFERENCES profesor(id));""")

        # Generación automática de los permisos de ADMINISTRADOR, ENCARGADO y PROFESOR para los usuarios
        is_admin = False
        is_manager = False
        is_profe = False
        self.cur.execute("SELECT nombre FROM permisos;")
        estados = self.cur.fetchall()
        for est in estados:
            if str(est) == "('ADMINISTRADOR',)":
                is_admin = True
            elif str(est) == "('ENCARGADO',)":
                is_manager = True
            elif str(est) == "('PROFESOR',)":
                is_profe = True
        if not is_admin:
            self.cur.execute("""INSERT INTO permisos (nombre) VALUES
                            ('ADMINISTRADOR');""")
        if not is_manager:
            self.cur.execute("""INSERT INTO permisos (nombre) VALUES
                            ('MANAGER');""")
        if not is_profe:
            self.cur.execute("""INSERT INTO permisos (nombre) VALUES
                            ('PROFESOR');""")

        # Generación automática de los usuarios ADMIN y MANAGER para la gestión de la base de datos desde su creación
        is_admin = False
        is_manager = False
        self.cur.execute("SELECT user FROM profesores;")
        profes_iniciales = self.cur.fetchall()
        for prof_ini in profes_iniciales:
            if str(prof_ini) == "('admin',)":
                is_admin = True
            elif str(prof_ini) == "('manager',)":
                is_manager = True
        if not is_admin:
            self.cur.execute("""INSERT INTO profesores (user, password, id_permisos, nombre, ape1, ape2) VALUES
                            ('admin', 'admin', 1, 'ADMIN', 'ADMIN', '');""")
        if not is_manager:
            self.cur.execute("""INSERT INTO profesores (user, password, id_permisos,  nombre, ape1, ape2) VALUES
                            ('manager', 'manager', 2, 'MANAGER', 'MANAGER', '');""")

        # Generación automática de los ESTADOS DISPONIBLE y NO DISPONIBLE de los materiales a dar en los préstamos
        is_libre = False
        is_prestado = False
        self.cur.execute("SELECT nombre FROM estado;")
        estados = self.cur.fetchall()
        for est in estados:
            if str(est) == "('DISPONIBLE',)":
                is_libre = True
            elif str(est) == "('NO DISPONIBLE',)":
                is_prestado = True
        if not is_libre:
            self.cur.execute("""INSERT INTO estado (nombre) VALUES
                            ('DISPONIBLE');""")
        if not is_prestado:
            self.cur.execute("""INSERT INTO estado (nombre) VALUES
                            ('NO DISPONIBLE');""")

        # Ejecución de las instrucciones
        self.con.commit()

# Finalización de la conexión a la base de datos
    def __del__(self):
        self.con.close()

# Funciones para manejar la tabla DEPARTAMENTOS
    # Mostrar todos los departamentos
    def view_departs(self):
        # Seleccionamos y devolvemos todos los departamentos guardados
        self.cur.execute("SELECT * FROM departamentos;")
        result = self.cur.fetchall()
        return result

    #Añadir departamento
    def insert_depart(self, nombre):
        # Añadimos el departamento a la tabla con los datos dados
        self.cur.execute("INSERT INTO departamentos VALUES (NULL, '"+nombre.upper()+"');")
        self.con.commit()

    # Modificar departamento
    def update_depart(self, id_update, nombre):
        # Si se ha seleccionado una entrada, se avisa al usuario por si quiere no modificarla
        if messagebox.askokcancel("Atención", "¿Está seguro de modificar la entrada seleccionada con los datos que va a proporcionar?"):
            # Se actualiza la entrada con el id dado (id_update) y se le cambia el nombre por el introducido (nombre)
            self.cur.execute("UPDATE departamentos SET nombre = '"+nombre.upper()+"' WHERE id = "+id_update+";")
            self.con.commit()

    # Eliminar departamento
    def delete_depart(self, id_delete):
        # Si se ha seleccionado una entrada, se avisa al usuario por si quiere no eliminarla
        if messagebox.askokcancel("Atención", "¿Está seguro de borrar la entrada seleccionada?"):
            # Se eliminan las relaciones que tuviera en la tabla profesores_departamentos
            self.cur.execute("DELETE FROM profesores_departamentos WHERE id_depart = "+id_delete+";")
            self.con.commit()

            # Se elimina el departamento con el id dado (id_delete)
            self.cur.execute("DELETE FROM departamentos WHERE id = "+id_delete+";")
            self.con.commit()

    # Buscar departamento
    def search_depart(self, nombre):
        # Seleccionamos y devolvemos el departamento que coincida con los datos dados
        self.cur.execute("SELECT * FROM departamentos WHERE nombre = '"+nombre.upper()+"';")
        result = self.cur.fetchall()
        return result

# Funciones para manejar la tabla MATERIAL
    # Mostrar todos los materiales
    def view_material(self):
        # Seleccionamos y devolvemos la información de todos los materiales guardados
        self.cur.execute("""SELECT material.id, material.nombre, material.codigo, estado.nombre
                        FROM material, estado
                        WHERE estado.id = material.id_estado;""")
        result = self.cur.fetchall()
        return result

    # Añadir material
    def insert_material(self, nombre, codigo, estado):
        id_estado = 0
        # Valor para ID_ESTADO en caso de que el estado sea "Disponible" o está vacío ("").
        if estado.upper() == "DISPONIBLE" or estado == "":
            id_estado = 1
        # Valor para ID_ESTADO en caso de que el estado sea "No Disponible".
        elif estado.upper() == "NO DISPONIBLE":
            id_estado = 2

        # Se compeueba que se ha introducido un estado correcto
        if id_estado != 0:
            if estado == "":
                # Si no se ha introducido ningún estado, se alerta de que se establecerá el estado por defecto ("Disponible").
                messagebox.showinfo("¡Atención!", "Se signará al material el estado por defecto ('Disponible').")
            # Añadimos el material a la tabla
            self.cur.execute("INSERT INTO material (nombre, codigo, id_estado) VALUES (?, ?, ?);",
                             (nombre.upper(), codigo.upper(), id_estado))
            self.con.commit()
        else:
            # En caso de no introducir un estado válido saltará una advertencia.
            messagebox.showwarning("Error", "El estado del material introducido no está permitido. Debe ser 'Disponible' o 'No Disponible'. Si no introduce ningún estado, se establecerá como 'Disponible'.")

    # Modificar material
    def update_material(self, id_update, nombre, codigo, estado):
        # Si se ha seleccionado una entrada, se avisa al usuario por si quiere no modificarla como ha indicado
        if messagebox.askokcancel("Atención", "¿Está seguro de modificar la entrada seleccionada con los datos que va a proporcionar?"):
            id_estado = 0
            # Valor para ID_ESTADO en caso de que el estado sea "Disponible" o está vacío ("").
            if estado.upper() == "DISPONIBLE" or estado == "":
                id_estado = 1
            # Valor para ID_ESTADO en caso de que el estado sea "No Disponible".
            elif estado.upper() == "NO DISPONIBLE":
                id_estado = 2

            #  Se compeueba que se ha introducido un estado correcto
            if id_estado != 0:
                # Se actualiza la entrada con el id seleccionado (id_update)
                self.cur.execute("UPDATE material SET nombre = ?, codigo = ?, id_estado = ? WHERE id = ?",
                                 (nombre, codigo, id_estado, id_update))
                self.con.commit()
            else:
                # En caso de no introducir un estado válido saltará una advertencia.
                messagebox.showwarning("Error", "El estado del material introducido no está permitido. Debe ser 'Disponible' o 'No Disponible'. Si no introduce ningún estado, se establecerá como 'Disponible'.")

    # Eliminar material
    def delete_material(self, id_delete):
        # Si se ha seleccionado una entrada, se avisa al usuario por si quiere no eliminarla en realidad
        if messagebox.askokcancel("Atención", "¿Está seguro de borrar la entrada seleccionada?"):
            # Se eliminan las relaciones que tuviera en la tabla de préstamos
            self.cur.execute("DELETE FROM prestamos WHERE id_material = "+id_delete+";")
            self.con.commit()

            # Se elimina el material con el id dado (id_delete)
            self.cur.execute("DELETE FROM material WHERE id = "+id_delete+";")
            self.con.commit()

    # Buscar material
    def search_material(self, nombre, codigo, estado):
        query = """SELECT material.id, material.nombre, material.codigo, estado.nombre
                FROM material, estado
                WHERE estado.id = material.id_estado"""
        # Comprobamos sobre que datos se desea buscar
        if estado != "":
            query += " AND estado.nombre = '"+estado.upper()+"'"
        if nombre != "":
            query += " AND material.nombre = '"+nombre.upper()+"'"
        if codigo != "":
            query += " AND material.codigo = '"+codigo.upper()+"'"

        # Seleccionamos y devolvemos los materiales que coincidan con los parámetros dados
        self.cur.execute(query)
        result = self.cur.fetchall()

        return result

# Funciones para la tabla PROFESORES
    # Mostrar todos los profesores y usuarios
    def view_profes(self):
        # Seleccionamos y devolvemos el todos los profesores guardados
        self.cur.execute("""SELECT profesores.id, permisos.nombre||'-', profesores.nombre, profesores.ape1, profesores.ape2,
                        profesores.user, profesores.password
                        FROM profesores, permisos
                        WHERE permisos.id = profesores.id_permisos;""")
        result = self.cur.fetchall()
        return result

    # Añadir profesor
    def insert_profe(self, permisos, nombre, ape1, ape2, user, password):
        id_permisos = 0
        # Valor para ID_PERMISOS en caso de que los permisos sean de "Administrador".
        if permisos.upper() == "ADMINISTRADOR":
            id_permisos = 1
        # Valor para ID_PERMISOS en caso de que los permisos sean de "Encargado".
        elif permisos.upper() == "ENCARGADO":
            id_permisos = 2
        # Valor para ID_PERMISOS en caso de que los permisos sean de "Profesor".
        elif permisos.upper() == "PROFESOR" or permisos == "":
            id_permisos = 3

        # Se comprueba que se han introducido unos permisos correctos.
        if id_permisos != 0:
            if permisos == "":
                # Si no se ha introducido ningún tipo depermiso, se alerta de que se establecerán los permisos por defecto ("Profesor").
                messagebox.showinfo("¡Atención!", "Se asignarán al nuevo usuario los permisos por defecto ('Profesor').")
            # Añadimos el profesor a la tabla
            self.cur.execute("INSERT INTO profesores (user, password, id_permisos, nombre, ape1, ape2) VALUES (?, ?, ?, ?, ?, ?);",
                             (user, password, id_permisos, nombre.upper(), ape1.upper(), ape2.upper()))
            self.con.commit()
        else:
            # Alerta en caso de que los permisos sean incorrectos
            messagebox.showwarning("Error", "Los permisos que desea asignar al nuevo usuario son incorrectos. Deben ser de 'Administrador', 'Encargado' o 'Profesor'.")

    # Modificar profesor
    def update_profe(self, id_update, permisos, nombre, ape1, ape2, user, password):
        # Si se ha seleccionado una entrada, se avisa al usuario por si quiere no modificarla como ha indicado
        if messagebox.askokcancel("Atención", "¿Está seguro de modificar la entrada seleccionada con los datos que va a proporcionar?"):
            id_permisos = 0
            if permisos.upper() == "ADMINISTRADOR":
                id_permisos = 1
            elif permisos.upper() == "ENCARGADO":
                id_permisos = 2
            elif permisos.upper() == "PROFESOR":
                id_permisos = 3

            if id_permisos != 0:
                # Se actualiza la entrada con el id dado (id_update) y se le dan los parámetros introducidos
                self.cur.execute("UPDATE profesores SET user = ?, password = ?, id_permisos = ?, nombre = ?, ape1 = ?, ape2 = ? WHERE id = ?",
                                 (user, password, id_permisos, nombre.upper(), ape1.upper(), ape2.upper(), id_update))
                self.con.commit()

            else:
                # Alerta en caso de que los permisos sean incorrectos
                messagebox.showwarning("Error", "Los permisos que desea asignar al usuario seleccionado son incorrectos. Deben ser de 'Administrador', 'Encargado' o 'Profesor'.")

    # Eliminar profesor
    def delete_profe(self, id_delete):
        # Si se ha seleccionado una entrada, se avisa al usuario por si quiere no eliminarla en realidad
        if messagebox.askokcancel("Atención", "¿Está seguro de borrar la entrada seleccionada?"):
            # Se eliminan las relaciones que tuviera en la tabla de préstamos
            self.cur.execute("DELETE FROM prestamos WHERE id_profesor ="+id_delete+";")
            self.con.commit()

            # Se eliminan las relaciones que tuviera en la tabla profesores_departamentos
            self.cur.execute("DELETE FROM profesores_departamentos WHERE id_profesor = "+id_delete+";")
            self.con.commit()

            # Se elimina el profesor con el id dado (id_delete)
            self.cur.execute("DELETE FROM profesores WHERE id = "+id_delete+";")
            self.con.commit()

    # Buscar profesor
    def search_profe(self, permisos, nombre, ape1, ape2, user, password):
        query = """SELECT profesores.id, permisos.nombre||'-', profesores.nombre, profesores.ape1, profesores.ape2,
                profesores.user, profesores.password
                FROM profesores, permisos
                WHERE permisos.id = profesores.id_permisos"""

        # Comprobamos sobre que datos se desea buscar
        if permisos != "":
            query += " AND permisos.nombre = '"+permisos.upper()+"'"
        if nombre != "":
            query += " AND profesores.nombre = '"+nombre.upper()+"'"
        if ape1 != "":
            query += " AND profesores.ape1 = '"+ape1.upper()+"'"
        if ape2 != "":
            query += " AND profesores.ape2 = '"+ape2.upper()+"'"
        if user != "":
            query += " AND profesores.user = '"+user+"'"
        if password != "":
            query += " AND profesores.password = '"+password+"'"

        # Seleccionamos y devolvemos la información del profesor que coincida con los parámetros dados
        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

# Relaciones entre profesores y departamentos
    # Mostrar todos los departamentos a los que pertenece el profesor seleccionado
    def view_profe_departs(self, id_user):
        # Seleccionamos y devolvemos todos los departamentos relacionados con el profesor indicado
        self.cur.execute("""SELECT departamentos.id, departamentos.nombre
                            FROM departamentos, profesores_departamentos
                            WHERE departamentos.id = profesores_departamentos.id_depart
                            AND profesores_departamentos.id_profesor = """+id_user+"""
                            ORDER BY departamentos.id""")
        result = self.cur.fetchall()
        return result

    # Buscar departamentos a los que pertenece el profesor seleccionado
    def search_profe_depart(self, nombre_depart, id_user):
        # Seleccionamos y devolvemos el departamento que coincida con el nombre dado
        self.cur.execute("""SELECT departamentos.id, departamentos.nombre
                            FROM departamentos, profesores_departamentos
                            WHERE departamentos.id = profesores_departamentos.id_depart
                            AND profesores_departamentos.id_profesor = ?
                            AND departamentos.nombre = ?""", (id_user, nombre_depart.upper()))
        result = self.cur.fetchall()
        return result

    # Eliminar departamento al que pertenece el profesor seleccionado
    def delete_profe_depart(self, id_depart, id_user):
        # Si se ha seleccionado una entrada, se avisa al usuario por si quiere no eliminarla en realidad
        if messagebox.askokcancel("Atención", "¿Está seguro de sacar al profesor del departamento seleccionado?"):
            # Se elimina el departamento del profesor con el id dado (id_delete)
            self.cur.execute("""DELETE FROM profesores_departamentos
                                WHERE id_depart = ?
                                AND id_profesor = ?""", (id_depart, id_user))
            self.con.commit()

    # Buscar departamentos que añadir al profesor seleccionado
    def search_seldepart(self, nombre_depart, id_user):
        # Seleccionamos y devolvemos el departamento que coincida con el nombre dado
        self.cur.execute("""SELECT departamentos.id, departamentos.nombre
                            FROM departamentos, profesores_departamentos
                            WHERE departamentos.id = profesores_departamentos.id_depart
                            AND profesores_departamentos.id_profesor = ?
                            AND departamentos.nombre != ?""", (id_user, nombre_depart.upper()))
        result = self.cur.fetchall()
        return result

    # Añadir departamento que añadir al profesor seleccionado
    def add_seldepart(self, id_user, id_depart):
        # Comprobamos que el profesor no pertenezca ya al departamento al que se le va a añadir
        self.cur.execute("""SELECT id_depart FROM profesores_departamentos
                            WHERE id_profesor = ?
                            AND id_depart = ?""", (id_user, id_depart))
        pertenece = self.cur.fetchall()

        if not pertenece:
            # Añadimos el departamento al profesor
            self.cur.execute("""INSERT INTO profesores_departamentos (id_profesor, id_depart)
                                VALUES (?, ?);""", (id_user, id_depart))
            self.con.commit()
        else:
            messagebox.showwarning("Error", "El profesor ya pertenece al departamento seleccionado.")

# Funciones para la tabla PRESTAMOS cuando se accede como ADMIN
    # Mostrar todos los préstamos de todos los usuarios
    def view_prestamos_admin(self):
        #Visualizamos todos los prestamos
        self.cur.execute("""SELECT prestamos.id, profesores.user, material.nombre, material.codigo,
                        prestamos.dia_ini, '/'||prestamos.mes_ini, '/'||prestamos.ano_ini,
                        '-'||prestamos.dia_fin, '/'||prestamos.mes_fin, '/'||prestamos.ano_fin
                        FROM prestamos, profesores, material
                        WHERE profesores.id = prestamos.id_profesor
                        AND material.id = prestamos.id_material""")
        result = self.cur.fetchall()
        return result

    # Modificar préstamo
    def update_prestamo(self, id_update, user, material, cod, dia_ini, mes_ini, ano_ini, dia_fin="", mes_fin="", ano_fin=""):
        # Si se ha seleccionado una entrada, se avisa al usuario por si quiere no modificarla como ha indicado
        if messagebox.askokcancel("Atención", "¿Está seguro de modificar la entrada seleccionada con los datos que va a proporcionar?"):
            # Obtenemos el id del profesor y del material para actualizar la tabla préstamos
            id_prof = ""
            id_mat = ""
            self.cur.execute("SELECT id FROM profesores WHERE user = '"+user+"'")
            id_profesor = self.cur.fetchall()
            for id_pr in id_profesor:
                for ip in id_pr:
                    id_prof = ip

            self.cur.execute("SELECT id FROM material WHERE nombre = ? AND codigo = ?",
                             (material.upper(), cod.upper()))
            id_material = self.cur.fetchall()
            for id_mt in id_material:
                for im in id_mt:
                    id_mat = im

            # Se actualiza la entrada con el id dado (id_update) y se le cambia los parámetros introducidos
            self.cur.execute("""UPDATE prestamos SET id_material = ?, id_profesor = ?,
                            dia_ini = ?, mes_ini = ?, ano_ini = ?,
                            dia_fin = ?, mes_fin = ?, ano_fin = ? WHERE id = ?""",
                             (id_mat, id_prof, dia_ini, mes_ini, ano_ini, dia_fin, mes_fin, ano_fin, id_update))
            self.con.commit()

    # Eliminar préstamo
    def delete_prestamo(self, id_delete, cod):
        # Si se ha seleccionado una entrada, se avisa al usuario por si quiere no eliminarla en realidad
        if messagebox.askokcancel("Atención", "¿Está seguro de eliminar el préstamo seleccionado?"):
            # Se comprueba si el préstamo a eliminar finalizó
            self.cur.execute("SELECT dia_fin FROM prestamos WHERE id = "+id_delete)
            fin = self.cur.fetchall()
            for f in fin:
                # Si no ha finalizado, volvemos a poner el material del préstamo como DISPONIBLE (id_estado = 1)
                if str(f) == "('',)":
                    self.cur.execute("UPDATE material SET id_estado = 1 WHERE codigo = '"+cod+"'")
                    self.con.commit()
            # Se elimina el préstamo con el id dado (id_delete)
            self.cur.execute("DELETE FROM prestamos WHERE id = "+id_delete)
            self.con.commit()

    # Buscar préstamo de cualquier usuario
    def search_prestamo_admin(self, user, material, cod, dia_ini, mes_ini, ano_ini, dia_fin, mes_fin, ano_fin):
        query = """SELECT prestamos.id, profesores.user, material.nombre, material.codigo,
                prestamos.dia_ini, '/'||prestamos.mes_ini, '/'||prestamos.ano_ini,
                '-'||prestamos.dia_fin, '/'||prestamos.mes_fin, '/'||prestamos.ano_fin
                FROM prestamos, profesores, material
                WHERE profesores.id = prestamos.id_profesor
                AND material.id = prestamos.id_material"""

        # Comprobamos sobre que datos se desea buscar
        if user != "":
            query += " AND profesores.user = '"+user+"'"
        if material != "":
            query += " AND material.nombre = '"+material.upper()+"'"
        if cod != "":
            query += " AND material.codigo = '"+cod.upper()+"'"
        if dia_ini != "":
            query += " AND prestamos.dia_ini = '"+dia_ini+"'"
        if mes_ini != "":
            query += " AND prestamos.mes_ini = '"+mes_ini+"'"
        if ano_ini != "":
            query += " AND prestamos.ano_ini = '"+ano_ini+"'"
        if dia_fin != "":
            query += " AND prestamos.dia_fin = '"+dia_fin+"'"
        if mes_fin != "":
            query += " AND prestamos.mes_fin = '"+mes_fin+"'"
        if ano_fin != "":
            query += " AND prestamos.ano_fin = '"+ano_fin+"'"

        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

# Funciones para la tabla PRESTAMOS como profesor
    # Mostrar todos los préstamos del profesor que ha iniciado sesión
    def view_prestamos(self, user):
        # Visualizamos los prestamos con un usuario normal
        self.cur.execute("""SELECT prestamos.id, material.nombre, material.codigo,
                            prestamos.dia_ini, '/'||prestamos.mes_ini, '/'||prestamos.ano_ini,
                            '-'||prestamos.dia_fin, '/'||prestamos.mes_fin, '/'||prestamos.ano_fin
                            FROM prestamos, profesores, material
                            WHERE profesores.id = prestamos.id_profesor
                            AND material.id = prestamos.id_material
                            AND profesores.user = '"""+user+"'")
        result = self.cur.fetchall()
        return result

    # Buscar préstmos del profesor que ha iniciado sesión
    def search_prestamo(self, user, material, cod, dia_ini, mes_ini, ano_ini, dia_fin, mes_fin, ano_fin):

        query = """SELECT prestamos.id, material.nombre, material.codigo,
                prestamos.dia_ini, '/'||prestamos.mes_ini, '/'||prestamos.ano_ini,
                '-'||prestamos.dia_fin, '/'||prestamos.mes_fin, '/'||prestamos.ano_fin
                FROM prestamos, profesores, material
                WHERE profesores.id = prestamos.id_profesor
                AND material.id = prestamos.id_material"""

        # Comprobamos sobre que datos se desea buscar
        if user != "":
            query += " AND profesores.user = '"+user+"'"
        if material != "":
            query += " AND material.nombre = '"+material.upper()+"'"
        if cod != "":
            query += " AND material.codigo = '"+cod.upper() + "'"
        if dia_ini != "":
            query += " AND prestamos.dia_ini = '"+dia_ini+"'"
        if mes_ini != "":
            query += " AND prestamos.mes_ini = '"+mes_ini+"'"
        if ano_ini != "":
            query += " AND prestamos.ano_ini = '"+ano_ini+"'"
        if dia_fin != "":
            query += " AND prestamos.dia_fin = '"+dia_fin+"'"
        if mes_fin != "":
            query += " AND prestamos.mes_fin = '"+mes_fin+"'"
        if ano_fin != "":
            query += " AND prestamos.ano_fin = '"+ano_fin+"'"

        self.cur.execute(query)
        result = self.cur.fetchall()
        return result

    # Añadir préstamo para cualquier usuario
    def add_prestamo(self, user, id_material, dia_ini, mes_ini, ano_ini):
        # Obtenemos el id del profesor
        id_prof = ""
        self.cur.execute("SELECT id FROM profesores WHERE user = '"+user+"'")
        id_profesor = self.cur.fetchall()
        for id_pr in id_profesor:
            for ip in id_pr:
                id_prof = ip
        # Realizamos el préstamo
        self.cur.execute("""INSERT INTO prestamos (id_material, id_profesor, dia_ini, mes_ini, ano_ini,
                        dia_fin, mes_fin, ano_fin)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                         (id_material, id_prof, dia_ini, mes_ini, ano_ini, "", "", ""))
        self.con.commit()

        # Cambiamos el estado del material prestado a NO DISPONIBLE (id_estado = 2)
        self.cur.execute("UPDATE material SET id_estado = 2 WHERE id = "+id_material)
        self.con.commit()

    # Finalizar préstamo para cualquier usuario
    def finish_prestamo(self, id_prestamo, id_material, dia_fin, mes_fin, ano_fin):
        # Se alerta de la finalixzación del préstamo al usuario
        if messagebox.askokcancel("Atención", "¿Está seguro de terminar el préstamo?"):
            # Se le añade la fecha de finalización al préstamo indicado
            self.cur.execute("UPDATE prestamos SET dia_fin = ?, mes_fin = ?, ano_fin = ? WHERE id = ?",
                             (dia_fin, mes_fin, ano_fin, id_prestamo))
            self.con.commit()

            # Cambiamos el estado del material prestado a DISPONIBLE (id_estado = 1)
            self.cur.execute("UPDATE material SET id_estado = 1 WHERE id = "+id_material)
            self.con.commit()
