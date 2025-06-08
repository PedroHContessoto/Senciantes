"""
Módulo que define a classe Flora para o jogo "O Mundo dos Senciantes".
A Flora representa plantas que habitam o ecossistema do mundo.
"""

import random
from utils.helpers import gerar_id, calcular_distancia, chance

class Flora:
    """
    Classe que representa uma planta no ecossistema.
    Contém características, crescimento e interações com Senciantes.
    """
    
    def __init__(self, especie=None, posicao=None, mundo=None):
        """
        Inicializa uma nova planta.
        
        Args:
            especie (str, optional): Espécie da planta. Se None, escolhe aleatoriamente.
            posicao (list, optional): Posição da planta [x, y]. Se None, escolhe aleatoriamente.
            mundo (Mundo, optional): Objeto mundo para referência.
        """
        self.id = gerar_id()
        self.especie = especie if especie else self._escolher_especie_aleatoria()
        self.posicao = posicao if posicao else [random.uniform(0, mundo.tamanho[0]), random.uniform(0, mundo.tamanho[1])] if mundo else [50, 50]
        
        # Características
        self.caracteristicas = self._definir_caracteristicas()
        self.idade = 0.0  # Idade em horas
        self.tamanho_atual = 0.1  # Tamanho atual (0.0 a 1.0)
        self.saude = 1.0  # Saúde (0.0 a 1.0)
        
        # Estado
        self.estado_crescimento = "crescimento"  # crescimento, maduro, decadência
        self.cultivada = False
        self.cultivador_id = None  # ID do Senciante cultivador, se cultivada
        
        # Propriedades especiais
        self.propriedades = self._definir_propriedades()
    
    def _escolher_especie_aleatoria(self):
        """
        Escolhe uma espécie aleatória para a planta.
        
        Returns:
            str: Espécie da planta.
        """
        especies = ["árvore_frutífera", "árvore_madeira", "arbusto_comestível", "erva_medicinal", "flor", "fungo", "planta_aquática", "cacto"]
        
        return random.choice(especies)
    
    def _definir_caracteristicas(self):
        """
        Define as características da planta com base na espécie.
        
        Returns:
            dict: Dicionário de características.
        """
        caracteristicas = {
            "tamanho_maximo": 0.0,  # 0.0 a 1.0
            "taxa_crescimento": 0.0,  # Por hora
            "valor_nutricional": 0.0,  # 0.0 a 1.0
            "valor_madeira": 0.0,  # 0.0 a 1.0
            "valor_medicinal": 0.0,  # 0.0 a 1.0
            "habitat_preferido": "",  # floresta, planície, montanha, água, deserto
            "expectativa_vida": 0.0,  # Em horas
            "taxa_reproducao": 0.0,  # 0.0 a 1.0
            "resistencia_clima": 0.0,  # 0.0 a 1.0
            "cultivabilidade": 0.0  # 0.0 a 1.0
        }
        
        # Definir características com base na espécie
        if self.especie == "árvore_frutífera":
            caracteristicas.update({
                "tamanho_maximo": random.uniform(0.7, 1.0),
                "taxa_crescimento": random.uniform(0.0001, 0.0003),
                "valor_nutricional": random.uniform(0.6, 0.9),
                "valor_madeira": random.uniform(0.4, 0.7),
                "valor_medicinal": random.uniform(0.1, 0.4),
                "habitat_preferido": random.choice(["floresta", "planície"]),
                "expectativa_vida": random.uniform(43800, 87600),  # 5-10 anos
                "taxa_reproducao": random.uniform(0.2, 0.4),
                "resistencia_clima": random.uniform(0.3, 0.6),
                "cultivabilidade": random.uniform(0.5, 0.8)
            })
        
        elif self.especie == "árvore_madeira":
            caracteristicas.update({
                "tamanho_maximo": random.uniform(0.8, 1.0),
                "taxa_crescimento": random.uniform(0.00005, 0.0002),
                "valor_nutricional": random.uniform(0.0, 0.2),
                "valor_madeira": random.uniform(0.7, 1.0),
                "valor_medicinal": random.uniform(0.1, 0.3),
                "habitat_preferido": random.choice(["floresta", "montanha"]),
                "expectativa_vida": random.uniform(87600, 175200),  # 10-20 anos
                "taxa_reproducao": random.uniform(0.1, 0.3),
                "resistencia_clima": random.uniform(0.5, 0.8),
                "cultivabilidade": random.uniform(0.3, 0.6)
            })
        
        elif self.especie == "arbusto_comestível":
            caracteristicas.update({
                "tamanho_maximo": random.uniform(0.3, 0.5),
                "taxa_crescimento": random.uniform(0.0003, 0.0006),
                "valor_nutricional": random.uniform(0.5, 0.8),
                "valor_madeira": random.uniform(0.1, 0.3),
                "valor_medicinal": random.uniform(0.2, 0.5),
                "habitat_preferido": random.choice(["floresta", "planície"]),
                "expectativa_vida": random.uniform(8760, 26280),  # 1-3 anos
                "taxa_reproducao": random.uniform(0.4, 0.7),
                "resistencia_clima": random.uniform(0.3, 0.6),
                "cultivabilidade": random.uniform(0.6, 0.9)
            })
        
        elif self.especie == "erva_medicinal":
            caracteristicas.update({
                "tamanho_maximo": random.uniform(0.1, 0.3),
                "taxa_crescimento": random.uniform(0.0005, 0.001),
                "valor_nutricional": random.uniform(0.2, 0.5),
                "valor_madeira": random.uniform(0.0, 0.1),
                "valor_medicinal": random.uniform(0.7, 1.0),
                "habitat_preferido": random.choice(["floresta", "planície", "montanha"]),
                "expectativa_vida": random.uniform(4380, 8760),  # 0.5-1 ano
                "taxa_reproducao": random.uniform(0.5, 0.8),
                "resistencia_clima": random.uniform(0.2, 0.5),
                "cultivabilidade": random.uniform(0.7, 1.0)
            })
        
        elif self.especie == "flor":
            caracteristicas.update({
                "tamanho_maximo": random.uniform(0.05, 0.2),
                "taxa_crescimento": random.uniform(0.001, 0.002),
                "valor_nutricional": random.uniform(0.1, 0.3),
                "valor_madeira": random.uniform(0.0, 0.1),
                "valor_medicinal": random.uniform(0.3, 0.7),
                "habitat_preferido": random.choice(["floresta", "planície"]),
                "expectativa_vida": random.uniform(720, 2160),  # 1-3 meses
                "taxa_reproducao": random.uniform(0.6, 0.9),
                "resistencia_clima": random.uniform(0.1, 0.4),
                "cultivabilidade": random.uniform(0.7, 1.0)
            })
        
        elif self.especie == "fungo":
            caracteristicas.update({
                "tamanho_maximo": random.uniform(0.05, 0.2),
                "taxa_crescimento": random.uniform(0.002, 0.005),
                "valor_nutricional": random.uniform(0.3, 0.6),
                "valor_madeira": random.uniform(0.0, 0.0),
                "valor_medicinal": random.uniform(0.4, 0.8),
                "habitat_preferido": "floresta",
                "expectativa_vida": random.uniform(168, 720),  # 1-4 semanas
                "taxa_reproducao": random.uniform(0.7, 1.0),
                "resistencia_clima": random.uniform(0.2, 0.5),
                "cultivabilidade": random.uniform(0.4, 0.7)
            })
        
        elif self.especie == "planta_aquática":
            caracteristicas.update({
                "tamanho_maximo": random.uniform(0.2, 0.6),
                "taxa_crescimento": random.uniform(0.0004, 0.0008),
                "valor_nutricional": random.uniform(0.3, 0.6),
                "valor_madeira": random.uniform(0.0, 0.2),
                "valor_medicinal": random.uniform(0.3, 0.6),
                "habitat_preferido": "água",
                "expectativa_vida": random.uniform(4380, 17520),  # 0.5-2 anos
                "taxa_reproducao": random.uniform(0.5, 0.8),
                "resistencia_clima": random.uniform(0.3, 0.6),
                "cultivabilidade": random.uniform(0.3, 0.6)
            })
        
        elif self.especie == "cacto":
            caracteristicas.update({
                "tamanho_maximo": random.uniform(0.3, 0.7),
                "taxa_crescimento": random.uniform(0.00008, 0.0002),
                "valor_nutricional": random.uniform(0.2, 0.4),
                "valor_madeira": random.uniform(0.1, 0.3),
                "valor_medicinal": random.uniform(0.3, 0.6),
                "habitat_preferido": "deserto",
                "expectativa_vida": random.uniform(26280, 43800),  # 3-5 anos
                "taxa_reproducao": random.uniform(0.2, 0.4),
                "resistencia_clima": random.uniform(0.7, 1.0),
                "cultivabilidade": random.uniform(0.2, 0.5)
            })
        
        return caracteristicas
    
    def _definir_propriedades(self):
        """
        Define propriedades especiais da planta com base na espécie.
        
        Returns:
            dict: Dicionário de propriedades especiais.
        """
        propriedades = {}
        
        # Propriedades comuns a todas as plantas
        propriedades["produz_oxigenio"] = True
        
        # Propriedades específicas por espécie
        if self.especie == "árvore_frutífera":
            propriedades["produz_frutos"] = True
            propriedades["ciclo_frutificacao"] = random.uniform(720, 2160)  # 1-3 meses
            propriedades["quantidade_frutos"] = lambda: random.uniform(1, 5) * self.tamanho_atual
        
        elif self.especie == "erva_medicinal":
            propriedades["efeito_medicinal"] = random.choice(["cura_doenca", "aumenta_saude", "reduz_estresse"])
            propriedades["potencia_medicinal"] = random.uniform(0.3, 0.8)
        
        elif self.especie == "fungo":
            # Alguns fungos são venenosos
            if chance(0.3):
                propriedades["venenoso"] = True
                propriedades["potencia_veneno"] = random.uniform(0.3, 0.8)
        
        return propriedades
    
    def atualizar(self, delta_tempo, mundo):
        """
        Atualiza o estado da planta.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            mundo (Mundo): Objeto mundo atual.
            
        Returns:
            bool: True se a planta ainda está viva, False se morreu.
        """
        # Atualizar idade
        self.idade += delta_tempo
        
        # Verificar morte por idade
        if self.idade > self.caracteristicas["expectativa_vida"]:
            return False
        
        # Verificar morte por saúde
        if self.saude <= 0.0:
            return False
        
        # Atualizar estado de crescimento
        if self.idade < self.caracteristicas["expectativa_vida"] * 0.2:
            self.estado_crescimento = "crescimento"
        elif self.idade < self.caracteristicas["expectativa_vida"] * 0.8:
            self.estado_crescimento = "maduro"
        else:
            self.estado_crescimento = "decadência"
        
        # Atualizar tamanho
        if self.estado_crescimento == "crescimento":
            # Crescimento rápido
            crescimento = self.caracteristicas["taxa_crescimento"] * delta_tempo
            
            # Ajustar com base no clima
            bioma = mundo.obter_bioma(self.posicao)
            if bioma == self.caracteristicas["habitat_preferido"]:
                crescimento *= 1.2
            
            # Ajustar com base na temperatura e precipitação
            temperatura_ideal = 0.5  # Normalizada (0.0 a 1.0)
            precipitacao_ideal = 0.5  # Normalizada (0.0 a 1.0)
            
            if self.caracteristicas["habitat_preferido"] == "deserto":
                temperatura_ideal = 0.8
                precipitacao_ideal = 0.2
            elif self.caracteristicas["habitat_preferido"] == "floresta":
                temperatura_ideal = 0.6
                precipitacao_ideal = 0.7
            
            # Simplificação: usar valores normalizados do clima
            temperatura_atual = (mundo.clima.temperatura - 0) / (40 - 0)  # Normalizar para 0.0 a 1.0
            precipitacao_atual = mundo.clima.precipitacao
            
            # Calcular fator de clima
            fator_temperatura = 1.0 - abs(temperatura_atual - temperatura_ideal) * (1.0 - self.caracteristicas["resistencia_clima"])
            fator_precipitacao = 1.0 - abs(precipitacao_atual - precipitacao_ideal) * (1.0 - self.caracteristicas["resistencia_clima"])
            
            fator_clima = (fator_temperatura + fator_precipitacao) / 2.0
            crescimento *= fator_clima
            
            # Se cultivada, crescimento mais rápido
            if self.cultivada:
                crescimento *= 1.5
            
            # Aplicar crescimento
            self.tamanho_atual = min(self.caracteristicas["tamanho_maximo"], self.tamanho_atual + crescimento)
        
        elif self.estado_crescimento == "decadência":
            # Redução lenta do tamanho
            self.tamanho_atual = max(0.0, self.tamanho_atual - 0.00001 * delta_tempo)
        
        # Verificar reprodução
        if self.estado_crescimento == "maduro" and self.tamanho_atual > self.caracteristicas["tamanho_maximo"] * 0.7:
            # Chance de reprodução baseada na taxa de reprodução e tempo decorrido
            chance_reproducao = self.caracteristicas["taxa_reproducao"] * delta_tempo * 0.01
            
            if chance(chance_reproducao):
                # Criar nova planta próxima
                return {"reproduzir": True}
        
        return True
    
    def coletar(self, quantidade):
        """
        Coleta recursos da planta.
        
        Args:
            quantidade (float): Quantidade a ser coletada (0.0 a 1.0).
            
        Returns:
            dict: Recursos coletados.
        """
        recursos = {}
        
        # Limitar quantidade ao tamanho atual
        quantidade_real = min(quantidade, self.tamanho_atual)
        
        # Reduzir tamanho
        self.tamanho_atual -= quantidade_real
        
        # Verificar se a planta morreu
        if self.tamanho_atual <= 0.1:
            self.saude = 0.0
        
        # Determinar recursos coletados com base na espécie
        if self.especie == "árvore_frutífera":
            recursos["fruta"] = quantidade_real * self.caracteristicas["valor_nutricional"]
            if quantidade_real > 0.5:
                recursos["madeira"] = quantidade_real * self.caracteristicas["valor_madeira"] * 0.5
        
        elif self.especie == "árvore_madeira":
            recursos["madeira"] = quantidade_real * self.caracteristicas["valor_madeira"]
        
        elif self.especie == "arbusto_comestível":
            recursos["comida"] = quantidade_real * self.caracteristicas["valor_nutricional"]
        
        elif self.especie == "erva_medicinal":
            recursos["erva_medicinal"] = quantidade_real * self.caracteristicas["valor_medicinal"]
        
        elif self.especie == "flor":
            recursos["flor"] = quantidade_real
        
        elif self.especie == "fungo":
            recursos["fungo"] = quantidade_real
            
            # Se for venenoso, marcar
            if self.propriedades.get("venenoso", False):
                recursos["venenoso"] = True
        
        elif self.especie == "planta_aquática":
            recursos["planta_aquatica"] = quantidade_real
        
        elif self.especie == "cacto":
            recursos["cacto"] = quantidade_real
            recursos["agua"] = quantidade_real * 0.3
        
        return recursos
    
    def cultivar(self, senciante_id):
        """
        Marca a planta como cultivada por um Senciante.
        
        Args:
            senciante_id (str): ID do Senciante cultivador.
            
        Returns:
            bool: True se a planta foi cultivada com sucesso.
        """
        # Verificar se a planta é cultivável
        if self.caracteristicas["cultivabilidade"] > 0.3:
            self.cultivada = True
            self.cultivador_id = senciante_id
            return True
        else:
            return False
    
    def to_dict(self):
        """
        Converte a planta para um dicionário.
        
        Returns:
            dict: Representação da planta como dicionário.
        """
        return {
            "id": self.id,
            "especie": self.especie,
            "posicao": self.posicao,
            "tamanho_atual": self.tamanho_atual,
            "tamanho_maximo": self.caracteristicas["tamanho_maximo"],
            "valor_nutricional": self.caracteristicas["valor_nutricional"],
            "valor_medicinal": self.caracteristicas["valor_medicinal"],
            "habitat_preferido": self.caracteristicas["habitat_preferido"],
            "idade": self.idade,
            "saude": self.saude,
            "estado_crescimento": self.estado_crescimento,
            "cultivada": self.cultivada,
            "cultivador_id": self.cultivador_id,
            "propriedades_especiais": list(self.propriedades.keys())
        }

