import sqlite3
from abc import ABC, abstractmethod

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

    def agregar_plan(self, plan_vuelo):
        self.planes_vuelo.append(plan_vuelo)
        self.guardar_en_base_de_datos("Planes_de_vuelo", plan_vuelo)

    def guardar_en_base_de_datos(self, tabla, entidad):
        conn = sqlite3.connect('control_transito_aereo.db')
        cursor = conn.cursor()

        if tabla == "Aeropuertos":
            cursor.execute('''
            INSERT OR REPLACE INTO Aeropuertos (codigo, capacidad)
            VALUES (?, ?)
            ''', (entidad.codigo, entidad.capacidad_pista))
            print(f"Aeropuerto {entidad.codigo} guardado en la base de datos.")

        elif tabla == "Aeronaves":
            cursor.execute('''
            INSERT OR REPLACE INTO Aeronaves (nombre)
            VALUES (?)
            ''', (entidad.nombre))
            print(f"Aeronave {entidad.nombre} guardada en la base de datos.")

        elif tabla == "Planes_de_vuelo":
            cursor.execute('''
                INSERT INTO planes_vuelo (aeronave_id, ruta)
                VALUES (?, ?)
                ''', (entidad.nombre, entidad.plan_vuelo))
            print(f"Plan de vuelo para {entidad.nombre} guardado en la base de datos.")

        conn.commit()
        conn.close()

    def obtener_estado_espacio_aereo(self):
        for aeronave in self.aeronaves:
            if aeronave.estado_alarma:
                print(f"¡La aeronave {aeronave.nombre} está en alarma!")
                self.aeronaves_en_alarma.append(aeronave)
        return self.aeronaves_en_alarma

    def verificar_misma_ubicacion(self, aeronave1, aeronave2):
        return aeronave1.ubicacion == aeronave2.ubicacion

class Aeronave:
    def __init__(self, nombre, aeropuerto):
        self.nombre = nombre
        self.aeropuerto = aeropuerto
        self.ubicacion = Terminal(aeropuerto)
        self.plan_vuelo = []
        self.guardar_en_base_de_datos()
        self.aeropuerto_destino = None
        self.estado_alarma = False
    
    def guardar_en_base_de_datos(self):
        print(f"La aeronave {self.nombre} ha sido guardada en la base de datos.")
        
    def configurar_plan_vuelo(self, ruta):
        self.plan_vuelo = ruta
        for aeropuerto in ruta:
            print(f"El plan de vuelo de {self.nombre} ahora tiene como destino {aeropuerto.codigo}")
        control.guardar_en_base_de_datos("Planes_de_vuelo", self)
        self.aeropuerto_destino = self.plan_vuelo[0]

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
            self.ubicacion = Pista(self.aeropuerto_destino)
            self.aeropuerto = self.aeropuerto_destino
            self.aeropuerto.pista.append(self) 
            print(f"{self.nombre} ha aterrizado en {self.aeropuerto.codigo}")
            if self.plan_vuelo.__contains__(self.aeropuerto_destino):
                self.plan_vuelo.remove(self.aeropuerto_destino) #removimos del plan de vuelo el aeropuerto en el que estamos
            if len(self.plan_vuelo) <= 0:
                self.ubicacion = Terminal(self.aeropuerto_destino)
                print(f"{self.nombre} ha llegado a su destino. Plan de vuelo completado. Se queda en terminal")
            else:
                self.aeropuerto_destino = self.plan_vuelo[0] #actualizamos al siguiente destino
                print(f"{self.nombre} no terminó su plan de vuelo. Su proximo destino es {self.plan_vuelo[0].codigo}.")
                
        else:
            print(f"{self.nombre} no está en vuelo, no puede aterrizar.")
    
    def vuelo(self):
        while len(self.plan_vuelo) > 0:
            if self.aeropuerto_destino.espacio_disponible() > 0:
                if not isinstance(self.ubicacion, Pista):
                    self.desplazarse_a_pista()
                self.despegar()
                self.aterrizar()
            else:
                self.estado_alarma = True
                print(f"La pista del aeropuerto {self.aeropuerto_destino.codigo} está llena. La aeronave {self.nombre} no puede aterrizar.")
                control.obtener_estado_espacio_aereo()
                break

#creando aeropuertos
aeropuerto1 = Aeropuerto("SAN", 2)
aeropuerto2 = Aeropuerto("AMD", 2)
aeropuerto3 = Aeropuerto("BAE", 2)
aeropuerto4 = Aeropuerto("ORD", 2)
aeropuerto5 = Aeropuerto("IAD", 2)

control = Control()

#agregando aeropuertos a control
control.agregar_aeropuerto(aeropuerto1)
control.agregar_aeropuerto(aeropuerto2)
control.agregar_aeropuerto(aeropuerto3)
control.agregar_aeropuerto(aeropuerto4)
control.agregar_aeropuerto(aeropuerto5)

#creando aeronaves
aeronave1 = Aeronave("A101", aeropuerto1)
aeronave2 = Aeronave("A102", aeropuerto2)
aeronave3 = Aeronave("A102", aeropuerto2)

#agregando aeronaves a control
control.agregar_aeronave(aeronave1)
control.agregar_aeronave(aeronave2)
#control.agregar_aeronave(aeronave3)

#dandoles plan de vuelo
aeronave1.configurar_plan_vuelo(ruta = [aeropuerto2, aeropuerto3, aeropuerto4, aeropuerto5])
aeronave2.configurar_plan_vuelo(ruta = [aeropuerto3, aeropuerto4])

#aeronave2.desplazarse_a_pista()
#aeronave3.desplazarse_a_pista()

#aeronave1.vuelo()
#aeronave2.vuelo()

#chequeo base de datos
conn = sqlite3.connect('control_transito_aereo.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM Aeropuertos')
aeropuertos = cursor.fetchall()
print("Aeropuertos:", aeropuertos)

cursor.execute('SELECT * FROM Aeronaves')
aeronaves = cursor.fetchall()
print("Aeronaves:", aeronaves)

cursor.execute('SELECT * FROM Planes_de_vuelo')
planes_vuelo = cursor.fetchall()
print("Planes de vuelo:", planes_vuelo)

conn.close()