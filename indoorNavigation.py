import networkx as nx  # Importa a biblioteca NetworkX para manipulação de grafos
import pyttsx3         # Importa a biblioteca pyttsx3 para síntese de voz
import speech_recognition as sr  # Importa a biblioteca speech_recognition para reconhecimento de fala

# Classe que representa um beacon (ponto de referência)
class Beacon:
    def __init__(self, id, name, position):
        self.id = id  # ID do beacon
        self.name = name  # Nome amigável do beacon
        self.position = position  # Posição (coordenadas) do beacon

# Classe para navegação indoor usando beacons e grafos
class IndoorNavigation:
    def __init__(self):
        self.beacons = {}  # Dicionário para armazenar beacons
        self.graph = nx.Graph()  # Cria um grafo usando NetworkX
        self.engine = pyttsx3.init()  # Inicializa o mecanismo de síntese de voz
        self.recognizer = sr.Recognizer()  # Inicializa o reconhecedor de fala

    # Adiciona um beacon ao grafo e ao dicionário de beacons
    def add_beacon(self, beacon):
        self.beacons[beacon.id] = beacon
        self.graph.add_node(beacon.id, position=beacon.position)

    # Adiciona um caminho (aresta) entre dois beacons no grafo
    def add_path(self, beacon1_id, beacon2_id, distance):
        self.graph.add_edge(beacon1_id, beacon2_id, weight=distance)

    # Encontra o caminho mais curto entre dois beacons usando o algoritmo de Dijkstra
    def get_shortest_path(self, start_id, end_id):
        return nx.dijkstra_path(self.graph, start_id, end_id, weight='weight')

    # Gera a instrução de direção específica com base nas condições fornecidas
    def get_direction_instruction(self, from_id, to_id, next_id):
        directions = {
            (2, 3, 4): "vire à direita",
            (5, 3, 4): "vire à esquerda",
            (10, 11, 12): "vire à esquerda",
            (10, 12, 11): "vire à esquerda",
            (10, 11, 15): "vire à direita",
            (15, 11, 14): "vire à direita",
            (15, 11, 10): "vire à esquerda",
            (13, 12, 10): "vire à direita",
            (9, 10, 12): "vire à esquerda",
            (9, 10, 11): "vire à direita",
            (11, 10, 9): "vire à esquerda",
            (3, 5, 6): "vire à esquerda",
            (6, 5, 3): "vire à direita",
            (7, 8, 9): "vire à esquerda",
            (9, 8, 7): "vire à direita",
        }
        return directions.get((from_id, to_id, next_id), None)

    # Simula a navegação gerando instruções a partir do caminho mais curto
    def simulate_navigation(self, start_id, end_id):
        path = self.get_shortest_path(start_id, end_id)  # Encontra o caminho mais curto
        instructions = []

        # Gera instruções para cada passo no caminho
        for i in range(len(path) - 1):
            from_beacon = self.beacons[path[i]]  # Beacon atual
            to_beacon = self.beacons[path[i + 1]]  # Próximo beacon
            if i + 2 < len(path):
                next_beacon = self.beacons[path[i + 2]]  # Beacon depois do próximo
                direction_instruction = self.get_direction_instruction(from_beacon.id, to_beacon.id, next_beacon.id)
                if direction_instruction:
                    instruction = f"Siga em frente até o {to_beacon.name} e {direction_instruction}."
                else:
                    instruction = f"Siga em frente usando o piso tátil como apoio até {to_beacon.name}."
            else:
                instruction = f"Siga em frente usando o piso tátil como apoio até {to_beacon.name}."
            
            instructions.append(instruction)

        return instructions

    # Fala as instruções geradas
    def speak_instructions(self, instructions):
        for instruction in instructions:
            print(instruction)  # Imprime a instrução no console
            self.engine.say(instruction)  # Converte a instrução em fala
            self.engine.runAndWait()  # Aguarda até que a fala seja concluída

    # Ouve o usuário para obter o nome do beacon através de comandos de voz
    def listen_for_beacon_name(self, prompt):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)  # Ajusta para o ruído ambiente
            print(prompt)
            self.engine.say(prompt)  # Solicita o nome do beacon ao usuário
            self.engine.runAndWait()
            audio = self.recognizer.listen(source)  # Escuta a resposta do usuário
            try:
                response = self.recognizer.recognize_google(audio, language='pt-BR')  # Reconhece a fala
                print(f"Reconhecido: {response}")
                self.engine.say(f"Você disse: {response}")
                self.engine.runAndWait()
                return response
            except sr.UnknownValueError:
                print("Desculpe, não entendi o que você disse. Por favor, tente novamente.")
                self.engine.say("Desculpe, não entendi o que você disse. Por favor, tente novamente.")
                self.engine.runAndWait()
                return self.listen_for_beacon_name(prompt)  # Tenta novamente em caso de erro
            except sr.RequestError as e:
                print(f"Erro ao se comunicar com o serviço de reconhecimento de fala: {e}")
                self.engine.say(f"Erro ao se comunicar com o serviço de reconhecimento de fala: {e}")
                self.engine.runAndWait()
                return None

    # Converte o nome do beacon para seu respectivo ID
    def get_beacon_id_by_name(self, name):
        for beacon in self.beacons.values():
            if beacon.name.lower() == name.lower():
                return beacon.id
        return None

# Configuração do grafo com os beacons e suas posições
beacons = [
    Beacon(1, "Sala 1", (0, 0)),
    Beacon(2, "Sala 2", (1, 0)),
    Beacon(3, "Secretaria 3", (2, 0)),
    Beacon(4, "Escada 4", (3, 0)),
    Beacon(5, "Sala 5", (2, 1)),
    Beacon(6, "Banheiro 6", (2, 2)),
    Beacon(7, "Sala 7", (3, 2)),
    Beacon(8, "Sala 8", (4, 2)),
    Beacon(9, "Laboratório de pesquisa 9", (5, 2)),
    Beacon(10, "Laboratório de computação 10", (6, 2)),
    Beacon(11, "Laboratório de computação 11", (6, 3)),
    Beacon(12, "Sala 12", (6, 1)),
    Beacon(13, "Sala 13", (7, 1)),
    Beacon(14, "Rampa 14", (7, 3)),
    Beacon(15, "Laboratório de computação 15", (7, 4)),
    Beacon(16, "Banheiro 16", (8, 4))
]

# Cria uma instância da classe IndoorNavigation
navigator = IndoorNavigation()

# Adiciona os beacons ao grafo
for beacon in beacons:
    navigator.add_beacon(beacon)

# Define as arestas do grafo com suas respectivas distâncias
edges = [
    (1, 2, 300),
    (2, 3, 300),
    (3, 4, 300),
    (3, 5, 300),
    (5, 6, 300),
    (6, 7, 300),
    (7, 8, 300),
    (8, 9, 300),
    (9, 10, 300),
    (10, 11, 300),
    (10, 12, 300),
    (12, 13, 300),
    (12, 11, 300),
    (11, 14, 300),
    (11, 15, 300),
    (15, 16, 300)
]

# Adiciona as arestas ao grafo
for edge in edges:
    navigator.add_path(*edge)

# Interação com o usuário para escolher o ponto de partida e destino por voz
start_name = navigator.listen_for_beacon_name("Diga o nome do local de partida:")
end_name = navigator.listen_for_beacon_name("Diga o nome do local de destino:")

# Converte os nomes dos locais para seus respectivos IDs
start_id = navigator.get_beacon_id_by_name(start_name)
end_id = navigator.get_beacon_id_by_name(end_name)

# Simulação da navegação do ponto de partida ao ponto de destino
if start_id is not None and end_id is not None:
    instructions = navigator.simulate_navigation(start_id, end_id)
    navigator.speak_instructions(instructions)
else:
    print("Não foi possível obter os IDs dos Beacons corretamente.")
    navigator.engine.say("Não foi possível obter os IDs dos Beacons corretamente.")
    navigator.engine.runAndWait()

#Melhorias
#1. colocar o nome das salas ao invés de números (X)
#2. pensar melhor sobre comunição com beacons ()
#3. pensar melhoria de banheiros por exemplo ()
#4. pensar na comunicação das instruções (distâncias, pontos de referência, etc.) (X)
#5. criar o grafo por completo (X)
#6. corrigir a direção (X)