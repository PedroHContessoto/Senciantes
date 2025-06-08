"""
Implementação das mecânicas de ecossistema simbiótico e predadores para o jogo "O Mundo dos Senciantes".
"""

import random
import numpy as np
from modelos.fauna import Fauna
from modelos.flora import Flora
from utils.helpers import chance, calcular_distancia

class MecanicaEcossistema:
    """
    Classe que implementa as mecânicas de ecossistema simbiótico e predadores.
    """
    
    def __init__(self, mundo):
        """
        Inicializa a mecânica de ecossistema.
        
        Args:
            mundo (Mundo): Objeto mundo para referência.
        """
        self.mundo = mundo
        self.fauna = {}  # Dicionário de id_fauna: fauna
        self.flora = {}  # Dicionário de id_flora: flora
        self.relacoes_simbioticas = {}  # Dicionário de id_relacao: relacao
        self.animais_domesticados = {}  # Dicionário de id_animal: {dono_id, nivel_domesticacao}
        self.plantas_cultivadas = {}  # Dicionário de id_planta: {cultivador_id, nivel_cultivo}
        
        # Tipos de fauna
        self.tipos_fauna = [
            "herbivoro_pequeno", "herbivoro_medio", "herbivoro_grande",
            "carnivoro_pequeno", "carnivoro_medio", "carnivoro_grande",
            "onivoro_pequeno", "onivoro_medio", "ave_pequena", "ave_media",
            "peixe_pequeno", "peixe_medio", "inseto", "reptil"
        ]
        
        # Tipos de flora
        self.tipos_flora = [
            "arvore_frutifera", "arvore_comum", "arbusto_frutas", "arbusto_comum",
            "grama", "flor", "fungo", "planta_aquatica", "cacto", "trepadeira",
            "planta_medicinal", "planta_venenosa"
        ]
        
        # Inicializar ecossistema
        self._inicializar_ecossistema()
    
    def _inicializar_ecossistema(self):
        """
        Inicializa o ecossistema com fauna e flora.
        """
        # Criar fauna inicial
        self._criar_fauna_inicial()
        
        # Criar flora inicial
        self._criar_flora_inicial()
        
        # Estabelecer relações simbióticas iniciais
        self._estabelecer_relacoes_simbioticas_iniciais()
    
    def _criar_fauna_inicial(self):
        """
        Cria a fauna inicial do mundo.
        """
        # Número de espécies de fauna
        num_especies = random.randint(10, 20)
        
        for _ in range(num_especies):
            # Escolher tipo de fauna
            tipo_fauna = random.choice(self.tipos_fauna)
            
            # Determinar biomas adequados
            biomas_adequados = self._determinar_biomas_adequados_fauna(tipo_fauna)
            
            # Determinar características
            if "herbivoro" in tipo_fauna or "onivoro" in tipo_fauna:
                dieta = "herbivoro" if "herbivoro" in tipo_fauna else "onivoro"
                predador = False
            else:
                dieta = "carnivoro"
                predador = True
            
            # Determinar tamanho
            if "pequeno" in tipo_fauna:
                tamanho = "pequeno"
                forca = random.uniform(0.1, 0.3)
            elif "medio" in tipo_fauna:
                tamanho = "medio"
                forca = random.uniform(0.3, 0.6)
            elif "grande" in tipo_fauna:
                tamanho = "grande"
                forca = random.uniform(0.6, 0.9)
            else:
                tamanho = "pequeno"
                forca = random.uniform(0.1, 0.3)
            
            # Determinar domesticabilidade
            if tipo_fauna in ["herbivoro_pequeno", "herbivoro_medio", "onivoro_pequeno", "ave_pequena"]:
                domesticabilidade = random.uniform(0.5, 0.9)
            elif tipo_fauna in ["herbivoro_grande", "onivoro_medio", "ave_media"]:
                domesticabilidade = random.uniform(0.3, 0.7)
            else:
                domesticabilidade = random.uniform(0.1, 0.4)
            
            # Criar espécie
            especie_id = f"fauna_{len(self.fauna) + 1}"
            
            # Gerar nome para a espécie
            nome = self._gerar_nome_especie(tipo_fauna)
            
            # Criar objeto Fauna
            fauna = Fauna(
                id=especie_id,
                nome=nome,
                tipo=tipo_fauna,
                biomas_adequados=biomas_adequados,
                dieta=dieta,
                predador=predador,
                tamanho=tamanho,
                forca=forca,
                velocidade=random.uniform(0.2, 0.8),
                agressividade=random.uniform(0.1, 0.9),
                domesticabilidade=domesticabilidade,
                valor_nutricional=random.uniform(0.2, 0.8),
                populacao=random.randint(50, 200)
            )
            
            # Adicionar ao dicionário de fauna
            self.fauna[especie_id] = fauna
            
            # Distribuir indivíduos pelo mundo
            self._distribuir_fauna(fauna)
    
    def _gerar_nome_especie(self, tipo):
        """
        Gera um nome para uma espécie.
        
        Args:
            tipo (str): Tipo da espécie.
            
        Returns:
            str: Nome gerado.
        """
        # Prefixos baseados no tipo
        prefixos = {
            "herbivoro_pequeno": ["Rato", "Coelho", "Esquilo", "Hamster", "Porquinho"],
            "herbivoro_medio": ["Cabra", "Ovelha", "Cervo", "Antílope", "Gazela"],
            "herbivoro_grande": ["Boi", "Búfalo", "Alce", "Girafa", "Elefante"],
            "carnivoro_pequeno": ["Raposa", "Gato", "Doninha", "Furão", "Texugo"],
            "carnivoro_medio": ["Lobo", "Hiena", "Chacal", "Lince", "Leopardo"],
            "carnivoro_grande": ["Leão", "Tigre", "Urso", "Puma", "Jaguar"],
            "onivoro_pequeno": ["Guaxinim", "Gambá", "Ouriço", "Tatu", "Porco"],
            "onivoro_medio": ["Javali", "Macaco", "Babuíno", "Chimpanzé", "Gorila"],
            "ave_pequena": ["Pardal", "Canário", "Beija-flor", "Pintassilgo", "Andorinha"],
            "ave_media": ["Corvo", "Falcão", "Águia", "Gavião", "Coruja"],
            "peixe_pequeno": ["Sardinha", "Lambari", "Tetra", "Guppy", "Neon"],
            "peixe_medio": ["Truta", "Tilápia", "Carpa", "Bagre", "Perca"],
            "inseto": ["Besouro", "Formiga", "Abelha", "Vespa", "Borboleta"],
            "reptil": ["Lagarto", "Cobra", "Tartaruga", "Iguana", "Camaleão"]
        }
        
        # Sufixos genéricos
        sufixos = [
            "Comum", "Selvagem", "Montês", "Dourado", "Prateado",
            "Manchado", "Listrado", "Gigante", "Anão", "Real",
            "do Norte", "do Sul", "do Leste", "do Oeste", "das Montanhas",
            "da Floresta", "do Deserto", "do Pântano", "da Planície", "da Costa"
        ]
        
        # Escolher prefixo e sufixo
        prefixo = random.choice(prefixos.get(tipo, ["Animal"]))
        sufixo = random.choice(sufixos)
        
        # Gerar nome
        nome = f"{prefixo} {sufixo}"
        
        return nome
    
    def _determinar_biomas_adequados_fauna(self, tipo_fauna):
        """
        Determina os biomas adequados para um tipo de fauna.
        
        Args:
            tipo_fauna (str): Tipo de fauna.
            
        Returns:
            list: Lista de biomas adequados.
        """
        biomas = ["floresta", "montanha", "planicie", "deserto", "pantano", "costa", "agua"]
        
        if "peixe" in tipo_fauna:
            return ["agua", "costa"]
        
        if "ave" in tipo_fauna:
            return ["floresta", "montanha", "planicie", "costa"]
        
        if "inseto" in tipo_fauna:
            return ["floresta", "planicie", "pantano"]
        
        if "reptil" in tipo_fauna:
            return ["floresta", "deserto", "pantano"]
        
        if "herbivoro" in tipo_fauna:
            if "pequeno" in tipo_fauna:
                return ["floresta", "planicie", "montanha"]
            elif "medio" in tipo_fauna:
                return ["planicie", "montanha", "floresta"]
            else:  # grande
                return ["planicie", "floresta"]
        
        if "carnivoro" in tipo_fauna:
            if "pequeno" in tipo_fauna:
                return ["floresta", "planicie", "montanha"]
            elif "medio" in tipo_fauna:
                return ["floresta", "planicie", "montanha"]
            else:  # grande
                return ["planicie", "floresta"]
        
        if "onivoro" in tipo_fauna:
            if "pequeno" in tipo_fauna:
                return ["floresta", "planicie", "pantano"]
            else:  # medio
                return ["floresta", "planicie"]
        
        # Caso padrão
        return random.sample(biomas, random.randint(1, 3))
    
    def _distribuir_fauna(self, fauna):
        """
        Distribui indivíduos de uma espécie de fauna pelo mundo.
        
        Args:
            fauna (Fauna): Espécie de fauna.
        """
        # Número de grupos
        num_grupos = random.randint(3, 10)
        
        # Tamanho médio de cada grupo
        tamanho_grupo = fauna.populacao // num_grupos
        
        # Distribuir grupos
        for _ in range(num_grupos):
            # Escolher bioma adequado
            bioma = random.choice(fauna.biomas_adequados)
            
            # Encontrar posição adequada
            posicao = self._encontrar_posicao_adequada(bioma)
            
            # Adicionar grupo
            grupo = {
                "especie_id": fauna.id,
                "posicao": posicao,
                "tamanho": max(1, int(tamanho_grupo * random.uniform(0.7, 1.3))),
                "bioma": bioma
            }
            
            # Adicionar à lista de grupos da fauna
            if not hasattr(fauna, "grupos"):
                fauna.grupos = []
            
            fauna.grupos.append(grupo)
    
    def _encontrar_posicao_adequada(self, bioma):
        """
        Encontra uma posição adequada para um bioma específico.
        
        Args:
            bioma (str): Tipo de bioma.
            
        Returns:
            list: Posição [x, y] no mundo.
        """
        # Tamanho do mundo
        tamanho_x, tamanho_y = self.mundo.tamanho
        
        # Tentar encontrar posição adequada
        for _ in range(10):
            # Posição aleatória
            pos_x = random.uniform(0, tamanho_x)
            pos_y = random.uniform(0, tamanho_y)
            
            # Verificar bioma
            bioma_local = self.mundo.obter_bioma([pos_x, pos_y])
            
            if bioma_local == bioma:
                return [pos_x, pos_y]
        
        # Se não encontrar, retornar posição aleatória
        return [random.uniform(0, tamanho_x), random.uniform(0, tamanho_y)]
    
    def _criar_flora_inicial(self):
        """
        Cria a flora inicial do mundo.
        """
        # Número de espécies de flora
        num_especies = random.randint(15, 25)
        
        for _ in range(num_especies):
            # Escolher tipo de flora
            tipo_flora = random.choice(self.tipos_flora)
            
            # Determinar biomas adequados
            biomas_adequados = self._determinar_biomas_adequados_flora(tipo_flora)
            
            # Determinar características
            if "frutifera" in tipo_flora or "frutas" in tipo_flora:
                comestivel = True
                valor_nutricional = random.uniform(0.5, 0.9)
            elif tipo_flora == "planta_medicinal":
                comestivel = True
                valor_nutricional = random.uniform(0.3, 0.6)
            elif tipo_flora == "planta_venenosa":
                comestivel = False
                valor_nutricional = 0.0
            else:
                comestivel = random.choice([True, False])
                valor_nutricional = random.uniform(0.1, 0.5) if comestivel else 0.0
            
            # Determinar cultivabilidade
            if tipo_flora in ["arvore_frutifera", "arbusto_frutas", "planta_medicinal"]:
                cultivabilidade = random.uniform(0.5, 0.9)
            elif tipo_flora in ["arvore_comum", "arbusto_comum", "flor"]:
                cultivabilidade = random.uniform(0.3, 0.7)
            else:
                cultivabilidade = random.uniform(0.1, 0.4)
            
            # Criar espécie
            especie_id = f"flora_{len(self.flora) + 1}"
            
            # Gerar nome para a espécie
            nome = self._gerar_nome_especie_flora(tipo_flora)
            
            # Criar objeto Flora
            flora = Flora(
                id=especie_id,
                nome=nome,
                tipo=tipo_flora,
                biomas_adequados=biomas_adequados,
                comestivel=comestivel,
                valor_nutricional=valor_nutricional,
                medicinal=(tipo_flora == "planta_medicinal"),
                venenosa=(tipo_flora == "planta_venenosa"),
                cultivabilidade=cultivabilidade,
                tempo_crescimento=random.uniform(24.0, 168.0),  # 1-7 dias
                populacao=random.randint(100, 500)
            )
            
            # Adicionar ao dicionário de flora
            self.flora[especie_id] = flora
            
            # Distribuir indivíduos pelo mundo
            self._distribuir_flora(flora)
    
    def _gerar_nome_especie_flora(self, tipo):
        """
        Gera um nome para uma espécie de flora.
        
        Args:
            tipo (str): Tipo da espécie.
            
        Returns:
            str: Nome gerado.
        """
        # Prefixos baseados no tipo
        prefixos = {
            "arvore_frutifera": ["Macieira", "Pereira", "Laranjeira", "Mangueira", "Abacateiro"],
            "arvore_comum": ["Carvalho", "Pinheiro", "Cedro", "Eucalipto", "Salgueiro"],
            "arbusto_frutas": ["Framboeseira", "Amoreira", "Mirtilo", "Groselha", "Morangueiro"],
            "arbusto_comum": ["Azaleia", "Hortênsia", "Buxo", "Lavanda", "Alecrim"],
            "grama": ["Grama", "Capim", "Relva", "Feno", "Erva"],
            "flor": ["Rosa", "Tulipa", "Margarida", "Lírio", "Orquídea"],
            "fungo": ["Cogumelo", "Fungo", "Mofo", "Levedura", "Micélio"],
            "planta_aquatica": ["Nenúfar", "Alga", "Junco", "Lótus", "Vitória-régia"],
            "cacto": ["Cacto", "Suculenta", "Agave", "Aloé", "Espinheiro"],
            "trepadeira": ["Hera", "Vinha", "Jasmim", "Glicínia", "Madressilva"],
            "planta_medicinal": ["Camomila", "Hortelã", "Alecrim", "Sálvia", "Erva-cidreira"],
            "planta_venenosa": ["Cicuta", "Beladona", "Acônito", "Dedaleira", "Hera-venenosa"]
        }
        
        # Sufixos genéricos
        sufixos = [
            "Comum", "Selvagem", "Dourada", "Prateada", "Gigante",
            "Anã", "Real", "do Norte", "do Sul", "do Leste",
            "do Oeste", "das Montanhas", "da Floresta", "do Deserto",
            "do Pântano", "da Planície", "da Costa", "Aromática",
            "Perfumada", "Espinhosa"
        ]
        
        # Escolher prefixo e sufixo
        prefixo = random.choice(prefixos.get(tipo, ["Planta"]))
        sufixo = random.choice(sufixos)
        
        # Gerar nome
        nome = f"{prefixo} {sufixo}"
        
        return nome
    
    def _determinar_biomas_adequados_flora(self, tipo_flora):
        """
        Determina os biomas adequados para um tipo de flora.
        
        Args:
            tipo_flora (str): Tipo de flora.
            
        Returns:
            list: Lista de biomas adequados.
        """
        biomas = ["floresta", "montanha", "planicie", "deserto", "pantano", "costa", "agua"]
        
        if "aquatica" in tipo_flora:
            return ["agua", "pantano", "costa"]
        
        if "arvore" in tipo_flora:
            if "frutifera" in tipo_flora:
                return ["floresta", "planicie"]
            else:
                return ["floresta", "montanha", "planicie"]
        
        if "arbusto" in tipo_flora:
            if "frutas" in tipo_flora:
                return ["floresta", "planicie"]
            else:
                return ["floresta", "montanha", "planicie", "pantano"]
        
        if tipo_flora == "grama":
            return ["planicie", "floresta", "montanha"]
        
        if tipo_flora == "flor":
            return ["floresta", "planicie", "montanha"]
        
        if tipo_flora == "fungo":
            return ["floresta", "pantano"]
        
        if tipo_flora == "cacto":
            return ["deserto"]
        
        if tipo_flora == "trepadeira":
            return ["floresta", "pantano"]
        
        if tipo_flora == "planta_medicinal":
            return ["floresta", "planicie", "montanha"]
        
        if tipo_flora == "planta_venenosa":
            return ["floresta", "pantano"]
        
        # Caso padrão
        return random.sample(biomas, random.randint(1, 3))
    
    def _distribuir_flora(self, flora):
        """
        Distribui indivíduos de uma espécie de flora pelo mundo.
        
        Args:
            flora (Flora): Espécie de flora.
        """
        # Número de grupos
        num_grupos = random.randint(5, 15)
        
        # Tamanho médio de cada grupo
        tamanho_grupo = flora.populacao // num_grupos
        
        # Distribuir grupos
        for _ in range(num_grupos):
            # Escolher bioma adequado
            bioma = random.choice(flora.biomas_adequados)
            
            # Encontrar posição adequada
            posicao = self._encontrar_posicao_adequada(bioma)
            
            # Adicionar grupo
            grupo = {
                "especie_id": flora.id,
                "posicao": posicao,
                "tamanho": max(1, int(tamanho_grupo * random.uniform(0.7, 1.3))),
                "bioma": bioma,
                "maturidade": random.uniform(0.5, 1.0)  # 0.0 = semente, 1.0 = madura
            }
            
            # Adicionar à lista de grupos da flora
            if not hasattr(flora, "grupos"):
                flora.grupos = []
            
            flora.grupos.append(grupo)
    
    def _estabelecer_relacoes_simbioticas_iniciais(self):
        """
        Estabelece relações simbióticas iniciais entre espécies.
        """
        # Número de relações simbióticas
        num_relacoes = random.randint(5, 10)
        
        for _ in range(num_relacoes):
            # Escolher tipo de relação
            tipo_relacao = random.choice(["mutualismo", "comensalismo", "parasitismo"])
            
            # Escolher espécies
            if tipo_relacao == "mutualismo":
                # Mutualismo: ambos se beneficiam
                # Exemplos: abelhas e flores, bactérias intestinais e animais
                especie1_id = random.choice(list(self.fauna.keys()) + list(self.flora.keys()))
                especie2_id = random.choice(list(self.fauna.keys()) + list(self.flora.keys()))
                
                beneficio1 = random.uniform(0.1, 0.3)
                beneficio2 = random.uniform(0.1, 0.3)
                
            elif tipo_relacao == "comensalismo":
                # Comensalismo: um se beneficia, outro não é afetado
                # Exemplos: pássaros que fazem ninhos em árvores
                especie1_id = random.choice(list(self.fauna.keys()))
                especie2_id = random.choice(list(self.flora.keys()))
                
                beneficio1 = random.uniform(0.1, 0.3)
                beneficio2 = 0.0
                
            else:  # parasitismo
                # Parasitismo: um se beneficia, outro é prejudicado
                # Exemplos: carrapatos, vermes parasitas
                especie1_id = random.choice(list(self.fauna.keys()))
                especie2_id = random.choice(list(self.fauna.keys()))
                
                beneficio1 = random.uniform(0.1, 0.3)
                beneficio2 = -random.uniform(0.1, 0.3)
            
            # Criar relação simbiótica
            relacao_id = f"relacao_{len(self.relacoes_simbioticas) + 1}"
            
            relacao = {
                "id": relacao_id,
                "tipo": tipo_relacao,
                "especie1_id": especie1_id,
                "especie2_id": especie2_id,
                "beneficio1": beneficio1,
                "beneficio2": beneficio2,
                "descricao": self._gerar_descricao_relacao(tipo_relacao, especie1_id, especie2_id)
            }
            
            # Adicionar ao dicionário de relações simbióticas
            self.relacoes_simbioticas[relacao_id] = relacao
    
    def _gerar_descricao_relacao(self, tipo_relacao, especie1_id, especie2_id):
        """
        Gera uma descrição para uma relação simbiótica.
        
        Args:
            tipo_relacao (str): Tipo de relação.
            especie1_id (str): ID da primeira espécie.
            especie2_id (str): ID da segunda espécie.
            
        Returns:
            str: Descrição da relação.
        """
        # Obter nomes das espécies
        nome1 = self._obter_nome_especie(especie1_id)
        nome2 = self._obter_nome_especie(especie2_id)
        
        if tipo_relacao == "mutualismo":
            descricoes = [
                f"{nome1} e {nome2} beneficiam-se mutuamente",
                f"{nome1} fornece proteção para {nome2} em troca de nutrientes",
                f"{nome1} e {nome2} cooperam para sobreviver",
                f"{nome1} poliniza {nome2} enquanto coleta néctar",
                f"{nome1} limpa parasitas de {nome2} e obtém alimento"
            ]
        elif tipo_relacao == "comensalismo":
            descricoes = [
                f"{nome1} utiliza {nome2} como abrigo sem prejudicá-lo",
                f"{nome1} se alimenta de restos deixados por {nome2}",
                f"{nome1} usa {nome2} como transporte",
                f"{nome1} vive sobre {nome2} sem causar danos",
                f"{nome1} se beneficia da presença de {nome2} sem afetá-lo"
            ]
        else:  # parasitismo
            descricoes = [
                f"{nome1} parasita {nome2}, extraindo nutrientes",
                f"{nome1} usa {nome2} como hospedeiro",
                f"{nome1} infecta {nome2}, causando danos",
                f"{nome1} se alimenta dos tecidos de {nome2}",
                f"{nome1} manipula o comportamento de {nome2} para seu benefício"
            ]
        
        return random.choice(descricoes)
    
    def _obter_nome_especie(self, especie_id):
        """
        Obtém o nome de uma espécie.
        
        Args:
            especie_id (str): ID da espécie.
            
        Returns:
            str: Nome da espécie.
        """
        if especie_id.startswith("fauna_") and especie_id in self.fauna:
            return self.fauna[especie_id].nome
        elif especie_id.startswith("flora_") and especie_id in self.flora:
            return self.flora[especie_id].nome
        else:
            return "Espécie Desconhecida"
    
    def atualizar(self, delta_tempo, senciantes):
        """
        Atualiza o estado do ecossistema no mundo.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Atualizar fauna
        self._atualizar_fauna(delta_tempo, senciantes)
        
        # Atualizar flora
        self._atualizar_flora(delta_tempo, senciantes)
        
        # Atualizar relações simbióticas
        self._atualizar_relacoes_simbioticas(delta_tempo)
        
        # Atualizar animais domesticados
        self._atualizar_animais_domesticados(delta_tempo, senciantes)
        
        # Atualizar plantas cultivadas
        self._atualizar_plantas_cultivadas(delta_tempo, senciantes)
        
        # Verificar interações entre Senciantes e fauna
        self._verificar_interacoes_senciantes_fauna(delta_tempo, senciantes)
        
        # Verificar interações entre Senciantes e flora
        self._verificar_interacoes_senciantes_flora(delta_tempo, senciantes)
    
    def _atualizar_fauna(self, delta_tempo, senciantes):
        """
        Atualiza o estado da fauna no mundo.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for fauna_id, fauna in self.fauna.items():
            # Atualizar grupos
            if hasattr(fauna, "grupos"):
                for grupo in fauna.grupos:
                    # Movimentação
                    self._movimentar_grupo_fauna(grupo, delta_tempo)
                    
                    # Alimentação
                    self._alimentar_grupo_fauna(grupo, delta_tempo)
                    
                    # Reprodução
                    self._reproduzir_grupo_fauna(grupo, delta_tempo)
                    
                    # Morte natural
                    self._morte_natural_grupo_fauna(grupo, delta_tempo)
            
            # Atualizar população total
            if hasattr(fauna, "grupos"):
                fauna.populacao = sum(grupo["tamanho"] for grupo in fauna.grupos)
            
            # Verificar extinção
            if fauna.populacao <= 0:
                # Registrar extinção
                self.mundo.historico.registrar_evento(
                    "extincao_fauna",
                    f"Espécie de fauna extinta: {fauna.nome}",
                    0,  # Tempo atual (será preenchido pelo motor de simulação)
                    []
                )
    
    def _movimentar_grupo_fauna(self, grupo, delta_tempo):
        """
        Movimenta um grupo de fauna.
        
        Args:
            grupo (dict): Grupo de fauna.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Obter espécie
        especie_id = grupo["especie_id"]
        
        if especie_id not in self.fauna:
            return
        
        fauna = self.fauna[especie_id]
        
        # Chance de movimento baseada na velocidade
        chance_movimento = fauna.velocidade * delta_tempo
        
        if chance(chance_movimento):
            # Determinar direção aleatória
            angulo = random.uniform(0, 2 * 3.14159)
            
            # Determinar distância baseada na velocidade
            distancia = fauna.velocidade * 10.0 * delta_tempo
            
            # Calcular nova posição
            nova_pos_x = grupo["posicao"][0] + distancia * np.cos(angulo)
            nova_pos_y = grupo["posicao"][1] + distancia * np.sin(angulo)
            
            # Verificar limites do mundo
            nova_pos_x = max(0, min(self.mundo.tamanho[0], nova_pos_x))
            nova_pos_y = max(0, min(self.mundo.tamanho[1], nova_pos_y))
            
            # Verificar bioma
            novo_bioma = self.mundo.obter_bioma([nova_pos_x, nova_pos_y])
            
            # Se o bioma for adequado, mover
            if novo_bioma in fauna.biomas_adequados:
                grupo["posicao"] = [nova_pos_x, nova_pos_y]
                grupo["bioma"] = novo_bioma
    
    def _alimentar_grupo_fauna(self, grupo, delta_tempo):
        """
        Alimenta um grupo de fauna.
        
        Args:
            grupo (dict): Grupo de fauna.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Obter espécie
        especie_id = grupo["especie_id"]
        
        if especie_id not in self.fauna:
            return
        
        fauna = self.fauna[especie_id]
        
        # Chance de alimentação baseada no tempo
        chance_alimentacao = 0.1 * delta_tempo
        
        if chance(chance_alimentacao):
            # Determinar tipo de alimentação
            if fauna.dieta == "herbivoro":
                # Procurar flora próxima
                self._alimentar_herbivoro(grupo, fauna)
            elif fauna.dieta == "carnivoro":
                # Procurar fauna próxima
                self._alimentar_carnivoro(grupo, fauna)
            else:  # onívoro
                # Procurar flora ou fauna próxima
                if chance(0.5):
                    self._alimentar_herbivoro(grupo, fauna)
                else:
                    self._alimentar_carnivoro(grupo, fauna)
    
    def _alimentar_herbivoro(self, grupo, fauna):
        """
        Alimenta um grupo de herbívoros.
        
        Args:
            grupo (dict): Grupo de fauna.
            fauna (Fauna): Espécie de fauna.
            
        Returns:
            bool: True se o grupo conseguiu se alimentar.
        """
        # Procurar grupos de flora próximos
        grupos_flora_proximos = []
        
        for flora_id, flora in self.flora.items():
            if hasattr(flora, "grupos"):
                for grupo_flora in flora.grupos:
                    # Calcular distância
                    distancia = calcular_distancia(grupo["posicao"], grupo_flora["posicao"])
                    
                    # Se estiver próximo e for comestível
                    if distancia <= 20.0 and flora.comestivel:
                        grupos_flora_proximos.append((grupo_flora, flora, distancia))
        
        # Ordenar por distância
        grupos_flora_proximos.sort(key=lambda x: x[2])
        
        # Tentar se alimentar do grupo mais próximo
        if grupos_flora_proximos:
            grupo_flora, flora, _ = grupos_flora_proximos[0]
            
            # Quantidade consumida
            quantidade_consumida = min(grupo["tamanho"] * 0.1, grupo_flora["tamanho"] * 0.2)
            
            # Reduzir tamanho do grupo de flora
            grupo_flora["tamanho"] = max(0, grupo_flora["tamanho"] - quantidade_consumida)
            
            # Chance de crescimento do grupo de fauna
            if quantidade_consumida > 0:
                crescimento = quantidade_consumida * flora.valor_nutricional * 0.1
                grupo["tamanho"] += crescimento
                
                return True
        
        return False
    
    def _alimentar_carnivoro(self, grupo, fauna):
        """
        Alimenta um grupo de carnívoros.
        
        Args:
            grupo (dict): Grupo de fauna.
            fauna (Fauna): Espécie de fauna.
            
        Returns:
            bool: True se o grupo conseguiu se alimentar.
        """
        # Procurar grupos de fauna próximos
        grupos_fauna_proximos = []
        
        for presa_id, presa in self.fauna.items():
            # Não caçar a própria espécie
            if presa_id == fauna.id:
                continue
            
            # Verificar se é uma presa adequada
            if presa.tamanho == "grande" and fauna.tamanho != "grande":
                continue  # Apenas predadores grandes podem caçar presas grandes
            
            if hasattr(presa, "grupos"):
                for grupo_presa in presa.grupos:
                    # Calcular distância
                    distancia = calcular_distancia(grupo["posicao"], grupo_presa["posicao"])
                    
                    # Se estiver próximo
                    if distancia <= 30.0:
                        grupos_fauna_proximos.append((grupo_presa, presa, distancia))
        
        # Ordenar por distância
        grupos_fauna_proximos.sort(key=lambda x: x[2])
        
        # Tentar caçar o grupo mais próximo
        if grupos_fauna_proximos:
            grupo_presa, presa, _ = grupos_fauna_proximos[0]
            
            # Chance de sucesso na caça
            chance_sucesso = fauna.forca / (fauna.forca + presa.velocidade)
            
            if chance(chance_sucesso):
                # Quantidade consumida
                quantidade_consumida = min(grupo["tamanho"] * 0.2, grupo_presa["tamanho"] * 0.5)
                
                # Reduzir tamanho do grupo de presa
                grupo_presa["tamanho"] = max(0, grupo_presa["tamanho"] - quantidade_consumida)
                
                # Crescimento do grupo de predadores
                if quantidade_consumida > 0:
                    crescimento = quantidade_consumida * presa.valor_nutricional * 0.1
                    grupo["tamanho"] += crescimento
                    
                    return True
        
        return False
    
    def _reproduzir_grupo_fauna(self, grupo, delta_tempo):
        """
        Reproduz um grupo de fauna.
        
        Args:
            grupo (dict): Grupo de fauna.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Chance de reprodução baseada no tempo
        chance_reproducao = 0.02 * delta_tempo
        
        if chance(chance_reproducao):
            # Taxa de reprodução
            taxa_reproducao = 0.1
            
            # Crescimento
            crescimento = grupo["tamanho"] * taxa_reproducao
            
            # Adicionar ao tamanho do grupo
            grupo["tamanho"] += crescimento
    
    def _morte_natural_grupo_fauna(self, grupo, delta_tempo):
        """
        Aplica morte natural a um grupo de fauna.
        
        Args:
            grupo (dict): Grupo de fauna.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Taxa de mortalidade
        taxa_mortalidade = 0.01 * delta_tempo
        
        # Redução
        reducao = grupo["tamanho"] * taxa_mortalidade
        
        # Reduzir tamanho do grupo
        grupo["tamanho"] = max(0, grupo["tamanho"] - reducao)
    
    def _atualizar_flora(self, delta_tempo, senciantes):
        """
        Atualiza o estado da flora no mundo.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for flora_id, flora in self.flora.items():
            # Atualizar grupos
            if hasattr(flora, "grupos"):
                for grupo in flora.grupos:
                    # Crescimento
                    self._crescer_grupo_flora(grupo, flora, delta_tempo)
                    
                    # Reprodução
                    self._reproduzir_grupo_flora(grupo, flora, delta_tempo)
                    
                    # Morte natural
                    self._morte_natural_grupo_flora(grupo, delta_tempo)
            
            # Atualizar população total
            if hasattr(flora, "grupos"):
                flora.populacao = sum(grupo["tamanho"] for grupo in flora.grupos)
            
            # Verificar extinção
            if flora.populacao <= 0:
                # Registrar extinção
                self.mundo.historico.registrar_evento(
                    "extincao_flora",
                    f"Espécie de flora extinta: {flora.nome}",
                    0,  # Tempo atual (será preenchido pelo motor de simulação)
                    []
                )
    
    def _crescer_grupo_flora(self, grupo, flora, delta_tempo):
        """
        Faz um grupo de flora crescer.
        
        Args:
            grupo (dict): Grupo de flora.
            flora (Flora): Espécie de flora.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Verificar se o grupo já está maduro
        if grupo["maturidade"] < 1.0:
            # Taxa de crescimento
            taxa_crescimento = delta_tempo / flora.tempo_crescimento
            
            # Aumentar maturidade
            grupo["maturidade"] = min(1.0, grupo["maturidade"] + taxa_crescimento)
    
    def _reproduzir_grupo_flora(self, grupo, flora, delta_tempo):
        """
        Reproduz um grupo de flora.
        
        Args:
            grupo (dict): Grupo de flora.
            flora (Flora): Espécie de flora.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Verificar se o grupo está maduro
        if grupo["maturidade"] >= 1.0:
            # Chance de reprodução baseada no tempo
            chance_reproducao = 0.01 * delta_tempo
            
            if chance(chance_reproducao):
                # Taxa de reprodução
                taxa_reproducao = 0.05
                
                # Crescimento
                crescimento = grupo["tamanho"] * taxa_reproducao
                
                # Adicionar ao tamanho do grupo
                grupo["tamanho"] += crescimento
                
                # Chance de criar novo grupo próximo
                if chance(0.2):
                    # Determinar posição próxima
                    angulo = random.uniform(0, 2 * 3.14159)
                    distancia = random.uniform(5.0, 15.0)
                    
                    nova_pos_x = grupo["posicao"][0] + distancia * np.cos(angulo)
                    nova_pos_y = grupo["posicao"][1] + distancia * np.sin(angulo)
                    
                    # Verificar limites do mundo
                    nova_pos_x = max(0, min(self.mundo.tamanho[0], nova_pos_x))
                    nova_pos_y = max(0, min(self.mundo.tamanho[1], nova_pos_y))
                    
                    # Verificar bioma
                    novo_bioma = self.mundo.obter_bioma([nova_pos_x, nova_pos_y])
                    
                    # Se o bioma for adequado, criar novo grupo
                    if novo_bioma in flora.biomas_adequados:
                        novo_grupo = {
                            "especie_id": flora.id,
                            "posicao": [nova_pos_x, nova_pos_y],
                            "tamanho": grupo["tamanho"] * 0.2,  # 20% do tamanho do grupo original
                            "bioma": novo_bioma,
                            "maturidade": 0.0  # Começa como semente
                        }
                        
                        # Reduzir tamanho do grupo original
                        grupo["tamanho"] *= 0.8  # 80% do tamanho original
                        
                        # Adicionar novo grupo
                        flora.grupos.append(novo_grupo)
    
    def _morte_natural_grupo_flora(self, grupo, delta_tempo):
        """
        Aplica morte natural a um grupo de flora.
        
        Args:
            grupo (dict): Grupo de flora.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Taxa de mortalidade
        taxa_mortalidade = 0.005 * delta_tempo
        
        # Redução
        reducao = grupo["tamanho"] * taxa_mortalidade
        
        # Reduzir tamanho do grupo
        grupo["tamanho"] = max(0, grupo["tamanho"] - reducao)
    
    def _atualizar_relacoes_simbioticas(self, delta_tempo):
        """
        Atualiza as relações simbióticas entre espécies.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        for relacao_id, relacao in self.relacoes_simbioticas.items():
            # Obter espécies
            especie1_id = relacao["especie1_id"]
            especie2_id = relacao["especie2_id"]
            
            # Verificar se as espécies existem
            especie1 = self._obter_especie(especie1_id)
            especie2 = self._obter_especie(especie2_id)
            
            if especie1 is None or especie2 is None:
                continue
            
            # Aplicar efeitos da relação
            self._aplicar_efeitos_relacao(relacao, especie1, especie2, delta_tempo)
    
    def _obter_especie(self, especie_id):
        """
        Obtém uma espécie pelo ID.
        
        Args:
            especie_id (str): ID da espécie.
            
        Returns:
            object: Objeto da espécie (Fauna ou Flora).
        """
        if especie_id.startswith("fauna_") and especie_id in self.fauna:
            return self.fauna[especie_id]
        elif especie_id.startswith("flora_") and especie_id in self.flora:
            return self.flora[especie_id]
        else:
            return None
    
    def _aplicar_efeitos_relacao(self, relacao, especie1, especie2, delta_tempo):
        """
        Aplica os efeitos de uma relação simbiótica.
        
        Args:
            relacao (dict): Relação simbiótica.
            especie1 (object): Primeira espécie.
            especie2 (object): Segunda espécie.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Verificar grupos próximos
        if hasattr(especie1, "grupos") and hasattr(especie2, "grupos"):
            for grupo1 in especie1.grupos:
                for grupo2 in especie2.grupos:
                    # Calcular distância
                    distancia = calcular_distancia(grupo1["posicao"], grupo2["posicao"])
                    
                    # Se estiverem próximos
                    if distancia <= 20.0:
                        # Aplicar benefícios/prejuízos
                        if relacao["beneficio1"] > 0:
                            # Benefício para espécie 1
                            grupo1["tamanho"] *= (1.0 + relacao["beneficio1"] * delta_tempo * 0.01)
                        elif relacao["beneficio1"] < 0:
                            # Prejuízo para espécie 1
                            grupo1["tamanho"] *= (1.0 + relacao["beneficio1"] * delta_tempo * 0.01)
                        
                        if relacao["beneficio2"] > 0:
                            # Benefício para espécie 2
                            grupo2["tamanho"] *= (1.0 + relacao["beneficio2"] * delta_tempo * 0.01)
                        elif relacao["beneficio2"] < 0:
                            # Prejuízo para espécie 2
                            grupo2["tamanho"] *= (1.0 + relacao["beneficio2"] * delta_tempo * 0.01)
    
    def _atualizar_animais_domesticados(self, delta_tempo, senciantes):
        """
        Atualiza os animais domesticados.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for animal_id, info in list(self.animais_domesticados.items()):
            # Verificar se o dono ainda existe
            dono_id = info["dono_id"]
            
            if dono_id not in senciantes:
                # Remover animal domesticado
                del self.animais_domesticados[animal_id]
                continue
            
            # Verificar se o animal ainda existe
            especie_id = info["especie_id"]
            
            if especie_id not in self.fauna:
                # Remover animal domesticado
                del self.animais_domesticados[animal_id]
                continue
            
            # Atualizar nível de domesticação
            info["nivel_domesticacao"] = min(1.0, info["nivel_domesticacao"] + 0.01 * delta_tempo)
            
            # Atualizar posição do animal para seguir o dono
            info["posicao"] = senciantes[dono_id].posicao.copy()
            
            # Chance de fornecer recursos
            chance_recursos = 0.05 * delta_tempo * info["nivel_domesticacao"]
            
            if chance(chance_recursos):
                # Fornecer recursos ao dono
                self._fornecer_recursos_animal_domesticado(animal_id, dono_id, senciantes)
    
    def _fornecer_recursos_animal_domesticado(self, animal_id, dono_id, senciantes):
        """
        Fornece recursos de um animal domesticado ao seu dono.
        
        Args:
            animal_id (str): ID do animal domesticado.
            dono_id (str): ID do Senciante dono.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Verificar se o animal existe
        if animal_id not in self.animais_domesticados:
            return
        
        # Verificar se o dono existe
        if dono_id not in senciantes:
            return
        
        info = self.animais_domesticados[animal_id]
        especie_id = info["especie_id"]
        
        if especie_id not in self.fauna:
            return
        
        fauna = self.fauna[especie_id]
        
        # Determinar tipo de recurso
        if "herbivoro" in fauna.tipo:
            # Herbívoros podem fornecer leite, lã, etc.
            recurso = random.choice(["leite", "la", "couro"])
        elif "ave" in fauna.tipo:
            # Aves podem fornecer ovos, penas, etc.
            recurso = random.choice(["ovo", "pena"])
        else:
            # Outros animais podem fornecer carne, couro, etc.
            recurso = random.choice(["carne", "couro", "osso"])
        
        # Quantidade de recurso
        quantidade = random.uniform(0.5, 2.0) * info["nivel_domesticacao"]
        
        # Adicionar ao inventário do dono
        if recurso not in senciantes[dono_id].inventario:
            senciantes[dono_id].inventario[recurso] = 0.0
        
        senciantes[dono_id].inventario[recurso] += quantidade
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "recurso_animal_domesticado",
            f"Animal domesticado forneceu {quantidade:.1f} unidades de {recurso} ao seu dono",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [dono_id]
        )
    
    def _atualizar_plantas_cultivadas(self, delta_tempo, senciantes):
        """
        Atualiza as plantas cultivadas.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for planta_id, info in list(self.plantas_cultivadas.items()):
            # Verificar se o cultivador ainda existe
            cultivador_id = info["cultivador_id"]
            
            if cultivador_id not in senciantes:
                # Remover planta cultivada
                del self.plantas_cultivadas[planta_id]
                continue
            
            # Verificar se a planta ainda existe
            especie_id = info["especie_id"]
            
            if especie_id not in self.flora:
                # Remover planta cultivada
                del self.plantas_cultivadas[planta_id]
                continue
            
            # Atualizar nível de cultivo
            info["nivel_cultivo"] = min(1.0, info["nivel_cultivo"] + 0.01 * delta_tempo)
            
            # Atualizar maturidade
            flora = self.flora[especie_id]
            
            # Taxa de crescimento acelerada para plantas cultivadas
            taxa_crescimento = delta_tempo / (flora.tempo_crescimento * 0.7)  # 30% mais rápido
            
            info["maturidade"] = min(1.0, info["maturidade"] + taxa_crescimento)
            
            # Se estiver madura, chance de fornecer recursos
            if info["maturidade"] >= 1.0:
                chance_recursos = 0.1 * delta_tempo * info["nivel_cultivo"]
                
                if chance(chance_recursos):
                    # Fornecer recursos ao cultivador
                    self._fornecer_recursos_planta_cultivada(planta_id, cultivador_id, senciantes)
                    
                    # Reiniciar maturidade
                    info["maturidade"] = 0.3  # Não começa do zero
    
    def _fornecer_recursos_planta_cultivada(self, planta_id, cultivador_id, senciantes):
        """
        Fornece recursos de uma planta cultivada ao seu cultivador.
        
        Args:
            planta_id (str): ID da planta cultivada.
            cultivador_id (str): ID do Senciante cultivador.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Verificar se a planta existe
        if planta_id not in self.plantas_cultivadas:
            return
        
        # Verificar se o cultivador existe
        if cultivador_id not in senciantes:
            return
        
        info = self.plantas_cultivadas[planta_id]
        especie_id = info["especie_id"]
        
        if especie_id not in self.flora:
            return
        
        flora = self.flora[especie_id]
        
        # Determinar tipo de recurso
        if "frutifera" in flora.tipo or "frutas" in flora.tipo:
            # Árvores frutíferas ou arbustos de frutas
            recurso = "fruta"
        elif flora.tipo == "planta_medicinal":
            # Plantas medicinais
            recurso = "erva_medicinal"
        elif "arvore" in flora.tipo:
            # Árvores comuns
            recurso = "madeira"
        else:
            # Outras plantas
            recurso = "planta"
        
        # Quantidade de recurso
        quantidade = random.uniform(1.0, 3.0) * info["nivel_cultivo"]
        
        # Adicionar ao inventário do cultivador
        if recurso not in senciantes[cultivador_id].inventario:
            senciantes[cultivador_id].inventario[recurso] = 0.0
        
        senciantes[cultivador_id].inventario[recurso] += quantidade
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "recurso_planta_cultivada",
            f"Planta cultivada forneceu {quantidade:.1f} unidades de {recurso} ao seu cultivador",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [cultivador_id]
        )
    
    def _verificar_interacoes_senciantes_fauna(self, delta_tempo, senciantes):
        """
        Verifica interações entre Senciantes e fauna.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for senciante_id, senciante in senciantes.items():
            # Verificar grupos de fauna próximos
            for fauna_id, fauna in self.fauna.items():
                if hasattr(fauna, "grupos"):
                    for grupo in fauna.grupos:
                        # Calcular distância
                        distancia = calcular_distancia(senciante.posicao, grupo["posicao"])
                        
                        # Se estiver próximo
                        if distancia <= 10.0:
                            # Chance de descobrir a espécie
                            chance_descoberta = 0.2 * delta_tempo
                            
                            if chance(chance_descoberta):
                                # Adicionar ao conhecimento do Senciante
                                if not hasattr(senciante, "fauna_conhecida"):
                                    senciante.fauna_conhecida = []
                                
                                if fauna_id not in senciante.fauna_conhecida:
                                    senciante.fauna_conhecida.append(fauna_id)
                                    
                                    # Registrar no histórico do mundo
                                    self.mundo.historico.registrar_evento(
                                        "fauna_descoberta",
                                        f"Senciante descobriu espécie de fauna: {fauna.nome}",
                                        0,  # Tempo atual (será preenchido pelo motor de simulação)
                                        [senciante_id]
                                    )
                            
                            # Se for predador, chance de ataque
                            if fauna.predador and fauna.agressividade > 0.5:
                                chance_ataque = fauna.agressividade * 0.1 * delta_tempo
                                
                                if chance(chance_ataque):
                                    # Atacar Senciante
                                    self._atacar_senciante(senciante, fauna, grupo)
                            
                            # Chance de tentar domesticar
                            if hasattr(senciante, "habilidades") and "domesticacao" in senciante.habilidades:
                                chance_domesticacao = senciante.habilidades["domesticacao"] * fauna.domesticabilidade * 0.05 * delta_tempo
                                
                                if chance(chance_domesticacao):
                                    # Tentar domesticar
                                    self._tentar_domesticar(senciante_id, fauna_id, grupo, senciante)
    
    def _atacar_senciante(self, senciante, fauna, grupo):
        """
        Ataca um Senciante com um grupo de fauna predadora.
        
        Args:
            senciante (Senciante): Senciante a ser atacado.
            fauna (Fauna): Espécie de fauna predadora.
            grupo (dict): Grupo de fauna.
        """
        # Calcular dano baseado na força do predador
        dano_base = fauna.forca * 0.2
        
        # Ajustar com base no tamanho do grupo
        dano = dano_base * min(1.0, grupo["tamanho"] / 10.0)
        
        # Aplicar dano
        senciante.estado["saude"] -= dano
        
        # Aumentar estresse
        senciante.estado["estresse"] = min(1.0, senciante.estado["estresse"] + 0.3)
        
        # Reduzir felicidade
        senciante.estado["felicidade"] = max(0.0, senciante.estado["felicidade"] - 0.3)
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "ataque_predador",
            f"Senciante foi atacado por {fauna.nome}, perdendo {dano:.2f} de saúde",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [senciante.id]
        )
        
        # Verificar morte
        if senciante.estado["saude"] <= 0.0:
            # Registrar morte
            self.mundo.historico.registrar_evento(
                "morte_predador",
                f"Senciante morreu devido a ataque de {fauna.nome}",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                [senciante.id]
            )
    
    def _tentar_domesticar(self, senciante_id, fauna_id, grupo, senciante):
        """
        Tenta domesticar um grupo de fauna.
        
        Args:
            senciante_id (str): ID do Senciante.
            fauna_id (str): ID da espécie de fauna.
            grupo (dict): Grupo de fauna.
            senciante (Senciante): Objeto Senciante.
            
        Returns:
            bool: True se a domesticação foi bem-sucedida.
        """
        # Verificar se a espécie existe
        if fauna_id not in self.fauna:
            return False
        
        fauna = self.fauna[fauna_id]
        
        # Verificar se o grupo é grande o suficiente
        if grupo["tamanho"] < 2.0:
            return False
        
        # Calcular chance de sucesso
        chance_sucesso = senciante.habilidades.get("domesticacao", 0.0) * fauna.domesticabilidade
        
        if chance(chance_sucesso):
            # Criar animal domesticado
            animal_id = f"animal_domesticado_{len(self.animais_domesticados) + 1}"
            
            self.animais_domesticados[animal_id] = {
                "id": animal_id,
                "especie_id": fauna_id,
                "dono_id": senciante_id,
                "nivel_domesticacao": 0.1,  # Começa baixo
                "posicao": senciante.posicao.copy(),
                "tempo_domesticacao": 0  # Será preenchido pelo motor
            }
            
            # Reduzir tamanho do grupo selvagem
            grupo["tamanho"] -= 1.0
            
            # Aumentar habilidade de domesticação
            senciante.habilidades["domesticacao"] = min(1.0, senciante.habilidades["domesticacao"] + 0.05)
            
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "animal_domesticado",
                f"Senciante domesticou um {fauna.nome}",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                [senciante_id]
            )
            
            return True
        
        return False
    
    def _verificar_interacoes_senciantes_flora(self, delta_tempo, senciantes):
        """
        Verifica interações entre Senciantes e flora.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        for senciante_id, senciante in senciantes.items():
            # Verificar grupos de flora próximos
            for flora_id, flora in self.flora.items():
                if hasattr(flora, "grupos"):
                    for grupo in flora.grupos:
                        # Calcular distância
                        distancia = calcular_distancia(senciante.posicao, grupo["posicao"])
                        
                        # Se estiver próximo
                        if distancia <= 10.0:
                            # Chance de descobrir a espécie
                            chance_descoberta = 0.2 * delta_tempo
                            
                            if chance(chance_descoberta):
                                # Adicionar ao conhecimento do Senciante
                                if not hasattr(senciante, "flora_conhecida"):
                                    senciante.flora_conhecida = []
                                
                                if flora_id not in senciante.flora_conhecida:
                                    senciante.flora_conhecida.append(flora_id)
                                    
                                    # Registrar no histórico do mundo
                                    self.mundo.historico.registrar_evento(
                                        "flora_descoberta",
                                        f"Senciante descobriu espécie de flora: {flora.nome}",
                                        0,  # Tempo atual (será preenchido pelo motor de simulação)
                                        [senciante_id]
                                    )
                            
                            # Chance de coletar recursos
                            if grupo["maturidade"] >= 0.8:  # Quase maduro ou maduro
                                chance_coleta = 0.1 * delta_tempo
                                
                                if chance(chance_coleta):
                                    # Coletar recursos
                                    self._coletar_recursos_flora(senciante, flora, grupo)
                            
                            # Chance de tentar cultivar
                            if hasattr(senciante, "habilidades") and "agricultura" in senciante.habilidades:
                                chance_cultivo = senciante.habilidades["agricultura"] * flora.cultivabilidade * 0.05 * delta_tempo
                                
                                if chance(chance_cultivo):
                                    # Tentar cultivar
                                    self._tentar_cultivar(senciante_id, flora_id, grupo, senciante)
    
    def _coletar_recursos_flora(self, senciante, flora, grupo):
        """
        Coleta recursos de um grupo de flora.
        
        Args:
            senciante (Senciante): Senciante que está coletando.
            flora (Flora): Espécie de flora.
            grupo (dict): Grupo de flora.
            
        Returns:
            bool: True se a coleta foi bem-sucedida.
        """
        # Verificar se a flora é comestível
        if not flora.comestivel and not flora.medicinal:
            return False
        
        # Determinar tipo de recurso
        if "frutifera" in flora.tipo or "frutas" in flora.tipo:
            # Árvores frutíferas ou arbustos de frutas
            recurso = "fruta"
        elif flora.tipo == "planta_medicinal":
            # Plantas medicinais
            recurso = "erva_medicinal"
        elif "arvore" in flora.tipo:
            # Árvores comuns
            recurso = "madeira"
        else:
            # Outras plantas
            recurso = "planta"
        
        # Quantidade coletada
        quantidade_coletada = min(grupo["tamanho"] * 0.2, 3.0)
        
        # Reduzir tamanho do grupo
        grupo["tamanho"] = max(0, grupo["tamanho"] - quantidade_coletada * 0.5)
        
        # Adicionar ao inventário do Senciante
        if recurso not in senciante.inventario:
            senciante.inventario[recurso] = 0.0
        
        senciante.inventario[recurso] += quantidade_coletada
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "recursos_flora_coletados",
            f"Senciante coletou {quantidade_coletada:.1f} unidades de {recurso} de {flora.nome}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [senciante.id]
        )
        
        return True
    
    def _tentar_cultivar(self, senciante_id, flora_id, grupo, senciante):
        """
        Tenta cultivar um grupo de flora.
        
        Args:
            senciante_id (str): ID do Senciante.
            flora_id (str): ID da espécie de flora.
            grupo (dict): Grupo de flora.
            senciante (Senciante): Objeto Senciante.
            
        Returns:
            bool: True se o cultivo foi bem-sucedido.
        """
        # Verificar se a espécie existe
        if flora_id not in self.flora:
            return False
        
        flora = self.flora[flora_id]
        
        # Verificar se o grupo é grande o suficiente
        if grupo["tamanho"] < 2.0:
            return False
        
        # Calcular chance de sucesso
        chance_sucesso = senciante.habilidades.get("agricultura", 0.0) * flora.cultivabilidade
        
        if chance(chance_sucesso):
            # Criar planta cultivada
            planta_id = f"planta_cultivada_{len(self.plantas_cultivadas) + 1}"
            
            self.plantas_cultivadas[planta_id] = {
                "id": planta_id,
                "especie_id": flora_id,
                "cultivador_id": senciante_id,
                "nivel_cultivo": 0.1,  # Começa baixo
                "posicao": senciante.posicao.copy(),
                "maturidade": 0.3,  # Começa parcialmente desenvolvida
                "tempo_cultivo": 0  # Será preenchido pelo motor
            }
            
            # Reduzir tamanho do grupo selvagem
            grupo["tamanho"] -= 1.0
            
            # Aumentar habilidade de agricultura
            senciante.habilidades["agricultura"] = min(1.0, senciante.habilidades["agricultura"] + 0.05)
            
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "planta_cultivada",
                f"Senciante começou a cultivar {flora.nome}",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                [senciante_id]
            )
            
            return True
        
        return False
    
    def domesticar_animal(self, senciante_id, fauna_id, senciantes):
        """
        Domestica um animal de uma espécie específica.
        
        Args:
            senciante_id (str): ID do Senciante.
            fauna_id (str): ID da espécie de fauna.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: ID do animal domesticado, ou None se falhou.
        """
        # Verificar se o Senciante existe
        if senciante_id not in senciantes:
            return None
        
        senciante = senciantes[senciante_id]
        
        # Verificar se a espécie existe
        if fauna_id not in self.fauna:
            return None
        
        fauna = self.fauna[fauna_id]
        
        # Verificar se o Senciante tem a habilidade necessária
        if not hasattr(senciante, "habilidades") or "domesticacao" not in senciante.habilidades:
            return None
        
        # Procurar grupos da espécie próximos ao Senciante
        grupos_proximos = []
        
        if hasattr(fauna, "grupos"):
            for grupo in fauna.grupos:
                # Calcular distância
                distancia = calcular_distancia(senciante.posicao, grupo["posicao"])
                
                # Se estiver próximo
                if distancia <= 20.0:
                    grupos_proximos.append((grupo, distancia))
        
        # Ordenar por distância
        grupos_proximos.sort(key=lambda x: x[1])
        
        # Tentar domesticar o grupo mais próximo
        if grupos_proximos:
            grupo, _ = grupos_proximos[0]
            
            # Tentar domesticar
            return self._tentar_domesticar(senciante_id, fauna_id, grupo, senciante)
        
        return None
    
    def cultivar_planta(self, senciante_id, flora_id, senciantes):
        """
        Cultiva uma planta de uma espécie específica.
        
        Args:
            senciante_id (str): ID do Senciante.
            flora_id (str): ID da espécie de flora.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: ID da planta cultivada, ou None se falhou.
        """
        # Verificar se o Senciante existe
        if senciante_id not in senciantes:
            return None
        
        senciante = senciantes[senciante_id]
        
        # Verificar se a espécie existe
        if flora_id not in self.flora:
            return None
        
        flora = self.flora[flora_id]
        
        # Verificar se o Senciante tem a habilidade necessária
        if not hasattr(senciante, "habilidades") or "agricultura" not in senciante.habilidades:
            return None
        
        # Procurar grupos da espécie próximos ao Senciante
        grupos_proximos = []
        
        if hasattr(flora, "grupos"):
            for grupo in flora.grupos:
                # Calcular distância
                distancia = calcular_distancia(senciante.posicao, grupo["posicao"])
                
                # Se estiver próximo
                if distancia <= 20.0:
                    grupos_proximos.append((grupo, distancia))
        
        # Ordenar por distância
        grupos_proximos.sort(key=lambda x: x[1])
        
        # Tentar cultivar o grupo mais próximo
        if grupos_proximos:
            grupo, _ = grupos_proximos[0]
            
            # Tentar cultivar
            return self._tentar_cultivar(senciante_id, flora_id, grupo, senciante)
        
        return None
    
    def obter_fauna_proxima(self, posicao, raio=30.0):
        """
        Obtém grupos de fauna próximos a uma posição.
        
        Args:
            posicao (list): Posição [x, y] no mundo.
            raio (float, optional): Raio de busca. Defaults to 30.0.
            
        Returns:
            list: Lista de grupos de fauna próximos.
        """
        grupos_proximos = []
        
        for fauna_id, fauna in self.fauna.items():
            if hasattr(fauna, "grupos"):
                for grupo in fauna.grupos:
                    # Calcular distância
                    distancia = calcular_distancia(posicao, grupo["posicao"])
                    
                    # Se estiver próximo
                    if distancia <= raio:
                        grupos_proximos.append({
                            "especie_id": fauna_id,
                            "especie_nome": fauna.nome,
                            "tipo": fauna.tipo,
                            "posicao": grupo["posicao"],
                            "tamanho": grupo["tamanho"],
                            "bioma": grupo["bioma"],
                            "distancia": distancia
                        })
        
        return grupos_proximos
    
    def obter_flora_proxima(self, posicao, raio=30.0):
        """
        Obtém grupos de flora próximos a uma posição.
        
        Args:
            posicao (list): Posição [x, y] no mundo.
            raio (float, optional): Raio de busca. Defaults to 30.0.
            
        Returns:
            list: Lista de grupos de flora próximos.
        """
        grupos_proximos = []
        
        for flora_id, flora in self.flora.items():
            if hasattr(flora, "grupos"):
                for grupo in flora.grupos:
                    # Calcular distância
                    distancia = calcular_distancia(posicao, grupo["posicao"])
                    
                    # Se estiver próximo
                    if distancia <= raio:
                        grupos_proximos.append({
                            "especie_id": flora_id,
                            "especie_nome": flora.nome,
                            "tipo": flora.tipo,
                            "posicao": grupo["posicao"],
                            "tamanho": grupo["tamanho"],
                            "bioma": grupo["bioma"],
                            "maturidade": grupo["maturidade"],
                            "distancia": distancia
                        })
        
        return grupos_proximos
    
    def obter_animais_domesticados_senciante(self, senciante_id):
        """
        Obtém os animais domesticados de um Senciante.
        
        Args:
            senciante_id (str): ID do Senciante.
            
        Returns:
            list: Lista de animais domesticados.
        """
        animais = []
        
        for animal_id, info in self.animais_domesticados.items():
            if info["dono_id"] == senciante_id:
                especie_id = info["especie_id"]
                
                if especie_id in self.fauna:
                    animais.append({
                        "id": animal_id,
                        "especie_id": especie_id,
                        "especie_nome": self.fauna[especie_id].nome,
                        "nivel_domesticacao": info["nivel_domesticacao"],
                        "tempo_domesticacao": info["tempo_domesticacao"]
                    })
        
        return animais
    
    def obter_plantas_cultivadas_senciante(self, senciante_id):
        """
        Obtém as plantas cultivadas de um Senciante.
        
        Args:
            senciante_id (str): ID do Senciante.
            
        Returns:
            list: Lista de plantas cultivadas.
        """
        plantas = []
        
        for planta_id, info in self.plantas_cultivadas.items():
            if info["cultivador_id"] == senciante_id:
                especie_id = info["especie_id"]
                
                if especie_id in self.flora:
                    plantas.append({
                        "id": planta_id,
                        "especie_id": especie_id,
                        "especie_nome": self.flora[especie_id].nome,
                        "nivel_cultivo": info["nivel_cultivo"],
                        "maturidade": info["maturidade"],
                        "tempo_cultivo": info["tempo_cultivo"]
                    })
        
        return plantas

