"""
Módulo que define a classe Doenca para o jogo "O Mundo dos Senciantes".
A Doenca representa uma condição que afeta a saúde dos Senciantes.
"""

import random
from utils.helpers import gerar_id, chance

class Doenca:
    """
    Classe que representa uma doença no mundo.
    Contém características, sintomas, transmissão e efeitos.
    """
    
    def __init__(self, nome=None, tipo=None, gravidade=None, transmissibilidade=None, duracao=None):
        """
        Inicializa uma nova Doença.
        
        Args:
            nome (str, optional): Nome da doença. Se None, gera um nome aleatório.
            tipo (str, optional): Tipo da doença. Se None, escolhe aleatoriamente.
            gravidade (float, optional): Gravidade da doença (0.0 a 1.0). Se None, gera aleatoriamente.
            transmissibilidade (float, optional): Taxa de transmissão (0.0 a 1.0). Se None, gera aleatoriamente.
            duracao (float, optional): Duração média em horas. Se None, gera aleatoriamente.
        """
        self.id = gerar_id()
        self.nome = nome if nome else self._gerar_nome_aleatorio()
        self.tipo = tipo if tipo else self._escolher_tipo_aleatorio()
        self.gravidade = gravidade if gravidade is not None else random.uniform(0.1, 0.9)
        self.transmissibilidade = transmissibilidade if transmissibilidade is not None else random.uniform(0.1, 0.9)
        self.duracao = duracao if duracao is not None else random.uniform(24.0, 168.0)  # 1 a 7 dias
        
        # Sintomas e efeitos
        self.sintomas = self._gerar_sintomas()
        self.efeitos = self._gerar_efeitos()
        
        # Resistência a tratamentos
        self.resistencia_tratamento = random.uniform(0.0, 0.5)
        
        # Condições de surgimento
        self.condicoes_surgimento = self._definir_condicoes_surgimento()
        
        # Mutações possíveis
        self.mutacoes_possiveis = []
        
        # Histórico de propagação
        self.historico_propagacao = []
    
    def _gerar_nome_aleatorio(self):
        """
        Gera um nome aleatório para a doença.
        
        Returns:
            str: Nome da doença.
        """
        prefixos = ["Febre", "Peste", "Mal", "Síndrome", "Infecção", "Doença"]
        sufixos = ["Vermelha", "Negra", "Branca", "do Sono", "Silenciosa", "Errante", "Sombria", "Aguda"]
        
        return f"{random.choice(prefixos)} {random.choice(sufixos)}"
    
    def _escolher_tipo_aleatorio(self):
        """
        Escolhe um tipo aleatório para a doença.
        
        Returns:
            str: Tipo da doença.
        """
        tipos = ["viral", "bacteriana", "parasitária", "fúngica", "degenerativa", "nutricional"]
        
        return random.choice(tipos)
    
    def _gerar_sintomas(self):
        """
        Gera sintomas para a doença com base no tipo e gravidade.
        
        Returns:
            list: Lista de sintomas.
        """
        todos_sintomas = {
            "viral": ["febre", "fadiga", "dores musculares", "tosse", "espirros", "congestão"],
            "bacteriana": ["febre alta", "inflamação", "dor localizada", "inchaço", "pus"],
            "parasitária": ["diarreia", "náusea", "dor abdominal", "perda de peso", "fraqueza"],
            "fúngica": ["coceira", "erupções cutâneas", "descamação", "vermelhidão"],
            "degenerativa": ["perda de coordenação", "fraqueza muscular", "confusão mental"],
            "nutricional": ["fraqueza", "tontura", "palidez", "unhas quebradiças"]
        }
        
        # Sintomas gerais
        sintomas_gerais = ["mal-estar", "perda de apetite", "irritabilidade"]
        
        # Selecionar sintomas específicos do tipo
        num_sintomas = max(1, int(self.gravidade * 5))
        sintomas_especificos = random.sample(todos_sintomas.get(self.tipo, []), min(num_sintomas, len(todos_sintomas.get(self.tipo, []))))
        
        # Adicionar sintomas gerais
        sintomas = sintomas_especificos + random.sample(sintomas_gerais, min(2, len(sintomas_gerais)))
        
        return sintomas
    
    def _gerar_efeitos(self):
        """
        Gera efeitos da doença nos Senciantes.
        
        Returns:
            dict: Dicionário de efeitos.
        """
        return {
            "saude": -0.1 * self.gravidade,  # Redução na saúde por hora
            "energia": -0.05 * self.gravidade,  # Redução na energia por hora
            "fome": 0.02 * self.gravidade,  # Aumento na fome por hora
            "sede": 0.03 * self.gravidade,  # Aumento na sede por hora
            "velocidade": -0.3 * self.gravidade,  # Redução na velocidade
            "percepcao": -0.2 * self.gravidade  # Redução na percepção
        }
    
    def _definir_condicoes_surgimento(self):
        """
        Define as condições para o surgimento da doença.
        
        Returns:
            dict: Dicionário de condições de surgimento.
        """
        condicoes = {}
        
        # Condições baseadas no tipo
        if self.tipo == "viral" or self.tipo == "bacteriana":
            condicoes["densidade_populacional"] = random.uniform(0.5, 0.9)  # Densidade populacional mínima
            condicoes["higiene"] = random.uniform(0.0, 0.5)  # Nível máximo de higiene
        
        elif self.tipo == "parasitária":
            condicoes["bioma"] = random.choice(["floresta", "pantano", "planicie"])
            condicoes["temperatura"] = random.uniform(0.6, 0.9)  # Temperatura mínima (normalizada)
        
        elif self.tipo == "fúngica":
            condicoes["umidade"] = random.uniform(0.7, 1.0)  # Umidade mínima
            condicoes["temperatura"] = random.uniform(0.4, 0.7)  # Temperatura mínima (normalizada)
        
        elif self.tipo == "nutricional":
            condicoes["escassez_alimentos"] = random.uniform(0.6, 0.9)  # Escassez mínima de alimentos
        
        return condicoes
    
    def verificar_condicoes_surgimento(self, ambiente):
        """
        Verifica se as condições ambientais favorecem o surgimento da doença.
        
        Args:
            ambiente (dict): Condições ambientais atuais.
            
        Returns:
            bool: True se as condições favorecem o surgimento, False caso contrário.
        """
        for condicao, valor in self.condicoes_surgimento.items():
            if condicao not in ambiente:
                return False
            
            if condicao == "higiene":
                # Para higiene, o valor ambiental deve ser MENOR que o valor da condição
                if ambiente[condicao] > valor:
                    return False
            else:
                # Para outras condições, o valor ambiental deve ser MAIOR que o valor da condição
                if ambiente[condicao] < valor:
                    return False
        
        return True
    
    def calcular_chance_transmissao(self, senciante_infectado, senciante_alvo):
        """
        Calcula a chance de transmissão da doença entre dois Senciantes.
        
        Args:
            senciante_infectado (Senciante): Senciante infectado.
            senciante_alvo (Senciante): Senciante alvo da transmissão.
            
        Returns:
            float: Chance de transmissão (0.0 a 1.0).
        """
        # Chance base de transmissão
        chance_base = self.transmissibilidade
        
        # Ajustar com base na distância
        distancia = ((senciante_infectado.posicao[0] - senciante_alvo.posicao[0])**2 + 
                     (senciante_infectado.posicao[1] - senciante_alvo.posicao[1])**2)**0.5
        
        if distancia > 2.0:
            chance_base *= 0.1  # Redução drástica para distâncias maiores
        
        # Ajustar com base na imunidade do alvo
        imunidade = senciante_alvo.modificadores.get("imunidade", 1.0)
        chance_base /= imunidade
        
        # Ajustar com base na higiene do alvo
        higiene = 1.0 - senciante_alvo.necessidades["higiene"]  # Inverter para que maior higiene = menor chance
        chance_base *= (2.0 - higiene)  # Fator entre 1.0 e 2.0
        
        return min(1.0, max(0.0, chance_base))
    
    def aplicar_efeitos(self, senciante, delta_tempo):
        """
        Aplica os efeitos da doença a um Senciante.
        
        Args:
            senciante (Senciante): Senciante afetado.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Aplicar efeitos na saúde
        senciante.estado["saude"] += self.efeitos["saude"] * delta_tempo
        
        # Aplicar efeitos na energia
        senciante.estado["energia"] += self.efeitos["energia"] * delta_tempo
        
        # Aplicar efeitos na fome
        senciante.necessidades["fome"] += self.efeitos["fome"] * delta_tempo
        
        # Aplicar efeitos na sede
        senciante.necessidades["sede"] += self.efeitos["sede"] * delta_tempo
        
        # Limitar valores
        senciante.estado["saude"] = max(0.0, min(1.0, senciante.estado["saude"]))
        senciante.estado["energia"] = max(0.0, min(1.0, senciante.estado["energia"]))
        senciante.necessidades["fome"] = max(0.0, min(1.0, senciante.necessidades["fome"]))
        senciante.necessidades["sede"] = max(0.0, min(1.0, senciante.necessidades["sede"]))
    
    def responder_tratamento(self, tipo_tratamento, eficacia_base):
        """
        Determina a eficácia de um tratamento contra a doença.
        
        Args:
            tipo_tratamento (str): Tipo de tratamento ("ervas", "ritual", "medicina_avancada").
            eficacia_base (float): Eficácia base do tratamento (0.0 a 1.0).
            
        Returns:
            float: Eficácia real do tratamento (0.0 a 1.0).
        """
        # Eficácia ajustada pela resistência da doença
        eficacia_ajustada = eficacia_base * (1.0 - self.resistencia_tratamento)
        
        # Ajustar com base no tipo de tratamento e tipo de doença
        if tipo_tratamento == "ervas":
            if self.tipo in ["viral", "bacteriana"]:
                eficacia_ajustada *= 0.7
            elif self.tipo == "fúngica":
                eficacia_ajustada *= 1.2
        
        elif tipo_tratamento == "ritual":
            # Rituais têm efeito principalmente psicológico
            eficacia_ajustada *= 0.5
        
        elif tipo_tratamento == "medicina_avancada":
            eficacia_ajustada *= 1.5
        
        return min(1.0, max(0.0, eficacia_ajustada))
    
    def mutar(self):
        """
        Cria uma mutação da doença.
        
        Returns:
            Doenca: Nova doença mutada.
        """
        # Chance de mudar o tipo
        novo_tipo = self.tipo
        if chance(0.1):
            tipos = ["viral", "bacteriana", "parasitária", "fúngica", "degenerativa", "nutricional"]
            tipos.remove(self.tipo)
            novo_tipo = random.choice(tipos)
        
        # Ajustar características
        nova_gravidade = min(1.0, max(0.1, self.gravidade + random.uniform(-0.2, 0.3)))
        nova_transmissibilidade = min(1.0, max(0.1, self.transmissibilidade + random.uniform(-0.2, 0.3)))
        nova_duracao = max(12.0, self.duracao + random.uniform(-24.0, 48.0))
        
        # Criar nova doença
        nova_doenca = Doenca(
            nome=f"{self.nome} Mutada",
            tipo=novo_tipo,
            gravidade=nova_gravidade,
            transmissibilidade=nova_transmissibilidade,
            duracao=nova_duracao
        )
        
        # Registrar relação
        self.mutacoes_possiveis.append(nova_doenca.id)
        
        return nova_doenca
    
    def registrar_propagacao(self, tempo, senciante_id):
        """
        Registra a propagação da doença para um novo Senciante.
        
        Args:
            tempo (float): Tempo da simulação.
            senciante_id (str): ID do Senciante infectado.
        """
        self.historico_propagacao.append({
            "tempo": tempo,
            "senciante_id": senciante_id
        })
    
    def to_dict(self):
        """
        Converte a doença para um dicionário.
        
        Returns:
            dict: Representação da doença como dicionário.
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "gravidade": self.gravidade,
            "transmissibilidade": self.transmissibilidade,
            "duracao": self.duracao,
            "sintomas": self.sintomas,
            "num_infectados": len(self.historico_propagacao)
        }


