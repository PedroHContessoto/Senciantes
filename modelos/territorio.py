"""
Módulo que define a classe Territorio para o jogo "O Mundo dos Senciantes".
O Territorio representa uma área do mundo com características e controle.
"""

import random
from utils.helpers import gerar_id, calcular_distancia

class Territorio:
    """
    Classe que representa um território no mundo.
    Contém informações sobre recursos, controle, fronteiras e cultura.
    """
    
    def __init__(self, nome=None, posicao_central=None, raio=None, mundo=None):
        """
        Inicializa um novo Território.
        
        Args:
            nome (str, optional): Nome do território. Se None, gera um nome aleatório.
            posicao_central (list, optional): Posição central do território [x, y]. Se None, escolhe aleatoriamente.
            raio (float, optional): Raio do território. Se None, gera aleatoriamente.
            mundo (Mundo, optional): Objeto mundo para referência.
        """
        self.id = gerar_id()
        self.nome = nome if nome else self._gerar_nome_aleatorio()
        self.posicao_central = posicao_central if posicao_central else [random.uniform(0, mundo.tamanho[0]), random.uniform(0, mundo.tamanho[1])] if mundo else [50, 50]
        self.raio = raio if raio is not None else random.uniform(5, 20)
        
        # Recursos e características
        self.recursos_principais = []  # Lista de tipos de recursos abundantes
        self.bioma_predominante = None
        self.nivel_desenvolvimento = 0.1
        
        # Controle e influência
        self.controlador_id = None  # ID do Senciante ou grupo que controla o território
        self.influencia = {}  # Dicionário de senciante_id/grupo_id: nível_influencia
        self.fronteiras_definidas = False
        
        # Cultura e história
        self.cultura_local = None  # Referência a um objeto Cultura
        self.eventos_historicos = []  # Eventos importantes ocorridos no território
        self.locais_sagrados = []  # Lista de posições de locais sagrados
        
        # Mapa (se explorado)
        self.mapa_conhecido = None  # Representação do mapa do território
        
        # Inicializar características com base no mundo (se fornecido)
        if mundo:
            self._inicializar_caracteristicas(mundo)
    
    def _gerar_nome_aleatorio(self):
        """
        Gera um nome aleatório para o território.
        
        Returns:
            str: Nome do território.
        """
        prefixos = ["Vale", "Montanhas", "Planícies", "Floresta", "Costa", "Deserto", "Pântano"]
        sufixos = ["Esquecido", "Antigo", "Dourado", "Sombrio", "Perdido", "Sagrado", "Proibido"]
        
        return f"{random.choice(prefixos)} {random.choice(sufixos)}"
    
    def _inicializar_caracteristicas(self, mundo):
        """
        Inicializa as características do território com base no mundo.
        
        Args:
            mundo (Mundo): Objeto mundo para referência.
        """
        # Determinar bioma predominante
        biomas_no_territorio = {}
        for x in range(int(self.posicao_central[0] - self.raio), int(self.posicao_central[0] + self.raio)):
            for y in range(int(self.posicao_central[1] - self.raio), int(self.posicao_central[1] + self.raio)):
                if 0 <= x < mundo.tamanho[0] and 0 <= y < mundo.tamanho[1]:
                    dist = calcular_distancia(self.posicao_central, [x, y])
                    if dist <= self.raio:
                        bioma = mundo.obter_bioma([x,y])
                        biomas_no_territorio[bioma] = biomas_no_territorio.get(bioma, 0) + 1
        
        if biomas_no_territorio:
            self.bioma_predominante = max(biomas_no_territorio, key=biomas_no_territorio.get)
        
        # Identificar recursos principais
        recursos_no_territorio = {}
        for recurso in mundo.recursos.values():
            dist = calcular_distancia(self.posicao_central, recurso.posicao)
            if dist <= self.raio:
                recursos_no_territorio[recurso.tipo] = recursos_no_territorio.get(recurso.tipo, 0) + recurso.quantidade
        
        # Selecionar os 2 recursos mais abundantes
        if recursos_no_territorio:
            recursos_ordenados = sorted(recursos_no_territorio.items(), key=lambda item: item[1], reverse=True)
            self.recursos_principais = [r[0] for r in recursos_ordenados[:2]]
    
    def atualizar(self, delta_tempo, mundo):
        """
        Atualiza o estado do território.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            mundo (Mundo): Objeto mundo atual.
        """
        # Lógica de atualização do território (ex: mudança de controle, desenvolvimento)
        pass
    
    def definir_controlador(self, senciante_id_ou_grupo_id):
        """
        Define o controlador do território.
        
        Args:
            senciante_id_ou_grupo_id (str): ID do Senciante ou grupo controlador.
        """
        self.controlador_id = senciante_id_ou_grupo_id
        # Resetar influências ao mudar o controlador principal
        self.influencia = {senciante_id_ou_grupo_id: 1.0}
    
    def adicionar_influencia(self, senciante_id_ou_grupo_id, nivel_influencia):
        """
        Adiciona ou atualiza a influência de um Senciante ou grupo no território.
        
        Args:
            senciante_id_ou_grupo_id (str): ID do Senciante ou grupo.
            nivel_influencia (float): Nível de influência (0.0 a 1.0).
        """
        self.influencia[senciante_id_ou_grupo_id] = min(1.0, max(0.0, nivel_influencia))
    
    def registrar_evento_historico(self, descricao, tempo):
        """
        Registra um evento histórico no território.
        
        Args:
            descricao (str): Descrição do evento.
            tempo (float): Tempo da simulação em que o evento ocorreu.
        """
        self.eventos_historicos.append({"descricao": descricao, "tempo": tempo})
    
    def adicionar_local_sagrado(self, posicao, nome):
        """
        Adiciona um local sagrado ao território.
        
        Args:
            posicao (list): Posição do local sagrado [x, y].
            nome (str): Nome do local sagrado.
        """
        self.locais_sagrados.append({"nome": nome, "posicao": posicao})
    
    def gerar_mapa_primitivo(self, senciante_explorador, mundo):
        """
        Gera um mapa primitivo do território com base na exploração.
        
        Args:
            senciante_explorador (Senciante): Senciante que está explorando.
            mundo (Mundo): Objeto mundo para referência.
        """
        # Simplificação: o mapa é uma lista de pontos de interesse conhecidos
        # Em uma implementação mais complexa, poderia ser uma grade ou grafo
        
        pontos_interesse = []
        
        # Adicionar recursos conhecidos pelo Senciante dentro do território
        for memoria in senciante_explorador.memoria:
            if memoria.tipo == "localizacao" and "recurso" in memoria.conteudo:
                # Extrair posição da memória (simplificado)
                try:
                    pos_str = memoria.conteudo.split("em ")[-1].replace("[", "").replace("]", "")
                    pos = [float(p.strip()) for p in pos_str.split(",")]
                    if calcular_distancia(self.posicao_central, pos) <= self.raio:
                        pontos_interesse.append({"tipo": "recurso", "posicao": pos, "descricao": memoria.conteudo})
                except:
                    pass # Ignorar se não conseguir parsear a posição
        
        # Adicionar construções conhecidas
        for construcao in mundo.construcoes.values():
            if calcular_distancia(self.posicao_central, construcao.posicao) <= self.raio:
                 # Verificar se o Senciante conhece a construção (simplificado)
                if calcular_distancia(senciante_explorador.posicao, construcao.posicao) < senciante_explorador.habilidades["percepcao"] * 20:
                    pontos_interesse.append({"tipo": "construcao", "posicao": construcao.posicao, "descricao": construcao.tipo})
        
        self.mapa_conhecido = {
            "territorio_id": self.id,
            "nome_territorio": self.nome,
            "explorador_id": senciante_explorador.id,
            "pontos_interesse": pontos_interesse
        }
        return self.mapa_conhecido

    def to_dict(self):
        """
        Converte o território para um dicionário.
        
        Returns:
            dict: Representação do território como dicionário.
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "posicao_central": self.posicao_central,
            "raio": self.raio,
            "recursos_principais": self.recursos_principais,
            "bioma_predominante": self.bioma_predominante,
            "nivel_desenvolvimento": self.nivel_desenvolvimento,
            "controlador_id": self.controlador_id,
            "influencia": self.influencia,
            "cultura_local_id": self.cultura_local.id if self.cultura_local else None,
            "num_eventos_historicos": len(self.eventos_historicos),
            "num_locais_sagrados": len(self.locais_sagrados),
            "mapa_conhecido": bool(self.mapa_conhecido)
        }

