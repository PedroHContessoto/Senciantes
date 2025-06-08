import random
import time
import json
import uuid
from enum import Enum

class TipoEvento(Enum):
    NASCIMENTO = "nascimento"
    MORTE = "morte"
    REPRODUCAO = "reproducao"
    DESCOBERTA = "descoberta"
    CONSTRUCAO = "construcao"
    ACAO_JOGADOR = "acao_jogador"
    MUDANCA_CLIMA = "mudanca_clima"
    FORMACAO_RELACAO = "formacao_relacao"
    MUDANCA_CULTURA = "mudanca_cultura"
    FORMACAO_RELIGIAO = "formacao_religiao"

class Evento:
    def __init__(self, tipo, tempo, envolvidos=None, descricao="", importancia=0.5):
        self.id = str(uuid.uuid4())
        self.tipo = tipo
        self.tempo = tempo
        self.envolvidos = envolvidos if envolvidos else []
        self.descricao = descricao
        self.importancia = importancia
    
    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo.value if isinstance(self.tipo, TipoEvento) else self.tipo,
            "tempo": self.tempo,
            "envolvidos": self.envolvidos,
            "descricao": self.descricao,
            "importancia": self.importancia
        }

class EventoManager:
    def __init__(self):
        self.observadores = {}  # Dicionário de observadores por tipo de evento
    
    def registrar_observador(self, tipo_evento, observador):
        if tipo_evento not in self.observadores:
            self.observadores[tipo_evento] = []
        self.observadores[tipo_evento].append(observador)
    
    def remover_observador(self, tipo_evento, observador):
        if tipo_evento in self.observadores and observador in self.observadores[tipo_evento]:
            self.observadores[tipo_evento].remove(observador)
    
    def notificar(self, evento):
        tipo = evento.tipo
        if isinstance(tipo, TipoEvento):
            tipo = tipo.value
        
        if tipo in self.observadores:
            for observador in self.observadores[tipo]:
                observador.atualizar(evento)
        
        # Notificar observadores que escutam todos os eventos
        if "*" in self.observadores:
            for observador in self.observadores["*"]:
                observador.atualizar(evento)

class Observador:
    def atualizar(self, evento):
        pass

class Genoma:
    def __init__(self, genes=None):
        self.genes = genes if genes else {
            "agressividade": random.uniform(0.0, 1.0),
            "empatia": random.uniform(0.0, 1.0),
            "curiosidade": random.uniform(0.0, 1.0),
            "capacidade_cognitiva": random.uniform(0.0, 1.0),
            "resistencia_doencas": random.uniform(0.0, 1.0),
            "fertilidade": random.uniform(0.0, 1.0),
            "tempo_vida": random.uniform(0.5, 1.5)  # Multiplicador do tempo de vida base
        }
        self.mutacoes = []  # Lista de mutações específicas
        self.especie = "senciante_base"  # Espécie do Senciante
    
    def mutar(self, taxa_mutacao=0.1):
        """Aplica mutações aleatórias ao genoma."""
        novo_genes = self.genes.copy()
        for gene in novo_genes:
            if random.random() < taxa_mutacao:
                # Aplicar uma pequena mutação ao gene
                delta = random.uniform(-0.1, 0.1)
                novo_genes[gene] = max(0.0, min(1.0, novo_genes[gene] + delta))
                
                # Para o gene tempo_vida, permitir um range maior
                if gene == "tempo_vida":
                    novo_genes[gene] = max(0.1, min(2.0, novo_genes[gene] + delta))
        
        # Chance de desenvolver uma mutação específica
        if random.random() < taxa_mutacao / 5:
            mutacao = f"mutacao_{len(self.mutacoes) + 1}"
            self.mutacoes.append(mutacao)
        
        return Genoma(novo_genes)
    
    def cruzar(self, outro_genoma, taxa_mutacao=0.1):
        """Cruza este genoma com outro genoma para produzir um filho."""
        genes_filho = {}
        for gene in self.genes:
            # 50% de chance de herdar de cada pai
            if random.random() < 0.5:
                genes_filho[gene] = self.genes[gene]
            else:
                genes_filho[gene] = outro_genoma.genes[gene]
        
        # Criar o genoma do filho
        genoma_filho = Genoma(genes_filho)
        
        # Aplicar mutações
        return genoma_filho.mutar(taxa_mutacao)
    
    def to_dict(self):
        return {
            "genes": self.genes,
            "mutacoes": self.mutacoes,
            "especie": self.especie
        }

class Memoria:
    def __init__(self, tipo, conteudo, importancia, tempo):
        self.id = str(uuid.uuid4())
        self.tipo = tipo            # Tipo de memória (experiência, conhecimento, etc.)
        self.conteudo = conteudo    # Conteúdo da memória
        self.importancia = importancia  # Importância da memória (0.0 a 1.0)
        self.tempo = tempo          # Tempo em que a memória foi criada
        self.forca = 1.0            # Força da memória (diminui com o tempo)
    
    def enfraquecer(self, taxa=0.01):
        """Enfraquece a memória com o tempo."""
        self.forca = max(0.0, self.forca - taxa)
        return self.forca > 0.1  # Retorna True se a memória ainda é relevante
    
    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "conteudo": self.conteudo,
            "importancia": self.importancia,
            "tempo": self.tempo,
            "forca": self.forca
        }

class Relacao:
    def __init__(self, id_outro_senciante, tipo, forca):
        self.id = str(uuid.uuid4())
        self.id_outro_senciante = id_outro_senciante  # ID do outro Senciante
        self.tipo = tipo            # Tipo de relação (amizade, rivalidade, amor, etc.)
        self.forca = forca          # Força da relação (0.0 a 1.0)
        self.historico = []         # Histórico de interações
    
    def adicionar_interacao(self, descricao, impacto):
        """Adiciona uma interação ao histórico e atualiza a força da relação."""
        self.historico.append({
            "descricao": descricao,
            "tempo": time.time(),
            "impacto": impacto
        })
        self.forca = max(0.0, min(1.0, self.forca + impacto))
    
    def to_dict(self):
        return {
            "id": self.id,
            "id_outro_senciante": self.id_outro_senciante,
            "tipo": self.tipo,
            "forca": self.forca,
            "historico": self.historico
        }

class Senciante(Observador):
    def __init__(self, id=None, genoma=None, posicao=None):
        self.id = id if id else str(uuid.uuid4())
        self.genoma = genoma if genoma else Genoma()
        self.posicao = posicao if posicao else (0, 0)
        self.necessidades = {
            "fome": 0.0,                  # 0.0 (saciado) a 1.0 (faminto)
            "sede": 0.0,                  # 0.0 (saciado) a 1.0 (sedento)
            "sono": 0.0,                  # 0.0 (descansado) a 1.0 (exausto)
            "higiene": 0.0,               # 0.0 (limpo) a 1.0 (sujo)
            "excrecao": 0.0               # 0.0 (aliviado) a 1.0 (necessitado)
        }
        self.estado = {
            "saude": 1.0,                 # 0.0 (morto) a 1.0 (saudável)
            "idade": 0,                   # Em horas
            "energia": 1.0                # 0.0 (sem energia) a 1.0 (energia máxima)
        }
        self.habilidades = {
            "comunicacao": 0.0,           # Nível de comunicação
            "construcao": 0.0,            # Nível de construção
            "tecnologia": 0.0,            # Nível de tecnologia
            "social": 0.0                 # Nível de habilidade social
        }
        self.memoria = []                 # Lista de memórias
        self.relacoes = {}                # Dicionário de relações com outros Senciantes
        self.inventario = []              # Lista de itens possuídos
        self.acoes_disponiveis = []       # Lista de ações que o Senciante pode realizar
        self.construcoes = []             # Lista de IDs de construções que o Senciante construiu
        self.tecnologias_conhecidas = []  # Lista de tecnologias conhecidas pelo Senciante
    
    def atualizar(self, evento):
        """Implementação do método da interface Observador."""
        # Processar o evento e atualizar o estado do Senciante conforme necessário
        if evento.tipo == TipoEvento.MUDANCA_CLIMA:
            self.adicionar_memoria("experiencia", f"Observei uma mudança no clima: {evento.descricao}", 0.3, evento.tempo)
        elif evento.tipo == TipoEvento.ACAO_JOGADOR and self.id in evento.envolvidos:
            self.adicionar_memoria("experiencia", f"Senti algo divino: {evento.descricao}", 0.8, evento.tempo)
    
    def atualizar_necessidades(self, delta_tempo):
        """Atualiza as necessidades do Senciante com base no tempo passado."""
        # Aumentar a fome (aproximadamente 0.25 a cada hora)
        self.necessidades["fome"] = min(1.0, self.necessidades["fome"] + 0.25 * delta_tempo)
        
        # Aumentar a sede (aproximadamente 0.5 a cada hora)
        self.necessidades["sede"] = min(1.0, self.necessidades["sede"] + 0.5 * delta_tempo)
        
        # Aumentar o sono (aproximadamente 0.1 a cada hora, mais se estiver ativo)
        sono_base = 0.1
        if self.estado["energia"] < 0.3:
            sono_base = 0.2
        self.necessidades["sono"] = min(1.0, self.necessidades["sono"] + sono_base * delta_tempo)
        
        # Aumentar a necessidade de higiene
        self.necessidades["higiene"] = min(1.0, self.necessidades["higiene"] + 0.05 * delta_tempo)
        
        # Aumentar a necessidade de excreção
        self.necessidades["excrecao"] = min(1.0, self.necessidades["excrecao"] + 0.15 * delta_tempo)
        
        # Atualizar a saúde com base nas necessidades
        self.atualizar_saude()
        
        # Atualizar a idade
        self.estado["idade"] += delta_tempo
        
        # Verificar se o Senciante morreu de velhice
        tempo_vida_maximo = 48 * self.genoma.genes["tempo_vida"]  # 48 horas (2 dias) * multiplicador
        if self.estado["idade"] >= tempo_vida_maximo:
            self.estado["saude"] = 0.0  # Morte por velhice
    
    def atualizar_saude(self):
        """Atualiza a saúde do Senciante com base nas necessidades."""
        saude = 1.0
        
        # Penalidades por necessidades extremas
        if self.necessidades["fome"] > 0.8:
            saude -= 0.2
        if self.necessidades["sede"] > 0.8:
            saude -= 0.3
        if self.necessidades["sono"] > 0.9:
            saude -= 0.1
        if self.necessidades["higiene"] > 0.9:
            saude -= 0.05
        if self.necessidades["excrecao"] > 0.9:
            saude -= 0.05
        
        # Aplicar resistência a doenças do genoma
        resistencia = self.genoma.genes["resistencia_doencas"]
        saude = min(1.0, saude + (resistencia * 0.2))
        
        self.estado["saude"] = max(0.0, saude)
    
    def tomar_decisao(self):
        """Decide a próxima ação do Senciante com base em suas necessidades e estado."""
        # Priorizar necessidades mais urgentes
        necessidade_prioritaria = max(self.necessidades.items(), key=lambda x: x[1])
        
        if necessidade_prioritaria[1] > 0.7:
            # Necessidade crítica, priorizar satisfazê-la
            if necessidade_prioritaria[0] == "fome":
                return "procurar_comida"
            elif necessidade_prioritaria[0] == "sede":
                return "procurar_agua"
            elif necessidade_prioritaria[0] == "sono":
                return "descansar"
            elif necessidade_prioritaria[0] == "higiene":
                return "limpar"
            elif necessidade_prioritaria[0] == "excrecao":
                return "excretar"
        
        # Se não há necessidades críticas, considerar outras atividades
        if random.random() < self.genoma.genes["curiosidade"]:
            return "explorar"
        
        if random.random() < self.genoma.genes["capacidade_cognitiva"] and self.habilidades["construcao"] > 0.3:
            return "construir"
        
        if random.random() < self.genoma.genes["empatia"] and self.habilidades["social"] > 0.2:
            return "socializar"
        
        # Ação padrão: explorar
        return "explorar"
    
    def executar_acao(self, acao, ambiente):
        """Executa a ação decidida pelo Senciante."""
        if acao == "procurar_comida":
            return self.procurar_comida(ambiente)
        elif acao == "procurar_agua":
            return self.procurar_agua(ambiente)
        elif acao == "descansar":
            return self.descansar()
        elif acao == "limpar":
            return self.limpar()
        elif acao == "excretar":
            return self.excretar()
        elif acao == "explorar":
            return self.explorar(ambiente)
        elif acao == "construir":
            return self.construir(ambiente)
        elif acao == "socializar":
            return self.socializar(ambiente)
        else:
            return f"Ação desconhecida: {acao}"
    
    def procurar_comida(self, ambiente):
        """Procura comida no ambiente."""
        # Implementação simplificada
        recursos_comida = [r for r in ambiente.recursos.values() if r.tipo == "comida"]
        if recursos_comida:
            # Encontrar o recurso de comida mais próximo
            recurso_mais_proximo = min(recursos_comida, key=lambda r: self.calcular_distancia(r.posicao))
            
            # Mover-se em direção ao recurso
            self.mover_para(recurso_mais_proximo.posicao)
            
            # Se estiver perto o suficiente, consumir o recurso
            if self.calcular_distancia(recurso_mais_proximo.posicao) < 1.0:
                quantidade_consumida = min(0.5, recurso_mais_proximo.quantidade)
                recurso_mais_proximo.quantidade -= quantidade_consumida
                self.necessidades["fome"] = max(0.0, self.necessidades["fome"] - quantidade_consumida)
                return f"Consumiu {quantidade_consumida} de comida"
            
            return "Movendo-se em direção à comida"
        else:
            # Não encontrou comida, explorar
            return self.explorar(ambiente)
    
    def procurar_agua(self, ambiente):
        """Procura água no ambiente."""
        # Implementação simplificada
        recursos_agua = [r for r in ambiente.recursos.values() if r.tipo == "agua"]
        if recursos_agua:
            # Encontrar o recurso de água mais próximo
            recurso_mais_proximo = min(recursos_agua, key=lambda r: self.calcular_distancia(r.posicao))
            
            # Mover-se em direção ao recurso
            self.mover_para(recurso_mais_proximo.posicao)
            
            # Se estiver perto o suficiente, consumir o recurso
            if self.calcular_distancia(recurso_mais_proximo.posicao) < 1.0:
                quantidade_consumida = min(0.5, recurso_mais_proximo.quantidade)
                recurso_mais_proximo.quantidade -= quantidade_consumida
                self.necessidades["sede"] = max(0.0, self.necessidades["sede"] - quantidade_consumida)
                return f"Consumiu {quantidade_consumida} de água"
            
            return "Movendo-se em direção à água"
        else:
            # Não encontrou água, explorar
            return self.explorar(ambiente)
    
    def descansar(self):
        """Descansa para recuperar energia e reduzir o sono."""
        self.necessidades["sono"] = max(0.0, self.necessidades["sono"] - 0.3)
        self.estado["energia"] = min(1.0, self.estado["energia"] + 0.2)
        return "Descansando"
    
    def limpar(self):
        """Limpa-se para reduzir a necessidade de higiene."""
        self.necessidades["higiene"] = max(0.0, self.necessidades["higiene"] - 0.5)
        return "Limpando-se"
    
    def excretar(self):
        """Excreta para reduzir a necessidade de excreção."""
        self.necessidades["excrecao"] = max(0.0, self.necessidades["excrecao"] - 0.8)
        return "Excretando"
    
    def explorar(self, ambiente):
        """Explora o ambiente em busca de recursos e conhecimento."""
        # Mover-se aleatoriamente
        direcao_x = random.uniform(-1, 1)
        direcao_y = random.uniform(-1, 1)
        
        nova_posicao_x = max(0, min(ambiente.tamanho[0], self.posicao[0] + direcao_x))
        nova_posicao_y = max(0, min(ambiente.tamanho[1], self.posicao[1] + direcao_y))
        
        self.posicao = (nova_posicao_x, nova_posicao_y)
        
        # Chance de descobrir algo novo
        if random.random() < self.genoma.genes["curiosidade"] * 0.2:
            # Descobrir um recurso
            recursos_proximos = [r for r in ambiente.recursos.values() 
                               if self.calcular_distancia(r.posicao) < 2.0]
            
            if recursos_proximos:
                recurso = random.choice(recursos_proximos)
                self.adicionar_memoria("conhecimento", f"Descobri um recurso: {recurso.tipo}", 0.6, time.time())
                return f"Descobriu um recurso: {recurso.tipo}"
            
            # Descobrir uma tecnologia
            if random.random() < self.genoma.genes["capacidade_cognitiva"] * 0.1:
                tecnologias_possiveis = ["ferramenta_basica", "abrigo_simples", "fogo", "agricultura_basica"]
                tecnologias_desconhecidas = [t for t in tecnologias_possiveis if t not in self.tecnologias_conhecidas]
                
                if tecnologias_desconhecidas:
                    nova_tecnologia = random.choice(tecnologias_desconhecidas)
                    self.tecnologias_conhecidas.append(nova_tecnologia)
                    self.adicionar_memoria("conhecimento", f"Descobri uma nova tecnologia: {nova_tecnologia}", 0.8, time.time())
                    
                    # Aumentar habilidade de tecnologia
                    self.habilidades["tecnologia"] += 0.1
                    
                    return f"Descobriu uma nova tecnologia: {nova_tecnologia}"
        
        return "Explorando o ambiente"
    
    def construir(self, ambiente):
        """Constrói algo no ambiente."""
        # Verificar se o Senciante tem conhecimento para construir
        if not self.tecnologias_conhecidas:
            return "Não possui conhecimento para construir"
        
        # Escolher uma tecnologia conhecida para construir
        tecnologia = random.choice(self.tecnologias_conhecidas)
        
        # Verificar se há recursos suficientes nas proximidades
        recursos_necessarios = {
            "ferramenta_basica": ["madeira"],
            "abrigo_simples": ["madeira", "pedra"],
            "fogo": ["madeira"],
            "agricultura_basica": ["terra", "agua"]
        }
        
        if tecnologia in recursos_necessarios:
            recursos_requeridos = recursos_necessarios[tecnologia]
            recursos_disponiveis = True
            
            for tipo_recurso in recursos_requeridos:
                recursos_proximos = [r for r in ambiente.recursos.values() 
                                   if r.tipo == tipo_recurso and self.calcular_distancia(r.posicao) < 2.0]
                
                if not recursos_proximos:
                    recursos_disponiveis = False
                    break
            
            if recursos_disponiveis:
                # Consumir recursos
                for tipo_recurso in recursos_requeridos:
                    recurso = next(r for r in ambiente.recursos.values() 
                                 if r.tipo == tipo_recurso and self.calcular_distancia(r.posicao) < 2.0)
                    recurso.quantidade -= 0.5
                
                # Criar construção
                nova_construcao = Construcao(
                    tipo=tecnologia,
                    posicao=self.posicao,
                    tamanho=1.0,
                    qualidade=self.habilidades["construcao"],
                    construtor=self.id
                )
                
                ambiente.construcoes.append(nova_construcao)
                self.construcoes.append(nova_construcao.id)
                
                # Aumentar habilidade de construção
                self.habilidades["construcao"] += 0.05
                
                return f"Construiu: {tecnologia}"
            else:
                return "Recursos insuficientes para construir"
        
        return "Não sabe como construir isso"
    
    def socializar(self, ambiente):
        """Socializa com outros Senciantes próximos."""
        # Encontrar Senciantes próximos
        senciantes_proximos = [s for s in ambiente.senciantes.values() 
                             if s.id != self.id and self.calcular_distancia(s.posicao) < 3.0]
        
        if not senciantes_proximos:
            return "Não há outros Senciantes próximos"
        
        # Escolher um Senciante para interagir
        outro_senciante = random.choice(senciantes_proximos)
        
        # Determinar o tipo de interação com base nos genes
        if random.random() < self.genoma.genes["agressividade"]:
            # Interação agressiva
            tipo_relacao = "rivalidade"
            forca_inicial = -0.2
        elif random.random() < self.genoma.genes["empatia"]:
            # Interação amigável
            tipo_relacao = "amizade"
            forca_inicial = 0.3
        else:
            # Interação neutra
            tipo_relacao = "conhecidos"
            forca_inicial = 0.1
        
        # Criar ou atualizar relação
        if outro_senciante.id in self.relacoes:
            relacao = self.relacoes[outro_senciante.id]
            impacto = random.uniform(-0.1, 0.2)
            relacao.adicionar_interacao(f"Interação com {outro_senciante.id}", impacto)
        else:
            relacao = Relacao(outro_senciante.id, tipo_relacao, forca_inicial)
            self.relacoes[outro_senciante.id] = relacao
        
        # Aumentar habilidade social
        self.habilidades["social"] += 0.02
        
        # Chance de aprender algo do outro Senciante
        if random.random() < self.genoma.genes["capacidade_cognitiva"] * 0.3:
            # Aprender tecnologia
            tecnologias_desconhecidas = [t for t in outro_senciante.tecnologias_conhecidas 
                                       if t not in self.tecnologias_conhecidas]
            
            if tecnologias_desconhecidas:
                nova_tecnologia = random.choice(tecnologias_desconhecidas)
                self.tecnologias_conhecidas.append(nova_tecnologia)
                self.adicionar_memoria("conhecimento", f"Aprendi uma nova tecnologia com {outro_senciante.id}: {nova_tecnologia}", 0.7, time.time())
                return f"Aprendeu {nova_tecnologia} com {outro_senciante.id}"
        
        return f"Socializou com {outro_senciante.id}"
    
    def reproduzir(self, parceiro, ambiente):
        """Tenta reproduzir com outro Senciante."""
        # Verificar condições para reprodução
        if self.estado["idade"] < 5 or parceiro.estado["idade"] < 5:
            return "Um dos Senciantes é muito jovem para reprodução"
        
        if self.estado["saude"] < 0.5 or parceiro.estado["saude"] < 0.5:
            return "Um dos Senciantes não está saudável o suficiente para reprodução"
        
        # Calcular probabilidade de reprodução bem-sucedida
        probabilidade = (self.genoma.genes["fertilidade"] + parceiro.genoma.genes["fertilidade"]) / 2
        
        if random.random() < probabilidade:
            # Reprodução bem-sucedida
            genoma_filho = self.genoma.cruzar(parceiro.genoma)
            
            # Criar novo Senciante
            filho = Senciante(genoma=genoma_filho, posicao=self.posicao)
            
            # Adicionar o filho ao ambiente
            ambiente.adicionar_senciante(filho)
            
            # Criar memórias sobre o nascimento
            self.adicionar_memoria("experiencia", f"Tive um filho com {parceiro.id}", 0.9, time.time())
            parceiro.adicionar_memoria("experiencia", f"Tive um filho com {self.id}", 0.9, time.time())
            
            return f"Reprodução bem-sucedida, novo Senciante criado: {filho.id}"
        else:
            return "Tentativa de reprodução falhou"
    
    def adicionar_memoria(self, tipo, conteudo, importancia, tempo):
        """Adiciona uma nova memória ao Senciante."""
        nova_memoria = Memoria(tipo, conteudo, importancia, tempo)
        self.memoria.append(nova_memoria)
        
        # Limitar o número de memórias (esquecer as menos importantes)
        if len(self.memoria) > 50:
            self.memoria.sort(key=lambda m: m.importancia * m.forca)
            self.memoria = self.memoria[-50:]
    
    def mover_para(self, destino):
        """Move o Senciante em direção a um destino."""
        # Calcular direção
        dx = destino[0] - self.posicao[0]
        dy = destino[1] - self.posicao[1]
        
        # Normalizar
        distancia = max(0.1, (dx**2 + dy**2)**0.5)
        dx /= distancia
        dy /= distancia
        
        # Mover (com velocidade baseada na energia)
        velocidade = 0.5 * self.estado["energia"]
        self.posicao = (
            self.posicao[0] + dx * velocidade,
            self.posicao[1] + dy * velocidade
        )
        
        # Consumir energia
        self.estado["energia"] = max(0.1, self.estado["energia"] - 0.05)
    
    def calcular_distancia(self, posicao):
        """Calcula a distância entre o Senciante e uma posição."""
        dx = posicao[0] - self.posicao[0]
        dy = posicao[1] - self.posicao[1]
        return (dx**2 + dy**2)**0.5
    
    def to_dict(self):
        """Converte o Senciante para um dicionário."""
        return {
            "id": self.id,
            "genoma": self.genoma.to_dict(),
            "posicao": self.posicao,
            "necessidades": self.necessidades,
            "estado": self.estado,
            "habilidades": self.habilidades,
            "memoria": [m.to_dict() for m in self.memoria],
            "relacoes": {k: v.to_dict() for k, v in self.relacoes.items()},
            "inventario": self.inventario,
            "construcoes": self.construcoes,
            "tecnologias_conhecidas": self.tecnologias_conhecidas
        }

class Recurso:
    def __init__(self, id=None, tipo="", quantidade=1.0, posicao=(0, 0), renovavel=False, taxa_renovacao=0.0):
        self.id = id if id else str(uuid.uuid4())
        self.tipo = tipo            # Tipo de recurso (água, comida, madeira, etc.)
        self.quantidade = quantidade  # Quantidade disponível
        self.posicao = posicao      # Posição no mundo
        self.renovavel = renovavel  # Se o recurso é renovável
        self.taxa_renovacao = taxa_renovacao   # Taxa de renovação (se aplicável)
    
    def atualizar(self, delta_tempo):
        """Atualiza o recurso, renovando-o se for renovável."""
        if self.renovavel and self.quantidade < 1.0:
            self.quantidade = min(1.0, self.quantidade + self.taxa_renovacao * delta_tempo)
    
    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "quantidade": self.quantidade,
            "posicao": self.posicao,
            "renovavel": self.renovavel,
            "taxa_renovacao": self.taxa_renovacao
        }

class Clima:
    def __init__(self):
        self.temperatura = 20.0     # Temperatura em graus Celsius
        self.umidade = 0.5          # Umidade (0.0 a 1.0)
        self.precipitacao = 0.0     # Precipitação (0.0 a 1.0)
        self.vento = 0.0            # Velocidade do vento
        self.eventos_climaticos = []  # Lista de eventos climáticos ativos
    
    def atualizar(self, delta_tempo):
        """Atualiza o clima, possivelmente gerando eventos climáticos."""
        # Variação aleatória na temperatura
        self.temperatura += random.uniform(-0.5, 0.5) * delta_tempo
        self.temperatura = max(0, min(40, self.temperatura))
        
        # Variação aleatória na umidade
        self.umidade += random.uniform(-0.05, 0.05) * delta_tempo
        self.umidade = max(0.1, min(1.0, self.umidade))
        
        # Variação aleatória na precipitação
        if self.umidade > 0.7 and random.random() < 0.1 * delta_tempo:
            self.precipitacao = random.uniform(0.5, 1.0)
        else:
            self.precipitacao = max(0.0, self.precipitacao - 0.1 * delta_tempo)
        
        # Variação aleatória no vento
        self.vento += random.uniform(-0.2, 0.2) * delta_tempo
        self.vento = max(0.0, min(10.0, self.vento))
        
        # Gerar eventos climáticos
        if random.random() < 0.05 * delta_tempo:
            if self.precipitacao > 0.8 and self.vento > 5.0:
                self.eventos_climaticos.append("tempestade")
            elif self.temperatura > 35:
                self.eventos_climaticos.append("onda_de_calor")
            elif self.temperatura < 5:
                self.eventos_climaticos.append("onda_de_frio")
        
        # Remover eventos climáticos antigos
        self.eventos_climaticos = [e for e in self.eventos_climaticos if random.random() > 0.2 * delta_tempo]
    
    def to_dict(self):
        return {
            "temperatura": self.temperatura,
            "umidade": self.umidade,
            "precipitacao": self.precipitacao,
            "vento": self.vento,
            "eventos_climaticos": self.eventos_climaticos
        }

class Construcao:
    def __init__(self, id=None, tipo="", posicao=(0, 0), tamanho=1.0, qualidade=0.5, construtor=""):
        self.id = id if id else str(uuid.uuid4())
        self.tipo = tipo            # Tipo de construção (abrigo, casa, fazenda, etc.)
        self.posicao = posicao      # Posição no mundo
        self.tamanho = tamanho      # Tamanho da construção
        self.qualidade = qualidade  # Qualidade da construção (0.0 a 1.0)
        self.construtor = construtor  # ID do Senciante que construiu
        self.habitantes = []        # Lista de IDs dos Senciantes que habitam
        self.recursos_armazenados = {}  # Recursos armazenados na construção
        self.funcoes = []           # Funções da construção (moradia, armazenamento, etc.)
        self.idade = 0              # Idade da construção em horas
        self.estado = 1.0           # Estado da construção (0.0 a 1.0)
    
    def atualizar(self, delta_tempo):
        """Atualiza o estado da construção com o tempo."""
        self.idade += delta_tempo
        
        # Deterioração natural
        taxa_deterioracao = 0.01 * (1.0 - self.qualidade)
        self.estado = max(0.0, self.estado - taxa_deterioracao * delta_tempo)
    
    def adicionar_habitante(self, id_senciante):
        """Adiciona um Senciante como habitante da construção."""
        if id_senciante not in self.habitantes:
            self.habitantes.append(id_senciante)
    
    def remover_habitante(self, id_senciante):
        """Remove um Senciante da lista de habitantes."""
        if id_senciante in self.habitantes:
            self.habitantes.remove(id_senciante)
    
    def armazenar_recurso(self, tipo_recurso, quantidade):
        """Armazena um recurso na construção."""
        if tipo_recurso in self.recursos_armazenados:
            self.recursos_armazenados[tipo_recurso] += quantidade
        else:
            self.recursos_armazenados[tipo_recurso] = quantidade
    
    def consumir_recurso(self, tipo_recurso, quantidade):
        """Consome um recurso armazenado na construção."""
        if tipo_recurso in self.recursos_armazenados:
            if self.recursos_armazenados[tipo_recurso] >= quantidade:
                self.recursos_armazenados[tipo_recurso] -= quantidade
                return quantidade
            else:
                quantidade_disponivel = self.recursos_armazenados[tipo_recurso]
                self.recursos_armazenados[tipo_recurso] = 0
                return quantidade_disponivel
        return 0
    
    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "posicao": self.posicao,
            "tamanho": self.tamanho,
            "qualidade": self.qualidade,
            "construtor": self.construtor,
            "habitantes": self.habitantes,
            "recursos_armazenados": self.recursos_armazenados,
            "funcoes": self.funcoes,
            "idade": self.idade,
            "estado": self.estado
        }

class Ambiente:
    def __init__(self, tamanho=(100, 100)):
        self.tamanho = tamanho      # Tamanho do mundo (x, y)
        self.mapa = []              # Matriz representando o mapa do mundo
        self.recursos = {}          # Dicionário de recursos disponíveis
        self.clima = Clima()        # Objeto representando o clima atual
        self.construcoes = []       # Lista de construções no mundo
        self.eventos = []           # Lista de eventos ativos no mundo
        self.senciantes = {}        # Dicionário de Senciantes no mundo
    
    def inicializar_mapa(self):
        """Inicializa o mapa do mundo."""
        # Implementação simplificada: mapa plano
        self.mapa = [[0 for _ in range(self.tamanho[1])] for _ in range(self.tamanho[0])]
    
    def gerar_recursos_iniciais(self):
        """Gera recursos iniciais no mundo."""
        # Água
        for _ in range(10):
            posicao = (random.uniform(0, self.tamanho[0]), random.uniform(0, self.tamanho[1]))
            recurso = Recurso(
                tipo="agua",
                quantidade=random.uniform(0.5, 1.0),
                posicao=posicao,
                renovavel=True,
                taxa_renovacao=0.1
            )
            self.recursos[recurso.id] = recurso
        
        # Comida
        for _ in range(15):
            posicao = (random.uniform(0, self.tamanho[0]), random.uniform(0, self.tamanho[1]))
            recurso = Recurso(
                tipo="comida",
                quantidade=random.uniform(0.3, 0.8),
                posicao=posicao,
                renovavel=True,
                taxa_renovacao=0.05
            )
            self.recursos[recurso.id] = recurso
        
        # Madeira
        for _ in range(20):
            posicao = (random.uniform(0, self.tamanho[0]), random.uniform(0, self.tamanho[1]))
            recurso = Recurso(
                tipo="madeira",
                quantidade=random.uniform(0.5, 1.0),
                posicao=posicao,
                renovavel=True,
                taxa_renovacao=0.02
            )
            self.recursos[recurso.id] = recurso
        
        # Pedra
        for _ in range(12):
            posicao = (random.uniform(0, self.tamanho[0]), random.uniform(0, self.tamanho[1]))
            recurso = Recurso(
                tipo="pedra",
                quantidade=random.uniform(0.7, 1.0),
                posicao=posicao,
                renovavel=False
            )
            self.recursos[recurso.id] = recurso
        
        # Terra
        for _ in range(25):
            posicao = (random.uniform(0, self.tamanho[0]), random.uniform(0, self.tamanho[1]))
            recurso = Recurso(
                tipo="terra",
                quantidade=1.0,
                posicao=posicao,
                renovavel=False
            )
            self.recursos[recurso.id] = recurso
    
    def adicionar_senciante(self, senciante):
        """Adiciona um Senciante ao mundo."""
        self.senciantes[senciante.id] = senciante
    
    def remover_senciante(self, id_senciante):
        """Remove um Senciante do mundo."""
        if id_senciante in self.senciantes:
            del self.senciantes[id_senciante]
    
    def atualizar(self, delta_tempo):
        """Atualiza o ambiente e todos os seus componentes."""
        # Atualizar clima
        self.clima.atualizar(delta_tempo)
        
        # Atualizar recursos
        for recurso in list(self.recursos.values()):
            recurso.atualizar(delta_tempo)
            
            # Remover recursos esgotados e não renováveis
            if recurso.quantidade <= 0 and not recurso.renovavel:
                del self.recursos[recurso.id]
        
        # Atualizar construções
        for construcao in self.construcoes:
            construcao.atualizar(delta_tempo)
        
        # Remover construções destruídas
        self.construcoes = [c for c in self.construcoes if c.estado > 0]
    
    def to_dict(self):
        return {
            "tamanho": self.tamanho,
            "clima": self.clima.to_dict(),
            "recursos": {k: v.to_dict() for k, v in self.recursos.items()},
            "construcoes": [c.to_dict() for c in self.construcoes],
            "eventos": self.eventos,
            "senciantes": {k: v.to_dict() for k, v in self.senciantes.items()}
        }

class EventoHistorico:
    def __init__(self, tipo, tempo, envolvidos=None, descricao="", importancia=0.5):
        self.id = str(uuid.uuid4())
        self.tipo = tipo            # Tipo de evento (nascimento, morte, guerra, etc.)
        self.tempo = tempo          # Tempo em que o evento ocorreu
        self.envolvidos = envolvidos if envolvidos else []  # Lista de IDs dos Senciantes envolvidos
        self.descricao = descricao  # Descrição do evento
        self.importancia = importancia  # Importância do evento (0.0 a 1.0)
    
    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "tempo": self.tempo,
            "envolvidos": self.envolvidos,
            "descricao": self.descricao,
            "importancia": self.importancia
        }

class Historico(Observador):
    def __init__(self):
        self.eventos = []           # Lista de eventos históricos
        self.genealogia = {}        # Dicionário de relações genealógicas
        self.avancos = []           # Lista de avanços tecnológicos e culturais
        self.estatisticas = {       # Estatísticas do mundo
            "populacao": [],        # Lista de (tempo, população)
            "mortes": [],           # Lista de (tempo, número de mortes)
            "nascimentos": [],      # Lista de (tempo, número de nascimentos)
            "construcoes": [],      # Lista de (tempo, número de construções)
            "descobertas": []       # Lista de (tempo, descoberta)
        }
    
    def atualizar(self, evento):
        """Implementação do método da interface Observador."""
        # Registrar o evento no histórico
        if isinstance(evento, Evento):
            evento_historico = EventoHistorico(
                tipo=evento.tipo,
                tempo=evento.tempo,
                envolvidos=evento.envolvidos,
                descricao=evento.descricao,
                importancia=evento.importancia
            )
            self.eventos.append(evento_historico)
            
            # Atualizar estatísticas
            if evento.tipo == TipoEvento.NASCIMENTO:
                self.estatisticas["nascimentos"].append((evento.tempo, 1))
            elif evento.tipo == TipoEvento.MORTE:
                self.estatisticas["mortes"].append((evento.tempo, 1))
            elif evento.tipo == TipoEvento.CONSTRUCAO:
                self.estatisticas["construcoes"].append((evento.tempo, 1))
            elif evento.tipo == TipoEvento.DESCOBERTA:
                self.estatisticas["descobertas"].append((evento.tempo, evento.descricao))
    
    def registrar_populacao(self, tempo, populacao):
        """Registra a população atual."""
        self.estatisticas["populacao"].append((tempo, populacao))
    
    def registrar_relacao_genealogica(self, id_pai, id_mae, id_filho):
        """Registra uma relação genealógica."""
        if id_filho not in self.genealogia:
            self.genealogia[id_filho] = {"pais": [id_pai, id_mae], "filhos": []}
        
        # Adicionar o filho aos pais
        for id_pai in [id_pai, id_mae]:
            if id_pai in self.genealogia:
                if "filhos" not in self.genealogia[id_pai]:
                    self.genealogia[id_pai]["filhos"] = []
                self.genealogia[id_pai]["filhos"].append(id_filho)
            else:
                self.genealogia[id_pai] = {"pais": [], "filhos": [id_filho]}
    
    def registrar_avanco(self, tempo, tipo, descricao, importancia=0.5):
        """Registra um avanço tecnológico ou cultural."""
        self.avancos.append({
            "tempo": tempo,
            "tipo": tipo,
            "descricao": descricao,
            "importancia": importancia
        })
    
    def obter_eventos_por_tipo(self, tipo):
        """Retorna todos os eventos de um determinado tipo."""
        return [e for e in self.eventos if e.tipo == tipo]
    
    def obter_eventos_por_envolvido(self, id_senciante):
        """Retorna todos os eventos que envolvem um determinado Senciante."""
        return [e for e in self.eventos if id_senciante in e.envolvidos]
    
    def obter_eventos_por_periodo(self, tempo_inicio, tempo_fim):
        """Retorna todos os eventos em um determinado período de tempo."""
        return [e for e in self.eventos if tempo_inicio <= e.tempo <= tempo_fim]
    
    def obter_estatisticas_por_periodo(self, tipo_estatistica, tempo_inicio, tempo_fim):
        """Retorna estatísticas de um determinado tipo em um período de tempo."""
        if tipo_estatistica in self.estatisticas:
            return [(t, v) for t, v in self.estatisticas[tipo_estatistica] if tempo_inicio <= t <= tempo_fim]
        return []
    
    def to_dict(self):
        return {
            "eventos": [e.to_dict() for e in self.eventos],
            "genealogia": self.genealogia,
            "avancos": self.avancos,
            "estatisticas": self.estatisticas
        }

class AcaoJogador:
    def __init__(self, tipo, alvo, intensidade, duracao):
        self.id = str(uuid.uuid4())
        self.tipo = tipo            # Tipo de ação (clima, biologia, manifestação, etc.)
        self.alvo = alvo            # Alvo da ação (posição, Senciante, etc.)
        self.intensidade = intensidade  # Intensidade da ação (0.0 a 1.0)
        self.duracao = duracao      # Duração da ação em tempo de jogo
        self.efeitos = []           # Lista de efeitos da ação
        self.tempo_inicio = time.time()  # Tempo de início da ação
    
    def esta_ativa(self, tempo_atual):
        """Verifica se a ação ainda está ativa."""
        return tempo_atual - self.tempo_inicio < self.duracao
    
    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "alvo": self.alvo,
            "intensidade": self.intensidade,
            "duracao": self.duracao,
            "efeitos": self.efeitos,
            "tempo_inicio": self.tempo_inicio
        }

class ArtefatoDivino:
    def __init__(self, tipo, poder, posicao):
        self.id = str(uuid.uuid4())
        self.tipo = tipo            # Tipo de artefato
        self.poder = poder          # Poder do artefato (0.0 a 1.0)
        self.posicao = posicao      # Posição no mundo
        self.efeitos = []           # Lista de efeitos do artefato
        self.descoberto = False     # Se o artefato foi descoberto por algum Senciante
        self.possuidor = None       # ID do Senciante que possui o artefato (se aplicável)
    
    def aplicar_efeito(self, senciante):
        """Aplica o efeito do artefato a um Senciante."""
        if self.tipo == "conhecimento":
            # Aumentar capacidade cognitiva
            senciante.genoma.genes["capacidade_cognitiva"] = min(1.0, senciante.genoma.genes["capacidade_cognitiva"] + 0.2 * self.poder)
            
            # Chance de descobrir tecnologias avançadas
            if random.random() < 0.5 * self.poder:
                tecnologias_avancadas = ["escrita", "metalurgia", "matematica", "medicina"]
                tecnologia = random.choice(tecnologias_avancadas)
                if tecnologia not in senciante.tecnologias_conhecidas:
                    senciante.tecnologias_conhecidas.append(tecnologia)
                    senciante.adicionar_memoria("conhecimento", f"O artefato me revelou: {tecnologia}", 0.9, time.time())
            
            self.efeitos.append(f"Aumentou a capacidade cognitiva de {senciante.id}")
        
        elif self.tipo == "poder":
            # Aumentar agressividade
            senciante.genoma.genes["agressividade"] = min(1.0, senciante.genoma.genes["agressividade"] + 0.3 * self.poder)
            
            # Aumentar energia
            senciante.estado["energia"] = 1.0
            
            self.efeitos.append(f"Aumentou a agressividade e energia de {senciante.id}")
        
        elif self.tipo == "vida":
            # Aumentar saúde
            senciante.estado["saude"] = 1.0
            
            # Aumentar tempo de vida
            senciante.genoma.genes["tempo_vida"] = min(2.0, senciante.genoma.genes["tempo_vida"] + 0.5 * self.poder)
            
            self.efeitos.append(f"Aumentou a saúde e tempo de vida de {senciante.id}")
        
        elif self.tipo == "harmonia":
            # Aumentar empatia
            senciante.genoma.genes["empatia"] = min(1.0, senciante.genoma.genes["empatia"] + 0.3 * self.poder)
            
            # Reduzir agressividade
            senciante.genoma.genes["agressividade"] = max(0.0, senciante.genoma.genes["agressividade"] - 0.2 * self.poder)
            
            self.efeitos.append(f"Aumentou a empatia e reduziu a agressividade de {senciante.id}")
    
    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "poder": self.poder,
            "posicao": self.posicao,
            "efeitos": self.efeitos,
            "descoberto": self.descoberto,
            "possuidor": self.possuidor
        }

class Simulacao:
    def __init__(self, tamanho_mundo=(100, 100), num_senciantes_iniciais=10):
        self.tempo_atual = 0
        self.tempo_inicio = time.time()
        self.tempo_ultima_atualizacao = self.tempo_inicio
        self.velocidade = 1.0  # Multiplicador de velocidade da simulação
        self.pausado = False
        
        # Inicializar componentes
        self.evento_manager = EventoManager()
        self.ambiente = Ambiente(tamanho=tamanho_mundo)
        self.historico = Historico()
        self.acoes_jogador = []
        self.artefatos = []
        
        # Registrar observadores
        self.evento_manager.registrar_observador("*", self.historico)
        
        # Inicializar ambiente
        self.ambiente.inicializar_mapa()
        self.ambiente.gerar_recursos_iniciais()
        
        # Criar Senciantes iniciais
        for _ in range(num_senciantes_iniciais):
            posicao = (random.uniform(0, tamanho_mundo[0]), random.uniform(0, tamanho_mundo[1]))
            senciante = Senciante(posicao=posicao)
            self.ambiente.adicionar_senciante(senciante)
            
            # Registrar o Senciante como observador de eventos
            self.evento_manager.registrar_observador("acao_jogador", senciante)
            self.evento_manager.registrar_observador("mudanca_clima", senciante)
    
    def atualizar(self):
        """Atualiza a simulação por um passo de tempo."""
        if self.pausado:
            return
        
        # Calcular delta de tempo
        tempo_atual = time.time()
        delta_tempo_real = tempo_atual - self.tempo_ultima_atualizacao
        delta_tempo = delta_tempo_real * self.velocidade  # Tempo de jogo
        
        self.tempo_atual += delta_tempo
        self.tempo_ultima_atualizacao = tempo_atual
        
        # Atualizar ambiente
        self.ambiente.atualizar(delta_tempo)
        
        # Atualizar Senciantes
        senciantes_mortos = []
        for senciante in self.ambiente.senciantes.values():
            # Atualizar necessidades
            senciante.atualizar_necessidades(delta_tempo)
            
            # Verificar se o Senciante morreu
            if senciante.estado["saude"] <= 0:
                senciantes_mortos.append(senciante.id)
                
                # Criar evento de morte
                evento_morte = Evento(
                    tipo=TipoEvento.MORTE,
                    tempo=self.tempo_atual,
                    envolvidos=[senciante.id],
                    descricao=f"Morte de {senciante.id}",
                    importancia=0.7
                )
                self.evento_manager.notificar(evento_morte)
                continue
            
            # Tomar decisão e executar ação
            acao = senciante.tomar_decisao()
            resultado = senciante.executar_acao(acao, self.ambiente)
            
            # Processar resultado da ação
            if "Descobriu" in resultado:
                # Criar evento de descoberta
                evento_descoberta = Evento(
                    tipo=TipoEvento.DESCOBERTA,
                    tempo=self.tempo_atual,
                    envolvidos=[senciante.id],
                    descricao=resultado,
                    importancia=0.6
                )
                self.evento_manager.notificar(evento_descoberta)
            
            elif "Construiu" in resultado:
                # Criar evento de construção
                evento_construcao = Evento(
                    tipo=TipoEvento.CONSTRUCAO,
                    tempo=self.tempo_atual,
                    envolvidos=[senciante.id],
                    descricao=resultado,
                    importancia=0.5
                )
                self.evento_manager.notificar(evento_construcao)
        
        # Remover Senciantes mortos
        for id_senciante in senciantes_mortos:
            self.ambiente.remover_senciante(id_senciante)
        
        # Processar acoes do jogador
        acoes_ativas = []
        for acao in self.acoes_jogador:
            if acao.esta_ativa(tempo_atual):
                self.processar_acao_jogador(acao)
                acoes_ativas.append(acao)
        
        self.acoes_jogador = acoes_ativas
        
        # Atualizar estatísticas
        self.historico.registrar_populacao(self.tempo_atual, len(self.ambiente.senciantes))
    
    def processar_acao_jogador(self, acao):
        """Processa uma ação do jogador."""
        if acao.tipo == "clima":
            # Alterar clima
            if acao.alvo == "temperatura":
                self.ambiente.clima.temperatura += acao.intensidade * 10 - 5  # -5 a +5
            elif acao.alvo == "precipitacao":
                self.ambiente.clima.precipitacao = max(0.0, min(1.0, self.ambiente.clima.precipitacao + acao.intensidade))
            elif acao.alvo == "vento":
                self.ambiente.clima.vento += acao.intensidade * 5
            
            # Criar evento de mudança de clima
            evento_clima = Evento(
                tipo=TipoEvento.MUDANCA_CLIMA,
                tempo=self.tempo_atual,
                descricao=f"Mudança no clima: {acao.alvo}",
                importancia=0.4
            )
            self.evento_manager.notificar(evento_clima)
        
        elif acao.tipo == "biologia":
            # Interferir biologicamente
            if acao.alvo == "evolucao":
                # Escolher Senciantes aleatórios para evoluir
                num_senciantes = max(1, int(len(self.ambiente.senciantes) * acao.intensidade))
                senciantes_aleatorios = random.sample(list(self.ambiente.senciantes.values()), min(num_senciantes, len(self.ambiente.senciantes)))
                
                for senciante in senciantes_aleatorios:
                    # Aumentar capacidade cognitiva
                    senciante.genoma.genes["capacidade_cognitiva"] = min(1.0, senciante.genoma.genes["capacidade_cognitiva"] + 0.2 * acao.intensidade)
                    
                    # Criar evento de evolução
                    evento_evolucao = Evento(
                        tipo=TipoEvento.ACAO_JOGADOR,
                        tempo=self.tempo_atual,
                        envolvidos=[senciante.id],
                        descricao=f"Evolução instantânea em {senciante.id}",
                        importancia=0.7
                    )
                    self.evento_manager.notificar(evento_evolucao)
            
            elif acao.alvo == "doenca":
                # Criar doença que afeta Senciantes
                num_senciantes = max(1, int(len(self.ambiente.senciantes) * acao.intensidade))
                senciantes_aleatorios = random.sample(list(self.ambiente.senciantes.values()), min(num_senciantes, len(self.ambiente.senciantes)))
                
                for senciante in senciantes_aleatorios:
                    # Reduzir saúde
                    senciante.estado["saude"] = max(0.1, senciante.estado["saude"] - 0.3 * acao.intensidade)
                    
                    # Criar evento de doença
                    evento_doenca = Evento(
                        tipo=TipoEvento.ACAO_JOGADOR,
                        tempo=self.tempo_atual,
                        envolvidos=[senciante.id],
                        descricao=f"Doença afetou {senciante.id}",
                        importancia=0.6
                    )
                    self.evento_manager.notificar(evento_doenca)
        
        elif acao.tipo == "manifestacao":
            # Manifestar-se visualmente
            if acao.alvo == "sinal_divino":
                # Afetar todos os Senciantes próximos à posição
                posicao = acao.alvo.get("posicao", (0, 0))
                raio = 10 * acao.intensidade
                
                senciantes_afetados = []
                for senciante in self.ambiente.senciantes.values():
                    distancia = ((senciante.posicao[0] - posicao[0])**2 + (senciante.posicao[1] - posicao[1])**2)**0.5
                    if distancia <= raio:
                        senciantes_afetados.append(senciante.id)
                        senciante.adicionar_memoria("experiencia", "Vi um sinal divino no céu!", 0.9, self.tempo_atual)
                
                # Criar evento de manifestação
                evento_manifestacao = Evento(
                    tipo=TipoEvento.ACAO_JOGADOR,
                    tempo=self.tempo_atual,
                    envolvidos=senciantes_afetados,
                    descricao="Um sinal divino apareceu no céu",
                    importancia=0.8
                )
                self.evento_manager.notificar(evento_manifestacao)
            
            elif acao.alvo == "possessao":
                # Possuir um Senciante específico
                id_senciante = acao.alvo.get("id_senciante")
                if id_senciante in self.ambiente.senciantes:
                    senciante = self.ambiente.senciantes[id_senciante]
                    
                    # Aumentar temporariamente as habilidades
                    for habilidade in senciante.habilidades:
                        senciante.habilidades[habilidade] = min(1.0, senciante.habilidades[habilidade] + 0.3 * acao.intensidade)
                    
                    # Criar evento de possessão
                    evento_possessao = Evento(
                        tipo=TipoEvento.ACAO_JOGADOR,
                        tempo=self.tempo_atual,
                        envolvidos=[id_senciante],
                        descricao=f"Possessão divina de {id_senciante}",
                        importancia=0.9
                    )
                    self.evento_manager.notificar(evento_possessao)
        
        elif acao.tipo == "recurso":
            # Distribuir ou remover recursos
            if acao.alvo == "criar":
                # Criar novo recurso
                tipo_recurso = acao.alvo.get("tipo", "comida")
                posicao = acao.alvo.get("posicao", (random.uniform(0, self.ambiente.tamanho[0]), random.uniform(0, self.ambiente.tamanho[1])))
                quantidade = acao.intensidade
                
                recurso = Recurso(
                    tipo=tipo_recurso,
                    quantidade=quantidade,
                    posicao=posicao,
                    renovavel=True,
                    taxa_renovacao=0.05
                )
                self.ambiente.recursos[recurso.id] = recurso
                
                # Criar evento de criação de recurso
                evento_recurso = Evento(
                    tipo=TipoEvento.ACAO_JOGADOR,
                    tempo=self.tempo_atual,
                    descricao=f"Criação divina de {tipo_recurso}",
                    importancia=0.5
                )
                self.evento_manager.notificar(evento_recurso)
            
            elif acao.alvo == "destruir":
                # Destruir recursos em uma área
                posicao = acao.alvo.get("posicao", (0, 0))
                raio = 10 * acao.intensidade
                
                recursos_para_remover = []
                for id_recurso, recurso in self.ambiente.recursos.items():
                    distancia = ((recurso.posicao[0] - posicao[0])**2 + (recurso.posicao[1] - posicao[1])**2)**0.5
                    if distancia <= raio:
                        recursos_para_remover.append(id_recurso)
                
                for id_recurso in recursos_para_remover:
                    del self.ambiente.recursos[id_recurso]
                
                # Criar evento de destruição de recursos
                evento_destruicao = Evento(
                    tipo=TipoEvento.ACAO_JOGADOR,
                    tempo=self.tempo_atual,
                    descricao="Destruição divina de recursos",
                    importancia=0.6
                )
                self.evento_manager.notificar(evento_destruicao)
        
        elif acao.tipo == "artefato":
            # Criar artefato divino
            tipo_artefato = acao.alvo.get("tipo", "conhecimento")
            posicao = acao.alvo.get("posicao", (random.uniform(0, self.ambiente.tamanho[0]), random.uniform(0, self.ambiente.tamanho[1])))
            poder = acao.intensidade
            
            artefato = ArtefatoDivino(
                tipo=tipo_artefato,
                poder=poder,
                posicao=posicao
            )
            self.artefatos.append(artefato)
            
            # Criar evento de criação de artefato
            evento_artefato = Evento(
                tipo=TipoEvento.ACAO_JOGADOR,
                tempo=self.tempo_atual,
                descricao=f"Criação de artefato divino: {tipo_artefato}",
                importancia=0.8
            )
            self.evento_manager.notificar(evento_artefato)
    
    def adicionar_acao_jogador(self, tipo, alvo, intensidade, duracao):
        """Adiciona uma ação do jogador à simulação."""
        acao = AcaoJogador(tipo, alvo, intensidade, duracao)
        self.acoes_jogador.append(acao)
        return acao.id
    
    def pausar(self):
        """Pausa a simulação."""
        self.pausado = True
    
    def retomar(self):
        """Retoma a simulação."""
        self.pausado = False
        self.tempo_ultima_atualizacao = time.time()
    
    def acelerar(self, fator=2):
        """Acelera a simulação."""
        self.velocidade *= fator
    
    def desacelerar(self, fator=2):
        """Desacelera a simulação."""
        self.velocidade /= fator
    
    def to_dict(self):
        """Converte a simulação para um dicionário."""
        return {
            "tempo_atual": self.tempo_atual,
            "tempo_inicio": self.tempo_inicio,
            "velocidade": self.velocidade,
            "pausado": self.pausado,
            "ambiente": self.ambiente.to_dict(),
            "historico": self.historico.to_dict(),
            "acoes_jogador": [a.to_dict() for a in self.acoes_jogador],
            "artefatos": [a.to_dict() for a in self.artefatos]
        }

# Função para salvar o estado da simulação
def salvar_simulacao(simulacao, caminho):
    """Salva o estado da simulação em um arquivo JSON."""
    with open(caminho, 'w') as f:
        json.dump(simulacao.to_dict(), f, indent=2)

# Função para carregar o estado da simulação
def carregar_simulacao(caminho):
    """Carrega o estado da simulação de um arquivo JSON."""
    # Implementação simplificada: criar uma nova simulação
    # Em uma implementação completa, reconstruiríamos a simulação a partir dos dados
    return Simulacao()

# Exemplo de uso
if __name__ == "__main__":
    # Criar simulação
    simulacao = Simulacao(tamanho_mundo=(100, 100), num_senciantes_iniciais=10)
    
    # Executar alguns passos de simulação
    for _ in range(10):
        simulacao.atualizar()
    
    # Salvar estado
    salvar_simulacao(simulacao, "simulacao_estado.json")
    
    print("Simulação inicializada e executada com sucesso!")

