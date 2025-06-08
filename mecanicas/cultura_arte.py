"""
Implementação das mecânicas de cultura material e arte para o jogo "O Mundo dos Senciantes".
"""

import random
import numpy as np
from modelos.artefato_cultural import ArtefatoCultural
from utils.helpers import chance, calcular_distancia

class MecanicaCulturaArte:
    """
    Classe que implementa as mecânicas de cultura material e arte.
    """
    
    def __init__(self, mundo):
        """
        Inicializa a mecânica de cultura material e arte.
        
        Args:
            mundo (Mundo): Objeto mundo para referência.
        """
        self.mundo = mundo
        self.artefatos = {}  # Dicionário de id_artefato: artefato
        self.locais_sagrados = {}  # Dicionário de id_local: local_sagrado
        self.tradicoes = {}  # Dicionário de id_tradicao: tradicao
        
        # Tipos de artefatos
        self.tipos_artefatos = [
            "pintura", "escultura", "instrumento_musical", "simbolo_religioso", 
            "objeto_ritual", "vestimenta_cerimonial", "mascara", "totem"
        ]
        
        # Tipos de locais sagrados
        self.tipos_locais_sagrados = [
            "templo", "altar", "monumento", "tumulo", "local_natural", 
            "circulo_ritual", "arvore_sagrada", "fonte_sagrada"
        ]
        
        # Tipos de tradições
        self.tipos_tradicoes = [
            "danca", "canto", "ritual", "festival", "cerimonia", 
            "narrativa_oral", "mito_fundador", "lenda"
        ]
    
    def atualizar(self, delta_tempo, senciantes):
        """
        Atualiza o estado da cultura material e arte no mundo.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Identificar grupos de Senciantes
        grupos = self._identificar_grupos(senciantes)
        
        # Chance de criação de novos artefatos
        self._verificar_criacao_artefatos(delta_tempo, grupos, senciantes)
        
        # Chance de estabelecimento de novos locais sagrados
        self._verificar_estabelecimento_locais_sagrados(delta_tempo, grupos, senciantes)
        
        # Chance de desenvolvimento de novas tradições
        self._verificar_desenvolvimento_tradicoes(delta_tempo, grupos, senciantes)
        
        # Atualizar influência cultural dos artefatos existentes
        self._atualizar_influencia_artefatos(delta_tempo, senciantes)
        
        # Atualizar influência dos locais sagrados
        self._atualizar_influencia_locais_sagrados(delta_tempo, senciantes)
        
        # Atualizar prática das tradições
        self._atualizar_pratica_tradicoes(delta_tempo, grupos, senciantes)
    
    def _identificar_grupos(self, senciantes):
        """
        Identifica grupos de Senciantes.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            dict: Dicionário de grupos identificados.
        """
        grupos = {}
        
        for senciante_id, senciante in senciantes.items():
            # Verificar se o Senciante tem um grupo
            grupo_id = senciante.grupo_id if hasattr(senciante, "grupo_id") else None
            
            # Se não tiver grupo, considerar como indivíduo
            if grupo_id is None:
                grupo_id = f"individual_{senciante_id}"
            
            # Adicionar ao dicionário de grupos
            if grupo_id not in grupos:
                grupos[grupo_id] = {
                    "membros": [],
                    "lider_id": None,
                    "posicao_media": [0.0, 0.0],
                    "nivel_cultural": 0.0,
                    "artefatos": [],
                    "locais_sagrados": [],
                    "tradicoes": []
                }
            
            grupos[grupo_id]["membros"].append(senciante_id)
            
            # Atualizar posição média
            if len(grupos[grupo_id]["membros"]) == 1:
                grupos[grupo_id]["posicao_media"] = senciante.posicao.copy()
            else:
                n = len(grupos[grupo_id]["membros"])
                grupos[grupo_id]["posicao_media"][0] = ((n - 1) * grupos[grupo_id]["posicao_media"][0] + senciante.posicao[0]) / n
                grupos[grupo_id]["posicao_media"][1] = ((n - 1) * grupos[grupo_id]["posicao_media"][1] + senciante.posicao[1]) / n
            
            # Calcular nível cultural
            nivel_cultural_individual = 0.0
            
            if hasattr(senciante, "habilidades"):
                nivel_cultural_individual += senciante.habilidades.get("arte", 0.0) * 0.5
                nivel_cultural_individual += senciante.habilidades.get("comunicacao", 0.0) * 0.3
                nivel_cultural_individual += senciante.habilidades.get("espiritualidade", 0.0) * 0.2
            
            grupos[grupo_id]["nivel_cultural"] += nivel_cultural_individual / len(grupos[grupo_id]["membros"])
            
            # Verificar se é líder
            if hasattr(senciante, "habilidades") and senciante.habilidades.get("lideranca", 0.0) > 0.5:
                if grupos[grupo_id]["lider_id"] is None or senciante.habilidades.get("lideranca", 0.0) > senciantes[grupos[grupo_id]["lider_id"]].habilidades.get("lideranca", 0.0):
                    grupos[grupo_id]["lider_id"] = senciante_id
            
            # Coletar artefatos, locais sagrados e tradições
            if hasattr(senciante, "artefatos_conhecidos"):
                grupos[grupo_id]["artefatos"].extend([a for a in senciante.artefatos_conhecidos if a not in grupos[grupo_id]["artefatos"]])
            
            if hasattr(senciante, "locais_sagrados_conhecidos"):
                grupos[grupo_id]["locais_sagrados"].extend([l for l in senciante.locais_sagrados_conhecidos if l not in grupos[grupo_id]["locais_sagrados"]])
            
            if hasattr(senciante, "tradicoes_conhecidas"):
                grupos[grupo_id]["tradicoes"].extend([t for t in senciante.tradicoes_conhecidas if t not in grupos[grupo_id]["tradicoes"]])
        
        return grupos
    
    def _verificar_criacao_artefatos(self, delta_tempo, grupos, senciantes):
        """
        Verifica a criação de novos artefatos.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for grupo_id, grupo in grupos.items():
            # Ignorar grupos individuais muito pequenos
            if grupo_id.startswith("individual_") and len(grupo["membros"]) <= 1:
                continue
            
            # Chance de criação de artefato baseada no nível cultural e tempo
            chance_criacao = 0.01 * grupo["nivel_cultural"] * delta_tempo
            
            if chance(chance_criacao):
                # Escolher um criador aleatório do grupo
                criadores_potenciais = []
                
                for membro_id in grupo["membros"]:
                    if membro_id in senciantes:
                        senciante = senciantes[membro_id]
                        
                        # Verificar habilidade artística
                        if hasattr(senciante, "habilidades") and senciante.habilidades.get("arte", 0.0) > 0.2:
                            criadores_potenciais.append(membro_id)
                
                # Se não há criadores potenciais, usar qualquer membro
                if not criadores_potenciais:
                    criadores_potenciais = grupo["membros"]
                
                criador_id = random.choice(criadores_potenciais)
                
                # Criar artefato
                self._criar_artefato(criador_id, grupo_id, senciantes)
    
    def _criar_artefato(self, criador_id, grupo_id, senciantes):
        """
        Cria um novo artefato cultural.
        
        Args:
            criador_id (str): ID do Senciante criador.
            grupo_id (str): ID do grupo do criador.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: ID do artefato criado.
        """
        # Verificar se o criador existe
        if criador_id not in senciantes:
            return None
        
        criador = senciantes[criador_id]
        
        # Escolher tipo de artefato
        tipo_artefato = random.choice(self.tipos_artefatos)
        
        # Determinar qualidade do artefato
        qualidade_base = 0.3
        
        if hasattr(criador, "habilidades"):
            qualidade_base += criador.habilidades.get("arte", 0.0) * 0.7
        
        # Adicionar variação aleatória
        qualidade = min(1.0, max(0.1, qualidade_base + random.uniform(-0.1, 0.1)))
        
        # Determinar significado cultural
        significados = [
            "fertilidade", "proteção", "sabedoria", "força", "união",
            "ancestralidade", "divindade", "natureza", "ciclo da vida", "harmonia"
        ]
        
        significado = random.choice(significados)
        
        # Criar artefato
        artefato_id = f"artefato_{len(self.artefatos) + 1}"
        
        artefato = ArtefatoCultural(
            id=artefato_id,
            tipo=tipo_artefato,
            criador_id=criador_id,
            grupo_id=grupo_id,
            qualidade=qualidade,
            significado=significado,
            posicao=criador.posicao.copy()
        )
        
        # Adicionar ao dicionário de artefatos
        self.artefatos[artefato_id] = artefato
        
        # Adicionar ao conhecimento do criador
        if not hasattr(criador, "artefatos_conhecidos"):
            criador.artefatos_conhecidos = []
        
        if artefato_id not in criador.artefatos_conhecidos:
            criador.artefatos_conhecidos.append(artefato_id)
        
        # Adicionar ao inventário do criador
        if not hasattr(criador, "artefatos_possuidos"):
            criador.artefatos_possuidos = []
        
        if artefato_id not in criador.artefatos_possuidos:
            criador.artefatos_possuidos.append(artefato_id)
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "artefato_criado",
            f"Senciante criou artefato: {tipo_artefato} com significado de {significado}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [criador_id]
        )
        
        return artefato_id
    
    def _verificar_estabelecimento_locais_sagrados(self, delta_tempo, grupos, senciantes):
        """
        Verifica o estabelecimento de novos locais sagrados.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for grupo_id, grupo in grupos.items():
            # Ignorar grupos individuais muito pequenos
            if grupo_id.startswith("individual_") and len(grupo["membros"]) <= 1:
                continue
            
            # Chance de estabelecimento de local sagrado baseada no nível cultural e tempo
            chance_estabelecimento = 0.005 * grupo["nivel_cultural"] * delta_tempo
            
            if chance(chance_estabelecimento):
                # Escolher um fundador aleatório do grupo
                fundadores_potenciais = []
                
                for membro_id in grupo["membros"]:
                    if membro_id in senciantes:
                        senciante = senciantes[membro_id]
                        
                        # Verificar habilidade espiritual
                        if hasattr(senciante, "habilidades") and senciante.habilidades.get("espiritualidade", 0.0) > 0.3:
                            fundadores_potenciais.append(membro_id)
                
                # Se não há fundadores potenciais, usar qualquer membro
                if not fundadores_potenciais:
                    fundadores_potenciais = grupo["membros"]
                
                fundador_id = random.choice(fundadores_potenciais)
                
                # Estabelecer local sagrado
                self._estabelecer_local_sagrado(fundador_id, grupo_id, senciantes)
    
    def _estabelecer_local_sagrado(self, fundador_id, grupo_id, senciantes):
        """
        Estabelece um novo local sagrado.
        
        Args:
            fundador_id (str): ID do Senciante fundador.
            grupo_id (str): ID do grupo do fundador.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: ID do local sagrado estabelecido.
        """
        # Verificar se o fundador existe
        if fundador_id not in senciantes:
            return None
        
        fundador = senciantes[fundador_id]
        
        # Escolher tipo de local sagrado
        tipo_local = random.choice(self.tipos_locais_sagrados)
        
        # Determinar importância do local
        importancia_base = 0.3
        
        if hasattr(fundador, "habilidades"):
            importancia_base += fundador.habilidades.get("espiritualidade", 0.0) * 0.7
        
        # Adicionar variação aleatória
        importancia = min(1.0, max(0.1, importancia_base + random.uniform(-0.1, 0.1)))
        
        # Determinar propósito
        propositos = [
            "adoração", "sacrifício", "meditação", "cura", "iniciação",
            "comunhão", "proteção", "fertilidade", "previsão", "purificação"
        ]
        
        proposito = random.choice(propositos)
        
        # Criar local sagrado
        local_id = f"local_sagrado_{len(self.locais_sagrados) + 1}"
        
        local_sagrado = {
            "id": local_id,
            "tipo": tipo_local,
            "fundador_id": fundador_id,
            "grupo_id": grupo_id,
            "importancia": importancia,
            "proposito": proposito,
            "posicao": fundador.posicao.copy(),
            "tempo_fundacao": 0,  # Será preenchido pelo motor
            "visitantes": [],
            "eventos_rituais": []
        }
        
        # Adicionar ao dicionário de locais sagrados
        self.locais_sagrados[local_id] = local_sagrado
        
        # Adicionar ao conhecimento do fundador
        if not hasattr(fundador, "locais_sagrados_conhecidos"):
            fundador.locais_sagrados_conhecidos = []
        
        if local_id not in fundador.locais_sagrados_conhecidos:
            fundador.locais_sagrados_conhecidos.append(local_id)
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "local_sagrado_estabelecido",
            f"Senciante estabeleceu local sagrado: {tipo_local} com propósito de {proposito}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [fundador_id]
        )
        
        return local_id
    
    def _verificar_desenvolvimento_tradicoes(self, delta_tempo, grupos, senciantes):
        """
        Verifica o desenvolvimento de novas tradições.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for grupo_id, grupo in grupos.items():
            # Ignorar grupos individuais muito pequenos
            if grupo_id.startswith("individual_") and len(grupo["membros"]) <= 1:
                continue
            
            # Chance de desenvolvimento de tradição baseada no nível cultural e tempo
            chance_desenvolvimento = 0.003 * grupo["nivel_cultural"] * delta_tempo
            
            if chance(chance_desenvolvimento):
                # Escolher um criador aleatório do grupo
                criadores_potenciais = []
                
                for membro_id in grupo["membros"]:
                    if membro_id in senciantes:
                        senciante = senciantes[membro_id]
                        
                        # Verificar habilidades relevantes
                        if hasattr(senciante, "habilidades") and (
                            senciante.habilidades.get("comunicacao", 0.0) > 0.3 or
                            senciante.habilidades.get("espiritualidade", 0.0) > 0.3 or
                            senciante.habilidades.get("arte", 0.0) > 0.3
                        ):
                            criadores_potenciais.append(membro_id)
                
                # Se não há criadores potenciais, usar qualquer membro
                if not criadores_potenciais:
                    criadores_potenciais = grupo["membros"]
                
                criador_id = random.choice(criadores_potenciais)
                
                # Desenvolver tradição
                self._desenvolver_tradicao(criador_id, grupo_id, senciantes)
    
    def _desenvolver_tradicao(self, criador_id, grupo_id, senciantes):
        """
        Desenvolve uma nova tradição cultural.
        
        Args:
            criador_id (str): ID do Senciante criador.
            grupo_id (str): ID do grupo do criador.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: ID da tradição desenvolvida.
        """
        # Verificar se o criador existe
        if criador_id not in senciantes:
            return None
        
        criador = senciantes[criador_id]
        
        # Escolher tipo de tradição
        tipo_tradicao = random.choice(self.tipos_tradicoes)
        
        # Determinar complexidade da tradição
        complexidade_base = 0.3
        
        if hasattr(criador, "habilidades"):
            if tipo_tradicao in ["danca", "canto"]:
                complexidade_base += criador.habilidades.get("arte", 0.0) * 0.7
            elif tipo_tradicao in ["ritual", "cerimonia"]:
                complexidade_base += criador.habilidades.get("espiritualidade", 0.0) * 0.7
            elif tipo_tradicao in ["narrativa_oral", "mito_fundador", "lenda"]:
                complexidade_base += criador.habilidades.get("comunicacao", 0.0) * 0.7
            else:
                complexidade_base += max(
                    criador.habilidades.get("arte", 0.0),
                    criador.habilidades.get("espiritualidade", 0.0),
                    criador.habilidades.get("comunicacao", 0.0)
                ) * 0.7
        
        # Adicionar variação aleatória
        complexidade = min(1.0, max(0.1, complexidade_base + random.uniform(-0.1, 0.1)))
        
        # Determinar propósito
        propositos = [
            "celebração", "luto", "iniciação", "passagem", "agradecimento",
            "proteção", "fertilidade", "união", "memória", "identidade"
        ]
        
        proposito = random.choice(propositos)
        
        # Criar tradição
        tradicao_id = f"tradicao_{len(self.tradicoes) + 1}"
        
        tradicao = {
            "id": tradicao_id,
            "tipo": tipo_tradicao,
            "criador_id": criador_id,
            "grupo_id": grupo_id,
            "complexidade": complexidade,
            "proposito": proposito,
            "tempo_criacao": 0,  # Será preenchido pelo motor
            "praticantes": [],
            "eventos_pratica": []
        }
        
        # Adicionar ao dicionário de tradições
        self.tradicoes[tradicao_id] = tradicao
        
        # Adicionar ao conhecimento do criador
        if not hasattr(criador, "tradicoes_conhecidas"):
            criador.tradicoes_conhecidas = []
        
        if tradicao_id not in criador.tradicoes_conhecidas:
            criador.tradicoes_conhecidas.append(tradicao_id)
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "tradicao_desenvolvida",
            f"Senciante desenvolveu tradição: {tipo_tradicao} com propósito de {proposito}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [criador_id]
        )
        
        return tradicao_id
    
    def _atualizar_influencia_artefatos(self, delta_tempo, senciantes):
        """
        Atualiza a influência cultural dos artefatos existentes.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for artefato_id, artefato in self.artefatos.items():
            # Verificar Senciantes próximos ao artefato
            for senciante_id, senciante in senciantes.items():
                # Calcular distância
                distancia = calcular_distancia(senciante.posicao, artefato.posicao)
                
                # Se estiver próximo
                if distancia <= 10.0:
                    # Chance de conhecer o artefato
                    chance_conhecer = 0.1 * delta_tempo * artefato.qualidade
                    
                    if chance(chance_conhecer):
                        # Adicionar ao conhecimento do Senciante
                        if not hasattr(senciante, "artefatos_conhecidos"):
                            senciante.artefatos_conhecidos = []
                        
                        if artefato_id not in senciante.artefatos_conhecidos:
                            senciante.artefatos_conhecidos.append(artefato_id)
                            
                            # Registrar no histórico do mundo
                            self.mundo.historico.registrar_evento(
                                "artefato_descoberto",
                                f"Senciante descobriu artefato: {artefato.tipo}",
                                0,  # Tempo atual (será preenchido pelo motor de simulação)
                                [senciante_id]
                            )
                            
                            # Influenciar o Senciante
                            self._influenciar_senciante_com_artefato(senciante, artefato)
    
    def _influenciar_senciante_com_artefato(self, senciante, artefato):
        """
        Influencia um Senciante com um artefato cultural.
        
        Args:
            senciante (Senciante): Senciante a ser influenciado.
            artefato (ArtefatoCultural): Artefato cultural.
        """
        # Aumentar habilidade artística
        if hasattr(senciante, "habilidades"):
            if "arte" not in senciante.habilidades:
                senciante.habilidades["arte"] = 0.0
            
            aumento = 0.01 * artefato.qualidade
            senciante.habilidades["arte"] = min(1.0, senciante.habilidades["arte"] + aumento)
        
        # Influenciar moralidade
        if hasattr(senciante, "moralidade") and senciante.moralidade is not None:
            if artefato.significado == "fertilidade":
                senciante.moralidade.ajustar_valor("vida", 0.02)
            elif artefato.significado == "proteção":
                senciante.moralidade.ajustar_valor("seguranca", 0.02)
            elif artefato.significado == "sabedoria":
                senciante.moralidade.ajustar_valor("conhecimento", 0.02)
            elif artefato.significado == "força":
                senciante.moralidade.ajustar_valor("poder", 0.02)
            elif artefato.significado == "união":
                senciante.moralidade.ajustar_valor("comunidade", 0.02)
            elif artefato.significado == "ancestralidade":
                senciante.moralidade.ajustar_valor("tradicao", 0.02)
            elif artefato.significado == "divindade":
                senciante.moralidade.ajustar_valor("espiritualidade", 0.02)
            elif artefato.significado == "natureza":
                senciante.moralidade.ajustar_valor("harmonia", 0.02)
            elif artefato.significado == "ciclo da vida":
                senciante.moralidade.ajustar_valor("aceitacao", 0.02)
            elif artefato.significado == "harmonia":
                senciante.moralidade.ajustar_valor("paz", 0.02)
    
    def _atualizar_influencia_locais_sagrados(self, delta_tempo, senciantes):
        """
        Atualiza a influência dos locais sagrados.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for local_id, local in self.locais_sagrados.items():
            # Verificar Senciantes próximos ao local sagrado
            for senciante_id, senciante in senciantes.items():
                # Calcular distância
                distancia = calcular_distancia(senciante.posicao, local["posicao"])
                
                # Se estiver próximo
                if distancia <= 15.0:
                    # Chance de conhecer o local sagrado
                    chance_conhecer = 0.1 * delta_tempo * local["importancia"]
                    
                    if chance(chance_conhecer):
                        # Adicionar ao conhecimento do Senciante
                        if not hasattr(senciante, "locais_sagrados_conhecidos"):
                            senciante.locais_sagrados_conhecidos = []
                        
                        if local_id not in senciante.locais_sagrados_conhecidos:
                            senciante.locais_sagrados_conhecidos.append(local_id)
                            
                            # Registrar no histórico do mundo
                            self.mundo.historico.registrar_evento(
                                "local_sagrado_descoberto",
                                f"Senciante descobriu local sagrado: {local['tipo']}",
                                0,  # Tempo atual (será preenchido pelo motor de simulação)
                                [senciante_id]
                            )
                            
                            # Influenciar o Senciante
                            self._influenciar_senciante_com_local_sagrado(senciante, local)
                    
                    # Chance de visitar o local sagrado
                    chance_visitar = 0.05 * delta_tempo * local["importancia"]
                    
                    if chance(chance_visitar):
                        # Adicionar à lista de visitantes
                        if senciante_id not in local["visitantes"]:
                            local["visitantes"].append(senciante_id)
                        
                        # Registrar visita
                        evento_visita = {
                            "tipo": "visita",
                            "senciante_id": senciante_id,
                            "tempo": 0  # Será preenchido pelo motor
                        }
                        
                        local["eventos_rituais"].append(evento_visita)
                        
                        # Influenciar o Senciante
                        self._influenciar_senciante_com_visita_local_sagrado(senciante, local)
    
    def _influenciar_senciante_com_local_sagrado(self, senciante, local):
        """
        Influencia um Senciante com um local sagrado.
        
        Args:
            senciante (Senciante): Senciante a ser influenciado.
            local (dict): Local sagrado.
        """
        # Aumentar habilidade espiritual
        if hasattr(senciante, "habilidades"):
            if "espiritualidade" not in senciante.habilidades:
                senciante.habilidades["espiritualidade"] = 0.0
            
            aumento = 0.01 * local["importancia"]
            senciante.habilidades["espiritualidade"] = min(1.0, senciante.habilidades["espiritualidade"] + aumento)
        
        # Influenciar moralidade
        if hasattr(senciante, "moralidade") and senciante.moralidade is not None:
            if local["proposito"] == "adoração":
                senciante.moralidade.ajustar_valor("espiritualidade", 0.02)
            elif local["proposito"] == "sacrifício":
                senciante.moralidade.ajustar_valor("dever", 0.02)
            elif local["proposito"] == "meditação":
                senciante.moralidade.ajustar_valor("harmonia", 0.02)
            elif local["proposito"] == "cura":
                senciante.moralidade.ajustar_valor("compaixao", 0.02)
            elif local["proposito"] == "iniciação":
                senciante.moralidade.ajustar_valor("tradicao", 0.02)
            elif local["proposito"] == "comunhão":
                senciante.moralidade.ajustar_valor("comunidade", 0.02)
            elif local["proposito"] == "proteção":
                senciante.moralidade.ajustar_valor("seguranca", 0.02)
            elif local["proposito"] == "fertilidade":
                senciante.moralidade.ajustar_valor("vida", 0.02)
            elif local["proposito"] == "previsão":
                senciante.moralidade.ajustar_valor("conhecimento", 0.02)
            elif local["proposito"] == "purificação":
                senciante.moralidade.ajustar_valor("pureza", 0.02)
    
    def _influenciar_senciante_com_visita_local_sagrado(self, senciante, local):
        """
        Influencia um Senciante com uma visita a um local sagrado.
        
        Args:
            senciante (Senciante): Senciante a ser influenciado.
            local (dict): Local sagrado.
        """
        # Reduzir estresse
        senciante.estado["estresse"] = max(0.0, senciante.estado["estresse"] - 0.1 * local["importancia"])
        
        # Aumentar felicidade
        senciante.estado["felicidade"] = min(1.0, senciante.estado["felicidade"] + 0.05 * local["importancia"])
        
        # Chance de cura
        if local["proposito"] == "cura" and senciante.estado["saude"] < 1.0:
            chance_cura = 0.2 * local["importancia"]
            
            if chance(chance_cura):
                cura = 0.1 * local["importancia"]
                senciante.estado["saude"] = min(1.0, senciante.estado["saude"] + cura)
                
                # Registrar no histórico do mundo
                self.mundo.historico.registrar_evento(
                    "cura_local_sagrado",
                    f"Senciante foi curado em local sagrado: {local['tipo']}",
                    0,  # Tempo atual (será preenchido pelo motor de simulação)
                    [senciante.id]
                )
    
    def _atualizar_pratica_tradicoes(self, delta_tempo, grupos, senciantes):
        """
        Atualiza a prática das tradições.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for grupo_id, grupo in grupos.items():
            # Ignorar grupos individuais muito pequenos
            if grupo_id.startswith("individual_") and len(grupo["membros"]) <= 1:
                continue
            
            # Para cada tradição conhecida pelo grupo
            for tradicao_id in grupo["tradicoes"]:
                if tradicao_id not in self.tradicoes:
                    continue
                
                tradicao = self.tradicoes[tradicao_id]
                
                # Chance de prática da tradição baseada no tempo
                chance_pratica = 0.02 * delta_tempo
                
                if chance(chance_pratica):
                    # Escolher participantes do grupo
                    num_participantes = min(len(grupo["membros"]), random.randint(2, 5))
                    participantes = random.sample(grupo["membros"], num_participantes)
                    
                    # Praticar tradição
                    self._praticar_tradicao(tradicao_id, participantes, senciantes)
    
    def _praticar_tradicao(self, tradicao_id, participantes, senciantes):
        """
        Pratica uma tradição cultural.
        
        Args:
            tradicao_id (str): ID da tradição.
            participantes (list): Lista de IDs dos Senciantes participantes.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Verificar se a tradição existe
        if tradicao_id not in self.tradicoes:
            return
        
        tradicao = self.tradicoes[tradicao_id]
        
        # Registrar evento de prática
        evento_pratica = {
            "tipo": "pratica",
            "participantes": participantes,
            "tempo": 0  # Será preenchido pelo motor
        }
        
        tradicao["eventos_pratica"].append(evento_pratica)
        
        # Adicionar participantes à lista de praticantes
        for participante_id in participantes:
            if participante_id not in tradicao["praticantes"]:
                tradicao["praticantes"].append(participante_id)
        
        # Influenciar os participantes
        for participante_id in participantes:
            if participante_id in senciantes:
                senciante = senciantes[participante_id]
                
                # Adicionar ao conhecimento do Senciante
                if not hasattr(senciante, "tradicoes_conhecidas"):
                    senciante.tradicoes_conhecidas = []
                
                if tradicao_id not in senciante.tradicoes_conhecidas:
                    senciante.tradicoes_conhecidas.append(tradicao_id)
                
                # Influenciar o Senciante
                self._influenciar_senciante_com_tradicao(senciante, tradicao)
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "tradicao_praticada",
            f"Grupo de Senciantes praticou tradição: {tradicao['tipo']}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            participantes
        )
    
    def _influenciar_senciante_com_tradicao(self, senciante, tradicao):
        """
        Influencia um Senciante com uma tradição cultural.
        
        Args:
            senciante (Senciante): Senciante a ser influenciado.
            tradicao (dict): Tradição cultural.
        """
        # Reduzir estresse
        senciante.estado["estresse"] = max(0.0, senciante.estado["estresse"] - 0.1)
        
        # Aumentar felicidade
        senciante.estado["felicidade"] = min(1.0, senciante.estado["felicidade"] + 0.1)
        
        # Aumentar habilidades relevantes
        if hasattr(senciante, "habilidades"):
            if tradicao["tipo"] in ["danca", "canto"]:
                if "arte" not in senciante.habilidades:
                    senciante.habilidades["arte"] = 0.0
                
                aumento = 0.01 * tradicao["complexidade"]
                senciante.habilidades["arte"] = min(1.0, senciante.habilidades["arte"] + aumento)
            
            elif tradicao["tipo"] in ["ritual", "cerimonia"]:
                if "espiritualidade" not in senciante.habilidades:
                    senciante.habilidades["espiritualidade"] = 0.0
                
                aumento = 0.01 * tradicao["complexidade"]
                senciante.habilidades["espiritualidade"] = min(1.0, senciante.habilidades["espiritualidade"] + aumento)
            
            elif tradicao["tipo"] in ["narrativa_oral", "mito_fundador", "lenda"]:
                if "comunicacao" not in senciante.habilidades:
                    senciante.habilidades["comunicacao"] = 0.0
                
                aumento = 0.01 * tradicao["complexidade"]
                senciante.habilidades["comunicacao"] = min(1.0, senciante.habilidades["comunicacao"] + aumento)
        
        # Influenciar moralidade
        if hasattr(senciante, "moralidade") and senciante.moralidade is not None:
            if tradicao["proposito"] == "celebração":
                senciante.moralidade.ajustar_valor("alegria", 0.02)
            elif tradicao["proposito"] == "luto":
                senciante.moralidade.ajustar_valor("aceitacao", 0.02)
            elif tradicao["proposito"] == "iniciação":
                senciante.moralidade.ajustar_valor("crescimento", 0.02)
            elif tradicao["proposito"] == "passagem":
                senciante.moralidade.ajustar_valor("mudanca", 0.02)
            elif tradicao["proposito"] == "agradecimento":
                senciante.moralidade.ajustar_valor("gratidao", 0.02)
            elif tradicao["proposito"] == "proteção":
                senciante.moralidade.ajustar_valor("seguranca", 0.02)
            elif tradicao["proposito"] == "fertilidade":
                senciante.moralidade.ajustar_valor("vida", 0.02)
            elif tradicao["proposito"] == "união":
                senciante.moralidade.ajustar_valor("comunidade", 0.02)
            elif tradicao["proposito"] == "memória":
                senciante.moralidade.ajustar_valor("tradicao", 0.02)
            elif tradicao["proposito"] == "identidade":
                senciante.moralidade.ajustar_valor("autenticidade", 0.02)
    
    def transmitir_conhecimento_cultural(self, senciante_origem_id, senciante_destino_id, tipo, id_item, senciantes):
        """
        Transmite conhecimento cultural entre Senciantes.
        
        Args:
            senciante_origem_id (str): ID do Senciante de origem.
            senciante_destino_id (str): ID do Senciante de destino.
            tipo (str): Tipo de conhecimento ("artefato", "local_sagrado", "tradicao").
            id_item (str): ID do item cultural.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            bool: True se a transmissão foi bem-sucedida.
        """
        # Verificar se os Senciantes existem
        if senciante_origem_id not in senciantes or senciante_destino_id not in senciantes:
            return False
        
        senciante_origem = senciantes[senciante_origem_id]
        senciante_destino = senciantes[senciante_destino_id]
        
        # Verificar se estão próximos
        distancia = calcular_distancia(senciante_origem.posicao, senciante_destino.posicao)
        
        if distancia > 5.0:
            return False
        
        # Verificar tipo de conhecimento
        if tipo == "artefato":
            # Verificar se o Senciante de origem conhece o artefato
            if not hasattr(senciante_origem, "artefatos_conhecidos") or id_item not in senciante_origem.artefatos_conhecidos:
                return False
            
            # Adicionar ao conhecimento do Senciante de destino
            if not hasattr(senciante_destino, "artefatos_conhecidos"):
                senciante_destino.artefatos_conhecidos = []
            
            if id_item not in senciante_destino.artefatos_conhecidos:
                senciante_destino.artefatos_conhecidos.append(id_item)
                
                # Influenciar o Senciante de destino
                if id_item in self.artefatos:
                    self._influenciar_senciante_com_artefato(senciante_destino, self.artefatos[id_item])
        
        elif tipo == "local_sagrado":
            # Verificar se o Senciante de origem conhece o local sagrado
            if not hasattr(senciante_origem, "locais_sagrados_conhecidos") or id_item not in senciante_origem.locais_sagrados_conhecidos:
                return False
            
            # Adicionar ao conhecimento do Senciante de destino
            if not hasattr(senciante_destino, "locais_sagrados_conhecidos"):
                senciante_destino.locais_sagrados_conhecidos = []
            
            if id_item not in senciante_destino.locais_sagrados_conhecidos:
                senciante_destino.locais_sagrados_conhecidos.append(id_item)
                
                # Influenciar o Senciante de destino
                if id_item in self.locais_sagrados:
                    self._influenciar_senciante_com_local_sagrado(senciante_destino, self.locais_sagrados[id_item])
        
        elif tipo == "tradicao":
            # Verificar se o Senciante de origem conhece a tradição
            if not hasattr(senciante_origem, "tradicoes_conhecidas") or id_item not in senciante_origem.tradicoes_conhecidas:
                return False
            
            # Adicionar ao conhecimento do Senciante de destino
            if not hasattr(senciante_destino, "tradicoes_conhecidas"):
                senciante_destino.tradicoes_conhecidas = []
            
            if id_item not in senciante_destino.tradicoes_conhecidas:
                senciante_destino.tradicoes_conhecidas.append(id_item)
                
                # Influenciar o Senciante de destino
                if id_item in self.tradicoes:
                    self._influenciar_senciante_com_tradicao(senciante_destino, self.tradicoes[id_item])
        
        else:
            return False
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "conhecimento_cultural_transmitido",
            f"Senciante transmitiu conhecimento cultural de tipo {tipo} para outro Senciante",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [senciante_origem_id, senciante_destino_id]
        )
        
        return True
    
    def doar_artefato(self, senciante_origem_id, senciante_destino_id, artefato_id, senciantes):
        """
        Doa um artefato de um Senciante para outro.
        
        Args:
            senciante_origem_id (str): ID do Senciante de origem.
            senciante_destino_id (str): ID do Senciante de destino.
            artefato_id (str): ID do artefato.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            bool: True se a doação foi bem-sucedida.
        """
        # Verificar se os Senciantes existem
        if senciante_origem_id not in senciantes or senciante_destino_id not in senciantes:
            return False
        
        senciante_origem = senciantes[senciante_origem_id]
        senciante_destino = senciantes[senciante_destino_id]
        
        # Verificar se estão próximos
        distancia = calcular_distancia(senciante_origem.posicao, senciante_destino.posicao)
        
        if distancia > 5.0:
            return False
        
        # Verificar se o Senciante de origem possui o artefato
        if not hasattr(senciante_origem, "artefatos_possuidos") or artefato_id not in senciante_origem.artefatos_possuidos:
            return False
        
        # Remover do Senciante de origem
        senciante_origem.artefatos_possuidos.remove(artefato_id)
        
        # Adicionar ao Senciante de destino
        if not hasattr(senciante_destino, "artefatos_possuidos"):
            senciante_destino.artefatos_possuidos = []
        
        senciante_destino.artefatos_possuidos.append(artefato_id)
        
        # Atualizar posição do artefato
        if artefato_id in self.artefatos:
            self.artefatos[artefato_id].posicao = senciante_destino.posicao.copy()
        
        # Adicionar ao conhecimento do Senciante de destino
        if not hasattr(senciante_destino, "artefatos_conhecidos"):
            senciante_destino.artefatos_conhecidos = []
        
        if artefato_id not in senciante_destino.artefatos_conhecidos:
            senciante_destino.artefatos_conhecidos.append(artefato_id)
            
            # Influenciar o Senciante de destino
            if artefato_id in self.artefatos:
                self._influenciar_senciante_com_artefato(senciante_destino, self.artefatos[artefato_id])
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "artefato_doado",
            f"Senciante doou artefato para outro Senciante",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [senciante_origem_id, senciante_destino_id]
        )
        
        return True
    
    def obter_artefatos_proximos(self, posicao, raio=20.0):
        """
        Obtém artefatos próximos a uma posição.
        
        Args:
            posicao (list): Posição [x, y] no mundo.
            raio (float, optional): Raio de busca. Defaults to 20.0.
            
        Returns:
            list: Lista de artefatos próximos.
        """
        artefatos_proximos = []
        
        for artefato_id, artefato in self.artefatos.items():
            distancia = calcular_distancia(posicao, artefato.posicao)
            
            if distancia <= raio:
                artefatos_proximos.append(artefato)
        
        return artefatos_proximos
    
    def obter_locais_sagrados_proximos(self, posicao, raio=30.0):
        """
        Obtém locais sagrados próximos a uma posição.
        
        Args:
            posicao (list): Posição [x, y] no mundo.
            raio (float, optional): Raio de busca. Defaults to 30.0.
            
        Returns:
            list: Lista de locais sagrados próximos.
        """
        locais_proximos = []
        
        for local_id, local in self.locais_sagrados.items():
            distancia = calcular_distancia(posicao, local["posicao"])
            
            if distancia <= raio:
                locais_proximos.append(local)
        
        return locais_proximos
    
    def obter_tradicoes_grupo(self, grupo_id):
        """
        Obtém tradições de um grupo.
        
        Args:
            grupo_id (str): ID do grupo.
            
        Returns:
            list: Lista de tradições do grupo.
        """
        tradicoes_grupo = []
        
        for tradicao_id, tradicao in self.tradicoes.items():
            if tradicao["grupo_id"] == grupo_id:
                tradicoes_grupo.append(tradicao)
        
        return tradicoes_grupo

