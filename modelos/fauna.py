"""
Módulo que define a classe Fauna para o jogo "O Mundo dos Senciantes".
A Fauna representa animais que habitam o ecossistema do mundo.
"""

import random
from utils.helpers import gerar_id, calcular_distancia, chance, mover_em_direcao

class Fauna:
    """
    Classe que representa um animal no ecossistema.
    Contém comportamento, características e interações com Senciantes.
    """
    
    def __init__(self, especie=None, posicao=None, mundo=None):
        """
        Inicializa um novo animal.
        
        Args:
            especie (str, optional): Espécie do animal. Se None, escolhe aleatoriamente.
            posicao (list, optional): Posição inicial do animal [x, y]. Se None, escolhe aleatoriamente.
            mundo (Mundo, optional): Objeto mundo para referência.
        """
        self.id = gerar_id()
        self.especie = especie if especie else self._escolher_especie_aleatoria()
        self.posicao = posicao if posicao else [random.uniform(0, mundo.tamanho[0]), random.uniform(0, mundo.tamanho[1])] if mundo else [50, 50]
        
        # Características
        self.caracteristicas = self._definir_caracteristicas()
        self.idade = 0.0  # Idade em horas
        self.saude = 1.0  # Saúde (0.0 a 1.0)
        self.fome = 0.0  # Fome (0.0 a 1.0)
        
        # Estado
        self.estado_atual = "vagar"  # vagar, caçar, fugir, descansar
        self.alvo_atual = None
        self.domesticado = False
        self.dono_id = None  # ID do Senciante dono, se domesticado
        
        # Relações com Senciantes
        self.relacoes = {}  # Dicionário de senciante_id: nível_relação (-1.0 a 1.0)
    
    def _escolher_especie_aleatoria(self):
        """
        Escolhe uma espécie aleatória para o animal.
        
        Returns:
            str: Espécie do animal.
        """
        especies = ["herbívoro_pequeno", "herbívoro_grande", "carnívoro_pequeno", "carnívoro_grande", "onívoro", "ave", "peixe", "inseto"]
        
        return random.choice(especies)
    
    def _definir_caracteristicas(self):
        """
        Define as características do animal com base na espécie.
        
        Returns:
            dict: Dicionário de características.
        """
        caracteristicas = {
            "tamanho": 0.0,  # 0.0 a 1.0
            "velocidade": 0.0,  # 0.0 a 1.0
            "forca": 0.0,  # 0.0 a 1.0
            "agressividade": 0.0,  # 0.0 a 1.0
            "domesticabilidade": 0.0,  # 0.0 a 1.0
            "valor_nutricional": 0.0,  # 0.0 a 1.0
            "valor_pele": 0.0,  # 0.0 a 1.0
            "tipo_alimentacao": "",  # herbívoro, carnívoro, onívoro
            "habitat_preferido": "",  # floresta, planície, montanha, água
            "expectativa_vida": 0.0,  # Em horas
            "taxa_reproducao": 0.0  # 0.0 a 1.0
        }
        
        # Definir características com base na espécie
        if self.especie == "herbívoro_pequeno":
            caracteristicas.update({
                "tamanho": random.uniform(0.1, 0.3),
                "velocidade": random.uniform(0.5, 0.8),
                "forca": random.uniform(0.1, 0.3),
                "agressividade": random.uniform(0.1, 0.3),
                "domesticabilidade": random.uniform(0.5, 0.9),
                "valor_nutricional": random.uniform(0.3, 0.5),
                "valor_pele": random.uniform(0.2, 0.4),
                "tipo_alimentacao": "herbívoro",
                "habitat_preferido": random.choice(["floresta", "planície"]),
                "expectativa_vida": random.uniform(8760, 17520),  # 1-2 anos
                "taxa_reproducao": random.uniform(0.6, 0.9)
            })
        
        elif self.especie == "herbívoro_grande":
            caracteristicas.update({
                "tamanho": random.uniform(0.6, 0.9),
                "velocidade": random.uniform(0.4, 0.7),
                "forca": random.uniform(0.5, 0.8),
                "agressividade": random.uniform(0.2, 0.5),
                "domesticabilidade": random.uniform(0.3, 0.7),
                "valor_nutricional": random.uniform(0.7, 0.9),
                "valor_pele": random.uniform(0.6, 0.9),
                "tipo_alimentacao": "herbívoro",
                "habitat_preferido": random.choice(["planície", "floresta"]),
                "expectativa_vida": random.uniform(26280, 43800),  # 3-5 anos
                "taxa_reproducao": random.uniform(0.3, 0.5)
            })
        
        elif self.especie == "carnívoro_pequeno":
            caracteristicas.update({
                "tamanho": random.uniform(0.2, 0.4),
                "velocidade": random.uniform(0.6, 0.9),
                "forca": random.uniform(0.3, 0.6),
                "agressividade": random.uniform(0.5, 0.8),
                "domesticabilidade": random.uniform(0.3, 0.6),
                "valor_nutricional": random.uniform(0.4, 0.6),
                "valor_pele": random.uniform(0.4, 0.7),
                "tipo_alimentacao": "carnívoro",
                "habitat_preferido": random.choice(["floresta", "planície"]),
                "expectativa_vida": random.uniform(13140, 26280),  # 1.5-3 anos
                "taxa_reproducao": random.uniform(0.4, 0.7)
            })
        
        elif self.especie == "carnívoro_grande":
            caracteristicas.update({
                "tamanho": random.uniform(0.7, 1.0),
                "velocidade": random.uniform(0.7, 1.0),
                "forca": random.uniform(0.7, 1.0),
                "agressividade": random.uniform(0.7, 1.0),
                "domesticabilidade": random.uniform(0.1, 0.3),
                "valor_nutricional": random.uniform(0.5, 0.7),
                "valor_pele": random.uniform(0.7, 1.0),
                "tipo_alimentacao": "carnívoro",
                "habitat_preferido": random.choice(["floresta", "montanha"]),
                "expectativa_vida": random.uniform(35040, 52560),  # 4-6 anos
                "taxa_reproducao": random.uniform(0.2, 0.4)
            })
        
        elif self.especie == "onívoro":
            caracteristicas.update({
                "tamanho": random.uniform(0.3, 0.6),
                "velocidade": random.uniform(0.4, 0.7),
                "forca": random.uniform(0.3, 0.6),
                "agressividade": random.uniform(0.3, 0.6),
                "domesticabilidade": random.uniform(0.4, 0.7),
                "valor_nutricional": random.uniform(0.5, 0.8),
                "valor_pele": random.uniform(0.4, 0.7),
                "tipo_alimentacao": "onívoro",
                "habitat_preferido": random.choice(["floresta", "planície"]),
                "expectativa_vida": random.uniform(17520, 35040),  # 2-4 anos
                "taxa_reproducao": random.uniform(0.4, 0.6)
            })
        
        elif self.especie == "ave":
            caracteristicas.update({
                "tamanho": random.uniform(0.1, 0.4),
                "velocidade": random.uniform(0.7, 1.0),
                "forca": random.uniform(0.1, 0.3),
                "agressividade": random.uniform(0.2, 0.5),
                "domesticabilidade": random.uniform(0.3, 0.7),
                "valor_nutricional": random.uniform(0.3, 0.5),
                "valor_pele": random.uniform(0.2, 0.5),
                "tipo_alimentacao": random.choice(["herbívoro", "onívoro", "carnívoro"]),
                "habitat_preferido": random.choice(["floresta", "planície", "montanha"]),
                "expectativa_vida": random.uniform(8760, 17520),  # 1-2 anos
                "taxa_reproducao": random.uniform(0.6, 0.9)
            })
        
        elif self.especie == "peixe":
            caracteristicas.update({
                "tamanho": random.uniform(0.1, 0.5),
                "velocidade": random.uniform(0.5, 0.8),
                "forca": random.uniform(0.1, 0.4),
                "agressividade": random.uniform(0.1, 0.4),
                "domesticabilidade": random.uniform(0.1, 0.3),
                "valor_nutricional": random.uniform(0.5, 0.8),
                "valor_pele": random.uniform(0.1, 0.3),
                "tipo_alimentacao": random.choice(["herbívoro", "carnívoro"]),
                "habitat_preferido": "água",
                "expectativa_vida": random.uniform(4380, 8760),  # 0.5-1 ano
                "taxa_reproducao": random.uniform(0.7, 1.0)
            })
        
        elif self.especie == "inseto":
            caracteristicas.update({
                "tamanho": random.uniform(0.01, 0.1),
                "velocidade": random.uniform(0.3, 0.6),
                "forca": random.uniform(0.01, 0.1),
                "agressividade": random.uniform(0.1, 0.5),
                "domesticabilidade": random.uniform(0.0, 0.2),
                "valor_nutricional": random.uniform(0.1, 0.3),
                "valor_pele": random.uniform(0.0, 0.1),
                "tipo_alimentacao": random.choice(["herbívoro", "carnívoro"]),
                "habitat_preferido": random.choice(["floresta", "planície"]),
                "expectativa_vida": random.uniform(720, 2160),  # 1-3 meses
                "taxa_reproducao": random.uniform(0.8, 1.0)
            })
        
        return caracteristicas
    
    def atualizar(self, delta_tempo, mundo, senciantes):
        """
        Atualiza o estado do animal.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            mundo (Mundo): Objeto mundo atual.
            senciantes (list): Lista de Senciantes no mundo.
            
        Returns:
            bool: True se o animal ainda está vivo, False se morreu.
        """
        # Atualizar idade
        self.idade += delta_tempo
        
        # Verificar morte por idade
        if self.idade > self.caracteristicas["expectativa_vida"]:
            return False
        
        # Atualizar fome
        self.fome += 0.05 * delta_tempo
        self.fome = min(1.0, self.fome)
        
        # Verificar morte por fome
        if self.fome >= 1.0:
            self.saude -= 0.1 * delta_tempo
        
        # Verificar morte por saúde
        if self.saude <= 0.0:
            return False
        
        # Se domesticado, comportamento diferente
        if self.domesticado:
            return self._comportamento_domesticado(delta_tempo, mundo, senciantes)
        else:
            return self._comportamento_selvagem(delta_tempo, mundo, senciantes)
    
    def _comportamento_domesticado(self, delta_tempo, mundo, senciantes):
        """
        Comportamento de animal domesticado.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            mundo (Mundo): Objeto mundo atual.
            senciantes (list): Lista de Senciantes no mundo.
            
        Returns:
            bool: True se o animal ainda está vivo, False se morreu.
        """
        # Encontrar o dono
        dono = None
        for senciante in senciantes:
            if senciante.id == self.dono_id:
                dono = senciante
                break
        
        # Se o dono não for encontrado, o animal volta a ser selvagem
        if not dono:
            self.domesticado = False
            self.dono_id = None
            return True
        
        # Seguir o dono
        distancia_dono = calcular_distancia(self.posicao, dono.posicao)
        
        if distancia_dono > 5.0:
            # Mover em direção ao dono
            velocidade = 2.0 * self.caracteristicas["velocidade"]
            self.posicao = mover_em_direcao(self.posicao, dono.posicao, velocidade)
        else:
            # Vagar próximo ao dono
            if chance(0.3):
                direcao_x = random.uniform(-1, 1)
                direcao_y = random.uniform(-1, 1)
                
                # Normalizar direção
                magnitude = (direcao_x**2 + direcao_y**2)**0.5
                if magnitude > 0:
                    direcao_x /= magnitude
                    direcao_y /= magnitude
                
                # Mover
                velocidade = 1.0 * self.caracteristicas["velocidade"]
                self.posicao[0] += direcao_x * velocidade
                self.posicao[1] += direcao_y * velocidade
                
                # Limitar à área do mundo
                self.posicao[0] = max(0, min(mundo.tamanho[0], self.posicao[0]))
                self.posicao[1] = max(0, min(mundo.tamanho[1], self.posicao[1]))
        
        return True
    
    def _comportamento_selvagem(self, delta_tempo, mundo, senciantes):
        """
        Comportamento de animal selvagem.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            mundo (Mundo): Objeto mundo atual.
            senciantes (list): Lista de Senciantes no mundo.
            
        Returns:
            bool: True se o animal ainda está vivo, False se morreu.
        """
        # Verificar ameaças (Senciantes próximos)
        ameaca_proxima = False
        for senciante in senciantes:
            distancia = calcular_distancia(self.posicao, senciante.posicao)
            
            # Se um Senciante estiver muito próximo
            if distancia < 5.0:
                # Verificar relação com o Senciante
                relacao = self.relacoes.get(senciante.id, 0.0)
                
                # Se a relação for negativa ou o animal for naturalmente medroso
                if relacao < 0.0 or self.caracteristicas["agressividade"] < 0.3:
                    ameaca_proxima = True
                    
                    # Fugir do Senciante
                    self.estado_atual = "fugir"
                    self.alvo_atual = senciante.posicao
                    break
        
        # Comportamento baseado no estado atual
        if self.estado_atual == "fugir":
            # Fugir da ameaça
            direcao_x = self.posicao[0] - self.alvo_atual[0]
            direcao_y = self.posicao[1] - self.alvo_atual[1]
            
            # Normalizar direção
            magnitude = (direcao_x**2 + direcao_y**2)**0.5
            if magnitude > 0:
                direcao_x /= magnitude
                direcao_y /= magnitude
            
            # Mover
            velocidade = 3.0 * self.caracteristicas["velocidade"]
            self.posicao[0] += direcao_x * velocidade
            self.posicao[1] += direcao_y * velocidade
            
            # Limitar à área do mundo
            self.posicao[0] = max(0, min(mundo.tamanho[0], self.posicao[0]))
            self.posicao[1] = max(0, min(mundo.tamanho[1], self.posicao[1]))
            
            # Chance de mudar de estado
            if chance(0.2):
                self.estado_atual = "vagar"
                self.alvo_atual = None
        
        elif self.estado_atual == "caçar":
            # Implementar comportamento de caça
            pass
        
        elif self.estado_atual == "descansar":
            # Descansar (recuperar energia)
            if chance(0.3):
                self.estado_atual = "vagar"
        
        else:  # vagar
            # Vagar aleatoriamente
            if chance(0.3):
                direcao_x = random.uniform(-1, 1)
                direcao_y = random.uniform(-1, 1)
                
                # Normalizar direção
                magnitude = (direcao_x**2 + direcao_y**2)**0.5
                if magnitude > 0:
                    direcao_x /= magnitude
                    direcao_y /= magnitude
                
                # Mover
                velocidade = 1.0 * self.caracteristicas["velocidade"]
                self.posicao[0] += direcao_x * velocidade
                self.posicao[1] += direcao_y * velocidade
                
                # Limitar à área do mundo
                self.posicao[0] = max(0, min(mundo.tamanho[0], self.posicao[0]))
                self.posicao[1] = max(0, min(mundo.tamanho[1], self.posicao[1]))
            
            # Chance de mudar para descansar
            if chance(0.1):
                self.estado_atual = "descansar"
        
        return True
    
    def interagir_com_senciante(self, senciante, tipo_interacao):
        """
        Processa uma interação com um Senciante.
        
        Args:
            senciante (Senciante): Senciante que está interagindo.
            tipo_interacao (str): Tipo de interação ("alimentar", "acariciar", "domesticar", "atacar").
            
        Returns:
            dict: Resultado da interação.
        """
        resultado = {"sucesso": False, "mensagem": ""}
        
        # Obter relação atual
        relacao_atual = self.relacoes.get(senciante.id, 0.0)
        
        if tipo_interacao == "alimentar":
            # Reduzir fome
            self.fome = max(0.0, self.fome - 0.3)
            
            # Melhorar relação
            nova_relacao = min(1.0, relacao_atual + 0.1)
            self.relacoes[senciante.id] = nova_relacao
            
            resultado["sucesso"] = True
            resultado["mensagem"] = "Animal alimentado com sucesso."
        
        elif tipo_interacao == "acariciar":
            # Verificar se o animal permite
            if relacao_atual > 0.0 or self.caracteristicas["domesticabilidade"] > 0.5:
                # Melhorar relação
                nova_relacao = min(1.0, relacao_atual + 0.05)
                self.relacoes[senciante.id] = nova_relacao
                
                resultado["sucesso"] = True
                resultado["mensagem"] = "Animal acariciado com sucesso."
            else:
                # Animal não permite, pode atacar
                if chance(self.caracteristicas["agressividade"]):
                    # Atacar o Senciante
                    dano = self.caracteristicas["forca"] * 0.2
                    senciante.estado["saude"] -= dano
                    
                    # Piorar relação
                    nova_relacao = max(-1.0, relacao_atual - 0.2)
                    self.relacoes[senciante.id] = nova_relacao
                    
                    resultado["sucesso"] = False
                    resultado["mensagem"] = f"Animal atacou! Dano: {dano:.2f}"
                else:
                    # Animal apenas foge
                    resultado["sucesso"] = False
                    resultado["mensagem"] = "Animal fugiu."
        
        elif tipo_interacao == "domesticar":
            # Verificar chance de domesticação
            chance_domesticacao = self.caracteristicas["domesticabilidade"] * (relacao_atual + 1.0) / 2.0
            
            if chance(chance_domesticacao):
                self.domesticado = True
                self.dono_id = senciante.id
                
                # Melhorar relação significativamente
                self.relacoes[senciante.id] = min(1.0, relacao_atual + 0.3)
                
                resultado["sucesso"] = True
                resultado["mensagem"] = "Animal domesticado com sucesso."
            else:
                # Falha na domesticação
                resultado["sucesso"] = False
                resultado["mensagem"] = "Falha na tentativa de domesticação."
        
        elif tipo_interacao == "atacar":
            # Senciante ataca o animal
            dano = senciante.habilidades.get("combate", 0.1) * 0.5
            self.saude -= dano
            
            # Piorar relação drasticamente
            self.relacoes[senciante.id] = -1.0
            
            if self.saude <= 0.0:
                # Animal morto
                resultado["sucesso"] = True
                resultado["mensagem"] = "Animal morto."
                resultado["recursos"] = self._gerar_recursos_ao_morrer()
            else:
                # Animal ferido, pode contra-atacar ou fugir
                if chance(self.caracteristicas["agressividade"]):
                    # Contra-atacar
                    dano_contra = self.caracteristicas["forca"] * 0.3
                    senciante.estado["saude"] -= dano_contra
                    
                    resultado["sucesso"] = True
                    resultado["mensagem"] = f"Animal ferido e contra-atacou! Dano: {dano_contra:.2f}"
                else:
                    # Fugir
                    resultado["sucesso"] = True
                    resultado["mensagem"] = "Animal ferido e fugiu."
        
        return resultado
    
    def _gerar_recursos_ao_morrer(self):
        """
        Gera recursos quando o animal morre.
        
        Returns:
            dict: Dicionário de recursos gerados.
        """
        recursos = {}
        
        # Carne
        quantidade_carne = self.caracteristicas["tamanho"] * self.caracteristicas["valor_nutricional"] * random.uniform(0.8, 1.2)
        recursos["carne"] = quantidade_carne
        
        # Pele
        quantidade_pele = self.caracteristicas["tamanho"] * self.caracteristicas["valor_pele"] * random.uniform(0.8, 1.2)
        recursos["pele"] = quantidade_pele
        
        return recursos
    
    def to_dict(self):
        """
        Converte o animal para um dicionário.
        
        Returns:
            dict: Representação do animal como dicionário.
        """
        return {
            "id": self.id,
            "especie": self.especie,
            "posicao": self.posicao,
            "tamanho": self.caracteristicas["tamanho"],
            "velocidade": self.caracteristicas["velocidade"],
            "forca": self.caracteristicas["forca"],
            "agressividade": self.caracteristicas["agressividade"],
            "domesticabilidade": self.caracteristicas["domesticabilidade"],
            "tipo_alimentacao": self.caracteristicas["tipo_alimentacao"],
            "habitat_preferido": self.caracteristicas["habitat_preferido"],
            "idade": self.idade,
            "saude": self.saude,
            "fome": self.fome,
            "estado_atual": self.estado_atual,
            "domesticado": self.domesticado,
            "dono_id": self.dono_id
        }

