from modelos.clima import Clima
from modelos.recurso import Recurso
from modelos.construcao import Construcao
from modelos.historico import Historico
import numpy as np
import random

class Mundo:
    """
    Classe que representa o ambiente do jogo.
    Contém informações sobre o terreno, recursos, construções e histórico.
    """
    
    def __init__(self, tamanho=(100, 100)):
        """
        Inicializa o mundo.
        
        Args:
            tamanho (tuple): Dimensões do mundo (largura, altura).
        """
        self.tamanho = tuple(tamanho) # Garante que tamanho seja uma tupla
        self.geografia = self._gerar_geografia()  # Elevação, biomas, etc.
        self.recursos = {}  # Dicionário de id: Recurso
        self.construcoes = {}  # Dicionário de id: Construcao
        self.clima = Clima()  # Objeto de clima
        self.historico = Historico()  # Objeto de histórico
        
        # Inicializar recursos
        self._inicializar_recursos()
        
    def inicializar(self, tamanho):
        """
        Inicializa o mundo com um novo tamanho.
        
        Args:
            tamanho (list): Dimensões do mundo [largura, altura].
        """
        self.tamanho = tuple(tamanho)
        self.geografia = self._gerar_geografia()
        self.recursos = {}
        self.construcoes = {}
        self.clima = Clima()
        self.historico = Historico()
        self._inicializar_recursos()

    def _gerar_geografia(self):
        """
        Gera a geografia do mundo (elevação, biomas).
        
        Returns:
            dict: Dicionário com dados geográficos.
        """
        # Exemplo simples: elevação aleatória
        elevacao = np.random.rand(self.tamanho[0], self.tamanho[1])
        
        # Exemplo simples: biomas
        biomas = np.full(self.tamanho, "planicie")
        
        return {"elevacao": elevacao, "biomas": biomas}
    
    def _inicializar_recursos(self):
        """
        Inicializa recursos no mundo.
        """
        # Exemplo: adicionar alguns recursos aleatórios
        for _ in range(20):
            tipo = random.choice(["comida", "agua", "madeira", "pedra"])
            posicao = (random.randint(0, self.tamanho[0]-1), random.randint(0, self.tamanho[1]-1))
            quantidade = random.randint(10, 50)
            recurso = Recurso(tipo, posicao, quantidade)
            self.recursos[recurso.id] = recurso
            
    def atualizar(self, delta_tempo):
        """
        Atualiza o estado do mundo.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        self.clima.atualizar(delta_tempo)
        # Outras atualizações do mundo (ex: crescimento de recursos)

    def encontrar_construcoes_proximas(self, posicao, raio, tipo=None):
        """
        Encontra construções próximas a uma posição.

        Args:
            posicao (tuple): Posição (x, y).
            raio (float): Raio de busca.
            tipo (str, optional): Tipo de construção a buscar. Se None, busca todas.

        Returns:
            list: Lista de construções encontradas.
        """
        construcoes_encontradas = []
        for construcao_id, construcao in self.construcoes.items():
            distancia = ((posicao[0] - construcao.posicao[0]) ** 2 + (posicao[1] - construcao.posicao[1]) ** 2) ** 0.5
            if distancia <= raio:
                if tipo is None or construcao.tipo == tipo:
                    construcoes_encontradas.append(construcao)
        return construcoes_encontradas
        
    def encontrar_recursos_proximos(self, posicao, raio, tipo=None):
        """
        Encontra recursos próximos a uma posição.
        
        Args:
            posicao (tuple): Posição (x, y).
            raio (float): Raio de busca.
            tipo (str, optional): Tipo de recurso a buscar. Se None, busca todos.
            
        Returns:
            list: Lista de recursos encontrados.
        """
        recursos_encontrados = []
        for recurso_id, recurso in self.recursos.items():
            distancia = ((posicao[0] - recurso.posicao[0])**2 + (posicao[1] - recurso.posicao[1])**2)**0.5
            if distancia <= raio:
                if tipo is None or recurso.tipo == tipo:
                    recursos_encontrados.append(recurso)
        return recursos_encontrados

    def adicionar_construcao(self, construcao):
        """
        Adiciona uma construção ao mundo.
        
        Args:
            construcao (Construcao): Objeto Construcao a ser adicionado.
        """
        self.construcoes[construcao.id] = construcao

    def remover_construcao(self, construcao_id):
        """
        Remove uma construção do mundo.
        
        Args:
            construcao_id (str): ID da construção a ser removida.
        """
        if construcao_id in self.construcoes:
            del self.construcoes[construcao_id]

    def to_dict(self):
        """
        Converte o objeto Mundo para um dicionário.
        
        Returns:
            dict: Dicionário representando o Mundo.
        """
        return {
            "tamanho": self.tamanho,
            "geografia": {
                "elevacao": self.geografia["elevacao"].tolist(),
                "biomas": self.geografia["biomas"].tolist()
            },
            "recursos": {id: rec.to_dict() for id, rec in self.recursos.items()},
            "construcoes": {id: constr.to_dict() for id, constr in self.construcoes.items()},
            "clima": self.clima.to_dict(),
            "historico": self.historico.to_dict()
        }


