"""
Módulo que define a classe Recurso para o jogo "O Mundo dos Senciantes".
O Recurso representa os recursos disponíveis no mundo que os Senciantes podem utilizar.
"""

from utils.helpers import gerar_id

class Recurso:
    """
    Classe que representa um recurso no mundo.
    Os recursos podem ser coletados e utilizados pelos Senciantes.
    """
    
    def __init__(self, tipo, posicao, quantidade, renovavel=False, taxa_renovacao=0.0):
        """
        Inicializa um novo Recurso.
        
        Args:
            tipo (str): Tipo do recurso (comida, água, madeira, etc.).
            posicao (list): Posição do recurso no mundo [x, y].
            quantidade (float): Quantidade disponível do recurso.
            renovavel (bool, optional): Se o recurso é renovável. Default é False.
            taxa_renovacao (float, optional): Taxa de renovação por hora. Default é 0.0.
        """
        self.id = gerar_id()
        self.tipo = tipo
        self.posicao = posicao
        self.quantidade = quantidade
        self.renovavel = renovavel
        self.taxa_renovacao = taxa_renovacao
        self.quantidade_maxima = quantidade
    
    def atualizar(self, delta_tempo, clima):
        """
        Atualiza o estado do recurso com base no tempo decorrido e no clima.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            clima (Clima): Objeto clima atual do mundo.
        """
        if self.renovavel and self.quantidade < self.quantidade_maxima:
            # Calcular taxa de renovação baseada no clima
            taxa_efetiva = self.taxa_renovacao
            
            # Ajustar baseado na temperatura
            if self.tipo == "comida" or self.tipo == "fruta":
                if clima.temperatura < 5 or clima.temperatura > 35:
                    taxa_efetiva *= 0.2  # Crescimento reduzido em temperaturas extremas
                elif clima.temperatura > 15 and clima.temperatura < 25:
                    taxa_efetiva *= 1.5  # Crescimento aumentado em temperaturas ideais
            
            # Ajustar baseado na precipitação
            if self.tipo == "agua":
                taxa_efetiva *= (1 + clima.precipitacao * 2)  # Mais chuva = mais água
            elif self.tipo == "comida" or self.tipo == "fruta":
                if clima.precipitacao < 0.2:
                    taxa_efetiva *= 0.5  # Crescimento reduzido em seca
                elif clima.precipitacao > 0.8:
                    taxa_efetiva *= 0.7  # Crescimento reduzido em chuva excessiva
                else:
                    taxa_efetiva *= (1 + clima.precipitacao)  # Crescimento ideal com chuva moderada
            
            # Ajustar baseado no ciclo dia/noite
            if self.tipo == "comida" or self.tipo == "fruta":
                # Plantas crescem mais durante o dia
                if 6 <= clima.ciclo_dia_noite < 18:
                    taxa_efetiva *= 1.5
                else:
                    taxa_efetiva *= 0.5
            
            # Renovar recurso
            self.quantidade = min(
                self.quantidade_maxima,
                self.quantidade + taxa_efetiva * delta_tempo
            )
    
    def coletar(self, quantidade):
        """
        Coleta uma quantidade do recurso.
        
        Args:
            quantidade (float): Quantidade a ser coletada.
            
        Returns:
            float: Quantidade efetivamente coletada.
        """
        # Limitar à quantidade disponível
        quantidade_coletada = min(self.quantidade, quantidade)
        
        # Reduzir a quantidade disponível
        self.quantidade -= quantidade_coletada
        
        return quantidade_coletada
    
    def esta_esgotado(self):
        """
        Verifica se o recurso está esgotado.
        
        Returns:
            bool: True se o recurso está esgotado, False caso contrário.
        """
        return self.quantidade <= 0
    
    def to_dict(self):
        """
        Converte o recurso para um dicionário.
        
        Returns:
            dict: Representação do recurso como dicionário.
        """
        return {
            "id": self.id,
            "tipo": self.tipo,
            "posicao": self.posicao,
            "quantidade": self.quantidade,
            "renovavel": self.renovavel,
            "taxa_renovacao": self.taxa_renovacao,
            "quantidade_maxima": self.quantidade_maxima
        }


