import sqlite3
from abc import ABC, abstractmethod

def crear_base_de_datos():
    conn = sqlite3.connect('control_transito_aereo.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aeropuertos (
            codigo TEXT PRIMARY KEY,
            capacidad_pista INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aeronaves (
            nombre TEXT PRIMARY KEY,
            aeropuerto_codigo TEXT,
            ubicacion TEXT,
            plan_vuelo TEXT,
            FOREIGN KEY (aeropuerto_codigo) REFERENCES aeropuertos(codigo)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planes_vuelo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aeronave_nombre TEXT,
            aeropuerto_destino_codigo TEXT,
            FOREIGN KEY (aeronave_nombre) REFERENCES aeronaves(nombre),
            FOREIGN KEY (aeropuerto_destino_codigo) REFERENCES aeropuertos(codigo)
        )
    ''')

    conn.commit()
    conn.close()

class Ubicacion(ABC):
    @abstractmethod
    def descripcion(self):
        pass

    @abstractmethod
    def permitir_operacion(self, aeronave):
        pass

class Terminal(Ubicacion):
    def __init__(self, aeropuerto):
        self.aeropuerto = aeropuerto

    def descripcion(self):
        return f"Terminal en el aeropuerto {self.aeropuerto.codigo}"

    def permitir_operacion(self, aeronave):
        if aeronave not in self.aeropuerto.terminal:
            self.aeropuerto.terminal.append(aeronave)

class Pista(Ubicacion):
    def __init__(self, aeropuerto):
        self.aeropuerto = aeropuerto

    def descripcion(self):
        return f"Pista en el aeropuerto {self.aeropuerto.codigo}"

    def permitir_operacion(self, aeronave):
        if aeronave not in self.aeropuerto.pista:
            self.aeropuerto.pista.append(aeronave)

class Vuelo(Ubicacion):
    def __init__(self, aeropuerto_origen, aeropuerto_destino):
        self.aeropuerto_origen = aeropuerto_origen
        self.aeropuerto_destino = aeropuerto_destino

    def descripcion(self):
        return f"En vuelo desde {self.aeropuerto_origen.codigo} hacia {self.aeropuerto_destino.codigo}"

    def permitir_operacion(self, aeronave):
        if aeronave not in self.aeropuerto_origen.pista:
            self.aeropuerto_origen.pista.append(aeronave)

class Aeropuerto:
    def __init__(self, codigo, capacidad_pista):
        self.codigo = codigo
        self.capacidad_pista = capacidad_pista
        self.terminal = []
        self.pista = []
    
    def obtener_estado(self):
        return {
            "terminal": [aeronave.nombre for aeronave in self.terminal],
            "pista": [aeronave.nombre for aeronave in self.pista],
            "capacidad_disponible": self.capacidad_pista - len(self.pista)
        }

class Control:
    def __init__(self):
        self.aeropuertos = []
        self.aeronaves = []
        self.planes_vuelo = []

    def agregar_aeropuerto(self, aeropuerto):
        self.aeropuertos.append(aeropuerto)
        self.guardar_en_base_de_datos("aeropuertos", aeropuerto)

    def agregar_aeronave(self, aeronave):
        self.aeronaves.append(aeronave)
        self.guardar_en_base_de_datos("aeronaves", aeronave)

    def guardar_en_base_de_datos(self, tipo, objeto):
        conn = sqlite3.connect('control_transito_aereo.db')
        cursor = conn.cursor()
        
        if tipo == "aeropuertos":
            cursor.execute('''
            INSERT OR REPLACE INTO aeropuertos (codigo, capacidad_pista)
            VALUES (?, ?)
            ''', (objeto.codigo, objeto.capacidad_pista))
            print(f"Aeropuerto {objeto.codigo} guardado en la base de datos.")

        elif tipo == "aeronaves":
            plan_vuelo_str = ','.join([aeropuerto.codigo for aeropuerto in objeto.plan_vuelo])
            cursor.execute('''
            INSERT OR REPLACE INTO aeronaves (nombre, aeropuerto_codigo, ubicacion, plan_vuelo)
            VALUES (?, ?, ?, ?)
            ''', (objeto.nombre, objeto.aeropuerto.codigo, objeto.ubicacion.descripcion(), plan_vuelo_str))
            print(f"Aeronave {objeto.nombre} guardada en la base de datos.")

        elif tipo == "planes_vuelo":
            for aeropuerto_destino in objeto.plan_vuelo:
                cursor.execute('''
                INSERT INTO planes_vuelo (aeronave_nombre, aeropuerto_destino_codigo)
                VALUES (?, ?)
                ''', (objeto.nombre, aeropuerto_destino.codigo))
                print(f"Plan de vuelo para {objeto.nombre} guardado en la base de datos.")

        conn.commit()
        conn.close()
    
    def obtener_estado_espacio_aereo(self):
        aeronaves_en_alarma = [
            aeronave for aeronave in self.aeronaves
            if isinstance(aeronave.ubicacion, Vuelo) and
            len(aeronave.aeropuerto.pista) >= aeronave.aeropuerto.capacidad_pista
        ]
        return {
            "aeronaves": [aeronave.nombre for aeronave in self.aeronaves],
            "vuelos_en_alarma": [aeronave.nombre for aeronave in aeronaves_en_alarma]
        }

    def verificar_misma_ubicacion(self, aeronave1, aeronave2):
        return aeronave1.ubicacion == aeronave2.ubicacion

class Aeronave:
    def __init__(self, nombre, aeropuerto):
        self.nombre = nombre
        self.aeropuerto = aeropuerto
        self.ubicacion = Terminal(aeropuerto)
        self.plan_vuelo = []
        self.guardar_en_base_de_datos()
    
    def guardar_en_base_de_datos(self):
        print(f"La aeronave {self.nombre} ha sido guardada en la base de datos.")
        
    def configurar_plan_vuelo(self, aeropuerto_destino):
        self.plan_vuelo = aeropuerto_destino
        for aeropuerto in aeropuerto_destino:
            print(f"El plan de vuelo de {self.nombre} ahora tiene como destino {aeropuerto.codigo}")

    def desplazarse_a_terminal(self):
        self.ubicacion = Terminal(self.aeropuerto)
        print(f"La aeronave {self.nombre} está ahora en la terminal del aeropuerto {self.aeropuerto.codigo}")

    def desplazarse_a_pista(self):
        self.ubicacion = Pista(self.aeropuerto)
        if len(self.aeropuerto.pista) < self.aeropuerto.capacidad_pista:
            self.aeropuerto.pista.append(self)
            print(f"La aeronave {self.nombre} está ahora en la pista del aeropuerto {self.aeropuerto.codigo}")
        else:
            print(f"La pista del aeropuerto {self.aeropuerto.codigo} está llena. La aeronave {self.nombre} no puede entrar.")

    def despegar(self):
        if isinstance(self.ubicacion, Pista):
            if self in self.aeropuerto.pista:
                self.aeropuerto.pista.remove(self)
                self.ubicacion = "En vuelo"
                print(f"{self.nombre} ha despegado desde {self.aeropuerto.codigo} y está en vuelo.")
            else:
                print(f"{self.nombre} no está en la pista, no puede despegar.")
        else:
            print(f"{self.nombre} no está en la pista, no puede despegar.")
    
    def aterrizar(self):
        if self.ubicacion == "En vuelo":
            aeropuerto_destino = self.plan_vuelo[0]
            if len(aeropuerto_destino.pista) < aeropuerto_destino.capacidad_pista:
                self.ubicacion = Pista(aeropuerto_destino)
                self.aeropuerto = aeropuerto_destino
                aeropuerto_destino.pista.append(self)
                print(f"{self.nombre} ha aterrizado en {aeropuerto_destino.codigo}")
                self.plan_vuelo.remove(aeropuerto_destino)
            else:
                print(f"La pista en {aeropuerto_destino.codigo} está llena, no puede aterrizar.")
                
            if len(self.plan_vuelo) <= 0:
                self.ubicacion = Terminal(aeropuerto_destino)
                print(f"{self.nombre} ha llegado a su destino. Plan de vuelo completado. Se queda en terminal")
            else:
                print(f"{self.nombre} no terminó su plan de vuelo. Su proximo destino es {self.plan_vuelo[0].codigo}.")
                
        else:
            print(f"{self.nombre} no está en vuelo, no puede aterrizar.")
    
    def obtener_estado(self):
        return {
            "ubicacion": self.ubicacion,
            "plan_vuelo": [aeropuerto.codigo for aeropuerto in self.plan_vuelo]
        }

crear_base_de_datos()

#creando aeropuertos
aeropuerto1 = Aeropuerto("A001", 2)
aeropuerto2 = Aeropuerto("A002", 2)
aeropuerto3 = Aeropuerto("A003", 2)
aeropuerto4 = Aeropuerto("A004", 2)

control = Control()

#agregando aeropuertos a control
control.agregar_aeropuerto(aeropuerto1)
control.agregar_aeropuerto(aeropuerto2)
control.agregar_aeropuerto(aeropuerto3)
control.agregar_aeropuerto(aeropuerto4)

#creando aeronaves
aeronave1 = Aeronave("Aeronave1", aeropuerto1)
aeronave2 = Aeronave("Aeronave2", aeropuerto1)
aeronave3 = Aeronave("Aeronave3", aeropuerto2)

#agregando aeronaves a control
control.agregar_aeronave(aeronave1)
control.agregar_aeronave(aeronave2)
#control.agregar_aeronave(aeronave3)

#dandoles plan de vuelo
aeronave1.configurar_plan_vuelo(aeropuerto_destino=[aeropuerto2, aeropuerto3])
aeronave2.configurar_plan_vuelo(aeropuerto_destino=[aeropuerto2, aeropuerto4])

#desplazando aeronaves a la pista 
aeronave1.desplazarse_a_pista()
aeronave2.desplazarse_a_pista()

#despegando
aeronave1.despegar()
aeronave2.despegar()

#aterrizar
aeronave1.aterrizar()

aeronave1.desplazarse_a_pista()

aeronave1.despegar()

aeronave1.aterrizar()

#chequeo base de datos
conn = sqlite3.connect('control_transito_aereo.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM aeropuertos')
aeropuertos = cursor.fetchall()
print("Aeropuertos:", aeropuertos)

cursor.execute('SELECT * FROM aeronaves')
aeronaves = cursor.fetchall()
print("Aeronaves:", aeronaves)

cursor.execute('SELECT * FROM planes_vuelo')
planes_vuelo = cursor.fetchall()
print("Planes de vuelo:", planes_vuelo)

conn.close()