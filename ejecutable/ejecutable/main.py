from database import *
import tkinter
from tkinter import messagebox
from tkinter import font
from PIL import Image
from PIL import ImageTk
from datetime import datetime
from fpdf import FPDF
import easygui


# Variables globales
image = Image.open("logo_alomadrigal.png")
select_page = ""
id_user_departs = ""
id_depart_profes = ""
user_login = ""

# Creación de la base de datos y un cursor para realizar consultas y acciones sobre ella
db = DataBase()
cur = db.con.cursor()

# variable con la fecha actual
now = datetime.now()


# Función para cerrar la app y la conexión a la base de datos
def close():
    global app, db
    # Alerta para recordar al usuario la perdida de los datos en caso de que no los haya guardado correctamente
    if messagebox.askokcancel("Cerrar", "¿Deseas salir de la aplicación? Se perderán los datos que no hayas guardado correctamente."):
        app.destroy()
        del db

# Clase principal
class App(tkinter.Tk):

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        # Tamaño minimo de la ventana
        self.minsize(1000, 500)

        # Fuentes para los elementos de la interfaz
        self.title_font = font.Font(family="Calibri", size=32, weight="bold", slant="italic")
        self.second_title_font = font.Font(family="calibri", size=16, weight="bold", slant="italic")
        self.label_font = font.Font(family="calibri", size=12, weight="bold", slant="roman")
        self.entry_font = font.Font(family="Calibri", size=12, weight="normal", slant="roman")
        self.button_font = font.Font(family="Calibri", size=12, weight="bold", slant="roman")
        self.list_font = font.Font(family="Calibri", size=16, weight="bold", slant="roman")

        # Icono y nombre de la aplicacion
        self.iconbitmap("logo_alomadrigal.ico")
        self.title("Préstamos IES Alonso de Madrigal")

        self.config(bd=5, bg="#003468")

        # frame contenedor sobre el que pondremos el frame que deseemos visualizar
        self.container = tkinter.Frame(self)
        self.container.pack(anchor="center", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Ponemos todos los frames uno encima del otro mediante su nombre. El que quede encima sera el visible
        self.frames = {}
        for f in (SelectMaterialPageProf,PrestamosPageProf, SelectMaterialPageAM, PrestamosPageAM, MaterialPage,
                  ProfeDepartsPage, SelectDepartsPage, ProfesPage, DepartsPage, ManagerPage, AdminPage, StartPage):
            page_name = f.__name__
            frame = f(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Forzamos que sea visible el frame de la pagina de inicio ("StartPage")
        self.show_frame("StartPage")

    # Función para mostrar el frame según su nombre (page_name)
    def show_frame(self, page_name):
        self.frame = self.frames[page_name]
        self.frame.tkraise()


#Función para iniciar sesión
def login(parent, user, password, controller):
    global cur, select_page, user_login
    is_user = False
    is_password = False

    # Comprobamos que se inicia sesión con un usuario existente
    cur.execute("SELECT user FROM profesores;")
    users = cur.fetchall()

    if user == "" or password == "":
        messagebox.showwarning("Log in incorrecto", "El nombre de usuario y/o la contraseña no se han introducido.")
    else:
        for u in users:
            if str(u) == "('"+user+"',)":
                is_user = True

        if not is_user:
            messagebox.showwarning("Log in incorrecto", "El nombre de usuario introducido no está registrado.")
        else:
            cur.execute("SELECT password FROM profesores WHERE user = '"+user+"';")
            passwords = cur.fetchall()

            for p in passwords:
                if str(p) == "('"+password+"',)":
                    is_password = True

            # Comprobamos que la contraseña introducida es la correspondiente al usuario
            if not is_password:
                messagebox.showwarning("Log in incorrecto", "La contraseña introducida es incorrecta.")
            else:
                if user == "admin":
                    user_login = user
                    parent.show_frame("AdminPage")
                    select_page = "AdminPage"
                elif user == "manager":
                    user_login = user
                    parent.show_frame("ManagerPage")
                    select_page = "ManagerPage"
                else:
                    user_login = user
                    parent.show_frame("PrestamosPageProf")
                    view_prestamos_command()
                    select_page = "StartPage"

        # Vaciamos los campos de usuario y contraseña para que no se mantengan al salir y ponemos focus en el campo del usuario
        controller.ent_user.delete(0, "end")
        controller.ent_pass.delete(0, "end")
        controller.ent_user.focus()

# Pagina de inicio de sesión
class StartPage(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=20)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(anchor="center", fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(anchor="center", fill="both", expand=True)

        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)

        # Contenido de la cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        global image
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, columnspan=2, sticky="nsew")

        # Campo para introducir el usuario
        self.lb_user = tkinter.Label(self.body, text="Usuraio", font=controller.label_font, bg="#2060C0")
        self.lb_user.grid(row=0, column=0, padx=10, sticky="nse")

        self.user_text = tkinter.StringVar()
        self.ent_user = tkinter.Entry(self.body, textvariable=self.user_text, width=30, font=controller.entry_font)
        self.ent_user.grid(row=0, column=1, sticky="nsw")
        # El entry para el nombre de usuario estara seleccionado de manera predeterminada
        self.ent_user.focus()

        # Campo para introducir la contraseña
        self.lb_pass = tkinter.Label(self.body, text="Contraseña", font=controller.label_font, bg="#2060C0")
        self.lb_pass.grid(row=1, column=0, padx=10, sticky="nse")

        self.pass_text = tkinter.StringVar()
        self.ent_pass = tkinter.Entry(self.body, textvariable=self.pass_text, width=30, font=controller.entry_font)
        self.ent_pass.grid(row=1, column=1, sticky="nsw")
        # Ciframos la contraseña para que al escribir solo se vean asteriscos (*)
        self.ent_pass.config(show="*")

        self.btn_login = tkinter.Button(self.body, text="Log in", font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, width=30, command=lambda: login(self.controller, self.user_text.get(), self.pass_text.get(), self))
        self.btn_login.grid(row=2, column=1, sticky="nsw")

        self.btn_exit = tkinter.Button(self.body, text="Cerrar", font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, width=30, command=close)
        self.btn_exit.grid(row=3, column=1, sticky="nsw")


# Función para visualizar siempre los préstamos con la información actualizada en caso de que se cambie aluna otra tabla
def go_to_material(controller):
    controller.show_frame("MaterialPage")
    view_material_command()

# Función para visualizar siempre los préstamos con la información actualizada en caso de que se cambie aluna otra tabla
def go_to_prestamosam(controller):
    controller.show_frame("PrestamosPageAM")
    view_prestamos_admin_command()

# Pagina de selección de tablas de la base de datos (ADMIN)
class AdminPage(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=20)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(anchor="center", fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(anchor="center", fill="both", expand=True)

        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_columnconfigure(2, weight=1)
        self.body.grid_columnconfigure(3, weight=1)

        # Cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        global image
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, sticky="nsew")

        self.btn_back = tkinter.Button(self.header, text="Salir", font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, command=lambda: self.controller.show_frame("StartPage"))
        self.btn_back.grid(row=1, column=0, padx=10, sticky="ew")

        # Cuerpo con las opciones de administrador
        self.label = tkinter.Label(self.header, text="Opciones de administrador", font=controller.second_title_font, bg="#2060C0", fg="#E0E0E0", pady=5)
        self.label.grid(row=1, column=1, sticky="w")

        self.btn_profes = tkinter.Button(self.body, text="Usuarios", font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: self.controller.show_frame("ProfesPage"))
        self.btn_profes.grid(row=0, column=0, sticky="new")

        self.btn_depart = tkinter.Button(self.body, text="Departamentos", font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: self.controller.show_frame("DepartsPage"))
        self.btn_depart.grid(row=0, column=1, sticky="new")

        self.btn_mater = tkinter.Button(self.body, text="Material", font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: go_to_material(self.controller))
        self.btn_mater.grid(row=0, column=2, sticky="new")

        self.btn_prest = tkinter.Button(self.body, text="Préstamos", font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: go_to_prestamosam(self.controller))
        self.btn_prest.grid(row=0, column=3, sticky="new")


# Pagina de selección de tablas de la base de datos (ENCARGADO DE MANTENIMIENTO)
class ManagerPage(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=20)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(anchor="center", fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(anchor="center", fill="both", expand=True)

        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)

        # Cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        global image
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, sticky="nsew")

        self.btn_back = tkinter.Button(self.header, text="Salir", font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, command=lambda: self.controller.show_frame("StartPage"))
        self.btn_back.grid(row=1, column=0, padx=10, sticky="ew")

        # Cuerpo con las opciones de mantenimiento
        self.label = tkinter.Label(self.header, text="Opciones de mantenimiento", font=controller.second_title_font, bg="#2060C0", fg="#E0E0E0", pady=5)
        self.label.grid(row=1, column=1, sticky="w")

        self.btn_mater = tkinter.Button(self.body, text="Material", font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: go_to_material(self.controller))
        self.btn_mater.grid(row=0, column=0, sticky="new")

        self.btn_prest = tkinter.Button(self.body, text="Préstamos", font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: go_to_prestamosam(self.controller))
        self.btn_prest.grid(row=0, column=1, sticky="new")


# Funciones de las entradas en la pantalla DEPARTAMENTOS
def view_departs_command(parent):
    global db
    parent.list_dep.delete(0, "end")
    for row in db.view_departs():
        parent.list_dep.insert("end", row)

def search_depart_command(parent):
    global db
    if parent.nombre_dep_text.get() == "":
        view_departs_command(parent)
    else:
        parent.list_dep.delete(0, "end")
        for row in db.search_depart(parent.nombre_dep_text.get()):
            parent.list_dep.insert("end", row)

def add_depart_command(parent):
    global db, cur
    is_dep = False
    if parent.nombre_dep_text.get() == "":
        messagebox.showwarning("Error", "El nombre del departamento no puede estar vacío.")
    else:
        # Comprobamos que el departamento a añadir no esté ya registrado
        cur.execute("SELECT nombre FROM departamentos;")
        deps = cur.fetchall()
        for d in deps:
            if str(d) == "('"+parent.nombre_dep_text.get().upper()+"',)":
                is_dep = True
                break
            else:
                is_dep = False
        if is_dep:
            messagebox.showwarning("Error", "El departamento ya está registrado.")
        else:
            db.insert_depart(parent.nombre_dep_text.get())
            view_departs_command(parent)
            parent.ent_nombre_dep.delete(0, "end")

def delete_depart_command(parent):
    global db
    try:
        db.delete_depart(str(selected_tuple_dep[0]))
        view_departs_command(parent)
        parent.ent_nombre_dep.delete(0, "end")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún departamento para eliminar.")

def update_depart_command(parent):
    global db, cur
    is_original = True
    is_cod = False
    try:
        if parent.nombre_dep_text.get() == "":
            messagebox.showwarning("Error", "El nombre del departamento no puede estar vacío.")
        else:
            # Permitimos que el nombre del departamento pueda ser el que se introdujo originalmente y no cambie
            cur.execute("SELECT nombre FROM departamentos WHERE id = "+str(selected_tuple_dep[0]))
            current_dep = cur.fetchall()
            for d in current_dep:
                if str(d) == ("('"+parent.nombre_dep_text.get().upper()+"',)"):
                    is_original = True
                    break
                else:
                    is_original = False
                    # Comprobamos que el departamento a modificar no esté ya registrado
                    cur.execute("SELECT nombre FROM departamentos;")
                    deps = cur.fetchall()
                    for d in deps:
                        if str(d) == ("('"+parent.nombre_dep_text.get().upper()+"',)"):
                            is_cod = True
                            break
                        else:
                            is_cod = False
            if not is_original and is_cod:
                messagebox.showwarning("Error", "El nombre del departamento ya está registrado. Elija uno diferente.")
            else:
                db.update_depart(str(selected_tuple_dep[0]), parent.nombre_dep_text.get())
                view_departs_command(parent)
                parent.ent_nombre_dep.delete(0, "end")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún departamento para modificar.")

# Pagina de consultas en la tabla DEPARTAMENTOS
class DepartsPage(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=20)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(anchor="center", fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(anchor="center", fill="both", expand=True)

        self.body.grid_rowconfigure(2, weight=1)
        self.body.grid_rowconfigure(3, weight=1)
        self.body.grid_rowconfigure(4, weight=1)
        self.body.grid_rowconfigure(5, weight=1)
        self.body.grid_columnconfigure(0, weight=1)

        # Variables globales usadas
        global image

        # Cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, sticky="nsw")

        self.lb_second_title = tkinter.Label(self.header, text="Gestión de departamentos", font=controller.second_title_font, bg="#2060C0", fg="#E0E0E0", pady=5)
        self.lb_second_title.grid(row=1, column=1, sticky="nsw")

        self.btn_back = tkinter.Button(self.header, text="Volver", font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, command=lambda: self.controller.show_frame("AdminPage"))
        self.btn_back.grid(row=1, column=0, padx=10, sticky="ew")

        # Cuerpo con las opciones de visualización y gestión de los departamentos
        self.lb_nombre_dep = tkinter.Label(self.body, text="Nombre del departamento", font=controller.label_font, bg="#2060C0")
        self.lb_nombre_dep.grid(row=0, column=0, padx=20, sticky="nsw")

        self.nombre_dep_text = tkinter.StringVar()
        self.ent_nombre_dep = tkinter.Entry(self.body, textvariable=self.nombre_dep_text, font=controller.entry_font)
        self.ent_nombre_dep.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

        self.list_dep = tkinter.Listbox(self.body, font=controller.list_font)
        self.list_dep.grid(row=2, column=0, rowspan=4, sticky="nsew")

        self.sb = tkinter.Scrollbar(self.body, orient="vertical", command=self.list_dep.yview)
        self.sb.grid(row=2, column=1, rowspan=4, sticky="nsw")

        self.list_dep.configure(yscrollcommand=self.sb.set)
        self.list_dep.bind('<<ListboxSelect>>', self.get_selected_row)

        self.btn_search = tkinter.Button(self.body, text="Buscar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: search_depart_command(self))
        self.btn_search.grid(row=2, column=2, sticky="nsw")

        self.btn_add = tkinter.Button(self.body, text="Añadir nuevo", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: add_depart_command(self))
        self.btn_add.grid(row=3, column=2, sticky="nsw")

        self.btn_update = tkinter.Button(self.body, text="Modificar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: update_depart_command(self))
        self.btn_update.grid(row=4, column=2, sticky="nsw")

        self.btn_delete = tkinter.Button(self.body, text="Eliminar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: delete_depart_command(self))
        self.btn_delete.grid(row=5, column=2, sticky="nsw")

        view_departs_command(self)

    def get_selected_row(self, event):
        global selected_tuple_dep
        try:
            index = self.list_dep.curselection()[0]
            selected_tuple_dep = self.list_dep.get(index)
            self.ent_nombre_dep.delete(0, "end")
            self.ent_nombre_dep.insert("end", selected_tuple_dep[1])
        except:
            del selected_tuple_dep


# Funciones de las entradas en la pantalla MATERIAL
def view_material_command():
    global db
    list_mat.delete(0, "end")
    for row in db.view_material():
        list_mat.insert("end", row)

def search_material_command(parent):
    global db
    if parent.nombre_mat_text.get() == "" and parent.codigo_text.get() == "" and parent.estado_text.get() == "":
        view_material_command()
    else:
        list_mat.delete(0, "end")
        for row in db.search_material(parent.nombre_mat_text.get(), parent.codigo_text.get(), parent.estado_text.get()):
            list_mat.insert("end", row)

def add_material_command(parent):
    global db, cur
    is_cod = False
    if parent.nombre_mat_text.get() == "" or parent.codigo_text.get() == "":
        messagebox.showwarning("Error", "Hay campos obligatorios del material sin información.")
    else:
        # Comprobamos que el código del material a modificar no esté ya registrado
        cur.execute("SELECT codigo FROM material;")
        cods = cur.fetchall()
        for c in cods:
            if str(c) == "('"+parent.codigo_text.get().upper()+"',)":
                is_cod = True
                break
            else:
                is_cod = False
        if is_cod:
            messagebox.showwarning("Error", "El código del material ya está registrado. Elija uno diferente que no pertenezca a ningún otro material.")
        else:
            db.insert_material(parent.nombre_mat_text.get(), parent.codigo_text.get(), parent.estado_text.get())
            view_material_command()
            parent.ent_nombre_mat.delete(0, "end")
            parent.ent_codigo.delete(0, "end")
            parent.ent_estado.delete(0, "end")

def delete_material_command(parent):
    global db, cur
    try:
        # Si vamos a eliminar un material comprobamos que el material no está en ningún préstamo sin finalizar
        cur.execute("""SELECT prestamos.id
                 FROM prestamos, material
                 WHERE material.id = prestamos.id_material
                 AND material.codigo = ? AND material.nombre = ?
                 AND prestamos.dia_fin == ''""", (parent.codigo_text.get().upper(), parent.nombre_mat_text.get().upper()))
        prests = cur.fetchall()
        if not prests:
            db.delete_material(str(selected_tuple_mat[0]))
            view_material_command()
            parent.ent_nombre_mat.delete(0, "end")
            parent.ent_codigo.delete(0, "end")
            parent.ent_estado.delete(0, "end")
        else:
            # Alerta en caso de que el material esté en un préstamo sin finalizar
            messagebox.showwarning("Error", "El material aún está bajo una solicitud. Consulte con el solicitante para realizar los cambios.")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún material para eliminar.")

def update_material_command(parent):
    global db, cur
    is_original = True
    is_cod = False
    try:
        if parent.nombre_mat_text.get() == "" or parent.codigo_text.get() == "":
            messagebox.showwarning("Error", "Hay campos obligatorios del material sin información.")
        else:
            # Permitimos que el código del material pueda ser el que se introdujo originalmente y no cambie
            cur.execute("SELECT codigo FROM material WHERE id = "+str(selected_tuple_mat[0]))
            current_cod = cur.fetchall()
            for c in current_cod:
                if str(c) == ("('"+parent.codigo_text.get().upper()+"',)"):
                    is_original = True
                    break
                else:
                    is_original = False
                    # Comprobamos que el código del material a modificar no esté ya registrado
                    cur.execute("SELECT codigo FROM material;")
                    cods = cur.fetchall()
                    for c in cods:
                        if str(c) == ("('"+parent.codigo_text.get().upper()+"',)"):
                            is_cod = True
                            break
                        else:
                            is_cod = False
            if not is_original and is_cod:
                messagebox.showwarning("Error", "El código del material ya está registrado. Elija uno diferente.")
            else:
                # Si se cambia el estado a DISPONIBLE comprobamos que el material no está en ningún préstamo sin finalizar
                cur.execute("""SELECT prestamos.id
                            FROM prestamos, material
                            WHERE material.id = prestamos.id_material
                            AND material.codigo = ? AND material.nombre = ?
                            AND prestamos.dia_fin == ''""", (parent.codigo_text.get().upper(), parent.nombre_mat_text.get().upper()))
                prests = cur.fetchall()
                if not prests:
                    db.update_material(str(selected_tuple_mat[0]), parent.nombre_mat_text.get(), parent.codigo_text.get(), parent.estado_text.get())
                    view_material_command()
                    parent.ent_nombre_mat.delete(0, "end")
                    parent.ent_codigo.delete(0, "end")
                    parent.ent_estado.delete(0, "end")
                else:
                    # Alerta en caso de que el material esté en un préstamo sin finalizar
                    messagebox.showwarning("Error", "El material aún está bajo una solicitud. Consulte con el solicitante para realizar los cambios.")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún material para modificar.")

# Pagina de consultas en la tabla MATERIAL
class MaterialPage(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=10)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(fill="both", expand=True)

        self.body.grid_rowconfigure(2, weight=1)
        self.body.grid_rowconfigure(3, weight=1)
        self.body.grid_rowconfigure(4, weight=1)
        self.body.grid_rowconfigure(5, weight=1)
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_columnconfigure(2, weight=1)

        # Variables globales usadas
        global image, select_page, list_mat

        # Cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, columnspan=8, sticky="nsw")

        self.lb_second_title = tkinter.Label(self.header, text="Gestión del material", font=controller.second_title_font, bg="#2060C0", fg="#E0E0E0", pady=5)
        self.lb_second_title.grid(row=1, column=1, columnspan=8, sticky="nsw")

        self.btn_back = tkinter.Button(self.header, text="Volver", width=14, font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, command=lambda: self.controller.show_frame(select_page))
        self.btn_back.grid(row=1, column=0, padx=10, sticky="ew")

        # Cuerpo con las opciones de visualización y gestión del material
        self.lb_nombre_mat = tkinter.Label(self.body, text="Nombre del material", font=controller.label_font, bg="#2060C0")
        self.lb_nombre_mat.grid(row=0, column=0, padx=15, sticky="nsw")

        self.lb_codigo = tkinter.Label(self.body, text="Código", font=controller.label_font, bg="#2060C0")
        self.lb_codigo.grid(row=0, column=1, sticky="nsw")

        self.lb_estado = tkinter.Label(self.body, text="Estado", font=controller.label_font, bg="#2060C0")
        self.lb_estado.grid(row=0, column=2, padx=15, sticky="nsw")

        self.nombre_mat_text = tkinter.StringVar()
        self.ent_nombre_mat = tkinter.Entry(self.body, textvariable=self.nombre_mat_text, font=controller.entry_font)
        self.ent_nombre_mat.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        self.codigo_text = tkinter.StringVar()
        self.ent_codigo = tkinter.Entry(self.body, textvariable=self.codigo_text, font=controller.entry_font)
        self.ent_codigo.grid(row=1, column=1, pady=5, sticky="nsew")

        self.estado_text = tkinter.StringVar()
        self.ent_estado = tkinter.Entry(self.body, textvariable=self.estado_text, font=controller.entry_font)
        self.ent_estado.grid(row=1, column=2, padx=15, pady=5, sticky="nsew")

        list_mat = tkinter.Listbox(self.body, font=controller.list_font)
        list_mat.grid(row=2, column=0, columnspan=3, rowspan=4, sticky="nsew")

        self.sb = tkinter.Scrollbar(self.body, orient="vertical", command=list_mat.yview)
        self.sb.grid(row=2, column=3, rowspan=4, sticky="nsw")

        list_mat.configure(yscrollcommand=self.sb.set)
        list_mat.bind('<<ListboxSelect>>', self.get_selected_row)

        self.btn_search = tkinter.Button(self.body, text="Buscar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: search_material_command(self))
        self.btn_search.grid(row=2, column=4, sticky="nsw")

        self.btn_add = tkinter.Button(self.body, text="Añadir nuevo", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: add_material_command(self))
        self.btn_add.grid(row=3, column=4, sticky="nsw")

        self.btn_update = tkinter.Button(self.body, text="Modificar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: update_material_command(self))
        self.btn_update.grid(row=4, column=4, sticky="nsw")

        self.btn_delete = tkinter.Button(self.body, text="Eliminar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda:delete_material_command(self))
        self.btn_delete.grid(row=5, column=4, sticky="nsw")

    def get_selected_row(self, event):
        global selected_tuple_mat
        try:
            index = list_mat.curselection()[0]
            selected_tuple_mat = list_mat.get(index)
            self.ent_nombre_mat.delete(0, "end")
            self.ent_nombre_mat.insert("end", selected_tuple_mat[1])
            self.ent_codigo.delete(0, "end")
            self.ent_codigo.insert("end", selected_tuple_mat[2])
            self.ent_estado.delete(0, "end")
            self.ent_estado.insert("end", selected_tuple_mat[3])
        except:
            del selected_tuple_mat


# Funciones de las entradas en la pantalla PROFESORES
def view_profes_command(parent):
    global db
    parent.list_prof.delete(0, "end")
    for row in db.view_profes():
        parent.list_prof.insert("end", row)

def search_profe_command(parent):
    global db
    if parent.permisos_text.get() == "" and parent.nombre_prof_text.get() == "" and parent.ape1_text.get() == "" and parent.ape2_text.get() == ""\
            and parent.user_text.get() == "" and parent.pass_text.get() == "":
        view_profes_command(parent)
    else:
        parent.list_prof.delete(0, "end")
        for row in db.search_profe(parent.permisos_text.get(), parent.nombre_prof_text.get(), parent.ape1_text.get(), parent.ape2_text.get(),
                                   parent.user_text.get(), parent.pass_text.get()):
            parent.list_prof.insert("end", row)

def add_profe_command(parent):
    global db, cur, id_user_departs
    is_user = False
    if parent.nombre_prof_text.get() == "" or parent.ape1_text.get() == "" or parent.user_text.get() == "" or parent.pass_text.get() == "":
        messagebox.showwarning("Error", "Hay campos obligatorios del profesor sin información.")
    else:
        # Comprobamos que el nombre de usuario para la aplicación (USER) a añadir no esté ya registrado
        cur.execute("SELECT user FROM profesores;")
        users = cur.fetchall()

        for u in users:
            if str(u) == ("('"+parent.user_text.get()+"',)"):
                is_user = True
                break
            else:
                is_user = False
        if is_user:
            messagebox.showwarning("Error", "El nombre de usuario ya existe. Elija uno diferente.")
        else:
            db.insert_profe(parent.permisos_text.get(), parent.nombre_prof_text.get(), parent.ape1_text.get(), parent.ape2_text.get(),
                            parent.user_text.get(), parent.pass_text.get())
            view_profes_command(parent)
            parent.ent_permisos.delete(0, "end")
            parent.ent_nombre_prof.delete(0, "end")
            parent.ent_ape1.delete(0, "end")
            parent.ent_ape2.delete(0, "end")
            parent.ent_user.delete(0, "end")
            parent.ent_pass.delete(0, "end")

def delete_profe_command(parent):
    global db
    try:
        db.delete_profe(str(selected_tuple_prof[0]))
        view_profes_command(parent)
        parent.ent_permisos.delete(0, "end")
        parent.ent_nombre_prof.delete(0, "end")
        parent.ent_ape1.delete(0, "end")
        parent.ent_ape2.delete(0, "end")
        parent.ent_user.delete(0, "end")
        parent.ent_pass.delete(0, "end")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún profesor para eliminar.")

def update_profe_command(parent):
    global db, cur
    is_original = True
    is_user = False
    try:
        if parent.nombre_prof_text.get() == "" or parent.ape1_text.get() == "" or parent.user_text.get() == "" or parent.pass_text.get() == "":
            messagebox.showwarning("Error", "Hay campos obligatorios del profesor sin información.")
        else:
            # Permitimos que el nombre de usuario (USER) pueda ser el que se introdujo originalmente y no cambie
            cur.execute("SELECT user FROM profesores WHERE id = " + str(selected_tuple_prof[0]))
            current_user = cur.fetchall()
            for u in current_user:
                if str(u) == ("('"+parent.user_text.get()+"',)"):
                    is_original = True
                    break
                else:
                    is_original = False
                    # Comprobamos que el nombre de usuario para la aplicación (USER) a añadir no esté ya registrado
                    cur.execute("SELECT user FROM profesores;")
                    users = cur.fetchall()
                    for u in users:
                        if str(u) == ("('"+parent.user_text.get()+"',)"):
                            is_user = True
                            break
                        else:
                            is_user = False
            if not is_original and is_user:
                messagebox.showwarning("Error", "El nombre de usuario ya existe. Elija uno diferente.")
            else:
                db.update_profe(str(selected_tuple_prof[0]), parent.permisos_text.get(), parent.nombre_prof_text.get(),
                                parent.ape1_text.get(), parent.ape2_text.get(),
                                parent.user_text.get(), parent.pass_text.get())
                view_profes_command(parent)
                parent.ent_permisos.delete(0, "end")
                parent.ent_nombre_prof.delete(0, "end")
                parent.ent_ape1.delete(0, "end")
                parent.ent_ape2.delete(0, "end")
                parent.ent_user.delete(0, "end")
                parent.ent_pass.delete(0, "end")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún profesor para modificar.")

# Función para mostrar la ventana con los departamentos a los que pertenece cada profesor
def show_profe_departs(parent):
    global id_user_departs
    try:
        id_user_departs = str(selected_tuple_prof[0])
        parent.show_frame("ProfeDepartsPage")
        view_profe_departs_command()
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún profesor para acceder a sus departamentos.")

# Pagina de consultas en la tabla PROFESORES
class ProfesPage(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=20)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(fill="both", expand=True)

        self.body.grid_rowconfigure(2, weight=1)
        self.body.grid_rowconfigure(3, weight=1)
        self.body.grid_rowconfigure(4, weight=1)
        self.body.grid_rowconfigure(5, weight=1)
        self.body.grid_rowconfigure(6, weight=1)
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_columnconfigure(2, weight=1)
        self.body.grid_columnconfigure(3, weight=1)
        self.body.grid_columnconfigure(4, weight=1)
        self.body.grid_columnconfigure(5, weight=1)

        # Variables globales usadas
        global image

        # Cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, sticky="nsw")

        self.lb_second_title = tkinter.Label(self.header, text="Gestión de usuarios", font=controller.second_title_font, bg="#2060C0", fg="#E0E0E0", pady=5)
        self.lb_second_title.grid(row=1, column=1, sticky="nsw")

        self.btn_back = tkinter.Button(self.header, text="Volver", font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, command=lambda: self.controller.show_frame("AdminPage"))
        self.btn_back.grid(row=1, column=0, padx=10, sticky="ew")

        # Cuerpo con las opciones de visualización y gestión de los profesores
        self.lb_permisos = tkinter.Label(self.body, text="Permisos", font=controller.label_font, bg="#2060C0")
        self.lb_permisos.grid(row=0, column=0, padx=15, sticky="nsw")

        self.lb_nombre_prof = tkinter.Label(self.body, text="Nombre", font=controller.label_font, bg="#2060C0")
        self.lb_nombre_prof.grid(row=0, column=1, sticky="nsw")

        self.lb_ape1 = tkinter.Label(self.body, text="1er Apellido", font=controller.label_font, bg="#2060C0")
        self.lb_ape1.grid(row=0, column=2, padx=15,  sticky="nsw")

        self.lb_estado = tkinter.Label(self.body, text="2do Apellido", font=controller.label_font, bg="#2060C0")
        self.lb_estado.grid(row=0, column=3, sticky="nsw")

        self.lb_user = tkinter.Label(self.body, text="Usuario", font=controller.label_font, bg="#2060C0")
        self.lb_user.grid(row=0, column=4, padx=15,  sticky="nsw")

        self.lb_pass = tkinter.Label(self.body, text="Contraseña", font=controller.label_font, bg="#2060C0")
        self.lb_pass.grid(row=0, column=5, sticky="nsw")

        self.permisos_text = tkinter.StringVar()
        self.ent_permisos = tkinter.Entry(self.body, textvariable=self.permisos_text, font=controller.entry_font)
        self.ent_permisos.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        self.nombre_prof_text = tkinter.StringVar()
        self.ent_nombre_prof = tkinter.Entry(self.body, textvariable=self.nombre_prof_text, font=controller.entry_font)
        self.ent_nombre_prof.grid(row=1, column=1, pady=5, sticky="nsew")

        self.ape1_text = tkinter.StringVar()
        self.ent_ape1 = tkinter.Entry(self.body, textvariable=self.ape1_text, font=controller.entry_font)
        self.ent_ape1.grid(row=1, column=2,  padx=15, pady=5, sticky="nsew")

        self.ape2_text = tkinter.StringVar()
        self.ent_ape2 = tkinter.Entry(self.body, textvariable=self.ape2_text, font=controller.entry_font)
        self.ent_ape2.grid(row=1, column=3, pady=5, sticky="nsew")

        self.user_text = tkinter.StringVar()
        self.ent_user = tkinter.Entry(self.body, textvariable=self.user_text, font=controller.entry_font)
        self.ent_user.grid(row=1, column=4, padx=15, pady=5, sticky="nsew")

        self.pass_text = tkinter.StringVar()
        self.ent_pass = tkinter.Entry(self.body, textvariable=self.pass_text, font=controller.entry_font)
        self.ent_pass.grid(row=1, column=5, pady=5, sticky="nsew")

        self.list_prof = tkinter.Listbox(self.body, font=controller.list_font)
        self.list_prof.grid(row=2, column=0, rowspan=5, columnspan=6, sticky="nsew")

        self.sb = tkinter.Scrollbar(self.body, orient="vertical", command=self.list_prof.yview)
        self.sb.grid(row=2, column=6, rowspan=5, sticky="nsw")

        self.list_prof.configure(yscrollcommand=self.sb.set)
        self.list_prof.bind('<<ListboxSelect>>', self.get_selected_row)

        self.btn_search = tkinter.Button(self.body, text="Buscar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: search_profe_command(self))
        self.btn_search.grid(row=2, column=7, sticky="nsew")

        self.btn_add = tkinter.Button(self.body, text="Añadir nuevo", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: add_profe_command(self))
        self.btn_add.grid(row=3, column=7, sticky="nsew")

        self.btn_update = tkinter.Button(self.body, text="Modificar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: update_profe_command(self))
        self.btn_update.grid(row=4, column=7, sticky="nsew")

        self.btn_departs = tkinter.Button(self.body, text="Departamentos", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: show_profe_departs(self.controller))
        self.btn_departs.grid(row=5, column=7, sticky="nsew")

        self.btn_delete = tkinter.Button(self.body, text="Eliminar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: delete_profe_command(self))
        self.btn_delete.grid(row=6, column=7, sticky="nsew")

        view_profes_command(self)

    def get_selected_row(self, event):
        global selected_tuple_prof
        try:
            index = self.list_prof.curselection()[0]
            selected_tuple_prof = self.list_prof.get(index)
            self.ent_permisos.delete(0, "end")
            permisos = selected_tuple_prof[1]
            self.ent_permisos.insert("end", permisos[0:(len(permisos)-1)])
            self.ent_nombre_prof.delete(0, "end")
            self.ent_nombre_prof.insert("end", selected_tuple_prof[2])
            self.ent_ape1.delete(0, "end")
            self.ent_ape1.insert("end", selected_tuple_prof[3])
            self.ent_ape2.delete(0, "end")
            self.ent_ape2.insert("end", selected_tuple_prof[4])
            self.ent_user.delete(0, "end")
            self.ent_user.insert("end", selected_tuple_prof[5])
            self.ent_pass.delete(0, "end")
            self.ent_pass.insert("end", selected_tuple_prof[6])
        except:
            del selected_tuple_prof


# Funciones de las entradas en la pantalla GESTIÓN DE DEPARTAMENTOS
def view_profe_departs_command():
    global db, id_user_departs
    list_profdep.delete(0, "end")
    for row in db.view_profe_departs(id_user_departs):
        list_profdep.insert("end", row)

def search_profe_departs_command(parent):
    global db, id_user_departs
    if parent.nombre_profdep_text.get() == "":
        view_profe_departs_command()
    else:
        list_profdep.delete(0, "end")
        for row in db.search_profe_depart(parent.nombre_profdep_text.get(), id_user_departs):
            list_profdep.insert("end", row)

def add_profe_departs_command(parent):
    parent.show_frame("SelectDepartsPage")
    view_seldeparts_command()

def delete_profe_departs_command(parent):
    global db, id_user_departs
    try:
        db.delete_profe_depart(str(selected_tuple_profdep[0]), id_user_departs)
        view_profe_departs_command()
        parent.ent_nom_profdep.delete(0, "end")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún departamento para eliminar.")

# Pagina para mostrar los departamentos a los que pertenece cada profesor
class ProfeDepartsPage(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=20)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(fill="both", expand=True)

        self.body.grid_rowconfigure(2, weight=1)
        self.body.grid_rowconfigure(3, weight=1)
        self.body.grid_rowconfigure(4, weight=1)
        self.body.grid_columnconfigure(0, weight=1)

        # Variables globales usadas
        global image, list_profdep

        # Cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, sticky="nsw")

        self.lb_second_title = tkinter.Label(self.header, text="Gestión de departamentos", font=controller.second_title_font, bg="#2060C0", fg="#E0E0E0", pady=5)
        self.lb_second_title.grid(row=1, column=1, sticky="nsw")

        self.btn_back = tkinter.Button(self.header, text="Volver", font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, command=lambda: self.controller.show_frame("ProfesPage"))
        self.btn_back.grid(row=1, column=0, padx=10, sticky="nsew")

        # Cuerpo con las opciones de visualización y gestión de los departamentos del profesor seleccionado
        self.lb_nombre = tkinter.Label(self.body, text="Nombre del departamento", font=controller.label_font, bg="#2060C0")
        self.lb_nombre.grid(row=0, column=0, pady=5, padx=20, sticky="nsw")

        self.nombre_profdep_text = tkinter.StringVar()
        self.ent_nom_profdep = tkinter.Entry(self.body, textvariable=self.nombre_profdep_text, font=controller.entry_font)
        self.ent_nom_profdep.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

        list_profdep = tkinter.Listbox(self.body, font=controller.list_font)
        list_profdep.grid(row=2, column=0, rowspan=3, sticky="nsew")

        self.sb = tkinter.Scrollbar(self.body, orient="vertical", command=list_profdep.yview)
        self.sb.grid(row=2, column=1, rowspan=3, sticky="nsw")

        list_profdep.configure(yscrollcommand=self.sb.set)
        list_profdep.bind('<<ListboxSelect>>', self.get_selected_row)

        self.btn_search = tkinter.Button(self.body, text="Buscar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: search_profe_departs_command(self))
        self.btn_search.grid(row=2, column=2, sticky="nsew")

        self.btn_add = tkinter.Button(self.body, text="Añadir más", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: add_profe_departs_command(self.controller))
        self.btn_add.grid(row=3, column=2, sticky="nsew")

        self.btn_delete = tkinter.Button(self.body, text="Eliminar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: delete_profe_departs_command(self))
        self.btn_delete.grid(row=4, column=2, sticky="nsew")

    def get_selected_row(self, event):
        global selected_tuple_profdep
        try:
            index = list_profdep.curselection()[0]
            selected_tuple_profdep = list_profdep.get(index)
            self.ent_nom_profdep.delete(0, "end")
            self.ent_nom_profdep.insert("end", selected_tuple_profdep[1])
        except:
            del selected_tuple_profdep


# Funciones de las entradas en la pantallade SELECCIÓN DE DEPARTAMENTOS
def view_seldeparts_command():
    global db, id_user_departs
    list_seldep.delete(0, "end")
    for row in db.view_departs():
        list_seldep.insert("end", row)

def search_seldeparts_command(parent):
    global db, id_user_departs
    if parent.nombre_seldep_text.get() == "":
        view_seldeparts_command()
    else:
        list_seldep.delete(0, "end")
        for row in db.search_profe_depart(parent.nombre_seldep_text.get(), id_user_departs):
            list_seldep.insert("end", row)

def add_seldeparts_command(parent):
    global db, id_user_departs, selected_tuple_seldep
    try:
        db.add_seldepart(id_user_departs, selected_tuple_seldep[0])
        view_seldeparts_command()
        parent.ent_nombre_seldep.delete(0, "end")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún departamento al que añadir al profesor.")

def back_profe_departs(controller):
    controller.show_frame("ProfeDepartsPage")
    view_profe_departs_command()


# Pagina para seleccionar los departamentos a los que pertenece un profesor
class SelectDepartsPage(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=20)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(fill="both", expand=True)

        self.body.grid_rowconfigure(2, weight=1)
        self.body.grid_rowconfigure(3, weight=1)
        self.body.grid_columnconfigure(0, weight=1)

        # Variables globales usadas
        global image, list_seldep

        # Cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, columnspan=4, sticky="nsw")

        self.lb_title = tkinter.Label(self.header, text="Selección de departamentos", font=controller.second_title_font, bg="#2060C0", fg="#E0E0E0", pady=5)
        self.lb_title.grid(row=1, column=1, sticky="nsw")

        self.btn_back = tkinter.Button(self.header, text="Volver", font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, command=lambda: back_profe_departs(self.controller))
        self.btn_back.grid(row=1, column=0, padx=10, sticky="ew")

        # Cuerpo con las opciones de visualización y gestión de los departamentos para añadir al profesor seleccionado
        self.lb_nombre_dep = tkinter.Label(self.body, text="Nombre del departamento", font=controller.label_font, bg="#2060C0")
        self.lb_nombre_dep.grid(row=0, column=0, padx=10, sticky="nsw")

        self.nombre_seldep_text = tkinter.StringVar()
        self.ent_nombre_seldep = tkinter.Entry(self.body, textvariable=self.nombre_seldep_text, font=controller.entry_font)
        self.ent_nombre_seldep.grid(row=1, column=0, pady=5, padx=15, sticky="nsew")

        list_seldep = tkinter.Listbox(self.body, font=controller.list_font)
        list_seldep.grid(row=2, column=0, rowspan=2, sticky="nsew")

        self.sb = tkinter.Scrollbar(self.body, orient="vertical", command=list_seldep.yview)
        self.sb.grid(row=2, column=3, rowspan=2, sticky="nsw")

        list_seldep.configure(yscrollcommand=self.sb.set)
        list_seldep.bind('<<ListboxSelect>>', self.get_selected_row)

        self.btn_search = tkinter.Button(self.body, text="Buscar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: search_seldeparts_command(self))
        self.btn_search.grid(row=2, column=4, sticky="nsew")

        self.btn_add = tkinter.Button(self.body, text="Añadir", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: add_seldeparts_command(self))
        self.btn_add.grid(row=3, column=4, sticky="nsew")

    def get_selected_row(self, event):
        global selected_tuple_seldep
        try:
            index = list_seldep.curselection()[0]
            selected_tuple_seldep = list_seldep.get(index)
            self.ent_nombre_seldep.delete(0, "end")
            self.ent_nombre_seldep.insert("end", selected_tuple_seldep[1])
        except:
            del selected_tuple_seldep


# Funciones de las entradas en la pantalla PRESTAMOS para ADMIN y MANAGER
def view_prestamos_admin_command():
    global db
    list_prestamos_admin.delete(0, "end")
    for row in db.view_prestamos_admin():
        list_prestamos_admin.insert("end", row)

def search_prestamo_admin_command(parent):
    global db
    # Si no se busca por ningún campo, se mostrarán todos los registros
    if parent.user_prest_text.get() == "" and parent.mat_prest_text.get() == "" and parent.cod_prest_text.get() == ""\
        and parent.dia_ini_text.get() == "" and parent.mes_ini_text.get() == "" and parent.ano_ini_text.get() == ""\
        and parent.dia_fin_text.get() == "" and parent.mes_fin_text.get() == "" and parent.ano_fin_text.get() == "":
        view_prestamos_admin_command()
    else:
        list_prestamos_admin.delete(0, "end")
        for row in db.search_prestamo_admin(parent.user_prest_text.get(), parent.mat_prest_text.get(), parent.cod_prest_text.get(),
            parent.dia_ini_text.get(), parent.mes_ini_text.get(), parent.ano_ini_text.get(),
            parent.dia_fin_text.get(), parent.mes_fin_text.get(), parent.ano_fin_text.get()):

            list_prestamos_admin.insert("end", row)

def update_prestamo_admin_command(parent):
    global db, cur
    date_ini = datetime.today().strftime('%Y-%m-%d')
    date_fin = datetime.today().strftime('%Y-%m-%d')
    ini_date = True
    fin_date = True
    try:
        if parent.user_prest_text.get() == "" or parent.mat_prest_text.get() == "" or parent.cod_prest_text.get() == ""\
        or parent.dia_ini_text.get() == "" or parent.mes_ini_text.get() == "" or parent.ano_ini_text.get() == "":
            messagebox.showwarning("Error", "Hay campos obligatorios del préstamo sin información.")
        else:
            # Comprobamos que las fechas de inicio y fin del préstamo sean correctas
            try:
                datetime(int(parent.ano_ini_text.get()), int(parent.mes_ini_text.get()), int(parent.dia_ini_text.get()))
                date_ini = datetime(int(parent.ano_ini_text.get()), int(parent.mes_ini_text.get()), int(parent.dia_ini_text.get()))
            except ValueError:
                ini_date = False
                pass

            if parent.dia_fin_text.get() != "" or parent.mes_fin_text.get() != "" or parent.ano_fin_text.get() != "":
                try:
                    datetime(int(parent.ano_fin_text.get()), int(parent.mes_fin_text.get()), int(parent.dia_fin_text.get()))
                    date_fin = datetime(int(parent.ano_fin_text.get()), int(parent.mes_fin_text.get()), int(parent.dia_fin_text.get()))
                except ValueError:
                    fin_date = False
                    pass

                if date_fin < date_ini:
                    # Alerta en caso de que la fecha de finalización sea anterior a la de realización
                    messagebox.showwarning("Error", "La fecha de finalización del préstamo no puede ser anterior a la de realización.")

            # Comprobamos que el material es correcto
            cur.execute("SELECT id FROM material WHERE nombre = ? AND codigo = ?", (parent.mat_prest_text.get(), parent.cod_prest_text.get()))
            mat = cur.fetchall()
            if not mat:
                is_material = False
            else:
                is_material = True

            # Comprobamos que el usuario es correcto
            cur.execute("SELECT id FROM profesores WHERE user ='"+parent.user_prest_text.get()+"';")
            user = cur.fetchall()
            if not user:
                is_user = False
            else:
                is_user = True

            # Si se da cualquier error, se mostrarán las alertas correspondientes
            if not ini_date or not fin_date or is_user == 0 or is_material == 0:

                if not ini_date and not fin_date:
                    # Alerta en caso de que ambas fechas tengan un formato erroneo
                    messagebox.showwarning("Error", "Las fechas de realización y finalización del préstamo a modificar no son válidas.")
                elif not ini_date:
                    # Alerta en caso de que la fecha de realización tenga un formato erroneo
                    messagebox.showwarning("Error", "La fecha de realización del préstamo a modificar no es válida.")
                elif not fin_date:
                    # Alerta en caso de que la fecha de finalización tenga un formato erroneo
                    messagebox.showwarning("Error", "La fecha de finalización del préstamo a modificar no es válida.")
                if not is_user:
                    # Alerta en caso de que el usuario no exista
                    messagebox.showwarning("Error", "El usuario del préstamo a modificar no existe.")
                if not is_material:
                    # Alerta en caso de que el material no exista
                    messagebox.showwarning("Error", "El material del préstamo a modificar no existe.")
            else:
                # Si añadimos fecha de finalización a un préstamo que no la tenía, pondremos su material como DISPONIBLE
                if fin_date and selected_tuple_prest_admin[7] == "-" and selected_tuple_prest_admin[8] == "/" and selected_tuple_prest_admin[9] == "/":
                    im = ""
                    cur.execute("SELECT id FROM material WHERE nombre = ? AND codigo = ?", (parent.mat_prest_text.get(), parent.cod_prest_text.get()))
                    mat = cur.fetchall()
                    for m in mat:
                        for id_m in m:
                            im = id_m

                    cur.execute("UPDATE material SET id_estado = 1 WHERE id = "+str(im))
                    db.con.commit()

                db.update_prestamo(str(selected_tuple_prest_admin[0]), parent.user_prest_text.get(), parent.mat_prest_text.get(), parent.cod_prest_text.get(),
                parent.dia_ini_text.get(), parent.mes_ini_text.get(), parent.ano_ini_text.get(),
                parent.dia_fin_text.get(), parent.mes_fin_text.get(), parent.ano_fin_text.get())
                view_prestamos_admin_command()
                parent.ent_user_prest.delete(0, "end")
                parent.ent_mat_prest.delete(0, "end")
                parent.ent_cod_prest.delete(0, "end")
                parent.ent_dia_ini.delete(0, "end")
                parent.ent_mes_ini.delete(0, "end")
                parent.ent_ano_ini.delete(0, "end")
                parent.ent_dia_fin.delete(0, "end")
                parent.ent_mes_fin.delete(0, "end")
                parent.ent_ano_fin.delete(0, "end")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún préstamo para modificar.")


def finish_prestamo_admin_command(parent):
    global db, cur, now
    is_finished = 0
    m = ""
    try:
        # Comprobamos que el préstamo no haya sido ya finalizado
        cur.execute("SELECT dia_fin FROM prestamos WHERE id = "+str(selected_tuple_prest_admin[0]))
        fin = cur.fetchall()
        for f in fin:
            if str(f) == "('',)":
                is_finished = 0
            else:
                is_finished = 1

        if is_finished == 1:
            messagebox.showwarning("Error", "El préstamo seleccionado ya ha sido finalizado.")
        else:
            # Obtenemos el id del material del que se finaliza el préstamo
            cur.execute("SELECT id FROM material WHERE nombre = ? AND codigo = ?", (parent.mat_prest_text.get(), parent.cod_prest_text.get()))
            id_mat = cur.fetchall()
            for id_m in id_mat:
                for im in id_m:
                    m = str(im)
                    print(m)
            db.finish_prestamo(str(selected_tuple_prest_admin[0]), m, now.day, now.month, now.year)
            view_prestamos_admin_command()
            parent.ent_user_prest.delete(0, "end")
            parent.ent_mat_prest.delete(0, "end")
            parent.ent_cod_prest.delete(0, "end")
            parent.ent_dia_ini.delete(0, "end")
            parent.ent_mes_ini.delete(0, "end")
            parent.ent_ano_ini.delete(0, "end")
            parent.ent_dia_fin.delete(0, "end")
            parent.ent_mes_fin.delete(0, "end")
            parent.ent_ano_fin.delete(0, "end")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún préstamo para finalizar.")

def select_material_admin_command(parent):
    parent.show_frame("SelectMaterialPageAM")
    view_select_material_admin()

# Funciones de las entradas en la pantalla PRESTAMOS para cualquier usuario
def delete_prestamo_command(parent):
    global db
    try:
        db.delete_prestamo(str(selected_tuple_prest_admin[0]), parent.cod_prest_text.get())
        view_prestamos_admin_command()
        parent.ent_user_prest.delete(0, "end")
        parent.ent_mat_prest.delete(0, "end")
        parent.ent_cod_prest.delete(0, "end")
        parent.ent_dia_ini.delete(0, "end")
        parent.ent_mes_ini.delete(0, "end")
        parent.ent_ano_ini.delete(0, "end")
        parent.ent_dia_fin.delete(0, "end")
        parent.ent_mes_fin.delete(0, "end")
        parent.ent_ano_fin.delete(0, "end")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún préstamo para eliminar.")

def print_prestamo_command(parent):
    global db, cur, user_login
    try:
        # Comprobamos los permisos del usuario para guardar el nombre correcto del realizador del préstamo
        fn = ""
        cur.execute("""SELECT id_permisos FROM profesores
                    WHERE user = '"""+user_login+"'")

        permisos = cur.fetchall()

        if str(permisos) == "[(1,)]" or str(permisos) == "[(2,)]":
            user = parent.user_prest_text.get()
            id_prest = str(selected_tuple_prest_admin[0])
        else:
            user = user_login
            id_prest = str(selected_tuple_prest_user[0])

        # Obtenemos el nombre completo registrado para el usuario del préstamo
        cur.execute("""SELECT nombre||' '||ape1||' '||ape2 FROM profesores
                    WHERE user = '"""+user+"'")
        full_name = cur.fetchall()
        for full_n in full_name:
            for f_n in full_n:
                fn = f_n

        # Creamos el pdf
        pdf = FPDF()

        # Cramos la página
        pdf.add_page()
        pdf.set_xy(0, 0)
        pdf.set_left_margin(16)
        pdf.set_right_margin(16)
        pdf.set_top_margin(10)

        # cabecera de pagina
        pdf.image('logo_alomadrigal.png', x=14, y=4, w=16, h=16)
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 5, "", 0, 1)
        pdf.cell(176, 16, "IES Alonso de Madrigal", 0, 1, 'R')

        # contenido de la pagina
        pdf.set_text_color(30, 120, 200)
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, "", 0, 2)
        pdf.cell(50, 10, "Solicitud de préstamo de material del centro Nº "+id_prest, 0, 2, 'L')

        pdf.cell(0, 10, "", 0, 1)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(5)
        pdf.cell(80, 15, "Solicitante: "+fn, 0, 1, 'L')

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(5)
        pdf.cell(80, 15, "Material solicitado: "+parent.mat_prest_text.get()+"("+parent.cod_prest_text.get()+")", 0, 1, 'L')

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(5)
        pdf.cell(80, 15, "Fecha de realización: "+parent.dia_ini_text.get()+"/"+parent.mes_ini_text.get()+"/"+parent.ano_ini_text.get(), 0, 1, 'L')

        if parent.dia_fin_text.get() != "" and parent.mes_fin_text.get() != "" and parent.ano_fin_text.get() != "":
            fecha_fin = parent.dia_fin_text.get()+"/"+parent.mes_fin_text.get()+"/"+parent.ano_fin_text.get()
        else:
            fecha_fin = "Préstamo no finalizado."

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(5)
        pdf.cell(80, 15, "Fecha de finalización: "+fecha_fin, 0, 1, 'L')

        # Generacion del PDF
        try:
            file = easygui.filesavebox('SAVE', 'Save File', 'Préstamo_'+id_prest+'.pdf', filetypes=["*.pdf"])
            pdf.output(file, 'F')
            messagebox.showinfo("Informe generado", "El informe ha sido generado con éxito.")
        except:
            pass
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún préstamo del que guardar un informe.")

# Pagina de consultas en la tabla PRESTAMOS para ADMIN y MANAGER
class PrestamosPageAM(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=20)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(fill="both", expand=True)

        self.body.grid_rowconfigure(3, weight=1)
        self.body.grid_rowconfigure(4, weight=1)
        self.body.grid_rowconfigure(5, weight=1)
        self.body.grid_rowconfigure(6, weight=1)
        self.body.grid_rowconfigure(7, weight=1)
        self.body.grid_rowconfigure(8, weight=1)
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_columnconfigure(2, weight=1)
        self.body.grid_columnconfigure(3, weight=1)
        self.body.grid_columnconfigure(4, weight=1)
        self.body.grid_columnconfigure(5, weight=1)
        self.body.grid_columnconfigure(6, weight=1)
        self.body.grid_columnconfigure(7, weight=1)
        self.body.grid_columnconfigure(8, weight=1)

        # Variables globales usadas
        global image, select_page, list_prestamos_admin

        # Cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, columnspan=10, sticky="nsw")

        self.lb_second_title = tkinter.Label(self.header, text="Gestión de préstamos", font=controller.second_title_font, bg="#2060C0", fg="#E0E0E0", pady=5)
        self.lb_second_title.grid(row=1, column=1, columnspan=3, sticky="nsw")

        self.btn_back = tkinter.Button(self.header, text="Volver", font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, command=lambda: self.controller.show_frame(select_page))
        self.btn_back.grid(row=1, column=0, sticky="ew")

        # Cuerpo con las opciones de visualización y gestión de los prestamos como administrador
        self.lb_fecha_ini = tkinter.Label(self.body, text="Realización", font=controller.label_font, bg="#2060C0", pady=5)
        self.lb_fecha_ini.grid(row=0, column=3, padx=15,  columnspan=3, sticky="nsw")

        self.lb_fecha_fin = tkinter.Label(self.body, text="Finalización", font=controller.label_font, bg="#2060C0", pady=5)
        self.lb_fecha_fin.grid(row=0, column=6, padx=15,  columnspan=3, sticky="nsw")

        self.lb_user_prest = tkinter.Label(self.body, text="Usuario", font=controller.label_font, bg="#2060C0")
        self.lb_user_prest.grid(row=1, column=0, padx=15, sticky="nsw")

        self.lb_mat_prest = tkinter.Label(self.body, text="Material", font=controller.label_font, bg="#2060C0")
        self.lb_mat_prest.grid(row=1, column=1, sticky="nsw")

        self.lb_cod_prest = tkinter.Label(self.body, text="Código", font=controller.label_font, bg="#2060C0")
        self.lb_cod_prest.grid(row=1, column=2, padx=15, sticky="nsw")

        self.lb_dia_ini = tkinter.Label(self.body, text="Día", font=controller.label_font, bg="#2060C0")
        self.lb_dia_ini.grid(row=1, column=3, padx=15,  sticky="nsw")

        self.lb_mes_ini = tkinter.Label(self.body, text="Mes", font=controller.label_font, bg="#2060C0")
        self.lb_mes_ini.grid(row=1, column=4, sticky="nsw")

        self.lb_ano_ini = tkinter.Label(self.body, text="Año", font=controller.label_font, bg="#2060C0")
        self.lb_ano_ini.grid(row=1, column=5, padx=15,  sticky="nsw")

        self.lb_dia_fin = tkinter.Label(self.body, text="Día", font=controller.label_font, bg="#2060C0")
        self.lb_dia_fin.grid(row=1, column=6, padx=15, sticky="nsw")

        self.lb_mes_fin = tkinter.Label(self.body, text="Mes", font=controller.label_font, bg="#2060C0")
        self.lb_mes_fin.grid(row=1, column=7, sticky="nsw")

        self.lb_ano_fin = tkinter.Label(self.body, text="Año", font=controller.label_font, bg="#2060C0")
        self.lb_ano_fin.grid(row=1, column=8, padx=15,  sticky="nsw")

        self.user_prest_text = tkinter.StringVar()
        self.ent_user_prest = tkinter.Entry(self.body, textvariable=self.user_prest_text, font=controller.entry_font)
        self.ent_user_prest.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")

        self.mat_prest_text = tkinter.StringVar()
        self.ent_mat_prest = tkinter.Entry(self.body, textvariable=self.mat_prest_text, font=controller.entry_font)
        self.ent_mat_prest.grid(row=2, column=1, pady=5, sticky="nsew")

        self.cod_prest_text = tkinter.StringVar()
        self.ent_cod_prest = tkinter.Entry(self.body, textvariable=self.cod_prest_text, font=controller.entry_font)
        self.ent_cod_prest.grid(row=2, column=2, padx=15, pady=5, sticky="nsw")

        self.dia_ini_text = tkinter.StringVar()
        self.ent_dia_ini = tkinter.Entry(self.body, textvariable=self.dia_ini_text, font=controller.entry_font)
        self.ent_dia_ini.grid(row=2, column=3, padx=15,  pady=5, sticky="nsw")

        self.mes_ini_text = tkinter.StringVar()
        self.ent_mes_ini = tkinter.Entry(self.body, textvariable=self.mes_ini_text, font=controller.entry_font)
        self.ent_mes_ini.grid(row=2, column=4, pady=5, sticky="nsw")

        self.ano_ini_text = tkinter.StringVar()
        self.ent_ano_ini = tkinter.Entry(self.body, textvariable=self.ano_ini_text, font=controller.entry_font)
        self.ent_ano_ini.grid(row=2, column=5, padx=15,  pady=5, sticky="nsw")

        self.dia_fin_text = tkinter.StringVar()
        self.ent_dia_fin = tkinter.Entry(self.body, textvariable=self.dia_fin_text, font=controller.entry_font)
        self.ent_dia_fin.grid(row=2, column=6, padx=15,  pady=5, sticky="nsw")

        self.mes_fin_text = tkinter.StringVar()
        self.ent_mes_fin = tkinter.Entry(self.body, textvariable=self.mes_fin_text, font=controller.entry_font)
        self.ent_mes_fin.grid(row=2, column=7, pady=5, sticky="nsw")

        self.ano_fin_text = tkinter.StringVar()
        self.ent_ano_fin = tkinter.Entry(self.body, textvariable=self.ano_fin_text, font=controller.entry_font)
        self.ent_ano_fin.grid(row=2, column=8, padx=15,  pady=5, sticky="nsw")

        list_prestamos_admin = tkinter.Listbox(self.body, font=controller.list_font)
        list_prestamos_admin.grid(row=3, column=0, rowspan=6, columnspan=9, sticky="nsew")

        self.sb = tkinter.Scrollbar(self.body, orient="vertical", command=list_prestamos_admin.yview)
        self.sb.grid(row=3, column=9, rowspan=6, sticky="nsw")

        list_prestamos_admin.configure(yscrollcommand=self.sb.set)
        list_prestamos_admin.bind('<<ListboxSelect>>', self.get_selected_row)

        self.btn_search = tkinter.Button(self.body, text="Buscar", width=15, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: search_prestamo_admin_command(self))
        self.btn_search.grid(row=3, column=10, sticky="nsew")

        self.btn_update = tkinter.Button(self.body, text="Modificar", width=15, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: update_prestamo_admin_command(self))
        self.btn_update.grid(row=4, column=10, sticky="nsew")

        self.btn_update = tkinter.Button(self.body, text="Eliminar", width=15, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: delete_prestamo_command(self))
        self.btn_update.grid(row=5, column=10, sticky="nsew")

        self.btn_solicitar = tkinter.Button(self.body, text="Nuevo préstamo", width=15, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: select_material_admin_command(self.controller))
        self.btn_solicitar.grid(row=6, column=10, sticky="nsew")

        self.btn_finish = tkinter.Button(self.body, text="Finalizar", width=15, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: finish_prestamo_admin_command(self))
        self.btn_finish.grid(row=7, column=10, sticky="nsew")

        self.btn_pdf = tkinter.Button(self.body, text="Guardar informe", width=15, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: print_prestamo_command(self))
        self.btn_pdf.grid(row=8, column=10, sticky="nsew")

    def get_selected_row(self, event):
        global selected_tuple_prest_admin
        try:
            index = list_prestamos_admin.curselection()[0]
            selected_tuple_prest_admin = list_prestamos_admin.get(index)
            self.ent_user_prest.delete(0, "end")
            self.ent_user_prest.insert("end", selected_tuple_prest_admin[1])
            self.ent_mat_prest.delete(0, "end")
            self.ent_mat_prest.insert("end", selected_tuple_prest_admin[2])
            self.ent_cod_prest.delete(0, "end")
            self.ent_cod_prest.insert("end", selected_tuple_prest_admin[3])

            self.ent_dia_ini.delete(0, "end")
            self.ent_dia_ini.insert("end", selected_tuple_prest_admin[4])

            m_ini = selected_tuple_prest_admin[5]
            mi = m_ini[1:]
            self.ent_mes_ini.delete(0, "end")
            self.ent_mes_ini.insert("end", mi)

            a_ini = selected_tuple_prest_admin[6]
            ai = a_ini[1:]
            self.ent_ano_ini.delete(0, "end")
            self.ent_ano_ini.insert("end", ai)

            d_fin = selected_tuple_prest_admin[7]
            df = d_fin[1:]
            self.ent_dia_fin.delete(0, "end")
            self.ent_dia_fin.insert("end", df)

            m_fin = selected_tuple_prest_admin[8]
            mf = m_fin[1:]
            self.ent_mes_fin.delete(0, "end")
            self.ent_mes_fin.insert("end", mf)

            a_fin = selected_tuple_prest_admin[9]
            af = a_fin[1:]
            self.ent_ano_fin.delete(0, "end")
            self.ent_ano_fin.insert("end", af)
        except:
            del selected_tuple_prest_admin

# Funciones de las entradas en la pantalla de selección de material para ADMIN y MANAGER
def view_select_material_admin():
    global db
    list_sel_mat_admin.delete(0, "end")
    for row in db.view_material():
        list_sel_mat_admin.insert("end", row)


def search_select_material_admin(parent):
    global db
    if parent.nombre_mat_text.get() == "" and parent.codigo_text.get() == "" and parent.estado_text.get() == "":
        view_select_material_admin()
    else:
        list_sel_mat_admin.delete(0, "end")
        for row in db.search_material(parent.nombre_mat_text.get(), parent.codigo_text.get(), parent.estado_text.get()):
            list_sel_mat_admin.insert("end", row)

def add_prestamo_admin(parent, controller):
    global db, cur, user_login, now

    try:
        # Comprobamos que el material del que se va a realizar el préstamo está disponible
        cur.execute("SELECT id_estado FROM material WHERE id = '"+str(selected_tuple_selmat_am[0])+"'")
        disponible = cur.fetchall()
        if str(disponible) == "[(1,)]":
            if parent.user_text.get() == "":
                if messagebox.askokcancel("Atención", "No ha introducido ningún solicitante, por lo tanto el préstamo se le asignará a su usuario ("+user_login+"). ¿Está seguro de realizar el préstamo?"):
                    db.add_prestamo(user_login, str(selected_tuple_selmat_am[0]), now.day, now.month, now.year)
                    back_prestamos_admin(controller)
            else:
                is_user = False

                # Comprobamos que el usuarion al que se le asigna el préstamo esté registrado
                cur.execute("SELECT user FROM profesores;")
                users = cur.fetchall()
                for u in users:
                    if str(u) == "('"+parent.user_text.get()+"',)":
                        is_user = True
                if not is_user:
                    messagebox.showwarning("Error", "El usuario introducido no está registrado.")
                elif messagebox.askokcancel("Atención", "Va a realizar un préstamo a nombre del usuario "+parent.user_text.get()+". ¿Está seguro de realizar el préstamo?"):
                    db.add_prestamo(parent.user_text.get(), str(selected_tuple_selmat_am[0]), now.day, now.month, now.year)
                    back_prestamos_admin(controller)
        else:
            # Alerta en caso de que el material no esté disponible
            messagebox.showwarning("Error", "El material seleccionado no está disponible.")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún material para realizar el préstamo.")

def back_prestamos_admin(controller):
    controller.show_frame("PrestamosPageAM")
    view_prestamos_admin_command()

# Pagina de selección de material para ADMIN y MANAGER
class SelectMaterialPageAM(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=10)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(fill="both", expand=True)

        self.body.grid_rowconfigure(2, weight=1)
        self.body.grid_rowconfigure(3, weight=1)
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_columnconfigure(2, weight=1)
        self.body.grid_columnconfigure(3, weight=1)

        # Variables globales usadas
        global image, select_page, list_sel_mat_admin

        # Cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, columnspan=8, sticky="nsw")

        self.lb_second_title = tkinter.Label(self.header, text="Gestión del material", font=controller.second_title_font, bg="#2060C0", fg="#E0E0E0", pady=5)
        self.lb_second_title.grid(row=1, column=1, columnspan=8, sticky="nsw")

        self.btn_back = tkinter.Button(self.header, text="Cancelar", width=14, font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, command=lambda: back_prestamos_admin(self.controller))
        self.btn_back.grid(row=1, column=0, padx=10, sticky="ew")

        # Cuerpo con las opciones de visualización y gestión del material para admin y manager
        self.lb_nombre_mat = tkinter.Label(self.body, text="Nombre del material", font=controller.label_font, bg="#2060C0")
        self.lb_nombre_mat.grid(row=0, column=0, padx=15, sticky="nsw")

        self.lb_codigo = tkinter.Label(self.body, text="Código", font=controller.label_font, bg="#2060C0")
        self.lb_codigo.grid(row=0, column=1, sticky="nsw")

        self.lb_estado = tkinter.Label(self.body, text="Estado", font=controller.label_font, bg="#2060C0")
        self.lb_estado.grid(row=0, column=2, padx=15, sticky="nsw")

        self.lb_codigo = tkinter.Label(self.body, text="Usuario solicitante", font=controller.label_font, bg="#2060C0")
        self.lb_codigo.grid(row=0, column=3, sticky="nsw")

        self.nombre_mat_text = tkinter.StringVar()
        self.ent_nombre_mat = tkinter.Entry(self.body, textvariable=self.nombre_mat_text, font=controller.entry_font)
        self.ent_nombre_mat.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        self.codigo_text = tkinter.StringVar()
        self.ent_codigo = tkinter.Entry(self.body, textvariable=self.codigo_text, font=controller.entry_font)
        self.ent_codigo.grid(row=1, column=1, pady=5, sticky="nsew")

        self.estado_text = tkinter.StringVar()
        self.ent_estado = tkinter.Entry(self.body, textvariable=self.estado_text, font=controller.entry_font)
        self.ent_estado.grid(row=1, column=2, padx=15, pady=5, sticky="nsew")

        self.user_text = tkinter.StringVar()
        self.ent_user = tkinter.Entry(self.body, textvariable=self.user_text, font=controller.entry_font)
        self.ent_user.grid(row=1, column=3, pady=5, sticky="nsew")

        list_sel_mat_admin = tkinter.Listbox(self.body, font=controller.list_font)
        list_sel_mat_admin.grid(row=2, column=0, columnspan=4, rowspan=4, sticky="nsew")

        self.sb = tkinter.Scrollbar(self.body, orient="vertical", command=list_sel_mat_admin.yview)
        self.sb.grid(row=2, column=4, rowspan=2, sticky="nsw")

        list_sel_mat_admin.configure(yscrollcommand=self.sb.set)
        list_sel_mat_admin.bind('<<ListboxSelect>>', self.get_selected_row)

        self.btn_search = tkinter.Button(self.body, text="Buscar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: search_select_material_admin(self))
        self.btn_search.grid(row=2, column=5, sticky="nsw")

        self.btn_add = tkinter.Button(self.body, text="Realiazr", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: add_prestamo_admin(self, self.controller))
        self.btn_add.grid(row=3, column=5, sticky="nsw")

    def get_selected_row(self, event):
        global selected_tuple_selmat_am
        try:
            index = list_sel_mat_admin.curselection()[0]
            selected_tuple_selmat_am = list_sel_mat_admin.get(index)
            self.ent_nombre_mat.delete(0, "end")
            self.ent_nombre_mat.insert("end", selected_tuple_selmat_am[1])
            self.ent_codigo.delete(0, "end")
            self.ent_codigo.insert("end", selected_tuple_selmat_am[2])
            self.ent_estado.delete(0, "end")
            self.ent_estado.insert("end", selected_tuple_selmat_am[3])
        except:
            del selected_tuple_selmat_am


# Funciones de las entradas en la pantalla PRESTAMOS para cualquier usuario que no sea ADMIN o MANAGER
def view_prestamos_command():
    global db, user_login
    list_prestamos.delete(0, "end")
    for row in db.view_prestamos(user_login):
        list_prestamos.insert("end", row)

def search_prestamo_command(parent):
    global db, user_login
    if parent.mat_prest_text.get() == "" and parent.cod_prest_text.get() == ""\
        and parent.dia_ini_text.get() == "" and parent.mes_ini_text.get() == "" and parent.ano_ini_text.get() == ""\
        and parent.dia_fin_text.get() == "" and parent.mes_fin_text.get() == "" and parent.ano_fin_text.get() == "":
        view_prestamos_command()
    else:
        list_prestamos.delete(0, "end")
        for row in db.search_prestamo(user_login, parent.mat_prest_text.get(), parent.cod_prest_text.get(),
            parent.dia_ini_text.get(), parent.mes_ini_text.get(), parent.ano_ini_text.get(),
            parent.dia_fin_text.get(), parent.mes_fin_text.get(), parent.ano_fin_text.get()):

            list_prestamos.insert("end", row)

def finish_prestamo_command(parent):
    global db, cur, now
    is_finished = False
    m = ""
    try:
        # Comprobamos que el préstamo no haya sido ya finalizado
        cur.execute("SELECT dia_fin FROM prestamos WHERE id = "+str(selected_tuple_prest_user[0]))
        fin = cur.fetchall()
        for f in fin:
            if str(f) == "('',)":
                is_finished = False
            else:
                is_finished = True

        if is_finished:
            messagebox.showwarning("Error", "El préstamo seleccionado ya ha sido finalizado.")
        else:
            # Obtenemos el id del material del que se finaliza el préstamo
            cur.execute("SELECT id FROM material WHERE nombre = ? AND codigo = ?", (parent.mat_prest_text.get(), parent.cod_prest_text.get()))
            id_mat = cur.fetchall()
            for id_m in id_mat:
                for im in id_m:
                    m = str(im)
                    print(m)
            db.finish_prestamo(str(selected_tuple_prest_user[0]), m, now.day, now.month, now.year)
            view_prestamos_command()
            parent.ent_mat_prest.delete(0, "end")
            parent.ent_cod_prest.delete(0, "end")
            parent.ent_dia_ini.delete(0, "end")
            parent.ent_mes_ini.delete(0, "end")
            parent.ent_ano_ini.delete(0, "end")
            parent.ent_dia_fin.delete(0, "end")
            parent.ent_mes_fin.delete(0, "end")
            parent.ent_ano_fin.delete(0, "end")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún préstamo para finalizar.")

def select_material_command(parent):
    parent.show_frame("SelectMaterialPageProf")
    view_select_material()

# Pagina de consultas en la tabla PRESTAMOS para PROFESORES
class PrestamosPageProf(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=20)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(fill="both", expand=True)

        self.body.grid_rowconfigure(3, weight=1)
        self.body.grid_rowconfigure(4, weight=1)
        self.body.grid_rowconfigure(5, weight=1)
        self.body.grid_rowconfigure(6, weight=1)
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_columnconfigure(2, weight=1)
        self.body.grid_columnconfigure(3, weight=1)
        self.body.grid_columnconfigure(4, weight=1)
        self.body.grid_columnconfigure(5, weight=1)
        self.body.grid_columnconfigure(6, weight=1)
        self.body.grid_columnconfigure(7, weight=1)
        self.body.grid_columnconfigure(8, weight=1)

        # Variables globales usadas
        global image, select_page, list_prestamos

        # Cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, columnspan=10, sticky="nsw")

        self.lb_second_title = tkinter.Label(self.header, text="Gestión de préstamos", font=controller.second_title_font, bg="#2060C0", fg="#E0E0E0", pady=5)
        self.lb_second_title.grid(row=1, column=1, columnspan=3, sticky="nsw")

        self.btn_back = tkinter.Button(self.header, text="Salir", font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, command=lambda: self.controller.show_frame(select_page))
        self.btn_back.grid(row=1, column=0, sticky="ew")

        # Cuerpo con las opciones de visualización y gestión de los prestamos para profesores
        self.lb_fecha_ini = tkinter.Label(self.body, text="Realización", font=controller.label_font, bg="#2060C0")
        self.lb_fecha_ini.grid(row=0, column=2, padx=15, pady=5, columnspan=3, sticky="nsw")

        self.lb_fecha_fin = tkinter.Label(self.body, text="Finalización", font=controller.label_font, bg="#2060C0")
        self.lb_fecha_fin.grid(row=0, column=5, padx=15, pady=5, columnspan=3, sticky="nsw")

        self.lb_mat_prest = tkinter.Label(self.body, text="Material", font=controller.label_font, bg="#2060C0")
        self.lb_mat_prest.grid(row=1, column=0, sticky="nsw")

        self.lb_cod_prest = tkinter.Label(self.body, text="Código", font=controller.label_font, bg="#2060C0")
        self.lb_cod_prest.grid(row=1, column=1, padx=15, sticky="nsw")

        self.lb_dia_ini = tkinter.Label(self.body, text="Día", font=controller.label_font, bg="#2060C0")
        self.lb_dia_ini.grid(row=1, column=2, padx=15, sticky="nsw")

        self.lb_mes_ini = tkinter.Label(self.body, text="Mes", font=controller.label_font, bg="#2060C0")
        self.lb_mes_ini.grid(row=1, column=3, sticky="nsw")

        self.lb_ano_ini = tkinter.Label(self.body, text="Año", font=controller.label_font, bg="#2060C0")
        self.lb_ano_ini.grid(row=1, column=4, padx=15, sticky="nsw")

        self.lb_dia_fin = tkinter.Label(self.body, text="Día", font=controller.label_font, bg="#2060C0")
        self.lb_dia_fin.grid(row=1, column=5, padx=15, sticky="nsw")

        self.lb_mes_fin = tkinter.Label(self.body, text="Mes", font=controller.label_font, bg="#2060C0")
        self.lb_mes_fin.grid(row=1, column=6, sticky="nsw")

        self.lb_ano_fin = tkinter.Label(self.body, text="Año", font=controller.label_font, bg="#2060C0")
        self.lb_ano_fin.grid(row=1, column=7, padx=15, sticky="nsw")

        self.mat_prest_text = tkinter.StringVar()
        self.ent_mat_prest = tkinter.Entry(self.body, textvariable=self.mat_prest_text, font=controller.entry_font)
        self.ent_mat_prest.grid(row=2, column=0, pady=5, sticky="nsew")

        self.cod_prest_text = tkinter.StringVar()
        self.ent_cod_prest = tkinter.Entry(self.body, textvariable=self.cod_prest_text, font=controller.entry_font)
        self.ent_cod_prest.grid(row=2, column=1, padx=15, pady=5, sticky="nsw")

        self.dia_ini_text = tkinter.StringVar()
        self.ent_dia_ini = tkinter.Entry(self.body, textvariable=self.dia_ini_text, font=controller.entry_font)
        self.ent_dia_ini.grid(row=2, column=2, padx=15, pady=5, sticky="nsw")

        self.mes_ini_text = tkinter.StringVar()
        self.ent_mes_ini = tkinter.Entry(self.body, textvariable=self.mes_ini_text, font=controller.entry_font)
        self.ent_mes_ini.grid(row=2, column=3, pady=5, sticky="nsw")

        self.ano_ini_text = tkinter.StringVar()
        self.ent_ano_ini = tkinter.Entry(self.body, textvariable=self.ano_ini_text, font=controller.entry_font)
        self.ent_ano_ini.grid(row=2, column=4, padx=15, pady=5, sticky="nsw")

        self.dia_fin_text = tkinter.StringVar()
        self.ent_dia_fin = tkinter.Entry(self.body, textvariable=self.dia_fin_text, font=controller.entry_font)
        self.ent_dia_fin.grid(row=2, column=5, padx=15, pady=5, sticky="nsw")

        self.mes_fin_text = tkinter.StringVar()
        self.ent_mes_fin = tkinter.Entry(self.body, textvariable=self.mes_fin_text, font=controller.entry_font)
        self.ent_mes_fin.grid(row=2, column=6, pady=5, sticky="nsw")

        self.ano_fin_text = tkinter.StringVar()
        self.ent_ano_fin = tkinter.Entry(self.body, textvariable=self.ano_fin_text, font=controller.entry_font)
        self.ent_ano_fin.grid(row=2, column=7, padx=15, pady=5, sticky="nsw")

        list_prestamos = tkinter.Listbox(self.body, font=controller.list_font)
        list_prestamos.grid(row=3, column=0, rowspan=4, columnspan=8, sticky="nsew")

        self.sb = tkinter.Scrollbar(self.body, orient="vertical", command=list_prestamos.yview)
        self.sb.grid(row=3, column=8, rowspan=4, sticky="nsw")

        list_prestamos.configure(yscrollcommand=self.sb.set)
        list_prestamos.bind('<<ListboxSelect>>', self.get_selected_row)

        self.btn_search = tkinter.Button(self.body, text="Buscar", width=15, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: search_prestamo_command(self))
        self.btn_search.grid(row=3, column=9, sticky="nsew")

        self.btn_solicitar = tkinter.Button(self.body, text="Nuevo préstamo", width=15, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: select_material_command(self.controller))
        self.btn_solicitar.grid(row=4, column=9, sticky="nsew")

        self.btn_finish = tkinter.Button(self.body, text="Finalizar", width=15, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: finish_prestamo_command(self))
        self.btn_finish.grid(row=5, column=9, sticky="nsew")

        self.btn_pdf = tkinter.Button(self.body, text="Guardar informe", width=15, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: print_prestamo_command(self))
        self.btn_pdf.grid(row=6, column=9, sticky="nsew")

    def get_selected_row(self, event):
        global selected_tuple_prest_user
        try:
            index = list_prestamos.curselection()[0]
            selected_tuple_prest_user = list_prestamos.get(index)
            self.ent_mat_prest.delete(0, "end")
            self.ent_mat_prest.insert("end", selected_tuple_prest_user[1])
            self.ent_cod_prest.delete(0, "end")
            self.ent_cod_prest.insert("end", selected_tuple_prest_user[2])

            self.ent_dia_ini.delete(0, "end")
            self.ent_dia_ini.insert("end", selected_tuple_prest_user[3])

            m_ini = selected_tuple_prest_user[4]
            mi = m_ini[1:]
            self.ent_mes_ini.delete(0, "end")
            self.ent_mes_ini.insert("end", mi)

            a_ini = selected_tuple_prest_user[5]
            ai = a_ini[1:]
            self.ent_ano_ini.delete(0, "end")
            self.ent_ano_ini.insert("end", ai)

            d_fin = selected_tuple_prest_user[6]
            df = d_fin[1:]
            self.ent_dia_fin.delete(0, "end")
            self.ent_dia_fin.insert("end", df)

            m_fin = selected_tuple_prest_user[7]
            mf = m_fin[1:]
            self.ent_mes_fin.delete(0, "end")
            self.ent_mes_fin.insert("end", mf)

            a_fin = selected_tuple_prest_user[8]
            af = a_fin[1:]
            self.ent_ano_fin.delete(0, "end")
            self.ent_ano_fin.insert("end", af)
        except:
            del selected_tuple_prest_user


# Funciones de las entradas en la pantalla de selección de material para profesores
def view_select_material():
    global db
    list_sel_mat.delete(0, "end")
    for row in db.view_material():
        list_sel_mat.insert("end", row)

def search_select_material(parent):
    global db
    if parent.nombre_mat_text.get() == "" and parent.codigo_text.get() == "" and parent.estado_text.get() == "":
        view_select_material()
    else:
        list_sel_mat.delete(0, "end")
        for row in db.search_material(parent.nombre_mat_text.get(), parent.codigo_text.get(), parent.estado_text.get()):
            list_sel_mat.insert("end", row)

def add_prestamo(controller):
    global db, user_login, now
    try:
        # Comprobamos que el material del que se va a realizar el préstamo está disponible
        cur.execute("SELECT id_estado FROM material WHERE id = '"+str(selected_tuple_selmat[0])+"'")
        disponible = cur.fetchall()
        if str(disponible) == "[(1,)]":
            if messagebox.askokcancel("Atención", "¿Está seguro de realizar el préstamo?"):
                db.add_prestamo(user_login, str(selected_tuple_selmat[0]), now.day, now.month, now.year)
                back_prestamos(controller)
        else:
            # Alerta en caso de que el material no esté disponible
            messagebox.showwarning("Error", "El material seleccionado no está disponible.")
    except:
        # Alerta en caso de que no haya ninguna entrada seleccionada
        messagebox.showwarning("Error", "No se ha seleccionado ningún material para realizar el préstamo.")

def back_prestamos(controller):
    controller.show_frame("PrestamosPageProf")
    view_prestamos_command()

# Página de selección de material para cualquier profesores
class SelectMaterialPageProf(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.config(bg="#2060C0", bd=10)
        self.controller = controller

        # Frames para contener la cabecera y el cuerpo de la página
        self.header = tkinter.Frame(self, bg="#2060C0")
        self.header.pack(fill="both", expand=True)

        self.body = tkinter.Frame(self, bg="#2060C0")
        self.body.pack(fill="both", expand=True)

        self.body.grid_rowconfigure(2, weight=1)
        self.body.grid_rowconfigure(3, weight=1)
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_columnconfigure(2, weight=1)

        # Variables globales usadas
        global image, select_page, list_sel_mat

        # Cabecera con el logo del IES Alonso de Madrigal y el nombre de la app
        self.resized_image = image.resize((60, 60), Image.ANTIALIAS)
        self.img_logo = ImageTk.PhotoImage(self.resized_image)

        self.title_img = tkinter.Label(self.header, image=self.img_logo, bg="#2060C0", bd=10)
        self.title_img.grid(row=0, column=0, sticky="nsew")

        self.lb_title = tkinter.Label(self.header, text="Préstamos IES Alonso de Madrigal", font=controller.title_font, bg="#2060C0", fg="#E0E0E0", bd=10)
        self.lb_title.grid(row=0, column=1, columnspan=8, sticky="nsw")

        self.lb_second_title = tkinter.Label(self.header, text="Gestión del material", font=controller.second_title_font, bg="#2060C0", fg="#E0E0E0", pady=5)
        self.lb_second_title.grid(row=1, column=1, columnspan=8, sticky="nsw")

        self.btn_back = tkinter.Button(self.header, text="Cancelar", width=14, font=controller.button_font, bg="#001040", fg="#CFCFCF", bd=1, command=lambda: back_prestamos(self.controller))
        self.btn_back.grid(row=1, column=0, padx=10, sticky="ew")

        # Cuerpo con las opciones de visualización y gestión del material para profesores
        self.lb_nombre_mat = tkinter.Label(self.body, text="Nombre del material", font=controller.label_font, bg="#2060C0")
        self.lb_nombre_mat.grid(row=0, column=0, padx=15, sticky="nsw")

        self.lb_codigo = tkinter.Label(self.body, text="Código", font=controller.label_font, bg="#2060C0")
        self.lb_codigo.grid(row=0, column=1, sticky="nsw")

        self.lb_estado = tkinter.Label(self.body, text="Estado", font=controller.label_font, bg="#2060C0")
        self.lb_estado.grid(row=0, column=2, padx=15, sticky="nsw")

        self.nombre_mat_text = tkinter.StringVar()
        self.ent_nombre_mat = tkinter.Entry(self.body, textvariable=self.nombre_mat_text, font=controller.entry_font)
        self.ent_nombre_mat.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        self.codigo_text = tkinter.StringVar()
        self.ent_codigo = tkinter.Entry(self.body, textvariable=self.codigo_text, font=controller.entry_font)
        self.ent_codigo.grid(row=1, column=1, pady=5, sticky="nsew")

        self.estado_text = tkinter.StringVar()
        self.ent_estado = tkinter.Entry(self.body, textvariable=self.estado_text, font=controller.entry_font)
        self.ent_estado.grid(row=1, column=2, padx=15, pady=5, sticky="nsew")

        list_sel_mat = tkinter.Listbox(self.body, font=controller.list_font)
        list_sel_mat.grid(row=2, column=0, columnspan=4, rowspan=4, sticky="nsew")

        self.sb = tkinter.Scrollbar(self.body, orient="vertical", command=list_sel_mat.yview)
        self.sb.grid(row=2, column=4, rowspan=2, sticky="nsw")

        list_sel_mat.configure(yscrollcommand=self.sb.set)
        list_sel_mat.bind('<<ListboxSelect>>', self.get_selected_row)

        self.btn_search = tkinter.Button(self.body, text="Buscar", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: search_select_material(self))
        self.btn_search.grid(row=2, column=5, sticky="nsw")

        self.btn_add = tkinter.Button(self.body, text="Realiazr", width=14, font=controller.button_font, bg="#0E2E6B", fg="#CFCFCF", bd=1, command=lambda: add_prestamo(self.controller))
        self.btn_add.grid(row=3, column=5, sticky="nsw")

    def get_selected_row(self, event):
        global selected_tuple_selmat
        try:
            index = list_sel_mat.curselection()[0]
            selected_tuple_selmat = list_sel_mat.get(index)
            self.ent_nombre_mat.delete(0, "end")
            self.ent_nombre_mat.insert("end", selected_tuple_selmat[1])
            self.ent_codigo.delete(0, "end")
            self.ent_codigo.insert("end", selected_tuple_selmat[2])
            self.ent_estado.delete(0, "end")
            self.ent_estado.insert("end", selected_tuple_selmat[3])
        except:
            del selected_tuple_selmat


if __name__ == "__main__":
    app = App()
    # Manejador para alertar del cierre la base de datos al cerrar la aplicacion con el boton "X" de la ventana
    app.protocol("WM_DELETE_WINDOW", close)
    app.mainloop()
