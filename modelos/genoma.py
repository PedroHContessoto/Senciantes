"""
Módulo que define a classe Genoma para o jogo "O Mundo dos Senciantes".
O Genoma representa as características genéticas de um Senciante.
"""

import random
from utils.config import GENE_MUTATION_RATE, GENE_MUTATION_RANGE, GENE_INHERITANCE_RATE
from utils.helpers import chance

class Genoma:
    """
    Classe que representa o genoma de um Senciante.
    Contém genes que determinam características físicas e comportamentais.
    """
    
    def __init__(self, genes=None, mutacoes=None):
        """
        Inicializa um novo Genoma.
        
        Args:
            genes (dict, optional): Dicionário de genes. Se None, gera genes aleatórios.
            mutacoes (list, optional): Lista de mutações. Se None, inicializa uma lista vazia.
        """
        self.genes = genes if genes else self._gerar_genes_aleatorios()
        self.mutacoes = mutacoes if mutacoes else []
    
    def _gerar_genes_aleatorios(self):
        """
        Gera um conjunto de genes aleatórios para um novo Senciante.
        
        Returns:
            dict: Dicionário de genes com valores aleatórios.
        """
        return {
            "tamanho": random.uniform(0.8, 1.2),        # Tamanho físico
            "velocidade": random.uniform(0.8, 1.2),     # Velocidade de movimento
            "inteligencia": random.uniform(0.8, 1.2),   # Capacidade de aprendizado
            "resistencia": random.uniform(0.8, 1.2),    # Resistência a doenças e condições adversas
            "social": random.uniform(0.8, 1.2),         # Aptidão social
            "forca": random.uniform(0.8, 1.2),          # Força física
            "percepcao": random.uniform(0.8, 1.2),      # Capacidade de percepção do ambiente
            "adaptabilidade": random.uniform(0.8, 1.2)  # Capacidade de adaptação a mudanças
        }
    
    def combinar(self, outro_genoma):
        """
        Combina este genoma com outro para criar um novo genoma (reprodução).
        
        Args:
            outro_genoma (Genoma): Outro genoma para combinar.
            
        Returns:
            Genoma: Novo genoma resultante da combinação.
        """
        # Combinar genes
        novo_genes = {}
        for gene, valor in self.genes.items():
            # 50% de chance de herdar de cada pai
            if chance(GENE_INHERITANCE_RATE):
                novo_genes[gene] = valor
            else:
                novo_genes[gene] = outro_genoma.genes[gene]
            
            # Pequena chance de mutação
            if chance(GENE_MUTATION_RATE):
                novo_genes[gene] *= random.uniform(
                    GENE_MUTATION_RANGE[0], 
                    GENE_MUTATION_RANGE[1]
                )
        
        # Herdar mutações
        novas_mutacoes = list(set(self.mutacoes + outro_genoma.mutacoes))
        
        # Chance de nova mutação
        if chance(GENE_MUTATION_RATE):
            novas_mutacoes.append(self._gerar_mutacao_aleatoria())
        
        return Genoma(novo_genes, novas_mutacoes)
    
    def _gerar_mutacao_aleatoria(self):
        """
        Gera uma mutação aleatória.
        
        Returns:
            str: Nome da mutação gerada.
        """
        mutacoes_possiveis = [
            "gene_comunicacao_avancada",
            "gene_metabolismo_eficiente",
            "gene_visao_noturna",
            "gene_resistencia_frio",
            "gene_resistencia_calor",
            "gene_longevidade",
            "gene_memoria_aprimorada",
            "gene_imunidade_doencas",
            "gene_forca_aumentada",
            "gene_velocidade_aumentada"
        ]
        
        return random.choice(mutacoes_possiveis)
    
    def aplicar_efeitos_mutacoes(self):
        """
        Aplica os efeitos das mutações aos genes.
        
        Returns:
            dict: Dicionário de modificadores a serem aplicados ao Senciante.
        """
        modificadores = {
            "metabolismo": 1.0,
            "percepcao_noturna": 1.0,
            "resistencia_temperatura": 1.0,
            "longevidade": 1.0,
            "capacidade_memoria": 1.0,
            "imunidade": 1.0
        }
        
        for mutacao in self.mutacoes:
            if mutacao == "gene_comunicacao_avancada":
                self.genes["social"] = min(2.0, self.genes["social"] * 1.2)
            elif mutacao == "gene_metabolismo_eficiente":
                modificadores["metabolismo"] = 0.8  # Consome 20% menos recursos
            elif mutacao == "gene_visao_noturna":
                modificadores["percepcao_noturna"] = 2.0  # 2x melhor visão noturna
            elif mutacao == "gene_resistencia_frio":
                modificadores["resistencia_temperatura"] = 1.5  # 50% mais resistente ao frio
            elif mutacao == "gene_resistencia_calor":
                modificadores["resistencia_temperatura"] = 1.5  # 50% mais resistente ao calor
            elif mutacao == "gene_longevidade":
                modificadores["longevidade"] = 1.3  # 30% mais tempo de vida
            elif mutacao == "gene_memoria_aprimorada":
                modificadores["capacidade_memoria"] = 1.5  # 50% mais capacidade de memória
            elif mutacao == "gene_imunidade_doencas":
                modificadores["imunidade"] = 2.0  # 2x mais resistente a doenças
            elif mutacao == "gene_forca_aumentada":
                self.genes["forca"] = min(2.0, self.genes["forca"] * 1.3)
            elif mutacao == "gene_velocidade_aumentada":
                self.genes["velocidade"] = min(2.0, self.genes["velocidade"] * 1.3)
        
        return modificadores
    
    def to_dict(self):
        """
        Converte o genoma para um dicionário.
        
        Returns:
            dict: Representação do genoma como dicionário.
        """
        return {
            "genes": self.genes,
            "mutacoes": self.mutacoes
        }



