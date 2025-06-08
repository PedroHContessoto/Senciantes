"""
Implementação das mecânicas de doenças e medicina evolutiva para o jogo "O Mundo dos Senciantes".
"""

import random
from modelos.doenca import Doenca
from utils.helpers import chance, calcular_distancia

class MecanicaDoencaMedicina:
    """
    Classe que implementa as mecânicas de doenças e medicina evolutiva.
    """
    
    def __init__(self, mundo):
        """
        Inicializa a mecânica de doenças e medicina.
        
        Args:
            mundo (Mundo): Objeto mundo para referência.
        """
        self.mundo = mundo
        self.doencas_ativas = {}  # Dicionário de id_doenca: doenca
        self.senciantes_infectados = {}  # Dicionário de senciante_id: [id_doenca1, id_doenca2, ...]
        self.tratamentos_conhecidos = {}  # Dicionário de id_doenca: {tipo_tratamento: eficacia}
        
        # Tipos de tratamentos possíveis
        self.tipos_tratamentos = ["ervas", "ritual", "medicina_avancada"]
        
        # Plantas medicinais conhecidas
        self.plantas_medicinais = {}  # Dicionário de id_planta: {efeito: potencia}
    
    def atualizar(self, delta_tempo, senciantes):
        """
        Atualiza o estado das doenças e medicina no mundo.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Chance de surgimento de nova doença
        if chance(0.01 * delta_tempo):
            self._gerar_nova_doenca()
        
        # Atualizar doenças existentes
        self._atualizar_doencas(delta_tempo, senciantes)
        
        # Atualizar senciantes infectados
        self._atualizar_senciantes_infectados(delta_tempo, senciantes)
        
        # Chance de descoberta de novo tratamento
        if chance(0.02 * delta_tempo) and self.doencas_ativas:
            self._descobrir_tratamento(senciantes)
    
    def _gerar_nova_doenca(self):
        """
        Gera uma nova doença no mundo.
        
        Returns:
            Doenca: Nova doença gerada.
        """
        # Criar nova doença
        doenca = Doenca()
        
        # Adicionar à lista de doenças ativas
        self.doencas_ativas[doenca.id] = doenca
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "doenca",
            f"Surgimento de nova doença: {doenca.nome} (tipo: {doenca.tipo})",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            []
        )
        
        return doenca
    
    def _atualizar_doencas(self, delta_tempo, senciantes):
        """
        Atualiza o estado das doenças ativas.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Verificar condições para surgimento de epidemias
        self._verificar_condicoes_epidemia(senciantes)
        
        # Chance de mutação de doenças existentes
        for doenca_id, doenca in list(self.doencas_ativas.items()):
            # Chance de mutação baseada no tempo
            if chance(0.005 * delta_tempo):
                nova_doenca = doenca.mutar()
                self.doencas_ativas[nova_doenca.id] = nova_doenca
                
                # Registrar no histórico do mundo
                self.mundo.historico.registrar_evento(
                    "doenca",
                    f"Mutação de doença: {doenca.nome} → {nova_doenca.nome}",
                    0,  # Tempo atual (será preenchido pelo motor de simulação)
                    []
                )
    
    def _verificar_condicoes_epidemia(self, senciantes):
        """
        Verifica se existem condições para o surgimento de uma epidemia.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Verificar densidade populacional
        regioes = {}
        
        # Dividir o mundo em regiões de 10x10
        tamanho_regiao = 10
        for senciante in senciantes.values():
            regiao_x = int(senciante.posicao[0] / tamanho_regiao)
            regiao_y = int(senciante.posicao[1] / tamanho_regiao)
            regiao_id = f"{regiao_x}_{regiao_y}"
            
            if regiao_id not in regioes:
                regioes[regiao_id] = []
            
            regioes[regiao_id].append(senciante.id)
        
        # Verificar regiões com alta densidade
        for regiao_id, senciantes_na_regiao in regioes.items():
            if len(senciantes_na_regiao) >= 5:  # Limiar de densidade
                # Verificar condições de higiene
                nivel_higiene_medio = 0.0
                
                for senciante_id in senciantes_na_regiao:
                    if senciante_id in senciantes:
                        nivel_higiene_medio += 1.0 - senciantes[senciante_id].necessidades["higiene"]
                
                nivel_higiene_medio /= len(senciantes_na_regiao)
                
                # Se higiene média for baixa, chance de epidemia
                if nivel_higiene_medio < 0.4:  # Limiar de higiene
                    if chance(0.2):  # 20% de chance de epidemia
                        self._iniciar_epidemia(senciantes_na_regiao, senciantes)
    
    def _iniciar_epidemia(self, senciantes_na_regiao, todos_senciantes):
        """
        Inicia uma epidemia em uma região.
        
        Args:
            senciantes_na_regiao (list): Lista de IDs de Senciantes na região.
            todos_senciantes (dict): Dicionário de todos os Senciantes.
        """
        # Escolher uma doença existente ou criar uma nova
        if self.doencas_ativas and chance(0.7):
            # Escolher uma doença existente
            doenca_id = random.choice(list(self.doencas_ativas.keys()))
            doenca = self.doencas_ativas[doenca_id]
        else:
            # Criar uma nova doença mais transmissível
            doenca = Doenca(
                transmissibilidade=random.uniform(0.6, 0.9),
                gravidade=random.uniform(0.4, 0.8)
            )
            self.doencas_ativas[doenca.id] = doenca
        
        # Infectar alguns Senciantes iniciais
        num_infectados_iniciais = max(1, int(len(senciantes_na_regiao) * 0.2))
        infectados_iniciais = random.sample(senciantes_na_regiao, num_infectados_iniciais)
        
        for senciante_id in infectados_iniciais:
            self.infectar_senciante(senciante_id, doenca.id, todos_senciantes)
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "epidemia",
            f"Início de epidemia: {doenca.nome} em região com {len(senciantes_na_regiao)} Senciantes",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            infectados_iniciais
        )
    
    def _atualizar_senciantes_infectados(self, delta_tempo, senciantes):
        """
        Atualiza o estado dos Senciantes infectados.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Para cada Senciante infectado
        for senciante_id, doencas_ids in list(self.senciantes_infectados.items()):
            # Verificar se o Senciante ainda existe
            if senciante_id not in senciantes:
                del self.senciantes_infectados[senciante_id]
                continue
            
            senciante = senciantes[senciante_id]
            
            # Para cada doença que afeta o Senciante
            for doenca_id in list(doencas_ids):
                # Verificar se a doença ainda existe
                if doenca_id not in self.doencas_ativas:
                    doencas_ids.remove(doenca_id)
                    continue
                
                doenca = self.doencas_ativas[doenca_id]
                
                # Aplicar efeitos da doença
                doenca.aplicar_efeitos(senciante, delta_tempo)
                
                # Verificar cura natural
                if self._verificar_cura_natural(senciante, doenca, delta_tempo):
                    doencas_ids.remove(doenca_id)
                    
                    # Registrar no histórico do mundo
                    self.mundo.historico.registrar_evento(
                        "cura",
                        f"Senciante curou-se naturalmente de {doenca.nome}",
                        0,  # Tempo atual (será preenchido pelo motor de simulação)
                        [senciante_id]
                    )
                    
                    continue
                
                # Verificar transmissão para outros Senciantes
                self._verificar_transmissao(senciante, doenca, senciantes)
            
            # Se não há mais doenças, remover da lista de infectados
            if not doencas_ids:
                del self.senciantes_infectados[senciante_id]
    
    def _verificar_cura_natural(self, senciante, doenca, delta_tempo):
        """
        Verifica se um Senciante se cura naturalmente de uma doença.
        
        Args:
            senciante (Senciante): Senciante infectado.
            doenca (Doenca): Doença que afeta o Senciante.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            
        Returns:
            bool: True se o Senciante se curou, False caso contrário.
        """
        # Chance de cura baseada na resistência do Senciante e no tempo
        resistencia = senciante.genoma.genes.get("resistencia", 1.0) * senciante.modificadores.get("imunidade", 1.0)
        
        # Chance base de cura por hora
        chance_cura_base = 0.01 * resistencia
        
        # Ajustar com base na gravidade da doença
        chance_cura = chance_cura_base * (1.0 - doenca.gravidade * 0.5)
        
        # Chance total para o período de tempo
        chance_cura_total = chance_cura * delta_tempo
        
        return chance(chance_cura_total)
    
    def _verificar_transmissao(self, senciante_infectado, doenca, senciantes):
        """
        Verifica a transmissão de uma doença para outros Senciantes.
        
        Args:
            senciante_infectado (Senciante): Senciante infectado.
            doenca (Doenca): Doença a ser transmitida.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Verificar Senciantes próximos
        for outro_id, outro_senciante in senciantes.items():
            # Ignorar o próprio Senciante infectado
            if outro_id == senciante_infectado.id:
                continue
            
            # Ignorar Senciantes já infectados com esta doença
            if outro_id in self.senciantes_infectados and doenca.id in self.senciantes_infectados[outro_id]:
                continue
            
            # Calcular distância
            distancia = calcular_distancia(senciante_infectado.posicao, outro_senciante.posicao)
            
            # Verificar se está próximo o suficiente para transmissão
            if distancia <= 2.0:
                # Calcular chance de transmissão
                chance_transmissao = doenca.calcular_chance_transmissao(senciante_infectado, outro_senciante)
                
                # Tentar transmitir
                if chance(chance_transmissao):
                    self.infectar_senciante(outro_id, doenca.id, senciantes)
    
    def infectar_senciante(self, senciante_id, doenca_id, senciantes):
        """
        Infecta um Senciante com uma doença.
        
        Args:
            senciante_id (str): ID do Senciante a ser infectado.
            doenca_id (str): ID da doença.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            bool: True se o Senciante foi infectado, False caso contrário.
        """
        # Verificar se o Senciante existe
        if senciante_id not in senciantes:
            return False
        
        # Verificar se a doença existe
        if doenca_id not in self.doencas_ativas:
            return False
        
        # Verificar se o Senciante já está infectado com esta doença
        if senciante_id in self.senciantes_infectados and doenca_id in self.senciantes_infectados[senciante_id]:
            return False
        
        # Adicionar à lista de infectados
        if senciante_id not in self.senciantes_infectados:
            self.senciantes_infectados[senciante_id] = []
        
        self.senciantes_infectados[senciante_id].append(doenca_id)
        
        # Registrar propagação na doença
        self.doencas_ativas[doenca_id].registrar_propagacao(0, senciante_id)  # Tempo será preenchido pelo motor
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "infeccao",
            f"Senciante infectado com {self.doencas_ativas[doenca_id].nome}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [senciante_id]
        )
        
        return True
    
    def _descobrir_tratamento(self, senciantes):
        """
        Descobre um novo tratamento para uma doença.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            dict: Informações sobre o tratamento descoberto.
        """
        # Escolher uma doença aleatória
        if not self.doencas_ativas:
            return None
        
        doenca_id = random.choice(list(self.doencas_ativas.keys()))
        doenca = self.doencas_ativas[doenca_id]
        
        # Escolher um tipo de tratamento
        tipo_tratamento = random.choice(self.tipos_tratamentos)
        
        # Verificar se já existe um tratamento deste tipo para esta doença
        if doenca_id in self.tratamentos_conhecidos and tipo_tratamento in self.tratamentos_conhecidos[doenca_id]:
            # Melhorar tratamento existente
            eficacia_atual = self.tratamentos_conhecidos[doenca_id][tipo_tratamento]
            nova_eficacia = min(1.0, eficacia_atual + random.uniform(0.1, 0.2))
            
            self.tratamentos_conhecidos[doenca_id][tipo_tratamento] = nova_eficacia
            
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "tratamento",
                f"Melhoria de tratamento para {doenca.nome}: {tipo_tratamento} (eficácia: {nova_eficacia:.2f})",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                []
            )
            
            return {
                "tipo": "melhoria",
                "doenca_id": doenca_id,
                "nome_doenca": doenca.nome,
                "tipo_tratamento": tipo_tratamento,
                "eficacia": nova_eficacia
            }
        else:
            # Criar novo tratamento
            eficacia_base = random.uniform(0.3, 0.6)
            
            # Inicializar dicionário de tratamentos para esta doença, se necessário
            if doenca_id not in self.tratamentos_conhecidos:
                self.tratamentos_conhecidos[doenca_id] = {}
            
            self.tratamentos_conhecidos[doenca_id][tipo_tratamento] = eficacia_base
            
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "tratamento",
                f"Descoberta de tratamento para {doenca.nome}: {tipo_tratamento} (eficácia: {eficacia_base:.2f})",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                []
            )
            
            return {
                "tipo": "descoberta",
                "doenca_id": doenca_id,
                "nome_doenca": doenca.nome,
                "tipo_tratamento": tipo_tratamento,
                "eficacia": eficacia_base
            }
    
    def aplicar_tratamento(self, senciante_id, doenca_id, tipo_tratamento, senciantes):
        """
        Aplica um tratamento a um Senciante infectado.
        
        Args:
            senciante_id (str): ID do Senciante a ser tratado.
            doenca_id (str): ID da doença a ser tratada.
            tipo_tratamento (str): Tipo de tratamento a ser aplicado.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            dict: Resultado do tratamento.
        """
        # Verificar se o Senciante existe e está infectado
        if (senciante_id not in senciantes or
            senciante_id not in self.senciantes_infectados or
            doenca_id not in self.senciantes_infectados[senciante_id]):
            return {"sucesso": False, "mensagem": "Senciante não está infectado com esta doença"}
        
        # Verificar se a doença existe
        if doenca_id not in self.doencas_ativas:
            return {"sucesso": False, "mensagem": "Doença não encontrada"}
        
        doenca = self.doencas_ativas[doenca_id]
        
        # Verificar se o tratamento é conhecido
        if (doenca_id not in self.tratamentos_conhecidos or
            tipo_tratamento not in self.tratamentos_conhecidos[doenca_id]):
            return {"sucesso": False, "mensagem": "Tratamento desconhecido para esta doença"}
        
        # Obter eficácia base do tratamento
        eficacia_base = self.tratamentos_conhecidos[doenca_id][tipo_tratamento]
        
        # Calcular eficácia real do tratamento
        eficacia_real = doenca.responder_tratamento(tipo_tratamento, eficacia_base)
        
        # Chance de cura baseada na eficácia real
        if chance(eficacia_real):
            # Remover doença do Senciante
            self.senciantes_infectados[senciante_id].remove(doenca_id)
            
            # Se não há mais doenças, remover da lista de infectados
            if not self.senciantes_infectados[senciante_id]:
                del self.senciantes_infectados[senciante_id]
            
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "cura",
                f"Senciante curado de {doenca.nome} com tratamento: {tipo_tratamento}",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                [senciante_id]
            )
            
            return {
                "sucesso": True,
                "mensagem": f"Tratamento bem-sucedido! {doenca.nome} curada.",
                "eficacia_real": eficacia_real
            }
        else:
            # Tratamento falhou, mas pode melhorar a condição
            senciante = senciantes[senciante_id]
            
            # Pequena melhora na saúde
            senciante.estado["saude"] = min(1.0, senciante.estado["saude"] + 0.05)
            
            return {
                "sucesso": False,
                "mensagem": f"Tratamento não curou a doença, mas trouxe algum alívio.",
                "eficacia_real": eficacia_real
            }
    
    def registrar_planta_medicinal(self, planta_id, efeito, potencia):
        """
        Registra uma planta com propriedades medicinais.
        
        Args:
            planta_id (str): ID da planta.
            efeito (str): Efeito medicinal da planta.
            potencia (float): Potência do efeito (0.0 a 1.0).
        """
        self.plantas_medicinais[planta_id] = {
            "efeito": efeito,
            "potencia": potencia
        }
    
    def obter_doencas_senciante(self, senciante_id):
        """
        Obtém as doenças que afetam um Senciante.
        
        Args:
            senciante_id (str): ID do Senciante.
            
        Returns:
            list: Lista de doenças que afetam o Senciante.
        """
        if senciante_id not in self.senciantes_infectados:
            return []
        
        doencas = []
        for doenca_id in self.senciantes_infectados[senciante_id]:
            if doenca_id in self.doencas_ativas:
                doencas.append(self.doencas_ativas[doenca_id])
        
        return doencas
    
    def obter_estatisticas_epidemia(self):
        """
        Obtém estatísticas sobre as epidemias atuais.
        
        Returns:
            dict: Estatísticas sobre as epidemias.
        """
        estatisticas = {}
        
        for doenca_id, doenca in self.doencas_ativas.items():
            # Contar infectados
            num_infectados = 0
            for doencas_senciante in self.senciantes_infectados.values():
                if doenca_id in doencas_senciante:
                    num_infectados += 1
            
            estatisticas[doenca_id] = {
                "nome": doenca.nome,
                "tipo": doenca.tipo,
                "gravidade": doenca.gravidade,
                "transmissibilidade": doenca.transmissibilidade,
                "num_infectados": num_infectados,
                "tratamentos_conhecidos": self.tratamentos_conhecidos.get(doenca_id, {})
            }
        
        return estatisticas

