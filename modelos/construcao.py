"""
Módulo que define a classe Construcao para o jogo "O Mundo dos Senciantes".
A Construcao representa estruturas construídas pelos Senciantes no mundo.
"""

from utils.helpers import gerar_id
from utils.config import CONSTRUCTION_TYPES

class Construcao:
    """
    Classe que representa uma construção no mundo.
    As construções são estruturas criadas pelos Senciantes.
    """
    
    def __init__(self, tipo, posicao, tamanho, proprietario_id=None):
        """
        Inicializa uma nova Construção.
        
        Args:
            tipo (str): Tipo da construção (abrigo, ferramenta, etc.).
            posicao (list): Posição da construção no mundo [x, y].
            tamanho (float): Tamanho da construção.
            proprietario_id (str, optional): ID do Senciante proprietário. Default é None.
        """
        self.id = gerar_id()
        self.tipo = tipo
        self.posicao = posicao
        self.tamanho = tamanho
        self.proprietario_id = proprietario_id
        self.ocupantes = []  # Lista de IDs de Senciantes ocupando a construção
        self.durabilidade = self._obter_durabilidade_inicial()
        self.durabilidade_maxima = self.durabilidade
        self.recursos_armazenados = {}  # Dicionário de recursos armazenados na construção
        self.funcionalidades = self._obter_funcionalidades()
    
    def _obter_durabilidade_inicial(self):
        """
        Obtém a durabilidade inicial da construção com base no tipo.
        
        Returns:
            float: Durabilidade inicial em horas.
        """
        for tipo_construcao in CONSTRUCTION_TYPES:
            if tipo_construcao["tipo"] == self.tipo:
                return tipo_construcao["durabilidade"]
        
        # Valor padrão se o tipo não for encontrado
        return 24.0
    
    def _obter_funcionalidades(self):
        """
        Obtém as funcionalidades da construção com base no tipo.
        
        Returns:
            dict: Dicionário de funcionalidades.
        """
        funcionalidades = {}
        
        if self.tipo.startswith("abrigo"):
            funcionalidades["protecao_clima"] = True
            funcionalidades["descanso"] = True
            
            if self.tipo == "abrigo_medio" or self.tipo == "abrigo_avancado":
                funcionalidades["armazenamento"] = True
            
            if self.tipo == "abrigo_avancado":
                funcionalidades["protecao_predadores"] = True
        
        elif self.tipo.startswith("ferramenta"):
            funcionalidades["eficiencia_coleta"] = 1.5  # 50% mais eficiente na coleta
            
            if self.tipo == "ferramenta_avancada":
                funcionalidades["eficiencia_construcao"] = 1.5  # 50% mais eficiente na construção
                funcionalidades["defesa"] = True
        
        return funcionalidades
    
    def atualizar(self, delta_tempo, clima):
        """
        Atualiza o estado da construção com base no tempo decorrido e no clima.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            clima (Clima): Objeto clima atual do mundo.
            
        Returns:
            bool: True se a construção ainda existe, False se foi destruída.
        """
        # Reduzir durabilidade com base no tempo e clima
        degradacao = delta_tempo * 0.01  # Degradação base
        
        # Aumentar degradação em condições climáticas adversas
        for evento in clima.eventos_climaticos:
            if evento["tipo"] in ["tempestade", "nevasca"]:
                degradacao *= (1 + evento["intensidade"])
        
        # Reduzir durabilidade
        self.durabilidade -= degradacao
        
        # Verificar se a construção foi destruída
        return self.durabilidade > 0
    
    def reparar(self, quantidade):
        """
        Repara a construção, aumentando sua durabilidade.
        
        Args:
            quantidade (float): Quantidade de durabilidade a ser restaurada.
            
        Returns:
            float: Quantidade efetivamente restaurada.
        """
        # Limitar à durabilidade máxima
        quantidade_reparada = min(
            self.durabilidade_maxima - self.durabilidade,
            quantidade
        )
        
        # Aumentar a durabilidade
        self.durabilidade += quantidade_reparada
        
        return quantidade_reparada
    
    def adicionar_ocupante(self, senciante_id):
        """
        Adiciona um Senciante como ocupante da construção.
        
        Args:
            senciante_id (str): ID do Senciante a ser adicionado.
            
        Returns:
            bool: True se o Senciante foi adicionado, False se já estava presente.
        """
        if senciante_id not in self.ocupantes:
            self.ocupantes.append(senciante_id)
            return True
        return False
    
    def remover_ocupante(self, senciante_id):
        """
        Remove um Senciante da lista de ocupantes da construção.
        
        Args:
            senciante_id (str): ID do Senciante a ser removido.
            
        Returns:
            bool: True se o Senciante foi removido, False se não estava presente.
        """
        if senciante_id in self.ocupantes:
            self.ocupantes.remove(senciante_id)
            return True
        return False
    
    def armazenar_recurso(self, tipo_recurso, quantidade):
        """
        Armazena um recurso na construção.
        
        Args:
            tipo_recurso (str): Tipo do recurso a ser armazenado.
            quantidade (float): Quantidade a ser armazenada.
            
        Returns:
            bool: True se o recurso foi armazenado, False se a construção não suporta armazenamento.
        """
        if "armazenamento" in self.funcionalidades:
            if tipo_recurso in self.recursos_armazenados:
                self.recursos_armazenados[tipo_recurso] += quantidade
            else:
                self.recursos_armazenados[tipo_recurso] = quantidade
            return True
        return False
    
    def retirar_recurso(self, tipo_recurso, quantidade):
        """
        Retira um recurso armazenado na construção.
        
        Args:
            tipo_recurso (str): Tipo do recurso a ser retirado.
            quantidade (float): Quantidade a ser retirada.
            
        Returns:
            float: Quantidade efetivamente retirada.
        """
        if tipo_recurso in self.recursos_armazenados:
            # Limitar à quantidade disponível
            quantidade_retirada = min(
                self.recursos_armazenados[tipo_recurso],
                quantidade
            )
            
            # Reduzir a quantidade armazenada
            self.recursos_armazenados[tipo_recurso] -= quantidade_retirada
            
            # Remover o tipo de recurso se a quantidade for zero
            if self.recursos_armazenados[tipo_recurso] <= 0:
                del self.recursos_armazenados[tipo_recurso]
            
            return quantidade_retirada
        
        return 0.0
    
    def obter_protecao_clima(self):
        """
        Obtém o nível de proteção contra o clima oferecido pela construção.
        
        Returns:
            float: Nível de proteção (0.0 a 1.0).
        """
        if "protecao_clima" in self.funcionalidades:
            # Ajustar proteção com base na durabilidade
            return (self.durabilidade / self.durabilidade_maxima) * 0.8
        return 0.0
    
    def to_dict(self):
        """
        Converte a construção para um dicionário.
        
        Returns:
            dict: Representação da construção como dicionário.
        """
        return {
            "id": self.id,
            "tipo": self.tipo,
            "posicao": self.posicao,
            "tamanho": self.tamanho,
            "proprietario_id": self.proprietario_id,
            "ocupantes": self.ocupantes,
            "durabilidade": self.durabilidade,
            "durabilidade_maxima": self.durabilidade_maxima,
            "recursos_armazenados": self.recursos_armazenados,
            "funcionalidades": list(self.funcionalidades.keys())
        }


