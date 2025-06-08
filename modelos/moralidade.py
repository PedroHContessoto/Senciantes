"""
Módulo que define a classe Moralidade para o jogo "O Mundo dos Senciantes".
A Moralidade representa os valores morais e éticos de um Senciante.
"""

import random
from utils.helpers import chance

class Moralidade:
    """
    Classe que representa a moralidade de um Senciante.
    Contém valores morais, princípios éticos e crenças.
    """
    
    def __init__(self, predisposicoes=None):
        """
        Inicializa uma nova Moralidade.
        
        Args:
            predisposicoes (dict, optional): Predisposições morais iniciais. Se None, gera aleatoriamente.
        """
        # Valores morais (0.0 a 1.0, onde 1.0 é forte adesão ao valor)
        self.valores = predisposicoes if predisposicoes else self._gerar_valores_aleatorios()
        
        # Experiências que formaram os valores morais
        self.experiencias = {
            "lealdade": [],
            "justica": [],
            "cuidado": [],
            "liberdade": [],
            "autoridade": [],
            "pureza": []
        }
        
        # Princípios éticos derivados dos valores
        self.principios = {}
        
        # Dilemas morais enfrentados e resolvidos
        self.dilemas_resolvidos = []
    
    def _gerar_valores_aleatorios(self):
        """
        Gera valores morais aleatórios.
        
        Returns:
            dict: Dicionário de valores morais com valores aleatórios.
        """
        return {
            "lealdade": random.uniform(0.3, 0.7),     # Lealdade ao grupo vs. individualismo
            "justica": random.uniform(0.3, 0.7),      # Justiça e equidade
            "cuidado": random.uniform(0.3, 0.7),      # Cuidado e proteção dos outros
            "liberdade": random.uniform(0.3, 0.7),    # Liberdade e autonomia
            "autoridade": random.uniform(0.3, 0.7),   # Respeito à autoridade e tradição
            "pureza": random.uniform(0.3, 0.7)        # Pureza e santidade
        }
    
    def registrar_experiencia(self, valor, descricao, impacto):
        """
        Registra uma experiência que afeta um valor moral.
        
        Args:
            valor (str): O valor moral afetado.
            descricao (str): Descrição da experiência.
            impacto (float): Impacto da experiência no valor (-1.0 a 1.0).
        """
        if valor in self.valores:
            # Registrar a experiência
            self.experiencias[valor].append({
                "descricao": descricao,
                "impacto": impacto
            })
            
            # Atualizar o valor moral
            self.valores[valor] += impacto * 0.1
            
            # Limitar o valor entre 0.0 e 1.0
            self.valores[valor] = max(0.0, min(1.0, self.valores[valor]))
            
            # Possivelmente formar um novo princípio ético
            self._formar_principio(valor)
    
    def _formar_principio(self, valor):
        """
        Possivelmente forma um novo princípio ético baseado em um valor moral.
        
        Args:
            valor (str): O valor moral que pode gerar um princípio.
        """
        # Verificar se o valor é forte o suficiente para formar um princípio
        if self.valores[valor] >= 0.7 and len(self.experiencias[valor]) >= 3:
            # Chance de formar um princípio baseado no valor
            if chance(0.3) and valor not in self.principios:
                if valor == "lealdade":
                    self.principios[valor] = "Nunca trair aqueles que confiam em mim"
                elif valor == "justica":
                    self.principios[valor] = "Tratar todos com igualdade e equidade"
                elif valor == "cuidado":
                    self.principios[valor] = "Proteger os mais vulneráveis"
                elif valor == "liberdade":
                    self.principios[valor] = "Respeitar a autonomia de cada indivíduo"
                elif valor == "autoridade":
                    self.principios[valor] = "Respeitar a hierarquia e a tradição"
                elif valor == "pureza":
                    self.principios[valor] = "Manter-se livre de contaminação física e espiritual"
    
    def resolver_dilema(self, dilema, escolha, consequencia):
        """
        Registra a resolução de um dilema moral.
        
        Args:
            dilema (str): Descrição do dilema moral.
            escolha (str): A escolha feita pelo Senciante.
            consequencia (str): A consequência da escolha.
        """
        self.dilemas_resolvidos.append({
            "dilema": dilema,
            "escolha": escolha,
            "consequencia": consequencia
        })
    
    def avaliar_acao(self, acao, contexto):
        """
        Avalia uma ação com base nos valores morais e princípios éticos.
        
        Args:
            acao (str): A ação a ser avaliada.
            contexto (dict): Contexto da ação.
            
        Returns:
            float: Avaliação da ação (-1.0 a 1.0, onde 1.0 é totalmente aprovada).
        """
        avaliacao = 0.0
        
        # Avaliar com base nos valores morais
        if "lealdade" in contexto:
            avaliacao += self.valores["lealdade"] * contexto["lealdade"]
        
        if "justica" in contexto:
            avaliacao += self.valores["justica"] * contexto["justica"]
        
        if "cuidado" in contexto:
            avaliacao += self.valores["cuidado"] * contexto["cuidado"]
        
        if "liberdade" in contexto:
            avaliacao += self.valores["liberdade"] * contexto["liberdade"]
        
        if "autoridade" in contexto:
            avaliacao += self.valores["autoridade"] * contexto["autoridade"]
        
        if "pureza" in contexto:
            avaliacao += self.valores["pureza"] * contexto["pureza"]
        
        # Normalizar a avaliação
        if len(contexto) > 0:
            avaliacao /= len(contexto)
        
        return avaliacao
    
    def compatibilidade_moral(self, outra_moralidade):
        """
        Calcula a compatibilidade moral com outro Senciante.
        
        Args:
            outra_moralidade (Moralidade): A moralidade do outro Senciante.
            
        Returns:
            float: Compatibilidade moral (0.0 a 1.0, onde 1.0 é totalmente compatível).
        """
        diferenca_total = 0.0
        
        for valor in self.valores:
            diferenca = abs(self.valores[valor] - outra_moralidade.valores[valor])
            diferenca_total += diferenca
        
        # Calcular compatibilidade (inverso da diferença média)
        compatibilidade = 1.0 - (diferenca_total / len(self.valores))
        
        return max(0.0, compatibilidade)
    
    def gerar_filosofia(self):
        """
        Gera um conceito filosófico baseado nos valores morais e experiências.
        
        Returns:
            str: Conceito filosófico.
        """
        # Encontrar o valor moral mais forte
        valor_mais_forte = max(self.valores, key=self.valores.get)
        
        # Gerar filosofia baseada no valor mais forte
        if valor_mais_forte == "lealdade":
            return "A verdadeira força vem da união e lealdade mútua"
        elif valor_mais_forte == "justica":
            return "A sociedade justa trata cada indivíduo de acordo com suas necessidades"
        elif valor_mais_forte == "cuidado":
            return "O cuidado com os outros é a base de uma vida significativa"
        elif valor_mais_forte == "liberdade":
            return "A liberdade de escolha é o fundamento da existência consciente"
        elif valor_mais_forte == "autoridade":
            return "A ordem e a hierarquia são necessárias para a harmonia social"
        elif valor_mais_forte == "pureza":
            return "A purificação do corpo e da mente leva à elevação espiritual"
    
    def to_dict(self):
        """
        Converte a moralidade para um dicionário.
        
        Returns:
            dict: Representação da moralidade como dicionário.
        """
        return {
            "valores": self.valores,
            "principios": self.principios,
            "dilemas_resolvidos": len(self.dilemas_resolvidos)
        }

