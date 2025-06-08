"""
Módulo que define a classe Memoria para o jogo "O Mundo dos Senciantes".
A Memoria representa as experiências e conhecimentos adquiridos por um Senciante.
"""

from utils.helpers import gerar_id
from utils.config import MEMORY_DECAY_RATE, MEMORY_THRESHOLD

class Memoria:
    """
    Classe que representa uma memória de um Senciante.
    Contém informações sobre eventos, experiências e conhecimentos adquiridos.
    """
    
    def __init__(self, tipo, conteudo, tempo, importancia=0.5):
        """
        Inicializa uma nova Memória.
        
        Args:
            tipo (str): Tipo da memória (evento, aprendizado, social, etc.).
            conteudo (str): Conteúdo da memória.
            tempo (float): Tempo da simulação em que a memória foi criada.
            importancia (float, optional): Importância da memória (0.0 a 1.0). Default é 0.5.
        """
        self.id = gerar_id()
        self.tipo = tipo
        self.conteudo = conteudo
        self.tempo = tempo
        self.importancia = importancia
        self.conexoes = []  # IDs de outras memórias relacionadas
    
    def envelhecer(self, delta_tempo):
        """
        Envelhece a memória, reduzindo sua importância com o tempo.
        Memórias muito importantes (>= 0.8) não perdem importância.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização.
            
        Returns:
            bool: True se a memória ainda é relevante, False se deve ser esquecida.
        """
        # Memórias muito importantes não perdem importância
        if self.importancia < 0.8:
            # Reduzir importância com base no tempo decorrido
            self.importancia *= (1 - MEMORY_DECAY_RATE * delta_tempo)
        
        # Retorna False se a memória deve ser esquecida
        return self.importancia > MEMORY_THRESHOLD
    
    def adicionar_conexao(self, memoria_id):
        """
        Adiciona uma conexão com outra memória.
        
        Args:
            memoria_id (str): ID da memória a ser conectada.
        """
        if memoria_id not in self.conexoes:
            self.conexoes.append(memoria_id)
    
    def aumentar_importancia(self, valor=0.1):
        """
        Aumenta a importância da memória.
        
        Args:
            valor (float, optional): Valor a ser adicionado à importância. Default é 0.1.
        """
        self.importancia = min(1.0, self.importancia + valor)
    
    def diminuir_importancia(self, valor=0.1):
        """
        Diminui a importância da memória.
        
        Args:
            valor (float, optional): Valor a ser subtraído da importância. Default é 0.1.
        """
        self.importancia = max(0.0, self.importancia - valor)
    
    def to_dict(self):
        """
        Converte a memória para um dicionário.
        
        Returns:
            dict: Representação da memória como dicionário.
        """
        return {
            "id": self.id,
            "tipo": self.tipo,
            "conteudo": self.conteudo,
            "tempo": self.tempo,
            "importancia": self.importancia,
            "conexoes": self.conexoes
        }

