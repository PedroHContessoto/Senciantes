from modelos.moralidade import Moralidade
from utils.helpers import chance

class MecanicaConscienciaMoralidade:
    """
    Classe que implementa as mecânicas de consciência e moralidade emergente.
    """
    
    def __init__(self, mundo):
        """
        Inicializa a mecânica de consciência e moralidade.
        
        Args:
            mundo (Mundo): Objeto mundo para referência.
        """
        self.mundo = mundo
        
        # Valores morais que podem ser formados
        self.valores_morais = [
            "lealdade", "justica", "cuidado", 
            "liberdade", "autoridade", "pureza"
        ]
        
        # Dilemas morais que podem surgir
        self.dilemas_morais = [
            {
                "descricao": "Compartilhar recursos escassos com estranhos",
                "opcoes": ["compartilhar", "recusar"],
                "valores_afetados": {
                    "compartilhar": {"cuidado": 0.1, "justica": 0.1, "lealdade": -0.05},
                    "recusar": {"cuidado": -0.1, "justica": -0.1, "lealdade": 0.05}
                }
            },
            {
                "descricao": "Obedecer a um líder que ordena algo questionável",
                "opcoes": ["obedecer", "recusar"],
                "valores_afetados": {
                    "obedecer": {"autoridade": 0.1, "lealdade": 0.1, "justica": -0.1},
                    "recusar": {"autoridade": -0.1, "lealdade": -0.05, "justica": 0.1, "liberdade": 0.1}
                }
            },
            {
                "descricao": "Punir um membro do grupo que quebrou regras",
                "opcoes": ["punir", "perdoar"],
                "valores_afetados": {
                    "punir": {"justica": 0.1, "autoridade": 0.1, "cuidado": -0.05},
                    "perdoar": {"cuidado": 0.1, "justica": -0.05, "autoridade": -0.05}
                }
            },
            {
                "descricao": "Aceitar práticas culturais diferentes das suas",
                "opcoes": ["aceitar", "rejeitar"],
                "valores_afetados": {
                    "aceitar": {"liberdade": 0.1, "pureza": -0.05},
                    "rejeitar": {"pureza": 0.1, "liberdade": -0.05}
                }
            },
            {
                "descricao": "Mentir para proteger um amigo",
                "opcoes": ["mentir", "dizer_verdade"],
                "valores_afetados": {
                    "mentir": {"lealdade": 0.1, "justica": -0.1},
                    "dizer_verdade": {"justica": 0.1, "lealdade": -0.1}
                }
            }
        ]
    
    def inicializar_senciante(self, senciante):
        """
        Inicializa a moralidade de um Senciante.
        
        Args:
            senciante (Senciante): Senciante a ser inicializado.
        """
        # Verificar se o Senciante já tem moralidade
        if not hasattr(senciante, "moralidade") or senciante.moralidade is None:
            # Criar predisposicoes morais baseadas no genoma
            predisposicoes = {}
            
            # Usar genes para influenciar predisposicoes morais iniciais
            for valor in self.valores_morais:
                # Base aleatoria
                base = 0.3 + 0.4 * chance(0.5)  # Entre 0.3 e 0.7
                
                # Ajustar com base nos genes
                if valor == "lealdade":
                    modificador = (senciante.genoma.genes.get("social", 1.0) - 1.0) * 0.2
                elif valor == "justica":
                    modificador = (senciante.genoma.genes.get("inteligencia", 1.0) - 1.0) * 0.2
                elif valor == "cuidado":
                    modificador = (senciante.genoma.genes.get("social", 1.0) - 1.0) * 0.2
                elif valor == "liberdade":
                    modificador = (senciante.genoma.genes.get("adaptabilidade", 1.0) - 1.0) * 0.2
                elif valor == "autoridade":
                    modificador = (senciante.genoma.genes.get("forca", 1.0) - 1.0) * 0.2
                elif valor == "pureza":
                    modificador = (senciante.genoma.genes.get("resistencia", 1.0) - 1.0) * 0.2
                else:
                    modificador = 0.0
                
                # Aplicar modificador
                predisposicoes[valor] = max(0.1, min(0.9, base + modificador))
            
            # Criar objeto Moralidade
            senciante.moralidade = Moralidade(predisposicoes)
    
    def atualizar_senciante(self, senciante, delta_tempo):
        """
        Atualiza a consciência e moralidade de um Senciante.
        
        Args:
            senciante (Senciante): Senciante a ser atualizado.
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Verificar se o Senciante tem moralidade
        if not hasattr(senciante, "moralidade") or senciante.moralidade is None:
            self.inicializar_senciante(senciante)
            return
        
        # Chance de enfrentar um dilema moral (raro)
        if chance(0.01 * delta_tempo):
            self._apresentar_dilema_moral(senciante)
        
        # Chance de formar um princípio ético baseado em experiências recentes
        if chance(0.02 * delta_tempo):
            self._formar_principio_etico(senciante)
        
        # Chance de desenvolver um conceito filosófico (muito raro, requer alta inteligência)
        if senciante.habilidades.get("aprendizado", 0) > 0.7 and chance(0.005 * delta_tempo):
            self._desenvolver_conceito_filosofico(senciante)
    
    def _apresentar_dilema_moral(self, senciante):
        """
        Apresenta um dilema moral ao Senciante.
        
        Args:
            senciante (Senciante): Senciante que enfrentará o dilema.
            
        Returns:
            dict: Resultado do dilema.
        """
        # Escolher um dilema aleatório
        dilema = self.dilemas_morais[int(len(self.dilemas_morais) * chance(1.0))]
        
        # Determinar a escolha com base nos valores morais atuais
        escolha = self._tomar_decisao_moral(senciante, dilema)
        
        # Aplicar consequências da escolha
        consequencias = self._aplicar_consequencias_dilema(senciante, dilema, escolha)
        
        # Registrar o dilema resolvido
        senciante.moralidade.resolver_dilema(
            dilema["descricao"],
            escolha,
            consequencias["descricao"]
        )
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_evento(
            "dilema_moral",
            f"Senciante enfrentou dilema: {dilema['descricao']} - Escolha: {escolha}",
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            [senciante.id]
        )
        
        return {
            "dilema": dilema["descricao"],
            "escolha": escolha,
            "consequencias": consequencias
        }
    
    def _tomar_decisao_moral(self, senciante, dilema):
        """
        Determina a decisão do Senciante em um dilema moral.
        
        Args:
            senciante (Senciante): Senciante que está tomando a decisão.
            dilema (dict): Dilema moral.
            
        Returns:
            str: Opção escolhida.
        """
        # Calcular pontuação para cada opção com base nos valores morais
        pontuacoes = {}
        
        for opcao, efeitos in dilema["valores_afetados"].items():
            pontuacao = 0.0
            
            for valor, efeito in efeitos.items():
                # Multiplicar o valor moral atual pelo efeito da opção
                if valor in senciante.moralidade.valores:
                    pontuacao += senciante.moralidade.valores[valor] * efeito
            
            pontuacoes[opcao] = pontuacao
        
        # Escolher a opção com maior pontuação
        # Adicionar um pouco de aleatoriedade para não ser totalmente determinístico
        opcoes = list(pontuacoes.keys())
        pesos = [pontuacoes[o] + 0.1 for o in opcoes]  # Adicionar 0.1 para evitar pesos negativos
        
        # Normalizar pesos
        soma_pesos = sum(pesos)
        if soma_pesos > 0:
            pesos = [p / soma_pesos for p in pesos]
        else:
            # Se todos os pesos forem zero, usar probabilidade uniforme
            pesos = [1.0 / len(opcoes) for _ in opcoes]
        
        # Escolher com base nos pesos
        valor_aleatorio = chance(1.0)
        soma_acumulada = 0.0
        
        for i, peso in enumerate(pesos):
            soma_acumulada += peso
            if valor_aleatorio <= soma_acumulada:
                return opcoes[i]
        
        # Fallback (não deveria chegar aqui)
        return opcoes[0]
    
    def _aplicar_consequencias_dilema(self, senciante, dilema, escolha):
        """
        Aplica as consequências da escolha em um dilema moral.
        
        Args:
            senciante (Senciante): Senciante que tomou a decisão.
            dilema (dict): Dilema moral.
            escolha (str): Opção escolhida.
            
        Returns:
            dict: Consequências da escolha.
        """
        # Aplicar mudanças nos valores morais
        if escolha in dilema["valores_afetados"]:
            for valor, efeito in dilema["valores_afetados"][escolha].items():
                # Registrar experiência que afeta o valor moral
                senciante.moralidade.registrar_experiencia(
                    valor,
                    f"Dilema: {dilema['descricao']} - Escolha: {escolha}",
                    efeito
                )
        
        # Determinar consequências emocionais
        efeito_felicidade = 0.0
        efeito_estresse = 0.0
        
        # Simplificação: decisões alinhadas com valores fortes aumentam felicidade
        # Decisões contra valores fortes aumentam estresse
        for valor, efeito in dilema["valores_afetados"][escolha].items():
            if valor in senciante.moralidade.valores:
                valor_atual = senciante.moralidade.valores[valor]
                
                if valor_atual > 0.6:  # Valor forte
                    if efeito > 0:  # Decisão alinhada
                        efeito_felicidade += 0.05
                    else:  # Decisão contra
                        efeito_estresse += 0.05
        
        # Aplicar efeitos emocionais
        senciante.estado["felicidade"] = min(1.0, senciante.estado["felicidade"] + efeito_felicidade)
        senciante.estado["estresse"] = min(1.0, senciante.estado["estresse"] + efeito_estresse)
        
        # Gerar descrição das consequências
        if efeito_felicidade > efeito_estresse:
            descricao = "Sente-se bem com a decisão tomada"
        elif efeito_estresse > efeito_felicidade:
            descricao = "Sente conflito interno pela decisão tomada"
        else:
            descricao = "A decisão não teve grande impacto emocional"
        
        return {
            "descricao": descricao,
            "efeito_felicidade": efeito_felicidade,
            "efeito_estresse": efeito_estresse
        }
    
    def _formar_principio_etico(self, senciante):
        """
        Forma um princípio ético baseado em experiências.
        
        Args:
            senciante (Senciante): Senciante que formará o princípio.
            
        Returns:
            str: Princípio formado, ou None se nenhum princípio foi formado.
        """
        # Verificar se há valores morais fortes
        valores_fortes = []
        for valor, nivel in senciante.moralidade.valores.items():
            if nivel >= 0.7:
                valores_fortes.append(valor)
        
        if not valores_fortes:
            return None
        
        # Escolher um valor forte aleatório
        valor = valores_fortes[int(len(valores_fortes) * chance(1.0))]
        
        # Verificar se já existe um princípio para este valor
        if valor in senciante.moralidade.principios:
            return None
        
        # Formar princípio
        senciante.moralidade._formar_principio(valor)
        
        # Verificar se um princípio foi formado
        if valor in senciante.moralidade.principios:
            # Registrar no histórico do mundo
            self.mundo.historico.registrar_evento(
                "principio_etico",
                f"Senciante formou princípio ético: {senciante.moralidade.principios[valor]}",
                0,  # Tempo atual (será preenchido pelo motor de simulação)
                [senciante.id]
            )
            
            return senciante.moralidade.principios[valor]
        
        return None
    
    def _desenvolver_conceito_filosofico(self, senciante):
        """
        Desenvolve um conceito filosófico.
        
        Args:
            senciante (Senciante): Senciante que desenvolverá o conceito.
            
        Returns:
            str: Conceito filosófico desenvolvido.
        """
        # Gerar conceito filosófico
        conceito = senciante.moralidade.gerar_filosofia()
        
        # Registrar no histórico do mundo
        self.mundo.historico.registrar_conceito_filosofico(
            0,  # Tempo atual (será preenchido pelo motor de simulação)
            conceito,
            senciante.id
        )
        
        return conceito
    
    def avaliar_compatibilidade_moral(self, senciante1, senciante2):
        """
        Avalia a compatibilidade moral entre dois Senciantes.
        
        Args:
            senciante1 (Senciante): Primeiro Senciante.
            senciante2 (Senciante): Segundo Senciante.
            
        Returns:
            float: Compatibilidade moral (0.0 a 1.0).
        """
        # Verificar se ambos têm moralidade
        if (not hasattr(senciante1, "moralidade") or senciante1.moralidade is None or
            not hasattr(senciante2, "moralidade") or senciante2.moralidade is None):
            return 0.5  # Valor neutro se não houver moralidade
        
        # Calcular compatibilidade
        return senciante1.moralidade.compatibilidade_moral(senciante2.moralidade)
    
    def avaliar_acao_moral(self, senciante, acao, contexto):
        """
        Avalia uma ação com base na moralidade do Senciante.
        
        Args:
            senciante (Senciante): Senciante que avalia a ação.
            acao (str): Descrição da ação.
            contexto (dict): Contexto da ação.
            
        Returns:
            float: Avaliação da ação (-1.0 a 1.0).
        """
        # Verificar se o Senciante tem moralidade
        if not hasattr(senciante, "moralidade") or senciante.moralidade is None:
            return 0.0  # Valor neutro se não houver moralidade
        
        # Avaliar ação
        return senciante.moralidade.avaliar_acao(acao, contexto)
    
    def gerar_conflito_etico(self, grupo1, grupo2):
        """
        Gera um conflito ético entre dois grupos com morais divergentes.
        
        Args:
            grupo1 (list): Lista de Senciantes do primeiro grupo.
            grupo2 (list): Lista de Senciantes do segundo grupo.
            
        Returns:
            dict: Descrição do conflito ético.
        """
        # Calcular valores morais médios de cada grupo
        valores_grupo1 = self._calcular_valores_medios(grupo1)
        valores_grupo2 = self._calcular_valores_medios(grupo2)
        
        # Encontrar o valor com maior divergência
        maior_divergencia = 0.0
        valor_divergente = None
        
        for valor in self.valores_morais:
            if valor in valores_grupo1 and valor in valores_grupo2:
                divergencia = abs(valores_grupo1[valor] - valores_grupo2[valor])
                
                if divergencia > maior_divergencia:
                    maior_divergencia = divergencia
                    valor_divergente = valor
        
        # Se não houver divergência signific


