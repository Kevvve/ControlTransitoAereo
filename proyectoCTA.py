import sqlite3
from abc import ABC, abstractmethod
from tkinter import *
from tkinter import ttk, messagebox

def crear_base_de_datos():
    conn = sqlite3.connect('control_transito_aereo.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Aeropuertos (
            aeropuerto_id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            capacidad INTEGER NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Aeronaves (
            aeronave_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            plan_vuelo TEXT 
        );
    ''')
    
    conn.commit()
    conn.close()
    

class Ubicacion(ABC):
    @abstractmethod
    def descripcion(self):
        pass

class Terminal(Ubicacion):
    def __init__(self, aeropuerto):
        self.aeropuerto = aeropuerto

    def descripcion(self):
        return f"Terminal en el aeropuerto {self.aeropuerto.codigo}"

class Pista(Ubicacion):
    def __init__(self, aeropuerto):
        self.aeropuerto = aeropuerto
    
    def descripcion(self):
        return f"Pista en el aeropuerto {self.aeropuerto.codigo}"

class Vuelo(Ubicacion):
    def __init__(self):
        pass

class Aeropuerto:
    def __init__(self, codigo, capacidad_pista):
        self.codigo = codigo
        self.capacidad_pista = capacidad_pista
        self.terminal = []
        self.pista = []
    
    def espacio_disponible(self):
        return self.capacidad_pista - len(self.pista)
    
    def estado_aeropuerto(self):
        print(f"Aeropuerto {self.codigo}")
        print(f"Aeronaves en terminal: {[aeronave.nombre for aeronave in self.terminal]}")
        print(f"Aeronaves en pista: {[aeronave.nombre for aeronave in self.pista]}")
        print(f"Capacidad disponible en pista: {self.espacio_disponible()}")

class Control:
    def __init__(self):
        self.aeropuertos = []
        self.aeronaves = []
        self.planes_vuelo = []
        self.aeronaves_en_alarma = []

    def agregar_aeropuerto(self, aeropuerto):
        self.aeropuertos.append(aeropuerto)
        self.guardar_en_base_de_datos("Aeropuertos", aeropuerto)

    def agregar_aeronave(self, aeronave):
        self.aeronaves.append(aeronave)
        self.guardar_en_base_de_datos("Aeronaves", aeronave)

    def guardar_en_base_de_datos(self, tabla, entidad):
        conn = sqlite3.connect('control_transito_aereo.db')
        cursor = conn.cursor()
    
        if tabla == "Aeropuertos":
            cursor.execute('''
            SELECT * FROM Aeropuertos WHERE codigo = ?
            ''', (entidad.codigo,))
            if cursor.fetchone():
                print(f"El aeropuerto {entidad.codigo} ya existe en la base de datos.")
            else:
                cursor.execute('''
                INSERT INTO Aeropuertos (codigo, capacidad)
                VALUES (?, ?)
                ''', (entidad.codigo, entidad.capacidad_pista))
                print(f"Aeropuerto {entidad.codigo} guardado en la base de datos.")

        elif tabla == "Aeronaves":
            plan_vuelo_str = ','.join([aeropuerto.codigo for aeropuerto in entidad.plan_vuelo])
            cursor.execute('''
            SELECT * FROM Aeronaves WHERE nombre = ?
            ''', (entidad.nombre,))
            if cursor.fetchone():
                print(f"La aeronave {entidad.nombre} ya existe en la base de datos.")
            else:
                cursor.execute('''
                INSERT INTO Aeronaves (nombre, plan_vuelo)
                VALUES (?, ?)
                ''', (entidad.nombre, plan_vuelo_str))
                print(f"Aeronave {entidad.nombre} guardada en la base de datos con plan de vuelo {plan_vuelo_str}.")
    
        conn.commit()
        conn.close()

    def obtener_estado_espacio_aereo(self):
        print("Estado del espacio aéreo:")
        print("Aeronaves activas:")
        for aeronave in self.aeronaves:
            if aeronave.estado_alarma == False:
                print(f"  - {aeronave.nombre}: {aeronave.ubicacion.descripcion() if isinstance(aeronave.ubicacion, Ubicacion) else 'Vuelo'}")
            else:
                self.aeronaves_en_alarma.append(aeronave)
        print("Aeronaves en alarma:")
        for aeronave in self.aeronaves_en_alarma:
            print(f"  - {aeronave.nombre}")

    def verificar_misma_ubicacion(self, aeronave1, aeronave2):
        if aeronave1.ubicacion == aeronave2.ubicacion:
            print(f"Las aeronaves {aeronave1.nombre} y {aeronave2.nombre} están en la misma ubicación: {aeronave1.ubicacion}.")
        else:
            print(f"Las aeronaves {aeronave1.nombre} y {aeronave2.nombre} NO están en la misma ubicación.")


class Aeronave:
    def __init__(self, nombre, aeropuerto, control):
        self.nombre = nombre
        self.aeropuerto = aeropuerto
        self.control = control
        self.ubicacion = Terminal(aeropuerto)
        self.plan_vuelo = []
        self.aeropuerto_destino = None
        self.estado_alarma = False
        
    def configurar_plan_vuelo(self, ruta):
        self.plan_vuelo = ruta
        for aeropuerto in ruta:
            print(f"El plan de vuelo de {self.nombre} ahora tiene como destino {self.aeropuerto.codigo}")
        self.aeropuerto_destino = self.plan_vuelo[0] if self.plan_vuelo else None

    def desplazarse_a_terminal(self):
        self.ubicacion = Terminal(self.aeropuerto)
        print(f"La aeronave {self.nombre} está ahora en la terminal del aeropuerto {self.aeropuerto.codigo}")

    def desplazarse_a_pista(self):
        if self.aeropuerto.capacidad_pista > len(self.aeropuerto.pista):
            self.aeropuerto.pista.append(self)
            self.ubicacion = Pista(self.aeropuerto)
            print(f"La aeronave {self.nombre} está ahora en la pista del aeropuerto {self.aeropuerto.codigo}")
        else:
            print(f"La pista del aeropuerto {self.aeropuerto.codigo} está llena. La aeronave {self.nombre} no puede entrar.")

    def despegar(self):
        if isinstance(self.ubicacion, Pista):
                self.aeropuerto.pista.remove(self)
                self.ubicacion = Vuelo
                print(f"{self.nombre} ha despegado desde {self.aeropuerto.codigo} y está en vuelo.")
        else:
            print(f"{self.nombre} no está en la pista, no puede despegar.")
    
    def aterrizar(self):
        if self.ubicacion is Vuelo:
            if self.aeropuerto_destino.espacio_disponible() > 0:
                self.ubicacion = Pista(self.aeropuerto_destino)
                self.aeropuerto = self.aeropuerto_destino
                self.aeropuerto.pista.append(self) 
                print(f"{self.nombre} ha aterrizado en {self.aeropuerto.codigo}")
                if self.aeropuerto_destino in self.plan_vuelo:
                    self.plan_vuelo.remove(self.aeropuerto_destino)
                if len(self.plan_vuelo) <= 0:
                    self.ubicacion = Terminal(self.aeropuerto_destino)
                    print(f"{self.nombre} ha llegado a su destino. Plan de vuelo completado. Se queda en terminal")
                else:
                    self.aeropuerto_destino = self.plan_vuelo[0]
                    print(f"{self.nombre} no terminó su plan de vuelo. Su proximo destino es {self.plan_vuelo[0].codigo}.")
            else:
                self.estado_alarma = True
                print(f"La pista del aeropuerto {self.aeropuerto_destino.codigo} está llena. La aeronave {self.nombre} no puede aterrizar.")
                self.control.obtener_estado_espacio_aereo()
        else:
            print(f"{self.nombre} no está en vuelo, no puede aterrizar.")
    
    def vuelo(self):
        while len(self.plan_vuelo) > 0 and self.estado_alarma == False:
                if not isinstance(self.ubicacion, Pista):
                    self.desplazarse_a_pista()
                self.despegar()
                self.aterrizar()
            

    def estado_aeronave(self):
        ubicacion = self.ubicacion.descripcion() if isinstance(self.ubicacion, Ubicacion) else "Vuelo"
        plan_vuelo_destinos = [aeropuerto.codigo for aeropuerto in self.plan_vuelo]
        print(f"Aeronave {self.nombre}")
        print(f"Ubicación actual: {ubicacion}")
        print(f"Plan de vuelo: {plan_vuelo_destinos}")

#interfaz

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Tránsito Aéreo")
        
        self.control = Control()

        #frames
        self.frame_aeropuertos = LabelFrame(self.root, text="Aeropuertos", padx=10, pady=10)
        self.frame_aeropuertos.grid(row=0, column=0, padx=10, pady=10)

        self.codigo_aeropuerto_label = Label(self.frame_aeropuertos, text="Código del aeropuerto:")
        self.codigo_aeropuerto_label.grid(row=0, column=0)
        self.codigo_aeropuerto_entry = Entry(self.frame_aeropuertos)
        self.codigo_aeropuerto_entry.grid(row=0, column=1)

        self.capacidad_aeropuerto_label = Label(self.frame_aeropuertos, text="Capacidad del aeropuerto:")
        self.capacidad_aeropuerto_label.grid(row=1, column=0)
        self.capacidad_aeropuerto_entry = Entry(self.frame_aeropuertos)
        self.capacidad_aeropuerto_entry.grid(row=1, column=1)

        self.agregar_aeropuerto_button = Button(self.frame_aeropuertos, text="Agregar Aeropuerto", command=self.agregar_aeropuerto)
        self.agregar_aeropuerto_button.grid(row=2, column=0, columnspan=2)

        self.ver_aeropuertos_button = Button(self.frame_aeropuertos, text="Ver Aeropuertos", command=self.ver_aeropuertos)
        self.ver_aeropuertos_button.grid(row=3, column=0, columnspan=2)

        self.frame_aeronaves = LabelFrame(self.root, text="Aeronaves", padx=10, pady=10)
        self.frame_aeronaves.grid(row=0, column=1, padx=10, pady=10)

        self.nombre_aeronave_label = Label(self.frame_aeronaves, text="Nombre de la aeronave:")
        self.nombre_aeronave_label.grid(row=0, column=0)
        self.nombre_aeronave_entry = Entry(self.frame_aeronaves)
        self.nombre_aeronave_entry.grid(row=0, column=1)

        self.aeropuerto_aeronave_label = Label(self.frame_aeronaves, text="Código del aeropuerto de origen:")
        self.aeropuerto_aeronave_label.grid(row=1, column=0)
        self.aeropuerto_aeronave_entry = Entry(self.frame_aeronaves)
        self.aeropuerto_aeronave_entry.grid(row=1, column=1)

        self.agregar_aeronave_button = Button(self.frame_aeronaves, text="Agregar Aeronave", command=self.agregar_aeronave)
        self.agregar_aeronave_button.grid(row=2, column=0, columnspan=2)

        self.dar_plan_vuelo_button = Button(self.frame_aeronaves, text="Dar Plan de Vuelo", command=self.dar_plan_vuelo)
        self.dar_plan_vuelo_button.grid(row=3, column=0, columnspan=2)

        self.iniciar_vuelo_button = Button(self.frame_aeronaves, text="Iniciar Plan de Vuelo", command=self.iniciar_vuelo)
        self.iniciar_vuelo_button.grid(row=4, column=0, columnspan=2)

        self.ver_aeronaves_button = Button(self.frame_aeronaves, text="Ver Aeronaves", command=self.ver_aeronaves)
        self.ver_aeronaves_button.grid(row=5, column=0, columnspan=2)

        self.ver_alarma_button = Button(self.frame_aeronaves, text="Ver Aeronaves en Alarma", command=self.ver_aeronaves_en_alarma)
        self.ver_alarma_button.grid(row=6, column=0, columnspan=2)

        self.verificar_ubicacion_button = Button(self.frame_aeronaves, text="Verificar Ubicación Aeronaves", command=self.verificar_ubicacion)
        self.verificar_ubicacion_button.grid(row=7, column=0, columnspan=2)

        self.mover_a_pista_button = Button(self.frame_aeronaves, text="Mover a Pista", command=self.mover_a_pista)
        self.mover_a_pista_button.grid(row=9, column=0, columnspan=2)

        self.aeronave_comparacion_label1 = Label(self.frame_aeronaves, text="Aeronave 1:")
        self.aeronave_comparacion_label1.grid(row=10, column=0)
        self.aeronave_comparacion_entry1 = Entry(self.frame_aeronaves)
        self.aeronave_comparacion_entry1.grid(row=10, column=1)

        self.aeronave_comparacion_label2 = Label(self.frame_aeronaves, text="Aeronave 2:")
        self.aeronave_comparacion_label2.grid(row=11, column=0)
        self.aeronave_comparacion_entry2 = Entry(self.frame_aeronaves)
        self.aeronave_comparacion_entry2.grid(row=11, column=1)

        self.verificar_ubicacion_dos_button = Button(self.frame_aeronaves, text="Comparar Ubicaciones", command=self.verificar_ubicacion_dos)
        self.verificar_ubicacion_dos_button.grid(row=12, column=0, columnspan=2)

        self.destinos_label = Label(self.frame_aeronaves, text="Seleccione los destinos:")
        self.destinos_label.grid(row=8, column=0)
        self.destinos_listbox = Listbox(self.frame_aeronaves, selectmode=MULTIPLE, height=5)
        self.destinos_listbox.grid(row=8, column=1)
        self.actualizar_destinos_listbox()

    def agregar_aeropuerto(self):
        codigo = self.codigo_aeropuerto_entry.get()
        capacidad = int(self.capacidad_aeropuerto_entry.get())
        aeropuerto = Aeropuerto(codigo, capacidad)
        self.control.agregar_aeropuerto(aeropuerto)
        self.actualizar_destinos_listbox()
        messagebox.showinfo("Éxito", f"Aeropuerto {codigo} agregado exitosamente.")

    def agregar_aeronave(self):
        nombre = self.nombre_aeronave_entry.get()
        codigo_aeropuerto = self.aeropuerto_aeronave_entry.get()
        aeropuerto = next((a for a in self.control.aeropuertos if a.codigo == codigo_aeropuerto), None)
        
        if aeropuerto:
            aeronave = Aeronave(nombre, aeropuerto, self.control)
            self.control.agregar_aeronave(aeronave)
            messagebox.showinfo("Éxito", f"Aeronave {nombre} agregada exitosamente.")
        else:
            messagebox.showerror("Error", "El aeropuerto no existe.")
    
    def ver_aeropuertos(self):
        lista_aeropuertos = "\n".join([aeropuerto.codigo for aeropuerto in self.control.aeropuertos])
        messagebox.showinfo("Aeropuertos", lista_aeropuertos if lista_aeropuertos else "No hay aeropuertos registrados.")

    def ver_aeronaves(self):
        lista_aeronaves = "\n".join([aeronave.nombre for aeronave in self.control.aeronaves])
        messagebox.showinfo("Aeronaves", lista_aeronaves if lista_aeronaves else "No hay aeronaves registradas.")

    def dar_plan_vuelo(self):
        nombre_aeronave = self.nombre_aeronave_entry.get()
        aeronave = next((a for a in self.control.aeronaves if a.nombre == nombre_aeronave), None)

        if aeronave:
            destinos_seleccionados = [self.control.aeropuertos[i] for i in self.destinos_listbox.curselection()]
            if destinos_seleccionados:
                aeronave.configurar_plan_vuelo(destinos_seleccionados)
                messagebox.showinfo("Plan de Vuelo", f"Plan de vuelo de {nombre_aeronave} configurado con destinos seleccionados.")
            else:
                messagebox.showerror("Error", "Debe seleccionar al menos un destino.")
        else:
            messagebox.showerror("Error", "Aeronave no encontrada.")

    def iniciar_vuelo(self):
        nombre_aeronave = self.nombre_aeronave_entry.get()
        aeronave = next((a for a in self.control.aeronaves if a.nombre == nombre_aeronave), None)
        if aeronave:
            aeronave.vuelo()
            messagebox.showinfo("Vuelo Iniciado", f"Vuelo de {nombre_aeronave} iniciado.")
        else:
            messagebox.showerror("Error", "Aeronave no encontrada.")

    def ver_aeronaves_en_alarma(self):
        aeronaves_en_alarma = [a.nombre for a in self.control.aeronaves_en_alarma]
        messagebox.showinfo("Aeronaves en Alarma", "\n".join(aeronaves_en_alarma) if aeronaves_en_alarma else "No hay aeronaves en alarma.")

    def verificar_ubicacion(self):
        aeronave1_nombre = self.nombre_aeronave_entry.get()
        aeronave2_nombre = self.aeropuerto_aeronave_entry.get()
        aeronave1 = next((a for a in self.control.aeronaves if a.nombre == aeronave1_nombre), None)
        aeronave2 = next((a for a in self.control.aeronaves if a.nombre == aeronave2_nombre), None)
        
        if aeronave1 and aeronave2:
            self.control.verificar_misma_ubicacion(aeronave1, aeronave2)
        else:
            messagebox.showerror("Error", "Una o ambas aeronaves no se encontraron.")
    
    def mover_a_pista(self):
        nombre_aeronave = self.nombre_aeronave_entry.get()
        aeronave = next((a for a in self.control.aeronaves if a.nombre == nombre_aeronave), None)
    
        if aeronave:
            aeronave.desplazarse_a_pista()
            messagebox.showinfo("Mover a Pista", f"Aeronave {nombre_aeronave} movida a la pista del aeropuerto {aeronave.aeropuerto.codigo}.")
        else:
            messagebox.showerror("Error", "Aeronave no encontrada.")

    def verificar_ubicacion_dos(self):
        nombre_aeronave1 = self.aeronave_comparacion_entry1.get()
        nombre_aeronave2 = self.aeronave_comparacion_entry2.get()
    
        aeronave1 = next((a for a in self.control.aeronaves if a.nombre == nombre_aeronave1), None)
        aeronave2 = next((a for a in self.control.aeronaves if a.nombre == nombre_aeronave2), None)
        if aeronave1 and aeronave2:
            if aeronave1.ubicacion.descripcion() == aeronave2.ubicacion.descripcion():
                messagebox.showinfo("Comparar Ubicaciones", f"Las aeronaves {nombre_aeronave1} y {nombre_aeronave2} están en la misma ubicación: {aeronave1.ubicacion.descripcion()}.")
            else:
                messagebox.showinfo("Comparar Ubicaciones", f"Las aeronaves {nombre_aeronave1} y {nombre_aeronave2} NO están en la misma ubicación.")
        else:
            messagebox.showerror("Error", "Una o ambas aeronaves no se encontraron.")

    def actualizar_destinos_listbox(self):
        """Actualiza la lista de aeropuertos disponibles para ser seleccionados como destinos."""
        self.destinos_listbox.delete(0, END)
        for aeropuerto in self.control.aeropuertos:
            self.destinos_listbox.insert(END, aeropuerto.codigo)

crear_base_de_datos()
root = Tk()
app = Aplicacion(root)
root.mainloop()


"""
crear_base_de_datos()
control = Control()

#creando aeropuertos
aeropuerto1 = Aeropuerto("SAN", 2)
aeropuerto2 = Aeropuerto("AMD", 2)
aeropuerto3 = Aeropuerto("BAE", 2)
aeropuerto4 = Aeropuerto("ORD", 2)
aeropuerto5 = Aeropuerto("IAD", 2)

#creando aeronaves
aeronave1 = Aeronave("A101", aeropuerto1, control)
aeronave2 = Aeronave("A102", aeropuerto2, control)
aeronave3 = Aeronave("A103", aeropuerto2, control)

#dandoles plan de vuelo
aeronave1.configurar_plan_vuelo(ruta = [aeropuerto2, aeropuerto3, aeropuerto4, aeropuerto5])
aeronave2.configurar_plan_vuelo(ruta = [aeropuerto3, aeropuerto4])


#agregando aeropuertos a control
control.agregar_aeropuerto(aeropuerto1)
control.agregar_aeropuerto(aeropuerto2)
control.agregar_aeropuerto(aeropuerto3)
control.agregar_aeropuerto(aeropuerto4)
control.agregar_aeropuerto(aeropuerto5)

#agregando aeronaves a control
control.agregar_aeronave(aeronave1)
control.agregar_aeronave(aeronave2)
control.agregar_aeronave(aeronave3)


aeronave2.desplazarse_a_pista()
aeronave3.desplazarse_a_pista()

print(control.verificar_misma_ubicacion(aeronave1, aeronave2))

aeronave1.vuelo()
aeronave2.vuelo()

#chequeo base de datos
conn = sqlite3.connect('control_transito_aereo.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM Aeropuertos')
aeropuertos = cursor.fetchall()
print("Aeropuertos:", aeropuertos)

cursor.execute('SELECT * FROM Aeronaves')
aeronaves = cursor.fetchall()
print("Aeronaves:", aeronaves)

conn.close()
"""