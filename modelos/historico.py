"""
Módulo que define a classe Historico para o jogo "O Mundo dos Senciantes".
O Historico registra eventos e estatísticas do mundo ao longo do tempo.
"""

from utils.config import HISTORY_MAX_EVENTS
from utils.helpers import registrar_evento

class Historico:
    """
    Classe que representa o histórico do mundo.
    Registra eventos, estatísticas e avanços ao longo do tempo.
    """
    
    def __init__(self):
        """
        Inicializa um novo Histórico.
        """
        self.eventos = []  # Lista de eventos
        self.estatisticas = {
            "populacao": [],  # Lista de [tempo, quantidade]
            "recursos": {},   # Dicionário de tipo_recurso: lista de [tempo, quantidade]
            "tecnologias": [],  # Lista de [tempo, tecnologia]
            "construcoes": [],  # Lista de [tempo, tipo_construcao]
            "mortes": [],       # Lista de [tempo, causa]
            "nascimentos": []   # Lista de [tempo]
        }
        self.genealogia = {}  # Dicionário de senciante_id: {progenitores: [], descendentes: []}
        self.avancos = []  # Lista de avanços tecnológicos e culturais
        self.palavras_inventadas = {}  # Dicionário de palavra: {significado, inventor_id, tempo}
        self.conceitos_filosoficos = []  # Lista de conceitos filosóficos
        self.religioes = []  # Lista de religiões
    
    def registrar_evento(self, tipo, descricao, tempo, envolvidos=None):
        """
        Registra um novo evento no histórico.
        
        Args:
            tipo (str): Tipo do evento.
            descricao (str): Descrição do evento.
            tempo (float): Tempo da simulação em que o evento ocorreu.
            envolvidos (list, optional): Lista de IDs de entidades envolvidas no evento.
            
        Returns:
            dict: Objeto do evento registrado.
        """
        evento = registrar_evento(tipo, descricao, tempo, envolvidos)
        
        # Adicionar evento à lista
        self.eventos.append(evento)
        
        # Limitar o número de eventos
        if len(self.eventos) > HISTORY_MAX_EVENTS:
            self.eventos = self.eventos[-HISTORY_MAX_EVENTS:]
        
        return evento
    
    def registrar_estatisticas(self, tempo, populacao, recursos=None):
        """
        Registra estatísticas do mundo em um determinado momento.
        
        Args:
            tempo (float): Tempo da simulação.
            populacao (int): Quantidade de Senciantes.
            recursos (dict, optional): Dicionário de tipo_recurso: quantidade.
        """
        # Registrar população
        self.estatisticas["populacao"].append([tempo, populacao])
        
        # Registrar recursos
        if recursos:
            for tipo, quantidade in recursos.items():
                if tipo not in self.estatisticas["recursos"]:
                    self.estatisticas["recursos"][tipo] = []
                
                self.estatisticas["recursos"][tipo].append([tempo, quantidade])
    
    def registrar_nascimento(self, tempo, senciante_id, progenitores):
        """
        Registra o nascimento de um Senciante.
        
        Args:
            tempo (float): Tempo da simulação.
            senciante_id (str): ID do Senciante nascido.
            progenitores (list): Lista de IDs dos progenitores.
        """
        # Registrar na lista de nascimentos
        self.estatisticas["nascimentos"].append([tempo])
        
        # Registrar na genealogia
        self.genealogia[senciante_id] = {
            "progenitores": progenitores,
            "descendentes": []
        }
        
        # Atualizar genealogia dos progenitores
        for progenitor_id in progenitores:
            if progenitor_id in self.genealogia:
                self.genealogia[progenitor_id]["descendentes"].append(senciante_id)
            else:
                self.genealogia[progenitor_id] = {
                    "progenitores": [],
                    "descendentes": [senciante_id]
                }
        
        # Registrar evento
        self.registrar_evento(
            "nascimento",
            f"Nascimento de um novo Senciante",
            tempo,
            [senciante_id] + progenitores
        )
    
    def registrar_morte(self, tempo, senciante_id, causa):
        """
        Registra a morte de um Senciante.
        
        Args:
            tempo (float): Tempo da simulação.
            senciante_id (str): ID do Senciante morto.
            causa (str): Causa da morte.
        """
        # Registrar na lista de mortes
        self.estatisticas["mortes"].append([tempo, causa])
        
        # Registrar evento
        self.registrar_evento(
            "morte",
            f"Morte de um Senciante por {causa}",
            tempo,
            [senciante_id]
        )
    
    def registrar_tecnologia(self, tempo, tecnologia, inventor_id):
        """
        Registra a descoberta de uma nova tecnologia.
        
        Args:
            tempo (float): Tempo da simulação.
            tecnologia (str): Nome da tecnologia descoberta.
            inventor_id (str): ID do Senciante inventor.
        """
        # Registrar na lista de tecnologias
        self.estatisticas["tecnologias"].append([tempo, tecnologia])
        
        # Registrar nos avanços
        self.avancos.append({
            "tipo": "tecnologia",
            "nome": tecnologia,
            "inventor_id": inventor_id,
            "tempo": tempo
        })
        
        # Registrar evento
        self.registrar_evento(
            "descoberta",
            f"Descoberta da tecnologia: {tecnologia}",
            tempo,
            [inventor_id]
        )
    
    def registrar_construcao(self, tempo, tipo_construcao, construtor_id):
        """
        Registra a construção de uma nova estrutura.
        
        Args:
            tempo (float): Tempo da simulação.
            tipo_construcao (str): Tipo da construção.
            construtor_id (str): ID do Senciante construtor.
        """
        # Registrar na lista de construções
        self.estatisticas["construcoes"].append([tempo, tipo_construcao])
        
        # Registrar evento
        self.registrar_evento(
            "construcao",
            f"Construção de {tipo_construcao}",
            tempo,
            [construtor_id]
        )
    
    def registrar_palavra(self, tempo, palavra, significado, inventor_id):
        """
        Registra a invenção de uma nova palavra.
        
        Args:
            tempo (float): Tempo da simulação.
            palavra (str): Palavra inventada.
            significado (str): Significado da palavra.
            inventor_id (str): ID do Senciante inventor.
        """
        # Registrar no dicionário de palavras
        self.palavras_inventadas[palavra] = {
            "significado": significado,
            "inventor_id": inventor_id,
            "tempo": tempo
        }
        
        # Registrar evento
        self.registrar_evento(
            "linguagem",
            f"Nova palavra inventada: {palavra} ({significado})",
            tempo,
            [inventor_id]
        )
    
    def registrar_conceito_filosofico(self, tempo, conceito, criador_id):
        """
        Registra a criação de um novo conceito filosófico.
        
        Args:
            tempo (float): Tempo da simulação.
            conceito (str): Descrição do conceito.
            criador_id (str): ID do Senciante criador.
        """
        # Registrar na lista de conceitos
        self.conceitos_filosoficos.append({
            "conceito": conceito,
            "criador_id": criador_id,
            "tempo": tempo
        })
        
        # Registrar nos avanços
        self.avancos.append({
            "tipo": "filosofia",
            "nome": conceito,
            "inventor_id": criador_id,
            "tempo": tempo
        })
        
        # Registrar evento
        self.registrar_evento(
            "filosofia",
            f"Novo conceito filosófico: {conceito}",
            tempo,
            [criador_id]
        )
    
    def registrar_religiao(self, tempo, nome, fundador_id, crenças):
        """
        Registra a fundação de uma nova religião.
        
        Args:
            tempo (float): Tempo da simulação.
            nome (str): Nome da religião.
            fundador_id (str): ID do Senciante fundador.
            crenças (list): Lista de crenças da religião.
        """
        # Registrar na lista de religiões
        self.religioes.append({
            "nome": nome,
            "fundador_id": fundador_id,
            "crenças": crenças,
            "tempo": tempo,
            "seguidores": [fundador_id]
        })
        
        # Registrar nos avanços
        self.avancos.append({
            "tipo": "religiao",
            "nome": nome,
            "inventor_id": fundador_id,
            "tempo": tempo
        })
        
        # Registrar evento
        self.registrar_evento(
            "religiao",
            f"Fundação da religião: {nome}",
            tempo,
            [fundador_id]
        )
    
    def adicionar_seguidor_religiao(self, nome_religiao, seguidor_id):
        """
        Adiciona um seguidor a uma religião existente.
        
        Args:
            nome_religiao (str): Nome da religião.
            seguidor_id (str): ID do Senciante seguidor.
            
        Returns:
            bool: True se o seguidor foi adicionado, False se a religião não existe.
        """
        for religiao in self.religioes:
            if religiao["nome"] == nome_religiao:
                if seguidor_id not in religiao["seguidores"]:
                    religiao["seguidores"].append(seguidor_id)
                return True
        
        return False
    
    def obter_eventos_por_tipo(self, tipo):
        """
        Obtém eventos de um determinado tipo.
        
        Args:
            tipo (str): Tipo de evento a ser filtrado.
            
        Returns:
            list: Lista de eventos do tipo especificado.
        """
        return [e for e in self.eventos if e["tipo"] == tipo]
    
    def obter_eventos_por_envolvido(self, senciante_id):
        """
        Obtém eventos que envolvem um determinado Senciante.
        
        Args:
            senciante_id (str): ID do Senciante.
            
        Returns:
            list: Lista de eventos que envolvem o Senciante.
        """
        return [e for e in self.eventos if "envolvidos" in e and senciante_id in e["envolvidos"]]
    
    def obter_eventos_por_periodo(self, tempo_inicio, tempo_fim):
        """
        Obtém eventos ocorridos em um determinado período.
        
        Args:
            tempo_inicio (float): Tempo inicial.
            tempo_fim (float): Tempo final.
            
        Returns:
            list: Lista de eventos ocorridos no período.
        """
        return [e for e in self.eventos if tempo_inicio <= e["tempo"] <= tempo_fim]
    
    def obter_arvore_genealogica(self, senciante_id, gerações_acima=2, gerações_abaixo=2):
        """
        Obtém a árvore genealógica de um Senciante.
        
        Args:
            senciante_id (str): ID do Senciante.
            gerações_acima (int, optional): Número de gerações acima a incluir. Default é 2.
            gerações_abaixo (int, optional): Número de gerações abaixo a incluir. Default é 2.
            
        Returns:
            dict: Árvore genealógica do Senciante.
        """
        if senciante_id not in self.genealogia:
            return {"progenitores": [], "descendentes": []}
        
        arvore = {
            "id": senciante_id,
            "progenitores": [],
            "descendentes": []
        }
        
        # Adicionar progenitores recursivamente
        if gerações_acima > 0:
            for progenitor_id in self.genealogia[senciante_id]["progenitores"]:
                if progenitor_id in self.genealogia:
                    arvore["progenitores"].append(
                        self.obter_arvore_genealogica(
                            progenitor_id,
                            gerações_acima - 1,
                            0  # Não incluir descendentes dos progenitores
                        )
                    )
        
        # Adicionar descendentes recursivamente
        if gerações_abaixo > 0:
            for descendente_id in self.genealogia[senciante_id]["descendentes"]:
                if descendente_id in self.genealogia:
                    arvore["descendentes"].append(
                        self.obter_arvore_genealogica(
                            descendente_id,
                            0,  # Não incluir progenitores dos descendentes
                            gerações_abaixo - 1
                        )
                    )
        
        return arvore
    
    def to_dict(self):
        """
        Converte o histórico para um dicionário.
        
        Returns:
            dict: Representação do histórico como dicionário.
        """
        return {
            "eventos": self.eventos[-100:],  # Limitar a 100 eventos mais recentes
            "estatisticas": self.estatisticas,
            "avancos": self.avancos,
            "palavras_inventadas": len(self.palavras_inventadas),
            "conceitos_filosoficos": len(self.conceitos_filosoficos),
            "religioes": [
                {
                    "nome": r["nome"],
                    "seguidores": len(r["seguidores"])
                } for r in self.religioes
            ]
        }



