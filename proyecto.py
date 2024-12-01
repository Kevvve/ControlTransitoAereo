from abc import ABC, abstractmethod

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

    def agregar_aeronave(self, aeronave):
        self.aeronaves.append(aeronave)

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
        self.ubicacion = Terminal(aeropuerto)  # Inicializamos en la terminal
        self.plan_vuelo = []

    def desplazarse_a_terminal(self):
        self.ubicacion = Terminal(self.aeropuerto)
        print(f"La aeronave {self.nombre} está ahora en la terminal del aeropuerto {self.aeropuerto.codigo}")

    def desplazarse_a_pista(self):
        self.ubicacion = Pista(self.aeropuerto)
        if self not in self.aeropuerto.pista:
            self.aeropuerto.pista.append(self)
        print(f"La aeronave {self.nombre} está ahora en la pista del aeropuerto {self.aeropuerto.codigo}")

    def despegar(self):
        if isinstance(self.ubicacion, Pista):
            if self in self.aeropuerto.pista:
                self.aeropuerto.pista.remove(self)
                print(f"{self.nombre} ha despegado desde {self.aeropuerto.codigo}")
            else:
                print(f"{self.nombre} no está en la pista, no puede despegar.")
        else:
            print(f"{self.nombre} no está en la pista, no puede despegar.")

    def aterrizar(self):
        if isinstance(self.ubicacion, Vuelo) and len(self.aeropuerto.pista) < self.aeropuerto.capacidad_pista:
            self.aeropuerto.pista.append(self)
            print(f"{self.nombre} ha aterrizado en {self.aeropuerto.codigo}")
        else:
            print(f"{self.nombre} no puede aterrizar. La pista está llena o no está en vuelo.")

    def inicializar_plan_vuelo(self):
        self.plan_vuelo = []
        print(f"El plan de vuelo de {self.nombre} ha sido inicializado.")

    def configurar_plan_vuelo(self, aeropuerto_destino):
        self.plan_vuelo.append(aeropuerto_destino)
        print(f"El plan de vuelo de {self.nombre} ahora tiene como destino {aeropuerto_destino.codigo}")

    def obtener_estado(self):
        return {
            "ubicacion": self.ubicacion.descripcion(),
            "plan_vuelo": [aeropuerto.codigo for aeropuerto in self.plan_vuelo]
        }
