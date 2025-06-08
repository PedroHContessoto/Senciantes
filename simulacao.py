import time
import threading
import random
from modelos.mundo import Mundo
from modelos.senciante import Senciante
from utils.config import (
    DEFAULT_WORLD_SIZE, DEFAULT_INITIAL_SENCIANTES,
    DEFAULT_SIMULATION_SPEED, DEFAULT_UPDATE_INTERVAL
)
from utils.helpers import posicao_aleatoria, log_info, log_error

class Simulacao:
    """
    Classe que representa o motor de simulação do jogo.
    Coordena a atualização do mundo e dos Senciantes.
    """
    
    def __init__(self, tamanho_mundo=None, num_senciantes_inicial=None):
        """
        Inicializa uma nova Simulação.
        
        Args:
            tamanho_mundo (list, optional): Tamanho do mundo [largura, altura]. Default é DEFAULT_WORLD_SIZE.
            num_senciantes_inicial (int, optional): Número inicial de Senciantes. Default é DEFAULT_INITIAL_SENCIANTES.
        """
        # Garante que tamanho_mundo seja uma tupla
        self.tamanho_mundo = tuple(tamanho_mundo) if tamanho_mundo else tuple(DEFAULT_WORLD_SIZE)
        self.num_senciantes_inicial = num_senciantes_inicial if num_senciantes_inicial else DEFAULT_INITIAL_SENCIANTES
        
        # Criar mundo
        self.mundo = Mundo(self.tamanho_mundo)
        
        # Criar Senciantes iniciais
        self.senciantes = {}  # Dicionário de id: Senciante
        self._criar_senciantes_iniciais()
        
        # Configurações de simulação
        self.velocidade = DEFAULT_SIMULATION_SPEED
        self.intervalo_atualizacao = DEFAULT_UPDATE_INTERVAL
        self.tempo_simulacao = 0.0  # Tempo decorrido na simulação em horas
        self.tempo_real_inicio = None  # Tempo real de início da simulação
        
        # Estado da simulação
        self.executando = False
        self.pausada = False
        self.thread_simulacao = None
        
        # Estatísticas
        self.estatisticas = {
            "nascimentos": 0,
            "mortes": 0,
            "construcoes": 0,
            "tecnologias": 0,
            "recursos_coletados": 0
        }
        
        # Eventos pendentes
        self.eventos_pendentes = []
        
        # Ações divinas pendentes
        self.acoes_divinas_pendentes = []
        
        # Callbacks
        self.callbacks = {
            "atualizacao": [],  # Chamados após cada atualização
            "nascimento": [],   # Chamados quando um Senciante nasce
            "morte": [],        # Chamados quando um Senciante morre
            "construcao": [],   # Chamados quando uma construção é criada
            "tecnologia": [],   # Chamados quando uma tecnologia é descoberta
            "evento": []        # Chamados quando um evento é registrado
        }
    
    def _criar_senciantes_iniciais(self):
        """
        Cria os Senciantes iniciais no mundo.
        """
        for _ in range(self.num_senciantes_inicial):
            # Gerar posição aleatória
            posicao = posicao_aleatoria(self.tamanho_mundo)
            
            # Criar Senciante
            senciante = Senciante(posicao)
            
            # Adicionar ao dicionário de Senciantes
            self.senciantes[senciante.id] = senciante
    
    def iniciar(self):
        """
        Inicia a simulação em uma thread separada.
        
        Returns:
            bool: True se a simulação foi iniciada, False se já estava em execução.
        """
        if self.executando:
            return False
        
        self.executando = True
        self.pausada = False
        self.tempo_real_inicio = time.time()
        
        # Iniciar thread de simulação
        self.thread_simulacao = threading.Thread(target=self._loop_simulacao)
        self.thread_simulacao.daemon = True
        self.thread_simulacao.start()
        
        log_info("Simulação iniciada")
        return True
    
    def pausar(self):
        """
        Pausa a simulação.
        
        Returns:
            bool: True se a simulação foi pausada, False se já estava pausada ou não estava em execução.
        """
        if not self.executando or self.pausada:
            return False
        
        self.pausada = True
        log_info("Simulação pausada")
        return True
    
    def retomar(self):
        """
        Retoma a simulação pausada.
        
        Returns:
            bool: True se a simulação foi retomada, False se não estava pausada ou não estava em execução.
        """
        if not self.executando or not self.pausada:
            return False
        
        self.pausada = False
        log_info("Simulação retomada")
        return True

    def acelerar(self, fator):
        """
        Acelera a simulação multiplicando a velocidade atual por um fator.

        Args:
            fator (float): Fator multiplicador da velocidade. Ex: 2.0 dobra a velocidade.
        """
        if fator <= 0:
            log_error("Fator de aceleração deve ser positivo.")
            return

        nova_velocidade = self.velocidade * fator
        self.definir_velocidade(nova_velocidade)
        log_info(f"Velocidade acelerada para {nova_velocidade}x (fator aplicado: {fator})")

    def desacelerar(self, fator):
        """
        Desacelera a simulação dividindo a velocidade atual por um fator.

        Args:
            fator (float): Fator divisor da velocidade. Ex: 2.0 reduz a velocidade pela metade.
        """
        if fator <= 0:
            log_error("Fator de desaceleração deve ser positivo.")
            return

        nova_velocidade = self.velocidade / fator
        self.definir_velocidade(nova_velocidade)
        log_info(f"Velocidade desacelerada para {nova_velocidade}x (fator aplicado: {fator})")

    def parar(self):
        """
        Para a simulação.
        
        Returns:
            bool: True se a simulação foi parada, False se não estava em execução.
        """
        if not self.executando:
            return False
        
        self.executando = False
        self.pausada = False
        
        # Aguardar thread terminar
        if self.thread_simulacao:
            self.thread_simulacao.join(timeout=1.0)
            self.thread_simulacao = None
        
        log_info("Simulação parada")
        return True
    
    def definir_velocidade(self, velocidade):
        """
        Define a velocidade da simulação.
        
        Args:
            velocidade (float): Nova velocidade (1.0 = tempo real).
            
        Returns:
            float: Velocidade definida.
        """
        # Limitar velocidade entre 0.1 e 10.0
        self.velocidade = max(0.1, min(10.0, velocidade))
        log_info(f"Velocidade da simulação definida para {self.velocidade}")
        return self.velocidade
    
    def _loop_simulacao(self):
        """
        Loop principal da simulação.
        """
        ultimo_tempo = time.time()
        
        try:
            while self.executando:
                # Verificar se está pausada
                if self.pausada:
                    time.sleep(0.1)
                    ultimo_tempo = time.time()
                    continue
                
                # Calcular delta tempo
                tempo_atual = time.time()
                delta_tempo_real = tempo_atual - ultimo_tempo
                ultimo_tempo = tempo_atual
                
                # Converter para tempo de simulação
                delta_tempo_simulacao = delta_tempo_real * self.velocidade
                
                # Limitar delta tempo para evitar saltos muito grandes
                delta_tempo_simulacao = min(delta_tempo_simulacao, 0.1)
                
                # Atualizar tempo de simulação
                self.tempo_simulacao += delta_tempo_simulacao
                
                # Atualizar simulação
                self._atualizar(delta_tempo_simulacao)
                
                # Processar eventos pendentes
                self._processar_eventos_pendentes()
                
                # Processar ações divinas pendentes
                self._processar_acoes_divinas_pendentes()
                
                # Chamar callbacks de atualização
                for callback in self.callbacks["atualizacao"]:
                    try:
                        callback(self)
                    except Exception as e:
                        log_error(f"Erro em callback de atualização: {e}")
                
                # Aguardar intervalo de atualização
                time.sleep(self.intervalo_atualizacao)
        
        except Exception as e:
            log_error(f"Erro no loop de simulação: {e}")
            self.executando = False

    def _atualizar(self, delta_tempo):
        """
        Atualiza o estado da simulação.

        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Atualizar mundo
        self.mundo.atualizar(delta_tempo)

        # Atualizar Senciantes
        senciantes_mortos = []

        for senciante_id, senciante in self.senciantes.items():
            # Atualizar Senciante
            if not senciante.atualizar(delta_tempo, self.mundo):
                # Senciante morreu
                senciantes_mortos.append(senciante_id)

                # Registrar morte no histórico
                causa = self._determinar_causa_morte(senciante)
                self.mundo.historico.registrar_morte(
                    self.tempo_simulacao,
                    senciante_id,
                    causa
                )

                # Atualizar estatísticas
                self.estatisticas["mortes"] += 1

                # Chamar callbacks de morte
                for callback in self.callbacks["morte"]:
                    try:
                        callback(self, senciante_id, causa)
                    except Exception as e:
                        log_error(f"Erro em callback de morte: {e}")

        # Remover Senciantes mortos
        for senciante_id in senciantes_mortos:
            del self.senciantes[senciante_id]

        # Processar interações entre Senciantes
        self._processar_interacoes()

        # Chance de reprodução
        self._processar_reproducao()

        # Registrar estatísticas no histórico
        self.mundo.historico.registrar_estatisticas(
            self.tempo_simulacao,
            len(self.senciantes),
            self._contar_recursos()
        )
    
    def _determinar_causa_morte(self, senciante):
        """
        Determina a causa da morte de um Senciante.
        
        Args:
            senciante (Senciante): Senciante que morreu.
            
        Returns:
            str: Causa da morte.
        """
        # Verificar as causas em ordem de prioridade
        if senciante.necessidades["fome"] >= 0.9:
            return "fome"
        elif senciante.necessidades["sede"] >= 0.9:
            return "sede"
        elif senciante.estado["saude"] <= 0.1:
            return "doença"
        elif senciante.idade > senciante.modificadores.get("longevidade", 1.0) * 0.9:
            return "velhice"
        else:
            return "desconhecida"
    
    def _contar_recursos(self):
        """
        Conta a quantidade total de cada tipo de recurso no mundo.
        
        Returns:
            dict: Dicionário de tipo_recurso: quantidade_total.
        """
        recursos = {}
        
        # Contar recursos no mundo
        for recurso in self.mundo.recursos.values():
            if recurso.tipo in recursos:
                recursos[recurso.tipo] += recurso.quantidade
            else:
                recursos[recurso.tipo] = recurso.quantidade
        
        # Contar recursos nos inventários dos Senciantes
        for senciante in self.senciantes.values():
            for tipo, quantidade in senciante.inventario.items():
                if tipo in recursos:
                    recursos[tipo] += quantidade
                else:
                    recursos[tipo] = quantidade
        
        # Contar recursos nas construções
        for construcao in self.mundo.construcoes.values():
            for tipo, quantidade in construcao.recursos_armazenados.items():
                if tipo in recursos:
                    recursos[tipo] += quantidade
                else:
                    recursos[tipo] = quantidade
        
        return recursos
    
    def _processar_interacoes(self):
        """
        Processa interações entre Senciantes próximos.
        """
        # Lista de pares de Senciantes que já interagiram neste ciclo
        interacoes_processadas = set()
        
        # Para cada Senciante
        for senciante_id, senciante in self.senciantes.items():
            # Encontrar Senciantes próximos
            for outro_id, outro in self.senciantes.items():
                # Ignorar a si mesmo
                if senciante_id == outro_id:
                    continue
                
                # Verificar se já interagiram neste ciclo
                par = tuple(sorted([senciante_id, outro_id]))
                if par in interacoes_processadas:
                    continue
                
                # Calcular distância
                distancia = ((senciante.posicao[0] - outro.posicao[0])**2 + 
                             (senciante.posicao[1] - outro.posicao[1])**2)**0.5
                
                # Interagir se estiverem próximos
                if distancia <= 2.0:
                    self._interagir(senciante, outro)
                    interacoes_processadas.add(par)
    
    def _interagir(self, senciante1, senciante2):
        """
        Processa uma interação entre dois Senciantes.
        
        Args:
            senciante1 (Senciante): Primeiro Senciante.
            senciante2 (Senciante): Segundo Senciante.
        """
        # Estabelecer relação se não existir
        if senciante2.id not in senciante1.relacoes:
            senciante1.estabelecer_relacao(senciante2.id, "conhecido", 0.3)
        
        if senciante1.id not in senciante2.relacoes:
            senciante2.estabelecer_relacao(senciante1.id, "conhecido", 0.3)
        
        # Fortalecer relação existente
        senciante1.fortalecer_relacao(senciante2.id, 0.05)
        senciante2.fortalecer_relacao(senciante1.id, 0.05)
        
        # Reduzir necessidade social
        senciante1.necessidades["social"] = max(0.0, senciante1.necessidades["social"] - 0.1)
        senciante2.necessidades["social"] = max(0.0, senciante2.necessidades["social"] - 0.1)
        
        # Chance de comunicação
        if random.random() < 0.3:
            # Determinar assunto
            assuntos = [
                {"tipo": "necessidade", "conteudo": "fome"},
                {"tipo": "necessidade", "conteudo": "sede"},
                {"tipo": "localizacao", "conteudo": "recurso"},
                {"tipo": "perigo", "conteudo": "clima"}
            ]
            
            # Adicionar tecnologias conhecidas como possíveis assuntos
            for tecnologia in senciante1.tecnologias_conhecidas:
                assuntos.append({"tipo": "tecnologia", "conteudo": tecnologia})
            
            # Escolher assunto aleatório
            assunto = random.choice(assuntos)
            
            # Tentar comunicar
            sucesso = senciante1.comunicar(senciante2, assunto)
            
            # Registrar evento de comunicação bem-sucedida
            if sucesso:
                self.mundo.historico.registrar_evento(
                    "comunicacao",
                    f"Comunicação sobre {assunto['tipo']} entre Senciantes",
                    self.tempo_simulacao,
                    [senciante1.id, senciante2.id]
                )
    
    def _processar_reproducao(self):
        """
        Processa a reprodução entre Senciantes.
        """
        # Lista de pares de Senciantes que já tentaram reproduzir neste ciclo
        reproducoes_processadas = set()
        
        # Para cada Senciante
        for senciante_id, senciante in self.senciantes.items():
            # Verificar se pode reproduzir
            if not senciante.pode_reproduzir():
                continue
            
            # Encontrar parceiros potenciais
            for outro_id, outro in self.senciantes.items():
                # Ignorar a si mesmo
                if senciante_id == outro_id:
                    continue
                
                # Verificar se já tentaram reproduzir neste ciclo
                par = tuple(sorted([senciante_id, outro_id]))
                if par in reproducoes_processadas:
                    continue
                
                # Verificar se o outro pode reproduzir
                if not outro.pode_reproduzir():
                    continue
                
                # Calcular distância
                distancia = ((senciante.posicao[0] - outro.posicao[0])**2 + 
                             (senciante.posicao[1] - outro.posicao[1])**2)**0.5
                
                # Reproduzir se estiverem próximos
                if distancia <= 2.0:
                    # Chance de reprodução
                    if random.random() < 0.5:
                        # Criar novo Senciante
                        novo_senciante = Senciante(senciante.posicao, 
                                                   progenitores=[senciante.id, outro.id])
                        
                        # Adicionar ao mundo
                        self.senciantes[novo_senciante.id] = novo_senciante
                        
                        # Registrar nascimento no histórico
                        self.mundo.historico.registrar_nascimento(
                            self.tempo_simulacao,
                            novo_senciante.id,
                            [senciante.id, outro.id]
                        )
                        
                        # Atualizar estatísticas
                        self.estatisticas["nascimentos"] += 1
                        
                        # Chamar callbacks de nascimento
                        for callback in self.callbacks["nascimento"]:
                            try:
                                callback(self, novo_senciante.id)
                            except Exception as e:
                                log_error(f"Erro em callback de nascimento: {e}")
                    
                    reproducoes_processadas.add(par)
    
    def _processar_eventos_pendentes(self):
        """
        Processa os eventos pendentes na fila.
        """
        for evento in self.eventos_pendentes:
            tipo = evento["tipo"]
            
            if tipo == "construcao":
                # Criar construção
                self.mundo.adicionar_construcao(
                    evento["posicao"],
                    evento["tipo_construcao"],
                    evento["tamanho"],
                    evento["proprietario_id"]
                )
                
                # Registrar no histórico
                self.mundo.historico.registrar_construcao(
                    self.tempo_simulacao,
                    evento["tipo_construcao"],
                    evento["proprietario_id"]
                )
                
                # Atualizar estatísticas
                self.estatisticas["construcoes"] += 1
                
                # Chamar callbacks de construção
                for callback in self.callbacks["construcao"]:
                    try:
                        callback(self, evento["tipo_construcao"], evento["proprietario_id"])
                    except Exception as e:
                        log_error(f"Erro em callback de construção: {e}")
            
            elif tipo == "tecnologia":
                # Registrar no histórico
                self.mundo.historico.registrar_tecnologia(
                    self.tempo_simulacao,
                    evento["tecnologia"],
                    evento["inventor_id"]
                )
                
                # Atualizar estatísticas
                self.estatisticas["tecnologias"] += 1
                
                # Chamar callbacks de tecnologia
                for callback in self.callbacks["tecnologia"]:
                    try:
                        callback(self, evento["tecnologia"], evento["inventor_id"])
                    except Exception as e:
                        log_error(f"Erro em callback de tecnologia: {e}")
            
            # Chamar callbacks de evento
            for callback in self.callbacks["evento"]:
                try:
                    callback(self, evento)
                except Exception as e:
                    log_error(f"Erro em callback de evento: {e}")
        
        # Limpar eventos pendentes
        self.eventos_pendentes = []
    
    def _processar_acoes_divinas_pendentes(self):
        """
        Processa as ações divinas pendentes na fila.
        """
        for acao in self.acoes_divinas_pendentes:
            tipo = acao["tipo"]
            
            if tipo == "clima":
                # Aplicar efeito no clima
                self.mundo.clima.aplicar_efeito(
                    acao["alvo"],
                    acao["intensidade"],
                    acao["duracao"]
                )
                log_info(f"Ação divina de clima aplicada: {acao}")
            
            elif tipo == "recurso":
                # Adicionar recurso ao mundo
                self.mundo.adicionar_recurso(
                    acao["posicao"],
                    acao["tipo"],
                    acao["quantidade"]
                )
                log_info(f"Ação divina de recurso aplicada: {acao}")
            
            elif tipo == "senciante":
                # Modificar Senciante
                senciante_id = acao["senciante_id"]
                if senciante_id in self.senciantes:
                    senciante = self.senciantes[senciante_id]
                    
                    if "saude" in acao:
                        senciante.estado["saude"] = max(0.0, min(1.0, senciante.estado["saude"] + acao["saude"]))
                    if "energia" in acao:
                        senciante.estado["energia"] = max(0.0, min(1.0, senciante.estado["energia"] + acao["energia"]))
                    if "fome" in acao:
                        senciante.necessidades["fome"] = max(0.0, min(1.0, senciante.necessidades["fome"] + acao["fome"]))
                    
                    log_info(f"Ação divina em Senciante {senciante_id} aplicada: {acao}")
                else:
                    log_error(f"Senciante {senciante_id} não encontrado para ação divina.")
        
        # Limpar ações divinas pendentes
        self.acoes_divinas_pendentes = []
    
    def adicionar_evento(self, tipo, dados):
        """
        Adiciona um evento à fila de eventos pendentes.
        
        Args:
            tipo (str): Tipo do evento (ex: "construcao", "tecnologia").
            dados (dict): Dicionário com os dados específicos do evento.
            
        Returns:
            bool: True se o evento foi adicionado, False caso contrário.
        """
        eventos_validos = ["construcao", "tecnologia"]
        if tipo not in eventos_validos:
            log_error(f"Tipo de evento inválido: {tipo}")
            return False
        
        self.eventos_pendentes.append({"tipo": tipo, **dados})
        return True
    
    def adicionar_acao_divina(self, tipo, dados):
        """
        Adiciona uma ação divina à fila de ações divinas pendentes.
        
        Args:
            tipo (str): Tipo da ação divina (ex: "clima", "recurso", "senciante").
            dados (dict): Dicionário com os dados específicos da ação.
            
        Returns:
            bool: True se a ação foi adicionada, False caso contrário.
        """
        acoes_validas = ["clima", "recurso", "senciante"]
        if tipo not in acoes_validas:
            log_error(f"Tipo de ação divina inválido: {tipo}")
            return False
        
        self.acoes_divinas_pendentes.append({"tipo": tipo, **dados})
        return True
    
    def registrar_callback(self, tipo, callback_func):
        """
        Registra uma função de callback para um tipo de evento específico.
        
        Args:
            tipo (str): Tipo de evento para o qual o callback será registrado.
            callback_func (function): Função a ser chamada quando o evento ocorrer.
            
        Returns:
            bool: True se o callback foi registrado, False caso contrário.
        """
        if tipo not in self.callbacks:
            log_error(f"Tipo de callback inválido: {tipo}")
            return False
        
        self.callbacks[tipo].append(callback_func)
        return True
    
    def remover_callback(self, tipo, callback_func):
        """
        Remove uma função de callback de um tipo de evento específico.
        
        Args:
            tipo (str): Tipo de evento do qual o callback será removido.
            callback_func (function): Função a ser removida.
            
        Returns:
            bool: True se o callback foi removido, False caso contrário.
        """
        if tipo not in self.callbacks:
            log_error(f"Tipo de callback inválido: {tipo}")
            return False
        
        try:
            self.callbacks[tipo].remove(callback_func)
            return True
        except ValueError:
            log_error(f"Callback não encontrado para o tipo {tipo}")
            return False
    
    def obter_estado(self):
        """
        Retorna o estado atual da simulação.
        
        Returns:
            dict: Dicionário com o estado da simulação.
        """
        return {
            "tempo_simulacao": self.tempo_simulacao,
            "executando": self.executando,
            "pausada": self.pausada,
            "velocidade": self.velocidade,
            "estatisticas": self.estatisticas,
            "num_senciantes": len(self.senciantes),
            "num_recursos": len(self.mundo.recursos),
            "num_construcoes": len(self.mundo.construcoes),
            "clima": self.mundo.clima.to_dict()
        }
    
    def to_dict(self):
        """
        Converte o objeto Simulacao para um dicionário serializável.
        
        Returns:
            dict: Dicionário representando o estado da simulação.
        """
        return {
            "estado": self.obter_estado(),
            "mundo": self.mundo.to_dict(),
            "senciantes": {id: s.to_dict() for id, s in self.senciantes.items()},
            "historico": self.mundo.historico.to_dict()
        }


