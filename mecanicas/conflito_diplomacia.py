"""
Implementação das mecânicas de conflito e diplomacia para o jogo "O Mundo dos Senciantes".
"""

import random
from utils.helpers import chance, calcular_distancia

class MecanicaConflitoDiplomacia:
    """
    Classe que implementa as mecânicas de conflito e diplomacia.
    """
    
    def __init__(self, mundo):
        """
        Inicializa a mecânica de conflito e diplomacia.
        
        Args:
            mundo (Mundo): Objeto mundo para referência.
        """
        self.mundo = mundo
        self.conflitos = {}  # Dicionário de id_conflito: conflito
        self.tratados = {}  # Dicionário de id_tratado: tratado
        self.trocas_comerciais = {}  # Dicionário de id_troca: troca
        
        # Tipos de conflitos
        self.tipos_conflitos = [
            "territorial", "recursos", "religioso", "cultural", "poder"
        ]
        
        # Tipos de tratados
        self.tipos_tratados = [
            "paz", "alianca", "comercio", "nao_agressao", "protecao"
        ]
    
    def atualizar(self, delta_tempo, senciantes):
        """
        Atualiza o estado dos conflitos e diplomacia no mundo.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Identificar grupos de Senciantes
        grupos = self._identificar_grupos(senciantes)
        
        # Atualizar conflitos existentes
        self._atualizar_conflitos(delta_tempo, grupos, senciantes)
        
        # Verificar surgimento de novos conflitos
        self._verificar_novos_conflitos(delta_tempo, grupos, senciantes)
        
        # Atualizar tratados existentes
        self._atualizar_tratados(delta_tempo, grupos, senciantes)
        
        # Verificar surgimento de novas negociações diplomáticas
        self._verificar_novas_negociacoes(delta_tempo, grupos, senciantes)
        
        # Atualizar trocas comerciais
        self._atualizar_trocas_comerciais(delta_tempo, grupos, senciantes)
    
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
                    "forca_total": 0.0,
                    "recursos": {},
                    "valores_morais": {},
                    "tecnologias": set()
                }
            
            grupos[grupo_id]["membros"].append(senciante_id)
            
            # Atualizar posição média
            if len(grupos[grupo_id]["membros"]) == 1:
                grupos[grupo_id]["posicao_media"] = senciante.posicao.copy()
            else:
                n = len(grupos[grupo_id]["membros"])
                grupos[grupo_id]["posicao_media"][0] = ((n - 1) * grupos[grupo_id]["posicao_media"][0] + senciante.posicao[0]) / n
                grupos[grupo_id]["posicao_media"][1] = ((n - 1) * grupos[grupo_id]["posicao_media"][1] + senciante.posicao[1]) / n
            
            # Calcular força individual
            forca_individual = 1.0
            
            if hasattr(senciante, "habilidades"):
                forca_individual += senciante.habilidades.get("combate", 0.0) * 2.0
                forca_individual += senciante.habilidades.get("lideranca", 0.0) * 1.0
            
            grupos[grupo_id]["forca_total"] += forca_individual
            
            # Verificar se é líder
            if hasattr(senciante, "habilidades") and senciante.habilidades.get("lideranca", 0.0) > 0.5:
                if grupos[grupo_id]["lider_id"] is None or senciante.habilidades.get("lideranca", 0.0) > senciantes[grupos[grupo_id]["lider_id"]].habilidades.get("lideranca", 0.0):
                    grupos[grupo_id]["lider_id"] = senciante_id
            
            # Coletar recursos
            for recurso, quantidade in senciante.inventario.items():
                if recurso not in grupos[grupo_id]["recursos"]:
                    grupos[grupo_id]["recursos"][recurso] = 0.0
                
                grupos[grupo_id]["recursos"][recurso] += quantidade
            
            # Coletar valores morais
            if hasattr(senciante, "moralidade") and senciante.moralidade is not None:
                for valor, nivel in senciante.moralidade.valores.items():
                    if valor not in grupos[grupo_id]["valores_morais"]:
                        grupos[grupo_id]["valores_morais"][valor] = []
                    
                    grupos[grupo_id]["valores_morais"][valor].append(nivel)
            
            # Coletar tecnologias
            if hasattr(senciante, "tecnologias"):
                grupos[grupo_id]["tecnologias"].update(senciante.tecnologias)
        
        # Calcular valores morais médios
        for grupo_id, grupo in grupos.items():
            valores_medios = {}
            
            for valor, niveis in grupo["valores_morais"].items():
                valores_medios[valor] = sum(niveis) / len(niveis)
            
            grupo["valores_morais"] = valores_medios
        
        return grupos
    
    def _atualizar_conflitos(self, delta_tempo, grupos, senciantes):
        """
        Atualiza os conflitos existentes.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for conflito_id, conflito in list(self.conflitos.items()):
            # Verificar se os grupos ainda existem
            if conflito["grupo1_id"] not in grupos or conflito["grupo2_id"] not in grupos:
                # Encerrar conflito
                self._encerrar_conflito(conflito_id, "dissolucao", "Um dos grupos envolvidos foi dissolvido")
                continue
            
            # Atualizar duração
            conflito["duracao"] += delta_tempo
            
            # Verificar resolução do conflito
            if self._verificar_resolucao_conflito(conflito_id, grupos):
                continue
            
            # Atualizar batalhas
            self._atualizar_batalhas(conflito_id, delta_tempo, grupos, senciantes)
    
    def _verificar_resolucao_conflito(self, conflito_id, grupos):
        """
        Verifica se um conflito foi resolvido.
        
        Args:
            conflito_id (str): ID do conflito.
            grupos (dict): Dicionário de grupos identificados.
            
        Returns:
            bool: True se o conflito foi resolvido.
        """
        conflito = self.conflitos[conflito_id]
        
        # Verificar se o conflito já durou tempo suficiente
        if conflito["duracao"] > 48.0:  # 2 dias
            # Chance de resolução aumenta com o tempo
            chance_resolucao = 0.1 * (conflito["duracao"] / 48.0)
            
            if chance(chance_resolucao):
                # Determinar vencedor com base na força e baixas
                grupo1 = grupos[conflito["grupo1_id"]]
                grupo2 = grupos[conflito["grupo2_id"]]
                
                forca_relativa1 = grupo1["forca_total"] / (grupo1["forca_total"] + grupo2["forca_total"])
                
                # Ajustar com base nas baixas
                baixas1 = conflito["baixas"].get(conflito["grupo1_id"], 0)
                baixas2 = conflito["baixas"].get(conflito["grupo2_id"], 0)
                
                if baixas1 + baixas2 > 0:
                    proporcao_baixas1 = baixas1 / (baixas1 + baixas2)
                    forca_relativa1 = forca_relativa1 * (1.0 - proporcao_baixas1)
                
                # Determinar vencedor
                if forca_relativa1 > 0.6:
                    vencedor_id = conflito["grupo1_id"]
                    perdedor_id = conflito["grupo2_id"]
                elif forca_relativa1 < 0.4:
                    vencedor_id = conflito["grupo2_id"]
                    perdedor_id = conflito["grupo1_id"]
                else:
                    # Empate
                    self._encerrar_conflito(conflito_id, "empate", "Nenhum lado conseguiu vantagem decisiva")
                    return True
                
                # Encerrar conflito com vitória
                self._encerrar_conflito(
                    conflito_id,
                    "vitoria",
                    f"Grupo {vencedor_id} venceu o conflito contra o grupo {perdedor_id}",
                    vencedor_id=vencedor_id,
                    perdedor_id=perdedor_id
                )
                
                return True
        
        return False
    
    def _atualizar_batalhas(self, conflito_id, delta_tempo, grupos, senciantes):
        """
        Atualiza as batalhas em um conflito.
        
        Args:
            conflito_id (str): ID do conflito.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        conflito = self.conflitos[conflito_id]
        
        # Chance de batalha baseada no tempo
        chance_batalha = 0.05 * delta_tempo
        
        if chance(chance_batalha):
            # Iniciar batalha
            grupo1_id = conflito["grupo1_id"]
            grupo2_id = conflito["grupo2_id"]
            
            grupo1 = grupos[grupo1_id]
            grupo2 = grupos[grupo2_id]
            
            # Selecionar participantes da batalha
            participantes1 = random.sample(grupo1["membros"], min(3, len(grupo1["membros"])))
            participantes2 = random.sample(grupo2["membros"], min(3, len(grupo2["membros"])))
            
            # Calcular força de cada lado
            forca1 = sum(1.0 + senciantes[s_id].habilidades.get("combate", 0.0) * 2.0 for s_id in participantes1)
            forca2 = sum(1.0 + senciantes[s_id].habilidades.get("combate", 0.0) * 2.0 for s_id in participantes2)
            
            # Determinar resultado da batalha
            forca_total = forca1 + forca2
            probabilidade_vitoria1 = forca1 / forca_total if forca_total > 0 else 0.5
            
            resultado = "vitoria1" if chance(probabilidade_vitoria1) else "vitoria2"
            
            # Aplicar consequências da batalha
            self._aplicar_consequencias_batalha(
                conflito_id,
                resultado,
                participantes1,
                participantes2,
                senciantes
            )
            
            # Registrar batalha
            batalha = {
                "participantes1": participantes1,
                "participantes2": participantes2,
                "resultado": resultado,
                "tempo": 0  # Será preenchido pelo motor
            }
            
            conflito["batalhas"].append(batalha)
            
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "batalha",
                f"Batalha entre grupos {grupo1_id} e {grupo2_id}: {resultado}",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                participantes1 + participantes2
            )
    
    def _aplicar_consequencias_batalha(self, conflito_id, resultado, participantes1, participantes2, senciantes):
        """
        Aplica as consequências de uma batalha.
        
        Args:
            conflito_id (str): ID do conflito.
            resultado (str): Resultado da batalha ("vitoria1", "vitoria2").
            participantes1 (list): Lista de IDs dos participantes do grupo 1.
            participantes2 (list): Lista de IDs dos participantes do grupo 2.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        conflito = self.conflitos[conflito_id]
        
        # Determinar vencedores e perdedores
        if resultado == "vitoria1":
            vencedores = participantes1
            perdedores = participantes2
            grupo_vencedor_id = conflito["grupo1_id"]
            grupo_perdedor_id = conflito["grupo2_id"]
        else:
            vencedores = participantes2
            perdedores = participantes1
            grupo_vencedor_id = conflito["grupo2_id"]
            grupo_perdedor_id = conflito["grupo1_id"]
        
        # Aplicar dano aos perdedores
        for perdedor_id in perdedores:
            if perdedor_id in senciantes:
                # Reduzir saúde
                dano = random.uniform(0.1, 0.3)
                senciantes[perdedor_id].estado["saude"] -= dano
                
                # Verificar morte
                if senciantes[perdedor_id].estado["saude"] <= 0.0:
                    # Registrar baixa
                    if grupo_perdedor_id not in conflito["baixas"]:
                        conflito["baixas"][grupo_perdedor_id] = 0
                    
                    conflito["baixas"][grupo_perdedor_id] += 1
                    
                    # Registrar no histórico do mundo
                    self.mundo.historico.registrar_evento(
                        "morte_batalha",
                        f"Senciante morreu em batalha",
                        0,  # Tempo atual (será preenchido pelo motor de simulação)
                        [perdedor_id]
                    )
                else:
                    # Aumentar estresse
                    senciantes[perdedor_id].estado["estresse"] = min(1.0, senciantes[perdedor_id].estado["estresse"] + 0.2)
                    
                    # Reduzir felicidade
                    senciantes[perdedor_id].estado["felicidade"] = max(0.0, senciantes[perdedor_id].estado["felicidade"] - 0.2)
        
        # Aplicar consequências aos vencedores
        for vencedor_id in vencedores:
            if vencedor_id in senciantes:
                # Pequeno dano
                dano = random.uniform(0.0, 0.1)
                senciantes[vencedor_id].estado["saude"] -= dano
                
                # Aumentar estresse
                senciantes[vencedor_id].estado["estresse"] = min(1.0, senciantes[vencedor_id].estado["estresse"] + 0.1)
                
                # Aumentar habilidade de combate
                if hasattr(senciantes[vencedor_id], "habilidades"):
                    if "combate" not in senciantes[vencedor_id].habilidades:
                        senciantes[vencedor_id].habilidades["combate"] = 0.0
                    
                    senciantes[vencedor_id].habilidades["combate"] = min(1.0, senciantes[vencedor_id].habilidades["combate"] + 0.02)
        
        # Atualizar pontuação do conflito
        if resultado == "vitoria1":
            conflito["pontuacao_grupo1"] += 1
        else:
            conflito["pontuacao_grupo2"] += 1
    
    def _encerrar_conflito(self, conflito_id, motivo, descricao, vencedor_id=None, perdedor_id=None):
        """
        Encerra um conflito.
        
        Args:
            conflito_id (str): ID do conflito.
            motivo (str): Motivo do encerramento ("vitoria", "empate", "acordo", "dissolucao").
            descricao (str): Descrição do encerramento.
            vencedor_id (str, optional): ID do grupo vencedor. Defaults to None.
            perdedor_id (str, optional): ID do grupo perdedor. Defaults to None.
        """
        conflito = self.conflitos[conflito_id]
        
        # Atualizar estado do conflito
        conflito["ativo"] = False
        conflito["motivo_encerramento"] = motivo
        conflito["descricao_encerramento"] = descricao
        conflito["vencedor_id"] = vencedor_id
        conflito["perdedor_id"] = perdedor_id
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "conflito_encerrado",
            f"Conflito encerrado: {descricao}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            []
        )
        
        # Se foi uma vitória, criar um tratado de paz
        if motivo == "vitoria" and vencedor_id is not None and perdedor_id is not None:
            self._criar_tratado_apos_conflito(vencedor_id, perdedor_id, conflito)
    
    def _criar_tratado_apos_conflito(self, vencedor_id, perdedor_id, conflito):
        """
        Cria um tratado após um conflito.
        
        Args:
            vencedor_id (str): ID do grupo vencedor.
            perdedor_id (str): ID do grupo perdedor.
            conflito (dict): Informações do conflito.
            
        Returns:
            str: ID do tratado criado.
        """
        # Determinar tipo de tratado
        tipo_tratado = "paz"
        
        # Determinar termos do tratado
        termos = []
        
        # Adicionar termo de não agressão
        termos.append({
            "tipo": "nao_agressao",
            "duracao": 168.0,  # 7 dias
            "descricao": f"Grupo {perdedor_id} não pode atacar o grupo {vencedor_id} por 7 dias"
        })
        
        # Se o conflito foi por território, adicionar termo de cessão territorial
        if conflito["tipo"] == "territorial" and "territorio_id" in conflito:
            termos.append({
                "tipo": "cessao_territorial",
                "territorio_id": conflito["territorio_id"],
                "descricao": f"Grupo {perdedor_id} cede controle do território para o grupo {vencedor_id}"
            })
        
        # Se o conflito foi por recursos, adicionar termo de tributo
        if conflito["tipo"] == "recursos":
            termos.append({
                "tipo": "tributo",
                "recurso": "comida",
                "quantidade": 10.0,
                "periodicidade": 24.0,  # 1 dia
                "duracao": 168.0,  # 7 dias
                "descricao": f"Grupo {perdedor_id} deve pagar tributo de 10 unidades de comida por dia durante 7 dias"
            })
        
        # Criar tratado
        tratado_id = f"tratado_{len(self.tratados) + 1}"
        
        self.tratados[tratado_id] = {
            "id": tratado_id,
            "tipo": tipo_tratado,
            "grupo1_id": vencedor_id,
            "grupo2_id": perdedor_id,
            "termos": termos,
            "tempo_criacao": 0,  # Será preenchido pelo motor
            "duracao": 168.0,  # 7 dias
            "ativo": True,
            "violacoes": []
        }
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "tratado_criado",
            f"Tratado de {tipo_tratado} criado entre grupos {vencedor_id} e {perdedor_id}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            []
        )
        
        return tratado_id
    
    def _verificar_novos_conflitos(self, delta_tempo, grupos, senciantes):
        """
        Verifica o surgimento de novos conflitos.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Ignorar grupos individuais
        grupos_reais = {id: g for id, g in grupos.items() if not id.startswith("individual_") or len(g["membros"]) > 1}
        
        # Se há poucos grupos, não criar conflitos
        if len(grupos_reais) < 2:
            return
        
        # Chance de novo conflito baseada no tempo
        chance_conflito = 0.02 * delta_tempo
        
        if chance(chance_conflito):
            # Escolher dois grupos aleatórios
            grupo_ids = list(grupos_reais.keys())
            grupo1_id, grupo2_id = random.sample(grupo_ids, 2)
            
            # Verificar se já existe conflito entre estes grupos
            for conflito in self.conflitos.values():
                if conflito["ativo"] and (
                    (conflito["grupo1_id"] == grupo1_id and conflito["grupo2_id"] == grupo2_id) or
                    (conflito["grupo1_id"] == grupo2_id and conflito["grupo2_id"] == grupo1_id)
                ):
                    return
            
            # Verificar se existe tratado de paz entre estes grupos
            for tratado in self.tratados.values():
                if tratado["ativo"] and tratado["tipo"] == "paz" and (
                    (tratado["grupo1_id"] == grupo1_id and tratado["grupo2_id"] == grupo2_id) or
                    (tratado["grupo1_id"] == grupo2_id and tratado["grupo2_id"] == grupo1_id)
                ):
                    # Verificar se o tratado tem termo de não agressão
                    for termo in tratado["termos"]:
                        if termo["tipo"] == "nao_agressao":
                            return
            
            # Determinar tipo de conflito
            tipo_conflito = random.choice(self.tipos_conflitos)
            
            # Criar conflito
            self._criar_conflito(grupo1_id, grupo2_id, tipo_conflito, grupos, senciantes)
    
    def _criar_conflito(self, grupo1_id, grupo2_id, tipo_conflito, grupos, senciantes):
        """
        Cria um novo conflito entre dois grupos.
        
        Args:
            grupo1_id (str): ID do primeiro grupo.
            grupo2_id (str): ID do segundo grupo.
            tipo_conflito (str): Tipo de conflito.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: ID do conflito criado.
        """
        # Gerar ID único para o conflito
        conflito_id = f"conflito_{len(self.conflitos) + 1}"
        
        # Determinar causa específica do conflito
        causa = self._determinar_causa_conflito(grupo1_id, grupo2_id, tipo_conflito, grupos)
        
        # Criar conflito
        self.conflitos[conflito_id] = {
            "id": conflito_id,
            "tipo": tipo_conflito,
            "grupo1_id": grupo1_id,
            "grupo2_id": grupo2_id,
            "causa": causa,
            "tempo_inicio": 0,  # Será preenchido pelo motor
            "duracao": 0.0,
            "ativo": True,
            "batalhas": [],
            "baixas": {},
            "pontuacao_grupo1": 0,
            "pontuacao_grupo2": 0,
            "motivo_encerramento": None,
            "descricao_encerramento": None,
            "vencedor_id": None,
            "perdedor_id": None
        }
        
        # Adicionar informações específicas do tipo de conflito
        if tipo_conflito == "territorial" and "territorio_id" in causa:
            self.conflitos[conflito_id]["territorio_id"] = causa["territorio_id"]
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "conflito_iniciado",
            f"Conflito {tipo_conflito} iniciado entre grupos {grupo1_id} e {grupo2_id}: {causa['descricao']}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            []
        )
        
        return conflito_id
    
    def _determinar_causa_conflito(self, grupo1_id, grupo2_id, tipo_conflito, grupos):
        """
        Determina a causa específica de um conflito.
        
        Args:
            grupo1_id (str): ID do primeiro grupo.
            grupo2_id (str): ID do segundo grupo.
            tipo_conflito (str): Tipo de conflito.
            grupos (dict): Dicionário de grupos identificados.
            
        Returns:
            dict: Informações sobre a causa do conflito.
        """
        grupo1 = grupos[grupo1_id]
        grupo2 = grupos[grupo2_id]
        
        if tipo_conflito == "territorial":
            # Conflito por território
            return {
                "descricao": "Disputa por controle de território",
                "territorio_id": f"territorio_{random.randint(1, 100)}"  # Território fictício
            }
        
        elif tipo_conflito == "recursos":
            # Conflito por recursos
            recursos = ["comida", "agua", "madeira", "pedra", "metal"]
            recurso = random.choice(recursos)
            
            return {
                "descricao": f"Disputa por recursos: {recurso}",
                "recurso": recurso
            }
        
        elif tipo_conflito == "religioso":
            # Conflito religioso
            return {
                "descricao": "Diferenças religiosas ou de crenças"
            }
        
        elif tipo_conflito == "cultural":
            # Conflito cultural
            return {
                "descricao": "Diferenças culturais ou de valores"
            }
        
        elif tipo_conflito == "poder":
            # Conflito por poder
            return {
                "descricao": "Disputa por influência e poder"
            }
        
        else:
            # Conflito genérico
            return {
                "descricao": "Causas diversas"
            }
    
    def _atualizar_tratados(self, delta_tempo, grupos, senciantes):
        """
        Atualiza os tratados existentes.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for tratado_id, tratado in list(self.tratados.items()):
            # Verificar se os grupos ainda existem
            if tratado["grupo1_id"] not in grupos or tratado["grupo2_id"] not in grupos:
                # Encerrar tratado
                self._encerrar_tratado(tratado_id, "dissolucao", "Um dos grupos envolvidos foi dissolvido")
                continue
            
            # Verificar se o tratado ainda está ativo
            if not tratado["ativo"]:
                continue
            
            # Atualizar duração
            tratado["tempo_atual"] = tratado.get("tempo_atual", 0.0) + delta_tempo
            
            # Verificar expiração
            if tratado["tempo_atual"] >= tratado["duracao"]:
                self._encerrar_tratado(tratado_id, "expiracao", "Tratado expirou")
                continue
            
            # Verificar cumprimento dos termos
            self._verificar_cumprimento_termos(tratado_id, delta_tempo, grupos, senciantes)
    
    def _verificar_cumprimento_termos(self, tratado_id, delta_tempo, grupos, senciantes):
        """
        Verifica o cumprimento dos termos de um tratado.
        
        Args:
            tratado_id (str): ID do tratado.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        tratado = self.tratados[tratado_id]
        
        for termo in tratado["termos"]:
            # Verificar tipo de termo
            if termo["tipo"] == "nao_agressao":
                # Verificar se houve agressão
                for conflito in self.conflitos.values():
                    if conflito["ativo"] and (
                        (conflito["grupo1_id"] == tratado["grupo1_id"] and conflito["grupo2_id"] == tratado["grupo2_id"]) or
                        (conflito["grupo1_id"] == tratado["grupo2_id"] and conflito["grupo2_id"] == tratado["grupo1_id"])
                    ):
                        # Registrar violação
                        self._registrar_violacao_tratado(
                            tratado_id,
                            "agressao",
                            f"Conflito iniciado entre grupos {conflito['grupo1_id']} e {conflito['grupo2_id']}"
                        )
            
            elif termo["tipo"] == "tributo":
                # Verificar se é hora de pagar tributo
                termo["tempo_atual"] = termo.get("tempo_atual", 0.0) + delta_tempo
                
                if termo["tempo_atual"] >= termo["periodicidade"]:
                    # Resetar contador
                    termo["tempo_atual"] = 0.0
                    
                    # Verificar se o grupo tem recursos suficientes
                    grupo_pagador_id = tratado["grupo2_id"]  # Assumindo que o grupo2 é o perdedor/pagador
                    
                    if grupo_pagador_id in grupos:
                        grupo_pagador = grupos[grupo_pagador_id]
                        
                        if termo["recurso"] in grupo_pagador["recursos"] and grupo_pagador["recursos"][termo["recurso"]] >= termo["quantidade"]:
                            # Pagar tributo
                            self._transferir_recurso(
                                grupo_pagador_id,
                                tratado["grupo1_id"],
                                termo["recurso"],
                                termo["quantidade"],
                                grupos,
                                senciantes
                            )
                        else:
                            # Registrar violação
                            self._registrar_violacao_tratado(
                                tratado_id,
                                "falta_pagamento",
                                f"Grupo {grupo_pagador_id} não pagou tributo de {termo['quantidade']} {termo['recurso']}"
                            )
    
    def _transferir_recurso(self, grupo_origem_id, grupo_destino_id, recurso, quantidade, grupos, senciantes):
        """
        Transfere recursos entre grupos.
        
        Args:
            grupo_origem_id (str): ID do grupo de origem.
            grupo_destino_id (str): ID do grupo de destino.
            recurso (str): Tipo de recurso.
            quantidade (float): Quantidade de recurso.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            bool: True se a transferência foi bem-sucedida.
        """
        # Verificar se os grupos existem
        if grupo_origem_id not in grupos or grupo_destino_id not in grupos:
            return False
        
        grupo_origem = grupos[grupo_origem_id]
        grupo_destino = grupos[grupo_destino_id]
        
        # Verificar se o grupo de origem tem recursos suficientes
        if recurso not in grupo_origem["recursos"] or grupo_origem["recursos"][recurso] < quantidade:
            return False
        
        # Remover recursos do grupo de origem
        # Distribuir a remoção entre os membros
        quantidade_por_membro = quantidade / len(grupo_origem["membros"])
        
        for membro_id in grupo_origem["membros"]:
            if membro_id in senciantes:
                if recurso in senciantes[membro_id].inventario:
                    # Remover no máximo o que o membro tem
                    quantidade_removida = min(quantidade_por_membro, senciantes[membro_id].inventario[recurso])
                    senciantes[membro_id].inventario[recurso] -= quantidade_removida
                    
                    # Atualizar quantidade restante
                    quantidade_por_membro = (quantidade - quantidade_removida) / max(1, len(grupo_origem["membros"]) - 1)
        
        # Adicionar recursos ao grupo de destino
        # Distribuir a adição entre os membros
        quantidade_por_membro = quantidade / len(grupo_destino["membros"])
        
        for membro_id in grupo_destino["membros"]:
            if membro_id in senciantes:
                if recurso not in senciantes[membro_id].inventario:
                    senciantes[membro_id].inventario[recurso] = 0.0
                
                senciantes[membro_id].inventario[recurso] += quantidade_por_membro
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "transferencia_recurso",
            f"Transferência de {quantidade} {recurso} do grupo {grupo_origem_id} para o grupo {grupo_destino_id}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            []
        )
        
        return True
    
    def _registrar_violacao_tratado(self, tratado_id, tipo_violacao, descricao):
        """
        Registra uma violação de tratado.
        
        Args:
            tratado_id (str): ID do tratado.
            tipo_violacao (str): Tipo de violação.
            descricao (str): Descrição da violação.
        """
        tratado = self.tratados[tratado_id]
        
        # Adicionar violação
        violacao = {
            "tipo": tipo_violacao,
            "descricao": descricao,
            "tempo": 0  # Será preenchido pelo motor
        }
        
        tratado["violacoes"].append(violacao)
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "violacao_tratado",
            f"Violação de tratado: {descricao}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            []
        )
        
        # Verificar se o tratado deve ser encerrado
        if len(tratado["violacoes"]) >= 3:
            self._encerrar_tratado(tratado_id, "violacao", "Múltiplas violações do tratado")
    
    def _encerrar_tratado(self, tratado_id, motivo, descricao):
        """
        Encerra um tratado.
        
        Args:
            tratado_id (str): ID do tratado.
            motivo (str): Motivo do encerramento ("expiracao", "violacao", "acordo", "dissolucao").
            descricao (str): Descrição do encerramento.
        """
        tratado = self.tratados[tratado_id]
        
        # Atualizar estado do tratado
        tratado["ativo"] = False
        tratado["motivo_encerramento"] = motivo
        tratado["descricao_encerramento"] = descricao
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "tratado_encerrado",
            f"Tratado encerrado: {descricao}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            []
        )
    
    def _verificar_novas_negociacoes(self, delta_tempo, grupos, senciantes):
        """
        Verifica o surgimento de novas negociações diplomáticas.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Ignorar grupos individuais
        grupos_reais = {id: g for id, g in grupos.items() if not id.startswith("individual_") or len(g["membros"]) > 1}
        
        # Se há poucos grupos, não criar negociações
        if len(grupos_reais) < 2:
            return
        
        # Chance de nova negociação baseada no tempo
        chance_negociacao = 0.01 * delta_tempo
        
        if chance(chance_negociacao):
            # Escolher dois grupos aleatórios
            grupo_ids = list(grupos_reais.keys())
            grupo1_id, grupo2_id = random.sample(grupo_ids, 2)
            
            # Verificar se existe conflito ativo entre estes grupos
            conflito_ativo = False
            for conflito in self.conflitos.values():
                if conflito["ativo"] and (
                    (conflito["grupo1_id"] == grupo1_id and conflito["grupo2_id"] == grupo2_id) or
                    (conflito["grupo1_id"] == grupo2_id and conflito["grupo2_id"] == grupo1_id)
                ):
                    conflito_ativo = True
                    break
            
            # Determinar tipo de negociação
            if conflito_ativo:
                # Se há conflito, negociar paz
                tipo_tratado = "paz"
            else:
                # Se não há conflito, escolher outro tipo de tratado
                tipos_possiveis = ["alianca", "comercio", "nao_agressao", "protecao"]
                tipo_tratado = random.choice(tipos_possiveis)
            
            # Iniciar negociação
            self._iniciar_negociacao(grupo1_id, grupo2_id, tipo_tratado, grupos, senciantes)
    
    def _iniciar_negociacao(self, grupo1_id, grupo2_id, tipo_tratado, grupos, senciantes):
        """
        Inicia uma negociação diplomática entre dois grupos.
        
        Args:
            grupo1_id (str): ID do primeiro grupo.
            grupo2_id (str): ID do segundo grupo.
            tipo_tratado (str): Tipo de tratado a ser negociado.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: ID do tratado criado, ou None se a negociação falhou.
        """
        # Verificar se os grupos têm líderes
        if grupos[grupo1_id]["lider_id"] is None or grupos[grupo2_id]["lider_id"] is None:
            return None
        
        lider1_id = grupos[grupo1_id]["lider_id"]
        lider2_id = grupos[grupo2_id]["lider_id"]
        
        # Calcular chance de sucesso da negociação
        chance_sucesso = 0.5
        
        # Ajustar com base nas habilidades diplomáticas dos líderes
        if lider1_id in senciantes and hasattr(senciantes[lider1_id], "habilidades"):
            chance_sucesso += senciantes[lider1_id].habilidades.get("diplomacia", 0.0) * 0.2
        
        if lider2_id in senciantes and hasattr(senciantes[lider2_id], "habilidades"):
            chance_sucesso += senciantes[lider2_id].habilidades.get("diplomacia", 0.0) * 0.2
        
        # Ajustar com base no tipo de tratado
        if tipo_tratado == "paz":
            # Paz é mais difícil de negociar
            chance_sucesso -= 0.2
        elif tipo_tratado == "alianca":
            # Aliança é mais difícil de negociar
            chance_sucesso -= 0.1
        
        # Verificar sucesso da negociação
        if chance(chance_sucesso):
            # Criar termos do tratado
            termos = self._criar_termos_tratado(tipo_tratado, grupo1_id, grupo2_id, grupos)
            
            # Criar tratado
            tratado_id = f"tratado_{len(self.tratados) + 1}"
            
            self.tratados[tratado_id] = {
                "id": tratado_id,
                "tipo": tipo_tratado,
                "grupo1_id": grupo1_id,
                "grupo2_id": grupo2_id,
                "termos": termos,
                "tempo_criacao": 0,  # Será preenchido pelo motor
                "tempo_atual": 0.0,
                "duracao": 168.0,  # 7 dias
                "ativo": True,
                "violacoes": []
            }
            
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "tratado_criado",
                f"Tratado de {tipo_tratado} criado entre grupos {grupo1_id} e {grupo2_id}",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                [lider1_id, lider2_id]
            )
            
            # Se for um tratado de paz, encerrar conflitos ativos
            if tipo_tratado == "paz":
                for conflito_id, conflito in list(self.conflitos.items()):
                    if conflito["ativo"] and (
                        (conflito["grupo1_id"] == grupo1_id and conflito["grupo2_id"] == grupo2_id) or
                        (conflito["grupo1_id"] == grupo2_id and conflito["grupo2_id"] == grupo1_id)
                    ):
                        self._encerrar_conflito(
                            conflito_id,
                            "acordo",
                            f"Acordo de paz entre grupos {grupo1_id} e {grupo2_id}"
                        )
            
            return tratado_id
        else:
            # Negociação falhou
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "negociacao_falhou",
                f"Negociação de {tipo_tratado} falhou entre grupos {grupo1_id} e {grupo2_id}",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                [lider1_id, lider2_id]
            )
            
            return None
    
    def _criar_termos_tratado(self, tipo_tratado, grupo1_id, grupo2_id, grupos):
        """
        Cria os termos de um tratado.
        
        Args:
            tipo_tratado (str): Tipo de tratado.
            grupo1_id (str): ID do primeiro grupo.
            grupo2_id (str): ID do segundo grupo.
            grupos (dict): Dicionário de grupos identificados.
            
        Returns:
            list: Lista de termos do tratado.
        """
        termos = []
        
        if tipo_tratado == "paz":
            # Tratado de paz
            # Termo de não agressão
            termos.append({
                "tipo": "nao_agressao",
                "duracao": 168.0,  # 7 dias
                "descricao": f"Grupos {grupo1_id} e {grupo2_id} não podem atacar um ao outro por 7 dias"
            })
        
        elif tipo_tratado == "alianca":
            # Tratado de aliança
            # Termo de não agressão
            termos.append({
                "tipo": "nao_agressao",
                "duracao": 336.0,  # 14 dias
                "descricao": f"Grupos {grupo1_id} e {grupo2_id} não podem atacar um ao outro por 14 dias"
            })
            
            # Termo de assistência mútua
            termos.append({
                "tipo": "assistencia_mutua",
                "duracao": 336.0,  # 14 dias
                "descricao": f"Grupos {grupo1_id} e {grupo2_id} devem se ajudar em caso de ataque externo"
            })
        
        elif tipo_tratado == "comercio":
            # Tratado de comércio
            # Escolher recursos para troca
            recursos = ["comida", "agua", "madeira", "pedra", "metal"]
            recurso1 = random.choice(recursos)
            recurso2 = random.choice([r for r in recursos if r != recurso1])
            
            # Determinar quantidades
            quantidade1 = random.uniform(1.0, 5.0)
            quantidade2 = random.uniform(1.0, 5.0)
            
            termos.append({
                "tipo": "troca_comercial",
                "recurso1": recurso1,
                "quantidade1": quantidade1,
                "recurso2": recurso2,
                "quantidade2": quantidade2,
                "periodicidade": 24.0,  # 1 dia
                "duracao": 168.0,  # 7 dias
                "descricao": f"Grupo {grupo1_id} fornece {quantidade1} {recurso1} em troca de {quantidade2} {recurso2} do grupo {grupo2_id} a cada dia por 7 dias"
            })
        
        elif tipo_tratado == "nao_agressao":
            # Tratado de não agressão
            termos.append({
                "tipo": "nao_agressao",
                "duracao": 168.0,  # 7 dias
                "descricao": f"Grupos {grupo1_id} e {grupo2_id} não podem atacar um ao outro por 7 dias"
            })
        
        elif tipo_tratado == "protecao":
            # Tratado de proteção
            # Determinar grupo protetor (geralmente o mais forte)
            forca1 = grupos[grupo1_id]["forca_total"]
            forca2 = grupos[grupo2_id]["forca_total"]
            
            if forca1 > forca2:
                protetor_id = grupo1_id
                protegido_id = grupo2_id
            else:
                protetor_id = grupo2_id
                protegido_id = grupo1_id
            
            # Termo de proteção
            termos.append({
                "tipo": "protecao",
                "protetor_id": protetor_id,
                "protegido_id": protegido_id,
                "duracao": 168.0,  # 7 dias
                "descricao": f"Grupo {protetor_id} protege o grupo {protegido_id} por 7 dias"
            })
            
            # Termo de tributo
            recurso = random.choice(["comida", "agua", "madeira", "pedra", "metal"])
            quantidade = random.uniform(1.0, 3.0)
            
            termos.append({
                "tipo": "tributo",
                "recurso": recurso,
                "quantidade": quantidade,
                "periodicidade": 24.0,  # 1 dia
                "duracao": 168.0,  # 7 dias
                "descricao": f"Grupo {protegido_id} deve pagar tributo de {quantidade} {recurso} por dia ao grupo {protetor_id} durante 7 dias"
            })
        
        return termos
    
    def _atualizar_trocas_comerciais(self, delta_tempo, grupos, senciantes):
        """
        Atualiza as trocas comerciais entre grupos.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Processar trocas comerciais de tratados
        for tratado_id, tratado in self.tratados.items():
            if not tratado["ativo"] or tratado["tipo"] != "comercio":
                continue
            
            # Verificar se os grupos ainda existem
            if tratado["grupo1_id"] not in grupos or tratado["grupo2_id"] not in grupos:
                continue
            
            # Processar termos de troca comercial
            for termo in tratado["termos"]:
                if termo["tipo"] != "troca_comercial":
                    continue
                
                # Verificar se é hora de realizar a troca
                termo["tempo_atual"] = termo.get("tempo_atual", 0.0) + delta_tempo
                
                if termo["tempo_atual"] >= termo["periodicidade"]:
                    # Resetar contador
                    termo["tempo_atual"] = 0.0
                    
                    # Realizar troca
                    self._realizar_troca_comercial(
                        tratado["grupo1_id"],
                        tratado["grupo2_id"],
                        termo["recurso1"],
                        termo["quantidade1"],
                        termo["recurso2"],
                        termo["quantidade2"],
                        grupos,
                        senciantes
                    )
    
    def _realizar_troca_comercial(self, grupo1_id, grupo2_id, recurso1, quantidade1, recurso2, quantidade2, grupos, senciantes):
        """
        Realiza uma troca comercial entre dois grupos.
        
        Args:
            grupo1_id (str): ID do primeiro grupo.
            grupo2_id (str): ID do segundo grupo.
            recurso1 (str): Recurso oferecido pelo primeiro grupo.
            quantidade1 (float): Quantidade do recurso1.
            recurso2 (str): Recurso oferecido pelo segundo grupo.
            quantidade2 (float): Quantidade do recurso2.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            bool: True se a troca foi bem-sucedida.
        """
        # Verificar se os grupos têm recursos suficientes
        grupo1 = grupos[grupo1_id]
        grupo2 = grupos[grupo2_id]
        
        if recurso1 not in grupo1["recursos"] or grupo1["recursos"][recurso1] < quantidade1:
            return False
        
        if recurso2 not in grupo2["recursos"] or grupo2["recursos"][recurso2] < quantidade2:
            return False
        
        # Realizar transferências
        sucesso1 = self._transferir_recurso(grupo1_id, grupo2_id, recurso1, quantidade1, grupos, senciantes)
        sucesso2 = self._transferir_recurso(grupo2_id, grupo1_id, recurso2, quantidade2, grupos, senciantes)
        
        if sucesso1 and sucesso2:
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "troca_comercial",
                f"Troca comercial entre grupos {grupo1_id} e {grupo2_id}: {quantidade1} {recurso1} por {quantidade2} {recurso2}",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                []
            )
            
            return True
        else:
            return False
    
    def iniciar_guerra_tribal(self, grupo1_id, grupo2_id, causa, grupos, senciantes):
        """
        Inicia uma guerra tribal entre dois grupos.
        
        Args:
            grupo1_id (str): ID do primeiro grupo.
            grupo2_id (str): ID do segundo grupo.
            causa (str): Causa da guerra.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: ID do conflito criado.
        """
        # Verificar se os grupos existem
        if grupo1_id not in grupos or grupo2_id not in grupos:
            return None
        
        # Criar conflito
        return self._criar_conflito(grupo1_id, grupo2_id, "tribal", grupos, senciantes)
    
    def iniciar_guerra_religiosa(self, grupo1_id, grupo2_id, causa, grupos, senciantes):
        """
        Inicia uma guerra religiosa entre dois grupos.
        
        Args:
            grupo1_id (str): ID do primeiro grupo.
            grupo2_id (str): ID do segundo grupo.
            causa (str): Causa da guerra.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: ID do conflito criado.
        """
        # Verificar se os grupos existem
        if grupo1_id not in grupos or grupo2_id not in grupos:
            return None
        
        # Criar conflito
        return self._criar_conflito(grupo1_id, grupo2_id, "religioso", grupos, senciantes)
    
    def propor_tratado(self, grupo1_id, grupo2_id, tipo_tratado, termos, grupos, senciantes):
        """
        Propõe um tratado entre dois grupos.
        
        Args:
            grupo1_id (str): ID do grupo proponente.
            grupo2_id (str): ID do grupo receptor.
            tipo_tratado (str): Tipo de tratado.
            termos (list): Lista de termos do tratado.
            grupos (dict): Dicionário de grupos identificados.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: ID do tratado criado, ou None se a proposta foi rejeitada.
        """
        # Verificar se os grupos existem
        if grupo1_id not in grupos or grupo2_id not in grupos:
            return None
        
        # Verificar se os grupos têm líderes
        if grupos[grupo1_id]["lider_id"] is None or grupos[grupo2_id]["lider_id"] is None:
            return None
        
        lider1_id = grupos[grupo1_id]["lider_id"]
        lider2_id = grupos[grupo2_id]["lider_id"]
        
        # Calcular chance de aceitação
        chance_aceitacao = 0.5
        
        # Ajustar com base nas habilidades diplomáticas dos líderes
        if lider1_id in senciantes and hasattr(senciantes[lider1_id], "habilidades"):
            chance_aceitacao += senciantes[lider1_id].habilidades.get("diplomacia", 0.0) * 0.2
        
        # Verificar aceitação
        if chance(chance_aceitacao):
            # Criar tratado
            tratado_id = f"tratado_{len(self.tratados) + 1}"
            
            self.tratados[tratado_id] = {
                "id": tratado_id,
                "tipo": tipo_tratado,
                "grupo1_id": grupo1_id,
                "grupo2_id": grupo2_id,
                "termos": termos,
                "tempo_criacao": 0,  # Será preenchido pelo motor
                "tempo_atual": 0.0,
                "duracao": 168.0,  # 7 dias
                "ativo": True,
                "violacoes": []
            }
            
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "tratado_criado",
                f"Tratado de {tipo_tratado} criado entre grupos {grupo1_id} e {grupo2_id}",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                [lider1_id, lider2_id]
            )
            
            return tratado_id
        else:
            # Proposta rejeitada
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "tratado_rejeitado",
                f"Proposta de tratado de {tipo_tratado} rejeitada pelo grupo {grupo2_id}",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                [lider1_id, lider2_id]
            )
            
            return None
    
    def obter_conflitos_ativos(self):
        """
        Obtém os conflitos ativos.
        
        Returns:
            dict: Dicionário de conflitos ativos.
        """
        return {id: c for id, c in self.conflitos.items() if c["ativo"]}
    
    def obter_tratados_ativos(self):
        """
        Obtém os tratados ativos.
        
        Returns:
            dict: Dicionário de tratados ativos.
        """
        return {id: t for id, t in self.tratados.items() if t["ativo"]}

