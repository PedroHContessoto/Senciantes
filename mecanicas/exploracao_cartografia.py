"""
Implementação das mecânicas de exploração do mundo e cartografia para o jogo "O Mundo dos Senciantes".
"""

import random
import numpy as np
from modelos.territorio import Territorio
from utils.helpers import chance, calcular_distancia

class MecanicaExploracao:
    """
    Classe que implementa as mecânicas de exploração do mundo e cartografia.
    """
    
    def __init__(self, mundo):
        """
        Inicializa a mecânica de exploração.
        
        Args:
            mundo (Mundo): Objeto mundo para referência.
        """
        self.mundo = mundo
        self.territorios = {}  # Dicionário de id_territorio: territorio
        self.regioes_nomeadas = {}  # Dicionário de id_regiao: {nome, descobridor_id, tempo_descoberta}
        self.mapas = {}  # Dicionário de id_mapa: {criador_id, tempo_criacao, regioes, precisao}
        
        # Matriz de exploração (0.0 = inexplorado, 1.0 = totalmente explorado)
        self.matriz_exploracao = np.zeros((int(mundo.tamanho[0] / 5), int(mundo.tamanho[1] / 5)))
        
        # Inicializar territórios iniciais
        self._inicializar_territorios()
    
    def _inicializar_territorios(self):
        """
        Inicializa territórios iniciais no mundo.
        """
        # Criar alguns territórios iniciais com recursos especiais
        num_territorios_iniciais = random.randint(3, 7)
        
        for _ in range(num_territorios_iniciais):
            # Posição aleatória
            pos_x = random.uniform(0, self.mundo.tamanho[0])
            pos_y = random.uniform(0, self.mundo.tamanho[1])
            
            # Tamanho aleatório
            tamanho = random.uniform(10, 30)
            
            # Criar território
            territorio = Territorio(
                posicao=[pos_x, pos_y],
                tamanho=tamanho,
                tipo=random.choice(["floresta", "montanha", "planicie", "deserto", "pantano", "costa"])
            )
            
            # Adicionar recursos especiais
            self._adicionar_recursos_especiais(territorio)
            
            # Adicionar à lista de territórios
            self.territorios[territorio.id] = territorio
    
    def _adicionar_recursos_especiais(self, territorio):
        """
        Adiciona recursos especiais a um território.
        
        Args:
            territorio (Territorio): Território a receber recursos especiais.
        """
        # Chance de recursos especiais baseada no tipo de território
        if territorio.tipo == "montanha":
            if chance(0.7):
                territorio.recursos_especiais.append("minerais")
            if chance(0.3):
                territorio.recursos_especiais.append("caverna")
        
        elif territorio.tipo == "floresta":
            if chance(0.6):
                territorio.recursos_especiais.append("plantas_raras")
            if chance(0.4):
                territorio.recursos_especiais.append("animais_raros")
        
        elif territorio.tipo == "planicie":
            if chance(0.8):
                territorio.recursos_especiais.append("terra_fertil")
            if chance(0.3):
                territorio.recursos_especiais.append("agua_fresca")
        
        elif territorio.tipo == "deserto":
            if chance(0.4):
                territorio.recursos_especiais.append("oasis")
            if chance(0.3):
                territorio.recursos_especiais.append("minerais_raros")
        
        elif territorio.tipo == "pantano":
            if chance(0.7):
                territorio.recursos_especiais.append("plantas_medicinais")
            if chance(0.5):
                territorio.recursos_especiais.append("fungos_raros")
        
        elif territorio.tipo == "costa":
            if chance(0.6):
                territorio.recursos_especiais.append("peixes_abundantes")
            if chance(0.3):
                territorio.recursos_especiais.append("conchas_raras")
    
    def atualizar(self, delta_tempo, senciantes):
        """
        Atualiza o estado da exploração no mundo.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Atualizar exploração para cada Senciante
        for senciante_id, senciante in senciantes.items():
            self._atualizar_exploracao_senciante(senciante, delta_tempo)
        
        # Chance de criar novos territórios com recursos especiais
        if chance(0.01 * delta_tempo):
            self._criar_novo_territorio()
        
        # Atualizar disputas territoriais
        self._atualizar_disputas_territoriais(senciantes)
    
    def _atualizar_exploracao_senciante(self, senciante, delta_tempo):
        """
        Atualiza a exploração para um Senciante.
        
        Args:
            senciante (Senciante): Senciante que está explorando.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Obter posição do Senciante
        pos_x, pos_y = senciante.posicao
        
        # Converter para índices na matriz de exploração
        idx_x = int(pos_x / 5)
        idx_y = int(pos_y / 5)
        
        # Verificar limites
        if (0 <= idx_x < self.matriz_exploracao.shape[0] and
            0 <= idx_y < self.matriz_exploracao.shape[1]):
            
            # Aumentar nível de exploração na posição atual
            aumento_exploracao = 0.1 * delta_tempo
            
            # Ajustar com base na habilidade de exploração do Senciante
            if hasattr(senciante, "habilidades") and "exploracao" in senciante.habilidades:
                aumento_exploracao *= (1.0 + senciante.habilidades["exploracao"])
            
            # Aplicar aumento
            self.matriz_exploracao[idx_x, idx_y] = min(1.0, self.matriz_exploracao[idx_x, idx_y] + aumento_exploracao)
            
            # Verificar descoberta de território
            self._verificar_descoberta_territorio(senciante, pos_x, pos_y)
            
            # Chance de nomear região
            if self.matriz_exploracao[idx_x, idx_y] >= 0.8 and chance(0.05 * delta_tempo):
                self._nomear_regiao(senciante, idx_x, idx_y)
            
            # Chance de criar mapa
            if hasattr(senciante, "habilidades") and "cartografia" in senciante.habilidades:
                chance_mapa = 0.02 * senciante.habilidades["cartografia"] * delta_tempo
                if chance(chance_mapa):
                    self._criar_mapa(senciante)
    
    def _verificar_descoberta_territorio(self, senciante, pos_x, pos_y):
        """
        Verifica se o Senciante descobriu um território.
        
        Args:
            senciante (Senciante): Senciante que está explorando.
            pos_x (float): Posição X do Senciante.
            pos_y (float): Posição Y do Senciante.
        """
        for territorio_id, territorio in self.territorios.items():
            # Verificar se o território já foi descoberto pelo Senciante
            if territorio_id in senciante.territorios_conhecidos:
                continue
            
            # Calcular distância ao centro do território
            distancia = calcular_distancia([pos_x, pos_y], territorio.posicao)
            
            # Se estiver dentro do território
            if distancia <= territorio.tamanho:
                # Descobrir território
                senciante.territorios_conhecidos.append(territorio_id)
                
                # Registrar descoberta no histórico do mundo
                self.mundo.historico.registrar_evento(
                    "descoberta_territorio",
                    f"Senciante descobriu território: {territorio.tipo} com recursos: {', '.join(territorio.recursos_especiais)}",
                    0,  # Tempo atual (será preenchido pelo motor de simulação)
                    [senciante.id]
                )
                
                # Verificar se é o primeiro a descobrir
                if territorio.descobridor_id is None:
                    territorio.descobridor_id = senciante.id
                    territorio.tempo_descoberta = 0  # Será preenchido pelo motor
                    
                    # Registrar como primeiro descobridor
                    self.mundo.historico.registrar_evento(
                        "primeiro_descobridor",
                        f"Senciante foi o primeiro a descobrir território: {territorio.tipo}",
                        0,  # Tempo atual (será preenchido pelo motor de simulação)
                        [senciante.id]
                    )
    
    def _nomear_regiao(self, senciante, idx_x, idx_y):
        """
        Nomeia uma região do mundo.
        
        Args:
            senciante (Senciante): Senciante que está nomeando a região.
            idx_x (int): Índice X na matriz de exploração.
            idx_y (int): Índice Y na matriz de exploração.
        """
        # Identificador único para a região
        regiao_id = f"{idx_x}_{idx_y}"
        
        # Verificar se a região já foi nomeada
        if regiao_id in self.regioes_nomeadas:
            return
        
        # Gerar nome para a região
        nome_regiao = self._gerar_nome_regiao(senciante, idx_x, idx_y)
        
        # Registrar região nomeada
        self.regioes_nomeadas[regiao_id] = {
            "nome": nome_regiao,
            "descobridor_id": senciante.id,
            "tempo_descoberta": 0  # Será preenchido pelo motor
        }
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "regiao_nomeada",
            f"Senciante nomeou região como: {nome_regiao}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [senciante.id]
        )
    
    def _gerar_nome_regiao(self, senciante, idx_x, idx_y):
        """
        Gera um nome para uma região.
        
        Args:
            senciante (Senciante): Senciante que está nomeando a região.
            idx_x (int): Índice X na matriz de exploração.
            idx_y (int): Índice Y na matriz de exploração.
            
        Returns:
            str: Nome gerado para a região.
        """
        # Determinar tipo de bioma predominante
        pos_x = idx_x * 5 + 2.5  # Centro da célula
        pos_y = idx_y * 5 + 2.5  # Centro da célula
        bioma = self.mundo.obter_bioma([pos_x, pos_y])
        
        # Prefixos baseados no bioma
        prefixos = {
            "floresta": ["Bosque", "Selva", "Arvoredo", "Mata", "Floresta"],
            "montanha": ["Monte", "Serra", "Pico", "Cordilheira", "Montanha"],
            "planicie": ["Campo", "Planície", "Pradaria", "Vale", "Campina"],
            "deserto": ["Deserto", "Dunas", "Areias", "Estepe", "Sertão"],
            "pantano": ["Pântano", "Brejo", "Charco", "Mangue", "Alagado"],
            "costa": ["Costa", "Praia", "Litoral", "Baía", "Enseada"],
            "agua": ["Lago", "Lagoa", "Rio", "Riacho", "Córrego"]
        }
        
        # Sufixos genéricos
        sufixos = [
            "Grande", "Pequeno", "Antigo", "Novo", "Belo", "Escuro", "Claro",
            "Sagrado", "Misterioso", "Encantado", "Perdido", "Esquecido",
            "do Norte", "do Sul", "do Leste", "do Oeste", "Central"
        ]
        
        # Escolher prefixo e sufixo
        prefixo = random.choice(prefixos.get(bioma, ["Terra"]))
        sufixo = random.choice(sufixos)
        
        # Gerar nome
        nome = f"{prefixo} {sufixo}"
        
        return nome
    
    def _criar_mapa(self, senciante):
        """
        Cria um mapa baseado na exploração do Senciante.
        
        Args:
            senciante (Senciante): Senciante que está criando o mapa.
            
        Returns:
            str: ID do mapa criado.
        """
        # Determinar precisão do mapa baseada na habilidade de cartografia
        precisao = 0.5
        if hasattr(senciante, "habilidades") and "cartografia" in senciante.habilidades:
            precisao = 0.3 + 0.5 * senciante.habilidades["cartografia"]
        
        # Coletar regiões conhecidas pelo Senciante
        regioes_conhecidas = []
        
        for regiao_id, info in self.regioes_nomeadas.items():
            idx_x, idx_y = map(int, regiao_id.split("_"))
            
            # Verificar se a região foi explorada pelo Senciante
            if (0 <= idx_x < self.matriz_exploracao.shape[0] and
                0 <= idx_y < self.matriz_exploracao.shape[1] and
                self.matriz_exploracao[idx_x, idx_y] >= 0.5):
                
                regioes_conhecidas.append({
                    "id": regiao_id,
                    "nome": info["nome"],
                    "posicao": [idx_x * 5 + 2.5, idx_y * 5 + 2.5]  # Centro da célula
                })
        
        # Coletar territórios conhecidos pelo Senciante
        territorios_conhecidos = []
        
        for territorio_id in senciante.territorios_conhecidos:
            if territorio_id in self.territorios:
                territorio = self.territorios[territorio_id]
                
                territorios_conhecidos.append({
                    "id": territorio_id,
                    "tipo": territorio.tipo,
                    "posicao": territorio.posicao,
                    "tamanho": territorio.tamanho,
                    "recursos": territorio.recursos_especiais
                })
        
        # Gerar ID único para o mapa
        mapa_id = f"mapa_{len(self.mapas) + 1}"
        
        # Criar mapa
        self.mapas[mapa_id] = {
            "criador_id": senciante.id,
            "tempo_criacao": 0,  # Será preenchido pelo motor
            "regioes": regioes_conhecidas,
            "territorios": territorios_conhecidos,
            "precisao": precisao
        }
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "mapa_criado",
            f"Senciante criou mapa com {len(regioes_conhecidas)} regiões e {len(territorios_conhecidos)} territórios",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [senciante.id]
        )
        
        return mapa_id
    
    def _criar_novo_territorio(self):
        """
        Cria um novo território com recursos especiais.
        
        Returns:
            Territorio: Novo território criado.
        """
        # Posição aleatória
        pos_x = random.uniform(0, self.mundo.tamanho[0])
        pos_y = random.uniform(0, self.mundo.tamanho[1])
        
        # Tamanho aleatório
        tamanho = random.uniform(10, 30)
        
        # Criar território
        territorio = Territorio(
            posicao=[pos_x, pos_y],
            tamanho=tamanho,
            tipo=random.choice(["floresta", "montanha", "planicie", "deserto", "pantano", "costa"])
        )
        
        # Adicionar recursos especiais
        self._adicionar_recursos_especiais(territorio)
        
        # Adicionar à lista de territórios
        self.territorios[territorio.id] = territorio
        
        return territorio
    
    def _atualizar_disputas_territoriais(self, senciantes):
        """
        Atualiza disputas territoriais entre grupos de Senciantes.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Identificar grupos de Senciantes em cada território
        grupos_por_territorio = {}
        
        for territorio_id, territorio in self.territorios.items():
            grupos_por_territorio[territorio_id] = {}
            
            for senciante_id, senciante in senciantes.items():
                # Verificar se o Senciante está no território
                distancia = calcular_distancia(senciante.posicao, territorio.posicao)
                
                if distancia <= territorio.tamanho:
                    # Identificar grupo do Senciante (simplificado)
                    grupo_id = senciante.grupo_id if hasattr(senciante, "grupo_id") else senciante_id
                    
                    if grupo_id not in grupos_por_territorio[territorio_id]:
                        grupos_por_territorio[territorio_id][grupo_id] = []
                    
                    grupos_por_territorio[territorio_id][grupo_id].append(senciante_id)
        
        # Verificar disputas
        for territorio_id, grupos in grupos_por_territorio.items():
            # Se há mais de um grupo no território
            if len(grupos) > 1:
                # Verificar se há disputa
                self._verificar_disputa_territorial(territorio_id, grupos, senciantes)
    
    def _verificar_disputa_territorial(self, territorio_id, grupos, senciantes):
        """
        Verifica se há disputa territorial entre grupos.
        
        Args:
            territorio_id (str): ID do território em disputa.
            grupos (dict): Dicionário de grupos no território.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        territorio = self.territorios[territorio_id]
        
        # Verificar se já há uma disputa ativa
        if territorio.em_disputa:
            return
        
        # Calcular força de cada grupo
        forcas_grupos = {}
        
        for grupo_id, membros in grupos.items():
            forca_total = 0.0
            
            for senciante_id in membros:
                if senciante_id in senciantes:
                    senciante = senciantes[senciante_id]
                    
                    # Calcular força individual
                    forca_individual = 1.0
                    
                    if hasattr(senciante, "habilidades"):
                        forca_individual += senciante.habilidades.get("combate", 0.0) * 2.0
                    
                    forca_total += forca_individual
            
            forcas_grupos[grupo_id] = forca_total
        
        # Verificar se há um grupo dominante
        grupo_dominante = None
        forca_dominante = 0.0
        
        for grupo_id, forca in forcas_grupos.items():
            if forca > forca_dominante:
                grupo_dominante = grupo_id
                forca_dominante = forca
        
        # Verificar se há disputa (forças próximas)
        for grupo_id, forca in forcas_grupos.items():
            if grupo_id != grupo_dominante and forca >= forca_dominante * 0.7:
                # Iniciar disputa
                territorio.em_disputa = True
                territorio.grupos_em_disputa = list(forcas_grupos.keys())
                
                # Registrar no histórico do mundo
                self.mundo.historico.registrar_evento(
                    "disputa_territorial",
                    f"Disputa territorial iniciada por território: {territorio.tipo} com recursos: {', '.join(territorio.recursos_especiais)}",
                    0,  # Tempo atual (será preenchido pelo motor de simulação)
                    [s for grupo in grupos.values() for s in grupo]
                )
                
                break
    
    def compartilhar_mapa(self, mapa_id, senciante_origem_id, senciante_destino_id, senciantes):
        """
        Compartilha um mapa entre Senciantes.
        
        Args:
            mapa_id (str): ID do mapa a ser compartilhado.
            senciante_origem_id (str): ID do Senciante que está compartilhando.
            senciante_destino_id (str): ID do Senciante que está recebendo.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            bool: True se o mapa foi compartilhado com sucesso.
        """
        # Verificar se o mapa existe
        if mapa_id not in self.mapas:
            return False
        
        # Verificar se os Senciantes existem
        if (senciante_origem_id not in senciantes or
            senciante_destino_id not in senciantes):
            return False
        
        # Verificar se o Senciante de origem é o criador ou possui o mapa
        mapa = self.mapas[mapa_id]
        if mapa["criador_id"] != senciante_origem_id and mapa_id not in senciantes[senciante_origem_id].mapas:
            return False
        
        # Adicionar mapa ao Senciante de destino
        if not hasattr(senciantes[senciante_destino_id], "mapas"):
            senciantes[senciante_destino_id].mapas = []
        
        if mapa_id not in senciantes[senciante_destino_id].mapas:
            senciantes[senciante_destino_id].mapas.append(mapa_id)
        
        # Adicionar territórios conhecidos
        for territorio in mapa["territorios"]:
            if territorio["id"] not in senciantes[senciante_destino_id].territorios_conhecidos:
                senciantes[senciante_destino_id].territorios_conhecidos.append(territorio["id"])
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "mapa_compartilhado",
            f"Senciante compartilhou mapa com outro Senciante",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [senciante_origem_id, senciante_destino_id]
        )
        
        return True
    
    def obter_nivel_exploracao(self, posicao):
        """
        Obtém o nível de exploração em uma posição.
        
        Args:
            posicao (list): Posição [x, y] no mundo.
            
        Returns:
            float: Nível de exploração (0.0 a 1.0).
        """
        # Converter para índices na matriz de exploração
        idx_x = int(posicao[0] / 5)
        idx_y = int(posicao[1] / 5)
        
        # Verificar limites
        if (0 <= idx_x < self.matriz_exploracao.shape[0] and
            0 <= idx_y < self.matriz_exploracao.shape[1]):
            return self.matriz_exploracao[idx_x, idx_y]
        else:
            return 0.0
    
    def obter_territorios_proximos(self, posicao, raio=50.0):
        """
        Obtém territórios próximos a uma posição.
        
        Args:
            posicao (list): Posição [x, y] no mundo.
            raio (float, optional): Raio de busca. Defaults to 50.0.
            
        Returns:
            list: Lista de territórios próximos.
        """
        territorios_proximos = []
        
        for territorio_id, territorio in self.territorios.items():
            distancia = calcular_distancia(posicao, territorio.posicao)
            
            if distancia <= raio:
                territorios_proximos.append(territorio)
        
        return territorios_proximos
    
    def obter_mapa_regiao(self, regiao_central, tamanho=50.0):
        """
        Obtém um mapa de uma região específica.
        
        Args:
            regiao_central (list): Posição central [x, y] da região.
            tamanho (float, optional): Tamanho da região. Defaults to 50.0.
            
        Returns:
            dict: Mapa da região.
        """
        # Coletar territórios na região
        territorios_regiao = []
        
        for territorio_id, territorio in self.territorios.items():
            distancia = calcular_distancia(regiao_central, territorio.posicao)
            
            if distancia <= tamanho:
                territorios_regiao.append({
                    "id": territorio_id,
                    "tipo": territorio.tipo,
                    "posicao": territorio.posicao,
                    "tamanho": territorio.tamanho,
                    "recursos": territorio.recursos_especiais,
                    "em_disputa": territorio.em_disputa
                })
        
        # Coletar regiões nomeadas na área
        regioes_nomeadas_area = []
        
        for regiao_id, info in self.regioes_nomeadas.items():
            idx_x, idx_y = map(int, regiao_id.split("_"))
            posicao = [idx_x * 5 + 2.5, idx_y * 5 + 2.5]  # Centro da célula
            
            distancia = calcular_distancia(regiao_central, posicao)
            
            if distancia <= tamanho:
                regioes_nomeadas_area.append({
                    "id": regiao_id,
                    "nome": info["nome"],
                    "posicao": posicao
                })
        
        # Extrair matriz de exploração da região
        x_min = max(0, int((regiao_central[0] - tamanho) / 5))
        x_max = min(self.matriz_exploracao.shape[0], int((regiao_central[0] + tamanho) / 5) + 1)
        y_min = max(0, int((regiao_central[1] - tamanho) / 5))
        y_max = min(self.matriz_exploracao.shape[1], int((regiao_central[1] + tamanho) / 5) + 1)
        
        matriz_exploracao_regiao = self.matriz_exploracao[x_min:x_max, y_min:y_max].tolist()
        
        return {
            "centro": regiao_central,
            "tamanho": tamanho,
            "territorios": territorios_regiao,
            "regioes_nomeadas": regioes_nomeadas_area,
            "matriz_exploracao": matriz_exploracao_regiao,
            "limites_matriz": [x_min, x_max, y_min, y_max]
        }

