"""
Módulo que define a classe ArtefatoCultural para o jogo "O Mundo dos Senciantes".
O ArtefatoCultural representa objetos com significado cultural e simbólico.
"""

import random
from utils.helpers import gerar_id

class ArtefatoCultural:
    """
    Classe que representa um artefato cultural no mundo.
    Contém informações sobre significado, criação e efeitos.
    """
    
    def __init__(self, nome=None, tipo=None, criador_id=None, posicao=None):
        """
        Inicializa um novo Artefato Cultural.
        
        Args:
            nome (str, optional): Nome do artefato. Se None, gera um nome aleatório.
            tipo (str, optional): Tipo do artefato. Se None, escolhe aleatoriamente.
            criador_id (str, optional): ID do Senciante criador. Se None, é considerado de origem desconhecida.
            posicao (list, optional): Posição do artefato [x, y]. Se None, deve ser definida posteriormente.
        """
        self.id = gerar_id()
        self.nome = nome if nome else self._gerar_nome_aleatorio()
        self.tipo = tipo if tipo else self._escolher_tipo_aleatorio()
        self.criador_id = criador_id
        self.posicao = posicao
        
        # Características
        self.significado = self._gerar_significado()
        self.valor_cultural = random.uniform(0.3, 1.0)
        self.idade = 0.0  # Idade em horas
        self.estado = 1.0  # Estado de conservação (0.0 a 1.0)
        
        # Efeitos
        self.efeitos = self._gerar_efeitos()
        
        # História
        self.eventos = []  # Eventos relacionados ao artefato
        self.proprietarios = []  # Lista de proprietários ao longo do tempo
        if criador_id:
            self.proprietarios.append({"id": criador_id, "tempo_inicio": 0.0, "tempo_fim": None})
    
    def _gerar_nome_aleatorio(self):
        """
        Gera um nome aleatório para o artefato.
        
        Returns:
            str: Nome do artefato.
        """
        prefixos = ["Totem", "Ídolo", "Amuleto", "Símbolo", "Relíquia", "Talismã", "Emblema"]
        sufixos = ["Sagrado", "Ancestral", "Eterno", "Divino", "Místico", "Protetor", "Iluminado"]
        
        return f"{random.choice(prefixos)} {random.choice(sufixos)}"
    
    def _escolher_tipo_aleatorio(self):
        """
        Escolhe um tipo aleatório para o artefato.
        
        Returns:
            str: Tipo do artefato.
        """
        tipos = ["escultura", "pintura", "instrumento_musical", "vestimenta", "ferramenta_ritual", "escrita", "joia"]
        
        return random.choice(tipos)
    
    def _gerar_significado(self):
        """
        Gera um significado para o artefato com base no tipo.
        
        Returns:
            str: Significado do artefato.
        """
        significados = {
            "escultura": ["representação divina", "símbolo de fertilidade", "proteção contra espíritos", "homenagem ancestral"],
            "pintura": ["registro histórico", "visão profética", "mapa estelar", "representação de sonhos"],
            "instrumento_musical": ["comunicação com divindades", "invocação de espíritos", "celebração de colheita", "ritual de passagem"],
            "vestimenta": ["status social", "proteção espiritual", "identidade tribal", "conexão com antepassados"],
            "ferramenta_ritual": ["cura de doenças", "previsão do futuro", "purificação", "comunicação com o além"],
            "escrita": ["conhecimento sagrado", "leis ancestrais", "profecias", "história do povo"],
            "joia": ["símbolo de poder", "amuleto de proteção", "conexão com elementos naturais", "status social"]
        }
        
        if self.tipo in significados:
            return random.choice(significados[self.tipo])
        else:
            return "objeto de significado cultural"
    
    def _gerar_efeitos(self):
        """
        Gera efeitos do artefato com base no tipo e significado.
        
        Returns:
            dict: Dicionário de efeitos.
        """
        efeitos = {}
        
        # Efeitos comuns a todos os artefatos
        efeitos["coesao_social"] = random.uniform(0.1, 0.3) * self.valor_cultural
        
        # Efeitos específicos por tipo
        if self.tipo == "escultura":
            efeitos["espiritualidade"] = random.uniform(0.2, 0.4) * self.valor_cultural
        
        elif self.tipo == "pintura":
            efeitos["conhecimento"] = random.uniform(0.1, 0.3) * self.valor_cultural
            efeitos["criatividade"] = random.uniform(0.2, 0.4) * self.valor_cultural
        
        elif self.tipo == "instrumento_musical":
            efeitos["felicidade"] = random.uniform(0.2, 0.5) * self.valor_cultural
            efeitos["comunicacao"] = random.uniform(0.1, 0.3) * self.valor_cultural
        
        elif self.tipo == "vestimenta":
            efeitos["status"] = random.uniform(0.2, 0.5) * self.valor_cultural
            efeitos["identidade_grupo"] = random.uniform(0.3, 0.6) * self.valor_cultural
        
        elif self.tipo == "ferramenta_ritual":
            efeitos["espiritualidade"] = random.uniform(0.3, 0.6) * self.valor_cultural
            if "cura" in self.significado:
                efeitos["saude"] = random.uniform(0.1, 0.2) * self.valor_cultural
        
        elif self.tipo == "escrita":
            efeitos["conhecimento"] = random.uniform(0.3, 0.6) * self.valor_cultural
            efeitos["memoria_cultural"] = random.uniform(0.4, 0.7) * self.valor_cultural
        
        elif self.tipo == "joia":
            efeitos["status"] = random.uniform(0.3, 0.6) * self.valor_cultural
            efeitos["diplomacia"] = random.uniform(0.2, 0.4) * self.valor_cultural
        
        return efeitos
    
    def atualizar(self, delta_tempo):
        """
        Atualiza o estado do artefato.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Aumentar idade
        self.idade += delta_tempo
        
        # Deterioração natural (muito lenta)
        self.estado -= 0.00001 * delta_tempo
        self.estado = max(0.0, self.estado)
    
    def mudar_proprietario(self, novo_proprietario_id, tempo):
        """
        Muda o proprietário do artefato.
        
        Args:
            novo_proprietario_id (str): ID do novo proprietário.
            tempo (float): Tempo da simulação em que ocorreu a mudança.
        """
        # Atualizar o proprietário atual
        if self.proprietarios and self.proprietarios[-1]["tempo_fim"] is None:
            self.proprietarios[-1]["tempo_fim"] = tempo
        
        # Adicionar novo proprietário
        self.proprietarios.append({
            "id": novo_proprietario_id,
            "tempo_inicio": tempo,
            "tempo_fim": None
        })
        
        # Registrar evento
        self.registrar_evento("mudanca_proprietario", f"Artefato passou para novo proprietário", tempo)
    
    def registrar_evento(self, tipo, descricao, tempo):
        """
        Registra um evento relacionado ao artefato.
        
        Args:
            tipo (str): Tipo do evento.
            descricao (str): Descrição do evento.
            tempo (float): Tempo da simulação em que ocorreu o evento.
        """
        self.eventos.append({
            "tipo": tipo,
            "descricao": descricao,
            "tempo": tempo
        })
    
    def aplicar_efeitos(self, senciante):
        """
        Aplica os efeitos do artefato a um Senciante.
        
        Args:
            senciante (Senciante): Senciante afetado.
            
        Returns:
            dict: Dicionário de efeitos aplicados.
        """
        efeitos_aplicados = {}
        
        # Aplicar efeitos relevantes
        if "felicidade" in self.efeitos:
            senciante.estado["felicidade"] = min(1.0, senciante.estado["felicidade"] + self.efeitos["felicidade"] * 0.1)
            efeitos_aplicados["felicidade"] = self.efeitos["felicidade"] * 0.1
        
        if "saude" in self.efeitos:
            senciante.estado["saude"] = min(1.0, senciante.estado["saude"] + self.efeitos["saude"] * 0.05)
            efeitos_aplicados["saude"] = self.efeitos["saude"] * 0.05
        
        # Outros efeitos são mais abstratos e afetam a sociedade ou grupo como um todo
        
        return efeitos_aplicados
    
    def to_dict(self):
        """
        Converte o artefato cultural para um dicionário.
        
        Returns:
            dict: Representação do artefato como dicionário.
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "criador_id": self.criador_id,
            "posicao": self.posicao,
            "significado": self.significado,
            "valor_cultural": self.valor_cultural,
            "idade": self.idade,
            "estado": self.estado,
            "efeitos": self.efeitos,
            "num_eventos": len(self.eventos),
            "num_proprietarios": len(self.proprietarios),
            "proprietario_atual": self.proprietarios[-1]["id"] if self.proprietarios else None
        }

