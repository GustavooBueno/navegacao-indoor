import networkx as nx
import pyttsx3
import speech_recognition as sr

class Beacon:
    def __init__(self, id, position):
        self.id = id
        self.position = position

class IndoorNavigation:
    def __init__(self):
        self.beacons = {}
        self.graph = nx.Graph()
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

    def add_beacon(self, beacon):
        self.beacons[beacon.id] = beacon
        self.graph.add_node(beacon.id, position=beacon.position)

    def add_path(self, beacon1_id, beacon2_id, distance):
        self.graph.add_edge(beacon1_id, beacon2_id, weight=distance)

    def get_shortest_path(self, start_id, end_id):
        return nx.dijkstra_path(self.graph, start_id, end_id, weight='weight')

    def direction(self, from_pos, to_pos):
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        
        if dx > 0:
            return "vire à direita"
        elif dx < 0:
            return "vire à esquerda"
        elif dy > 0:
            return "siga em frente"
        elif dy < 0:
            return "retorne"
        else:
            return "continue"

    def simulate_navigation(self, start_id, end_id):
        path = self.get_shortest_path(start_id, end_id)
        instructions = []
        
        for i in range(len(path) - 1):
            current_beacon = self.beacons[path[i]]
            next_beacon = self.beacons[path[i + 1]]
            direction = self.direction(current_beacon.position, next_beacon.position)
            instruction = f"A {self.graph.edges[path[i], path[i + 1]]['weight']} metros {direction} para Beacon {next_beacon.id}."
            instructions.append(instruction)
        
        return instructions

    def speak_instructions(self, instructions):
        for instruction in instructions:
            print(instruction)  # Print to console
            self.engine.say(instruction)
            self.engine.runAndWait()

    def listen_for_beacon_id(self, prompt):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print(prompt)
            self.engine.say(prompt)
            self.engine.runAndWait()
            audio = self.recognizer.listen(source)
            try:
                response = self.recognizer.recognize_google(audio, language='pt-BR')
                print(f"Reconhecido: {response}")
                self.engine.say(f"Você disse: {response}")
                self.engine.runAndWait()
                if "vértice" in response:
                    beacon_id = int(response.split()[-1])
                    return beacon_id
                else:
                    raise ValueError("Formato inválido")
            except sr.UnknownValueError:
                print("Desculpe, não entendi o que você disse. Por favor, tente novamente.")
                self.engine.say("Desculpe, não entendi o que você disse. Por favor, tente novamente.")
                self.engine.runAndWait()
                return self.listen_for_beacon_id(prompt)
            except sr.RequestError as e:
                print(f"Erro ao se comunicar com o serviço de reconhecimento de fala: {e}")
                self.engine.say(f"Erro ao se comunicar com o serviço de reconhecimento de fala: {e}")
                self.engine.runAndWait()
                return None
            except ValueError:
                print("Desculpe, o formato não está correto. Por favor, diga 'Vértice' seguido do número.")
                self.engine.say("Desculpe, o formato não está correto. Por favor, diga 'Vértice' seguido do número.")
                self.engine.runAndWait()
                return self.listen_for_beacon_id(prompt)

# Configuração do grafo
beacon1 = Beacon(1, (0, 0))
beacon2 = Beacon(2, (1, 0))
beacon3 = Beacon(3, (1, 1))
beacon4 = Beacon(4, (2, 1))
beacon5 = Beacon(5, (1, 2))

navigator = IndoorNavigation()
navigator.add_beacon(beacon1)
navigator.add_beacon(beacon2)
navigator.add_beacon(beacon3)
navigator.add_beacon(beacon4)
navigator.add_beacon(beacon5)

navigator.add_path(1, 2, 300)  # 300 metros
navigator.add_path(2, 3, 300)  # 300 metros
navigator.add_path(3, 4, 300)  # 300 metros
navigator.add_path(3, 5, 300)  # 300 metros

# Interação com o usuário para escolher o ponto de partida e destino por voz
start_id = navigator.listen_for_beacon_id("Diga o ID do Beacon de partida: (por exemplo, 'Vértice 1')")
end_id = navigator.listen_for_beacon_id("Diga o ID do Beacon de destino: (por exemplo, 'Vértice 5')")

# Simulação da navegação do ponto de partida ao ponto de destino
if start_id is not None and end_id is not None:
    instructions = navigator.simulate_navigation(start_id, end_id)
    navigator.speak_instructions(instructions)
else:
    print("Não foi possível obter os IDs dos Beacons corretamente.")
    navigator.engine.say("Não foi possível obter os IDs dos Beacons corretamente.")
    navigator.engine.runAndWait()
