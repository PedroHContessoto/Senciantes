"""
Módulo que define a classe Senciante para o jogo "O Mundo dos Senciantes".
O Senciante representa um ser artificial inteligente no mundo.
"""

import random
from modelos.genoma import Genoma
from modelos.memoria import Memoria
from utils.helpers import gerar_id, calcular_distancia, chance, mover_em_direcao
from utils.config import (
    SENCIANTE_MAX_AGE, SENCIANTE_REPRODUCTION_MIN_AGE,
    SENCIANTE_NEEDS_DECAY_RATES, SENCIANTE_NEEDS_CRITICAL_THRESHOLDS,
    SENCIANTE_NEEDS_URGENT_THRESHOLDS, SENCIANTE_NEEDS_WEIGHTS,
    LEARNING_BASE_RATE, COMMUNICATION_EVOLUTION_STAGES,
    COMMUNICATION_EVOLUTION_THRESHOLDS, RELATION_TYPES,
    RELATION_STRENGTH_DECAY_RATE, RELATION_STRENGTH_THRESHOLD
)

class Senciante:
    """
    Classe que representa um Senciante no mundo.
    Contém estado físico, genoma, habilidades, memória, relações sociais e comportamento.
    """
    
    def __init__(self, posicao, genoma=None, idade_inicial=0.0):
        """
        Inicializa um novo Senciante.
        
        Args:
            posicao (list): Posição inicial do Senciante no mundo [x, y].
            genoma (Genoma, optional): Genoma do Senciante. Se None, gera um genoma aleatório.
            idade_inicial (float, optional): Idade inicial em horas. Default é 0.0.
        """
        self.id = gerar_id()
        self.posicao = posicao
        self.genoma = genoma if genoma else Genoma()
        self.modificadores = self.genoma.aplicar_efeitos_mutacoes()
        
        # Necessidades fisiológicas (0.0 a 1.0, onde 1.0 é crítico)
        self.necessidades = {
            "fome": 0.0,
            "sede": 0.0,
            "sono": 0.0,
            "higiene": 0.0,
            "social": 0.0
        }
        
        # Estado geral
        self.estado = {
            "idade": idade_inicial,
            "saude": 1.0,
            "energia": 1.0,
            "felicidade": 0.5,
            "estresse": 0.0
        }
        
        # Habilidades (0.0 a 1.0, onde 1.0 é domínio completo)
        self.habilidades = {
            "coleta": 0.1,
            "construcao": 0.1,
            "comunicacao": 0.1,
            "combate": 0.1,
            "aprendizado": 0.1
        }
        
        # Memória
        self.memoria = []
        
        # Relações sociais
        self.relacoes = {}  # Dicionário de senciante_id: {"tipo": tipo, "forca": valor}
        
        # Tecnologias conhecidas
        self.tecnologias_conhecidas = []
        
        # Inventário
        self.inventario = {}  # Dicionário de tipo_recurso: quantidade
        
        # Estado atual de atividade
        self.atividade_atual = None
        self.alvo_atual = None
        
        # Nível de comunicação
        self.nivel_comunicacao = 0  # Índice no COMMUNICATION_EVOLUTION_STAGES
    
    def atualizar(self, delta_tempo, mundo):
        """
        Atualiza o estado do Senciante com base no tempo decorrido e no mundo.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            mundo (Mundo): Objeto mundo atual.
            
        Returns:
            bool: True se o Senciante ainda está vivo, False se morreu.
        """
        # Atualizar idade
        self.estado["idade"] += delta_tempo
        
        # Atualizar necessidades
        self._atualizar_necessidades(delta_tempo)
        
        # Atualizar saúde
        self._atualizar_saude()
        
        # Verificar morte
        if self._verificar_morte():
            return False
        
        # Tomar decisões e agir
        self._tomar_decisao(delta_tempo, mundo)
        
        # Aprender
        self._aprender(delta_tempo)
        
        # Atualizar relações
        self._atualizar_relacoes(delta_tempo)
        
        # Atualizar memórias
        self._atualizar_memorias(delta_tempo)
        
        # Atualizar nível de comunicação
        self._atualizar_nivel_comunicacao()
        
        return True
    
    def _atualizar_necessidades(self, delta_tempo):
        """
        Atualiza as necessidades fisiológicas do Senciante.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Aumentar fome
        self.necessidades["fome"] += SENCIANTE_NEEDS_DECAY_RATES["fome"] * delta_tempo * self.modificadores.get("metabolismo", 1.0)
        
        # Aumentar sede
        self.necessidades["sede"] += SENCIANTE_NEEDS_DECAY_RATES["sede"] * delta_tempo * self.modificadores.get("metabolismo", 1.0)
        
        # Aumentar sono (diminuir energia)
        if self.estado["energia"] > 0:
            self.estado["energia"] -= SENCIANTE_NEEDS_DECAY_RATES["sono"] * delta_tempo
        self.necessidades["sono"] = 1.0 - self.estado["energia"]
        
        # Aumentar necessidade de higiene
        self.necessidades["higiene"] += SENCIANTE_NEEDS_DECAY_RATES["higiene"] * delta_tempo
        
        # Aumentar necessidade social
        self.necessidades["social"] += SENCIANTE_NEEDS_DECAY_RATES["social"] * delta_tempo
        
        # Limitar valores
        for necessidade in self.necessidades:
            self.necessidades[necessidade] = max(0.0, min(1.0, self.necessidades[necessidade]))
    
    def _atualizar_saude(self):
        """
        Atualiza o estado de saúde do Senciante com base nas necessidades.
        """
        # Calcular penalidades de saúde baseadas nas necessidades
        penalidade_fome = self.necessidades["fome"] * 0.5
        penalidade_sede = self.necessidades["sede"] * 0.7
        penalidade_sono = self.necessidades["sono"] * 0.3
        penalidade_higiene = self.necessidades["higiene"] * 0.2
        penalidade_social = self.necessidades["social"] * 0.1
        
        # Calcular saúde alvo
        saude_alvo = 1.0 - (
            penalidade_fome + penalidade_sede + penalidade_sono +
            penalidade_higiene + penalidade_social
        ) / 5.0
        
        # Ajustar saúde gradualmente
        self.estado["saude"] += (saude_alvo - self.estado["saude"]) * 0.1
        
        # Limitar valor
        self.estado["saude"] = max(0.0, min(1.0, self.estado["saude"]))
        
        # Atualizar felicidade com base na saúde e necessidades
        felicidade_alvo = (
            self.estado["saude"] * 0.5 +
            (1.0 - self.necessidades["fome"]) * 0.1 +
            (1.0 - self.necessidades["sede"]) * 0.1 +
            (1.0 - self.necessidades["sono"]) * 0.1 +
            (1.0 - self.necessidades["social"]) * 0.2
        )
        
        # Ajustar felicidade gradualmente
        self.estado["felicidade"] += (felicidade_alvo - self.estado["felicidade"]) * 0.05
        
        # Limitar valor
        self.estado["felicidade"] = max(0.0, min(1.0, self.estado["felicidade"]))
    
    def _verificar_morte(self):
        """
        Verifica se o Senciante morreu.
        
        Returns:
            bool: True se o Senciante morreu, False caso contrário.
        """
        # Verificar morte por idade
        if self.estado["idade"] > SENCIANTE_MAX_AGE * self.modificadores.get("longevidade", 1.0):
            return True
        
        # Verificar morte por saúde
        if self.estado["saude"] <= 0.0:
            return True
        
        # Verificar morte por fome extrema
        if self.necessidades["fome"] >= SENCIANTE_NEEDS_CRITICAL_THRESHOLDS["fome"]:
            return True
        
        # Verificar morte por sede extrema
        if self.necessidades["sede"] >= SENCIANTE_NEEDS_CRITICAL_THRESHOLDS["sede"]:
            return True
        
        return False
    
    def _tomar_decisao(self, delta_tempo, mundo):
        """
        Toma decisões e executa ações com base no estado atual e no mundo.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            mundo (Mundo): Objeto mundo atual.
        """
        # Determinar necessidade mais urgente
        necessidade_urgente = self._obter_necessidade_mais_urgente()
        
        # Se estiver em uma atividade, verificar se deve continuar
        if self.atividade_atual:
            # Verificar se surgiu uma necessidade mais urgente
            if necessidade_urgente and necessidade_urgente != self.atividade_atual:
                # Interromper atividade atual
                self.atividade_atual = None
                self.alvo_atual = None
        
        # Se não estiver em uma atividade ou se a atividade foi interrompida
        if not self.atividade_atual:
            # Determinar ação baseada na necessidade
            if necessidade_urgente == "fome":
                self._buscar_comida(mundo)
            elif necessidade_urgente == "sede":
                self._buscar_agua(mundo)
            elif necessidade_urgente == "sono":
                self._descansar(mundo)
            elif necessidade_urgente == "higiene":
                self._limpar(mundo)
            elif necessidade_urgente == "social":
                self._socializar(mundo)
            else:
                # Se não há necessidades urgentes, explorar ou melhorar
                if chance(0.7):
                    self._explorar(mundo)
                else:
                    self._melhorar_habilidades(delta_tempo)
        else:
            # Continuar atividade atual
            if self.atividade_atual == "buscar_comida":
                self._continuar_buscar_comida(mundo)
            elif self.atividade_atual == "buscar_agua":
                self._continuar_buscar_agua(mundo)
            elif self.atividade_atual == "descansar":
                self._continuar_descansar(delta_tempo)
            elif self.atividade_atual == "limpar":
                self._continuar_limpar(delta_tempo)
            elif self.atividade_atual == "socializar":
                self._continuar_socializar(mundo)
            elif self.atividade_atual == "explorar":
                self._continuar_explorar(mundo)
            elif self.atividade_atual == "construir":
                self._continuar_construir(mundo)
    
    def _obter_necessidade_mais_urgente(self):
        """
        Determina a necessidade mais urgente do Senciante.
        
        Returns:
            str: Nome da necessidade mais urgente, ou None se não houver necessidades urgentes.
        """
        # Pesos de urgência para cada necessidade
        urgencias = {}
        
        for necessidade, valor in self.necessidades.items():
            # Calcular urgência ponderada
            urgencia = valor * SENCIANTE_NEEDS_WEIGHTS.get(necessidade, 1.0)
            
            # Verificar se está acima do limiar de urgência
            if valor >= SENCIANTE_NEEDS_URGENT_THRESHOLDS.get(necessidade, 0.7):
                urgencias[necessidade] = urgencia
        
        # Se não há necessidades urgentes
        if not urgencias:
            return None
        
        # Encontrar necessidade mais urgente
        return max(urgencias, key=urgencias.get)
    
    def _buscar_comida(self, mundo):
        """
        Inicia a busca por comida.
        
        Args:
            mundo (Mundo): Objeto mundo atual.
        """
        # Verificar se já tem comida no inventário
        if "comida" in self.inventario and self.inventario["comida"] > 0:
            # Consumir comida do inventário
            self._consumir_recurso("comida", 1.0)
            return
        
        # Verificar se há comida no inventário de construções ocupadas
        for construcao_id in [c.id for c in mundo.encontrar_construcoes_proximas(self.posicao, 5) if self.id in c.ocupantes]:
            construcao = mundo.construcoes.get(construcao_id)
            if construcao and "comida" in construcao.recursos_armazenados and construcao.recursos_armazenados["comida"] > 0:
                # Retirar comida da construção
                quantidade = construcao.retirar_recurso("comida", 1.0)
                # Consumir imediatamente
                self._consumir_recurso("comida", quantidade)
                return
        
        # Procurar recursos de comida próximos
        recursos_comida = mundo.encontrar_recursos_proximos(self.posicao, 20, "comida")
        
        if recursos_comida:
            # Definir alvo como o recurso mais próximo
            self.alvo_atual = recursos_comida[0]
            self.atividade_atual = "buscar_comida"
        else:
            # Procurar recursos de fruta como alternativa
            recursos_fruta = mundo.encontrar_recursos_proximos(self.posicao, 20, "fruta")
            
            if recursos_fruta:
                # Definir alvo como o recurso mais próximo
                self.alvo_atual = recursos_fruta[0]
                self.atividade_atual = "buscar_comida"
            else:
                # Explorar para encontrar comida
                self._explorar(mundo)
    
    def _continuar_buscar_comida(self, mundo):
        """
        Continua a busca por comida.
        
        Args:
            mundo (Mundo): Objeto mundo atual.
        """
        # Verificar se o alvo ainda existe
        if isinstance(self.alvo_atual, Recurso) and self.alvo_atual.id not in mundo.recursos:
            # Alvo não existe mais, procurar outro
            self._buscar_comida(mundo)
            return
        
        # Calcular distância até o alvo
        distancia = calcular_distancia(self.posicao, self.alvo_atual.posicao)
        
        if distancia <= 1.0:
            # Chegou ao alvo, coletar comida
            quantidade = self.alvo_atual.coletar(1.0)
            
            # Consumir parte imediatamente
            quantidade_consumida = min(0.5, quantidade)
            self._consumir_recurso("comida", quantidade_consumida)
            
            # Armazenar o restante no inventário
            quantidade_restante = quantidade - quantidade_consumida
            if quantidade_restante > 0:
                if "comida" in self.inventario:
                    self.inventario["comida"] += quantidade_restante
                else:
                    self.inventario["comida"] = quantidade_restante
            
            # Melhorar habilidade de coleta
            self._ganhar_experiencia("coleta", 0.01)
            
            # Registrar memória
            self._adicionar_memoria(
                "coleta",
                f"Coletei comida em {self.alvo_atual.posicao}",
                0.5  # Importância média
            )
            
            # Atividade concluída
            self.atividade_atual = None
            self.alvo_atual = None
        else:
            # Mover em direção ao alvo
            velocidade = 2.0 * self.genoma.genes["velocidade"]
            self.posicao = mover_em_direcao(self.posicao, self.alvo_atual.posicao, velocidade)
    
    def _buscar_agua(self, mundo):
        """
        Inicia a busca por água.
        
        Args:
            mundo (Mundo): Objeto mundo atual.
        """
        # Verificar se já tem água no inventário
        if "agua" in self.inventario and self.inventario["agua"] > 0:
            # Consumir água do inventário
            self._consumir_recurso("agua", 1.0)
            return
        
        # Verificar se há água no inventário de construções ocupadas
        for construcao_id in [c.id for c in mundo.encontrar_construcoes_proximas(self.posicao, 5) if self.id in c.ocupantes]:
            construcao = mundo.construcoes.get(construcao_id)
            if construcao and "agua" in construcao.recursos_armazenados and construcao.recursos_armazenados["agua"] > 0:
                # Retirar água da construção
                quantidade = construcao.retirar_recurso("agua", 1.0)
                # Consumir imediatamente
                self._consumir_recurso("agua", quantidade)
                return
        
        # Procurar recursos de água próximos
        recursos_agua = mundo.encontrar_recursos_proximos(self.posicao, 20, "agua")
        
        if recursos_agua:
            # Definir alvo como o recurso mais próximo
            self.alvo_atual = recursos_agua[0]
            self.atividade_atual = "buscar_agua"
        else:
            # Explorar para encontrar água
            self._explorar(mundo)
    
    def _continuar_buscar_agua(self, mundo):
        """
        Continua a busca por água.
        
        Args:
            mundo (Mundo): Objeto mundo atual.
        """
        # Verificar se o alvo ainda existe
        if isinstance(self.alvo_atual, Recurso) and self.alvo_atual.id not in mundo.recursos:
            # Alvo não existe mais, procurar outro
            self._buscar_agua(mundo)
            return
        
        # Calcular distância até o alvo
        distancia = calcular_distancia(self.posicao, self.alvo_atual.posicao)
        
        if distancia <= 1.0:
            # Chegou ao alvo, coletar água
            quantidade = self.alvo_atual.coletar(1.0)
            
            # Consumir parte imediatamente
            quantidade_consumida = min(0.5, quantidade)
            self._consumir_recurso("agua", quantidade_consumida)
            
            # Armazenar o restante no inventário
            quantidade_restante = quantidade - quantidade_consumida
            if quantidade_restante > 0:
                if "agua" in self.inventario:
                    self.inventario["agua"] += quantidade_restante
                else:
                    self.inventario["agua"] = quantidade_restante
            
            # Melhorar habilidade de coleta
            self._ganhar_experiencia("coleta", 0.01)
            
            # Registrar memória
            self._adicionar_memoria(
                "coleta",
                f"Coletei água em {self.alvo_atual.posicao}",
                0.5  # Importância média
            )
            
            # Atividade concluída
            self.atividade_atual = None
            self.alvo_atual = None
        else:
            # Mover em direção ao alvo
            velocidade = 2.0 * self.genoma.genes["velocidade"]
            self.posicao = mover_em_direcao(self.posicao, self.alvo_atual.posicao, velocidade)
    
    def _descansar(self, mundo):
        """
        Inicia o descanso para recuperar energia.
        
        Args:
            mundo (Mundo): Objeto mundo atual.
        """
        # Procurar abrigos próximos
        abrigos = mundo.encontrar_construcoes_proximas(self.posicao, 10, "abrigo")
        
        if abrigos:
            # Definir alvo como o abrigo mais próximo
            self.alvo_atual = abrigos[0]
            self.atividade_atual = "descansar"
        else:
            # Descansar onde está
            self.alvo_atual = None
            self.atividade_atual = "descansar"
    
    def _continuar_descansar(self, delta_tempo):
        """
        Continua o descanso para recuperar energia.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Se tem um abrigo como alvo, mover-se até ele
        if isinstance(self.alvo_atual, Construcao):
            # Calcular distância até o abrigo
            distancia = calcular_distancia(self.posicao, self.alvo_atual.posicao)
            
            if distancia > 1.0:
                # Mover em direção ao abrigo
                velocidade = 2.0 * self.genoma.genes["velocidade"]
                self.posicao = mover_em_direcao(self.posicao, self.alvo_atual.posicao, velocidade)
                return
            
            # Chegou ao abrigo, ocupá-lo
            self.alvo_atual.adicionar_ocupante(self.id)
        
        # Recuperar energia
        taxa_recuperacao = 0.1  # Taxa base de recuperação por hora
        
        # Aumentar taxa se estiver em um abrigo
        if isinstance(self.alvo_atual, Construcao) and "descanso" in self.alvo_atual.funcionalidades:
            taxa_recuperacao *= 2.0
        
        # Recuperar energia
        self.estado["energia"] += taxa_recuperacao * delta_tempo
        
        # Limitar energia
        self.estado["energia"] = min(1.0, self.estado["energia"])
        
        # Atualizar necessidade de sono
        self.necessidades["sono"] = 1.0 - self.estado["energia"]
        
        # Verificar se já descansou o suficiente
        if self.necessidades["sono"] < 0.3:
            # Descanso concluído
            
            # Se estiver em um abrigo, sair dele
            if isinstance(self.alvo_atual, Construcao):
                self.alvo_atual.remover_ocupante(self.id)
            
            # Registrar memória
            self._adicionar_memoria(
                "descanso",
                "Descansei e recuperei energia",
                0.3  # Importância baixa
            )
            
            # Atividade concluída
            self.atividade_atual = None
            self.alvo_atual = None
    
    def _limpar(self, mundo):
        """
        Inicia a limpeza para melhorar a higiene.
        
        Args:
            mundo (Mundo): Objeto mundo atual.
        """
        # Procurar água próxima para se limpar
        recursos_agua = mundo.encontrar_recursos_proximos(self.posicao, 10, "agua")
        
        if recursos_agua:
            # Definir alvo como a água mais próxima
            self.alvo_atual = recursos_agua[0]
            self.atividade_atual = "limpar"
        else:
            # Limpar-se onde está (menos eficiente)
            self.alvo_atual = None
            self.atividade_atual = "limpar"
    
    def _continuar_limpar(self, delta_tempo):
        """
        Continua a limpeza para melhorar a higiene.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Se tem água como alvo, mover-se até ela
        if isinstance(self.alvo_atual, Recurso):
            # Calcular distância até a água
            distancia = calcular_distancia(self.posicao, self.alvo_atual.posicao)
            
            if distancia > 1.0:
                # Mover em direção à água
                velocidade = 2.0 * self.genoma.genes["velocidade"]
                self.posicao = mover_em_direcao(self.posicao, self.alvo_atual.posicao, velocidade)
                return
        
        # Melhorar higiene
        taxa_melhoria = 0.2  # Taxa base de melhoria por hora
        
        # Aumentar taxa se estiver próximo à água
        if isinstance(self.alvo_atual, Recurso) and self.alvo_atual.tipo == "agua":
            taxa_melhoria *= 2.0
            
            # Consumir um pouco de água
            self.alvo_atual.coletar(0.1)
        
        # Melhorar higiene
        self.necessidades["higiene"] -= taxa_melhoria * delta_tempo
        
        # Limitar higiene
        self.necessidades["higiene"] = max(0.0, self.necessidades["higiene"])
        
        # Verificar se já se limpou o suficiente
        if self.necessidades["higiene"] < 0.3:
            # Limpeza concluída
            
            # Registrar memória
            self._adicionar_memoria(
                "higiene",
                "Me limpei e melhorei minha higiene",
                0.3  # Importância baixa
            )
            
            # Atividade concluída
            self.atividade_atual = None
            self.alvo_atual = None
    
    def _socializar(self, mundo):
        """
        Inicia a socialização com outros Senciantes.
        
        Args:
            mundo (Mundo): Objeto mundo atual.
            senciantes (dict): Dicionário de todos os Senciantes (id: Senciante).
        """
        # Esta função será implementada quando tivermos acesso a outros Senciantes
        # Por enquanto, apenas definimos a atividade
        self.atividade_atual = "socializar"
        self.alvo_atual = None
    
    def _continuar_socializar(self, mundo):
        """
        Continua a socialização com outros Senciantes.
        
        Args:
            mundo (Mundo): Objeto mundo atual.
            senciantes (dict): Dicionário de todos os Senciantes (id: Senciante).
        """
        # Esta função será implementada quando tivermos acesso a outros Senciantes
        # Por enquanto, apenas concluímos a atividade
        
        # Melhorar necessidade social um pouco
        self.necessidades["social"] = max(0.0, self.necessidades["social"] - 0.1)
        
        # Atividade concluída
        self.atividade_atual = None
        self.alvo_atual = None
    
    def _explorar(self, mundo):
        """
        Inicia a exploração do mundo.
        
        Args:
            mundo (Mundo): Objeto mundo atual.
        """
        # Escolher uma direção aleatória
        direcao = [
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        ]
        
        # Normalizar direção
        magnitude = (direcao[0]**2 + direcao[1]**2)**0.5
        if magnitude > 0:
            direcao = [direcao[0] / magnitude, direcao[1] / magnitude]
        
        # Calcular posição alvo (10 unidades na direção escolhida)
        alvo = [
            max(0, min(mundo.tamanho[0], self.posicao[0] + direcao[0] * 10)),
            max(0, min(mundo.tamanho[1], self.posicao[1] + direcao[1] * 10))
        ]
        
        # Definir alvo e atividade
        self.alvo_atual = {"posicao": alvo}
        self.atividade_atual = "explorar"
    
    def _continuar_explorar(self, mundo):
        """
        Continua a exploração do mundo.
        
        Args:
            mundo (Mundo): Objeto mundo atual.
        """
        # Calcular distância até o alvo
        distancia = calcular_distancia(self.posicao, self.alvo_atual["posicao"])
        
        if distancia <= 1.0:
            # Chegou ao alvo, exploração concluída
            
            # Registrar memória
            self._adicionar_memoria(
                "exploracao",
                f"Explorei a área em {self.alvo_atual['posicao']}",
                0.3  # Importância baixa
            )
            
            # Atividade concluída
            self.atividade_atual = None
            self.alvo_atual = None
            
            # Chance de descobrir algo
            if chance(0.2):
                # Descobrir recurso próximo
                tipos_recurso = ["comida", "agua", "madeira", "pedra", "fruta"]
                recursos_proximos = mundo.encontrar_recursos_proximos(
                    self.posicao,
                    5,
                    random.choice(tipos_recurso)
                )
                
                if recursos_proximos:
                    # Registrar memória da descoberta
                    self._adicionar_memoria(
                        "descoberta",
                        f"Descobri {recursos_proximos[0].tipo} em {recursos_proximos[0].posicao}",
                        0.7  # Importância alta
                    )
        else:
            # Mover em direção ao alvo
            velocidade = 2.0 * self.genoma.genes["velocidade"]
            self.posicao = mover_em_direcao(self.posicao, self.alvo_atual["posicao"], velocidade)
    
    def _melhorar_habilidades(self, delta_tempo):
        """
        Melhora as habilidades do Senciante.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Escolher uma habilidade aleatória para melhorar
        habilidades = list(self.habilidades.keys())
        habilidade = random.choice(habilidades)
        
        # Melhorar a habilidade
        self._ganhar_experiencia(habilidade, 0.05 * delta_tempo)
        
        # Registrar memória
        self._adicionar_memoria(
            "aprendizado",
            f"Pratiquei e melhorei minha habilidade de {habilidade}",
            0.4  # Importância média-baixa
        )
    
    def _consumir_recurso(self, tipo, quantidade):
        """
        Consome um recurso para satisfazer necessidades.
        
        Args:
            tipo (str): Tipo do recurso a ser consumido.
            quantidade (float): Quantidade a ser consumida.
            
        Returns:
            float: Quantidade efetivamente consumida.
        """
        # Verificar se tem o recurso no inventário
        if tipo in self.inventario and self.inventario[tipo] > 0:
            # Limitar à quantidade disponível
            quantidade_consumida = min(self.inventario[tipo], quantidade)
            
            # Reduzir a quantidade no inventário
            self.inventario[tipo] -= quantidade_consumida
            
            # Remover o tipo de recurso se a quantidade for zero
            if self.inventario[tipo] <= 0:
                del self.inventario[tipo]
            
            # Aplicar efeitos do consumo
            if tipo == "comida":
                # Reduzir fome
                self.necessidades["fome"] = max(0.0, self.necessidades["fome"] - quantidade_consumida * 0.5)
            elif tipo == "agua":
                # Reduzir sede
                self.necessidades["sede"] = max(0.0, self.necessidades["sede"] - quantidade_consumida * 0.7)
            
            return quantidade_consumida
        
        return 0.0
    
    def _ganhar_experiencia(self, habilidade, quantidade):
        """
        Aumenta o nível de uma habilidade.
        
        Args:
            habilidade (str): Nome da habilidade.
            quantidade (float): Quantidade de experiência a ser adicionada.
        """
        if habilidade in self.habilidades:
            # Aplicar modificador de inteligência
            quantidade *= self.genoma.genes["inteligencia"]
            
            # Aplicar modificador de aprendizado
            quantidade *= (1.0 + self.habilidades["aprendizado"])
            
            # Aumentar a habilidade
            self.habilidades[habilidade] = min(1.0, self.habilidades[habilidade] + quantidade)
    
    def _aprender(self, delta_tempo):
        """
        Atualiza o aprendizado passivo do Senciante.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Taxa base de aprendizado
        taxa_base = LEARNING_BASE_RATE * delta_tempo
        
        # Modificador baseado no gene de inteligência
        modificador_inteligencia = self.genoma.genes["inteligencia"]
        
        # Modificador baseado na habilidade de aprendizado
        modificador_habilidade = 1.0 + self.habilidades["aprendizado"]
        
        # Taxa final de aprendizado
        taxa_aprendizado = taxa_base * modificador_inteligencia * modificador_habilidade
        
        # Aprendizado passivo de todas as habilidades
        for habilidade in self.habilidades:
            ganho = taxa_aprendizado * 0.1  # Ganho reduzido para aprendizado passivo
            self.habilidades[habilidade] = min(1.0, self.habilidades[habilidade] + ganho)
    
    def _adicionar_memoria(self, tipo, conteudo, importancia=0.5):
        """
        Adiciona uma nova memória ao Senciante.
        
        Args:
            tipo (str): Tipo da memória.
            conteudo (str): Conteúdo da memória.
            importancia (float, optional): Importância da memória (0.0 a 1.0). Default é 0.5.
        """
        # Criar nova memória
        memoria = Memoria(tipo, conteudo, 0, importancia)  # Tempo será preenchido pelo motor de simulação
        
        # Adicionar à lista de memórias
        self.memoria.append(memoria)
        
        # Limitar número de memórias (manter as mais importantes)
        if len(self.memoria) > 50:
            # Ordenar por importância (decrescente)
            self.memoria.sort(key=lambda m: m.importancia, reverse=True)
            
            # Manter apenas as 50 mais importantes
            self.memoria = self.memoria[:50]
    
    def _atualizar_memorias(self, delta_tempo):
        """
        Atualiza as memórias do Senciante, esquecendo as menos importantes.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Atualizar cada memória
        memorias_atualizadas = []
        
        for memoria in self.memoria:
            # Envelhecer a memória
            if memoria.envelhecer(delta_tempo):
                # Manter memória se ainda for relevante
                memorias_atualizadas.append(memoria)
        
        self.memoria = memorias_atualizadas
    
    def _atualizar_relacoes(self, delta_tempo):
        """
        Atualiza as relações sociais do Senciante.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Atualizar cada relação
        relacoes_para_remover = []
        
        for senciante_id, relacao in self.relacoes.items():
            # Reduzir força da relação com o tempo
            relacao["forca"] *= (1.0 - RELATION_STRENGTH_DECAY_RATE * delta_tempo)
            
            # Marcar relações fracas para remoção
            if relacao["forca"] < RELATION_STRENGTH_THRESHOLD:
                relacoes_para_remover.append(senciante_id)
        
        # Remover relações fracas
        for senciante_id in relacoes_para_remover:
            del self.relacoes[senciante_id]
    
    def _atualizar_nivel_comunicacao(self):
        """
        Atualiza o nível de comunicação do Senciante com base na habilidade de comunicação.
        """
        # Determinar nível com base na habilidade de comunicação
        habilidade = self.habilidades["comunicacao"]
        
        for i, limiar in enumerate(COMMUNICATION_EVOLUTION_THRESHOLDS):
            if habilidade < limiar:
                self.nivel_comunicacao = i
                return
        
        # Se passou por todos os limiares, está no nível máximo
        self.nivel_comunicacao = len(COMMUNICATION_EVOLUTION_THRESHOLDS)
    
    def estabelecer_relacao(self, senciante_id, tipo, forca=0.5):
        """
        Estabelece ou atualiza uma relação com outro Senciante.
        
        Args:
            senciante_id (str): ID do outro Senciante.
            tipo (str): Tipo da relação.
            forca (float, optional): Força da relação (0.0 a 1.0). Default é 0.5.
        """
        # Verificar se o tipo é válido
        if tipo not in RELATION_TYPES:
            tipo = "conhecido"
        
        # Atualizar relação existente ou criar nova
        if senciante_id in self.relacoes:
            # Atualizar tipo se for mais "forte"
            tipos_ordem = {t: i for i, t in enumerate(RELATION_TYPES)}
            
            if tipos_ordem.get(tipo, 0) > tipos_ordem.get(self.relacoes[senciante_id]["tipo"], 0):
                self.relacoes[senciante_id]["tipo"] = tipo
            
            # Atualizar força
            self.relacoes[senciante_id]["forca"] = max(self.relacoes[senciante_id]["forca"], forca)
        else:
            # Criar nova relação
            self.relacoes[senciante_id] = {
                "tipo": tipo,
                "forca": forca
            }
    
    def fortalecer_relacao(self, senciante_id, valor=0.1):
        """
        Fortalece uma relação existente com outro Senciante.
        
        Args:
            senciante_id (str): ID do outro Senciante.
            valor (float, optional): Valor a ser adicionado à força. Default é 0.1.
            
        Returns:
            bool: True se a relação foi fortalecida, False se não existe.
        """
        if senciante_id in self.relacoes:
            self.relacoes[senciante_id]["forca"] = min(1.0, self.relacoes[senciante_id]["forca"] + valor)
            return True
        return False
    
    def enfraquecer_relacao(self, senciante_id, valor=0.1):
        """
        Enfraquece uma relação existente com outro Senciante.
        
        Args:
            senciante_id (str): ID do outro Senciante.
            valor (float, optional): Valor a ser subtraído da força. Default é 0.1.
            
        Returns:
            bool: True se a relação foi enfraquecida, False se não existe.
        """
        if senciante_id in self.relacoes:
            self.relacoes[senciante_id]["forca"] = max(0.0, self.relacoes[senciante_id]["forca"] - valor)
            return True
        return False
    
    def comunicar(self, outro_senciante, assunto):
        """
        Tenta comunicar um assunto a outro Senciante.
        
        Args:
            outro_senciante (Senciante): Outro Senciante para comunicar.
            assunto (dict): Informações sobre o assunto a ser comunicado.
            
        Returns:
            bool: True se a comunicação foi bem-sucedida, False caso contrário.
        """
        from utils.helpers import determinar_complexidade_comunicacao
        
        # Verificar capacidade de comunicação
        nivel_comunicacao1 = self.habilidades["comunicacao"]
        nivel_comunicacao2 = outro_senciante.habilidades["comunicacao"]
        
        # Determinar eficácia da comunicação
        eficacia = (nivel_comunicacao1 + nivel_comunicacao2) / 2.0
        
        # Determinar complexidade do assunto
        complexidade = determinar_complexidade_comunicacao(assunto)
        
        # Verificar se a comunicação foi bem-sucedida
        sucesso = eficacia >= complexidade
        
        if sucesso:
            # Transferir conhecimento
            if assunto["tipo"] == "tecnologia" and assunto["conteudo"] in self.tecnologias_conhecidas:
                if assunto["conteudo"] not in outro_senciante.tecnologias_conhecidas:
                    outro_senciante.tecnologias_conhecidas.append(assunto["conteudo"])
                    outro_senciante._adicionar_memoria(
                        "aprendizado",
                        f"Aprendi sobre {assunto['conteudo']} com {self.id}",
                        0.8
                    )
            
            # Fortalecer relação
            self.fortalecer_relacao(outro_senciante.id, 0.1)
            outro_senciante.fortalecer_relacao(self.id, 0.1)
            
            # Melhorar habilidade de comunicação
            self._ganhar_experiencia("comunicacao", 0.01)
            outro_senciante._ganhar_experiencia("comunicacao", 0.01)
        
        return sucesso
    
    def pode_reproduzir(self):
        """
        Verifica se o Senciante pode se reproduzir.
        
        Returns:
            bool: True se pode se reproduzir, False caso contrário.
        """
        # Verificar idade mínima
        if self.estado["idade"] < SENCIANTE_REPRODUCTION_MIN_AGE:
            return False
        
        # Verificar energia mínima
        if self.estado["energia"] < 0.5:
            return False
        
        # Verificar saúde mínima
        if self.estado["saude"] < 0.6:
            return False
        
        # Verificar felicidade mínima
        if self.estado["felicidade"] < 0.5:
            return False
        
        return True
    
    def reproduzir(self, outro_senciante, posicao=None):
        """
        Reproduz com outro Senciante para criar um novo Senciante.
        
        Args:
            outro_senciante (Senciante): Outro Senciante para reproduzir.
            posicao (list, optional): Posição para o novo Senciante. Se None, usa a média das posições dos progenitores.
            
        Returns:
            Senciante: Novo Senciante criado, ou None se a reprodução falhou.
        """
        # Verificar se ambos podem se reproduzir
        if not self.pode_reproduzir() or not outro_senciante.pode_reproduzir():
            return None
        
        # Combinar genomas
        novo_genoma = self.genoma.combinar(outro_senciante.genoma)
        
        # Determinar posição do novo Senciante
        if posicao is None:
            posicao = [
                (self.posicao[0] + outro_senciante.posicao[0]) / 2.0,
                (self.posicao[1] + outro_senciante.posicao[1]) / 2.0
            ]
        
        # Criar novo Senciante
        novo_senciante = Senciante(posicao, novo_genoma)
        
        # Estabelecer relações familiares
        novo_senciante.estabelecer_relacao(self.id, "familia", 0.8)
        novo_senciante.estabelecer_relacao(outro_senciante.id, "familia", 0.8)
        self.estabelecer_relacao(novo_senciante.id, "familia", 0.8)
        outro_senciante.estabelecer_relacao(novo_senciante.id, "familia", 0.8)
        
        # Registrar memória do evento
        self._adicionar_memoria(
            "reproducao",
            f"Tive um descendente com {outro_senciante.id}",
            0.9  # Importância alta
        )
        outro_senciante._adicionar_memoria(
            "reproducao",
            f"Tive um descendente com {self.id}",
            0.9  # Importância alta
        )
        
        # Consumir energia dos progenitores
        self.estado["energia"] *= 0.7
        outro_senciante.estado["energia"] *= 0.7
        
        return novo_senciante
    
    def esta_morto(self):
        """
        Verifica se o Senciante está morto.
        
        Returns:
            bool: True se o Senciante está morto, False caso contrário.
        """
        return self._verificar_morte()
    
    def to_dict(self):
        """
        Converte o Senciante para um dicionário.
        
        Returns:
            dict: Representação do Senciante como dicionário.
        """
        return {
            "id": self.id,
            "posicao": self.posicao,
            "genoma": self.genoma.to_dict(),
            "necessidades": self.necessidades,
            "estado": self.estado,
            "habilidades": self.habilidades,
            "memoria": [m.to_dict() for m in self.memoria],
            "relacoes": self.relacoes,
            "tecnologias_conhecidas": self.tecnologias_conhecidas,
            "inventario": self.inventario,
            "atividade_atual": self.atividade_atual,
            "nivel_comunicacao": {
                "indice": self.nivel_comunicacao,
                "estagio": COMMUNICATION_EVOLUTION_STAGES[self.nivel_comunicacao]
            }
        }

