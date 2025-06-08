"""
Módulo que define a classe FerramentasAdministracao para o jogo "O Mundo dos Senciantes".
As FerramentasAdministracao fornecem funcionalidades avançadas para observação e análise do mundo.
"""

import numpy as np
import random
from utils.helpers import calcular_distancia

class FerramentasAdministracao:
    """
    Classe que fornece ferramentas avançadas para administração e observação do mundo.
    """
    
    def __init__(self, mundo, senciantes):
        """
        Inicializa as Ferramentas de Administração.
        
        Args:
            mundo (Mundo): Objeto mundo para referência.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        self.mundo = mundo
        self.senciantes = senciantes
        
        # Cache para análises
        self.cache_redes_sociais = None
        self.cache_diversidade_genetica = None
        self.cache_equilibrio_ecologico = None
        
        # Timestamp do último cálculo
        self.ultimo_calculo = {
            "redes_sociais": 0.0,
            "diversidade_genetica": 0.0,
            "equilibrio_ecologico": 0.0
        }
    
    def visualizar_redes_sociais(self, tempo_atual):
        """
        Visualiza as redes de influência social entre os Senciantes.
        
        Args:
            tempo_atual (float): Tempo atual da simulação.
            
        Returns:
            dict: Representação das redes sociais.
        """
        # Verificar se o cache está atualizado (recalcular a cada 24 horas simuladas)
        if tempo_atual - self.ultimo_calculo["redes_sociais"] >= 24.0:
            # Construir grafo de relações
            grafo = {}
            
            for senciante_id, senciante in self.senciantes.items():
                grafo[senciante_id] = {
                    "conexoes": {},
                    "influencia": 0.0,
                    "posicao": senciante.posicao
                }
                
                # Adicionar conexões baseadas nas relações
                for outro_id, relacao in senciante.relacoes.items():
                    if outro_id in self.senciantes:
                        # Só adicionar relações significativas
                        if abs(relacao["forca"]) >= 0.3:
                            grafo[senciante_id]["conexoes"][outro_id] = {
                                "tipo": relacao["tipo"],
                                "forca": relacao["forca"]
                            }
            
            # Calcular influência de cada Senciante (centralidade)
            for senciante_id in grafo:
                # Influência baseada no número de conexões e força delas
                influencia = 0.0
                for _, conexao in grafo[senciante_id]["conexoes"].items():
                    influencia += abs(conexao["forca"])
                
                grafo[senciante_id]["influencia"] = influencia
            
            # Identificar comunidades (simplificado)
            comunidades = self._identificar_comunidades(grafo)
            
            # Atualizar cache
            self.cache_redes_sociais = {
                "grafo": grafo,
                "comunidades": comunidades
            }
            
            self.ultimo_calculo["redes_sociais"] = tempo_atual
        
        return self.cache_redes_sociais
    
    def _identificar_comunidades(self, grafo):
        """
        Identifica comunidades na rede social (algoritmo simplificado).
        
        Args:
            grafo (dict): Grafo de relações sociais.
            
        Returns:
            list: Lista de comunidades identificadas.
        """
        # Implementação simplificada de detecção de comunidades
        # Baseada em proximidade física e relações positivas
        
        # Inicializar cada Senciante como sua própria comunidade
        comunidades = {senciante_id: i for i, senciante_id in enumerate(grafo.keys())}
        comunidade_para_membros = {i: [senciante_id] for i, senciante_id in enumerate(grafo.keys())}
        
        # Mesclar comunidades com base em relações fortes
        for senciante_id, dados in grafo.items():
            for outro_id, conexao in dados["conexoes"].items():
                # Se a relação for positiva e forte
                if conexao["forca"] >= 0.6:
                    # Mesclar comunidades
                    comunidade1 = comunidades[senciante_id]
                    comunidade2 = comunidades[outro_id]
                    
                    if comunidade1 != comunidade2:
                        # Escolher a comunidade menor para mesclar na maior
                        if len(comunidade_para_membros[comunidade1]) < len(comunidade_para_membros[comunidade2]):
                            menor, maior = comunidade1, comunidade2
                        else:
                            menor, maior = comunidade2, comunidade1
                        
                        # Mesclar
                        for membro in comunidade_para_membros[menor]:
                            comunidades[membro] = maior
                            comunidade_para_membros[maior].append(membro)
                        
                        # Remover comunidade menor
                        del comunidade_para_membros[menor]
        
        # Converter para formato de saída
        resultado = []
        for comunidade_id, membros in comunidade_para_membros.items():
            # Calcular centro da comunidade
            if membros:
                centro_x = sum(grafo[m]["posicao"][0] for m in membros) / len(membros)
                centro_y = sum(grafo[m]["posicao"][1] for m in membros) / len(membros)
                
                resultado.append({
                    "id": comunidade_id,
                    "membros": membros,
                    "tamanho": len(membros),
                    "centro": [centro_x, centro_y]
                })
        
        return resultado
    
    def visualizar_sentimentos(self, senciante_id=None):
        """
        Visualiza em tempo real os sentimentos dos Senciantes.
        
        Args:
            senciante_id (str, optional): ID do Senciante específico. Se None, visualiza todos.
            
        Returns:
            dict: Representação dos sentimentos.
        """
        sentimentos = {}
        
        # Se um ID específico for fornecido
        if senciante_id:
            if senciante_id in self.senciantes:
                senciante = self.senciantes[senciante_id]
                sentimentos[senciante_id] = self._extrair_sentimentos(senciante)
        else:
            # Visualizar todos os Senciantes
            for id, senciante in self.senciantes.items():
                sentimentos[id] = self._extrair_sentimentos(senciante)
        
        return sentimentos
    
    def _extrair_sentimentos(self, senciante):
        """
        Extrai informações de sentimentos de um Senciante.
        
        Args:
            senciante (Senciante): Objeto Senciante.
            
        Returns:
            dict: Representação dos sentimentos.
        """
        # Extrair sentimentos básicos
        sentimentos_basicos = {
            "felicidade": senciante.estado["felicidade"],
            "estresse": senciante.estado["estresse"]
        }
        
        # Extrair necessidades
        necessidades = {
            "fome": senciante.necessidades["fome"],
            "sede": senciante.necessidades["sede"],
            "sono": senciante.necessidades["sono"],
            "higiene": senciante.necessidades["higiene"],
            "social": senciante.necessidades["social"]
        }
        
        # Extrair valores morais (se disponíveis)
        valores_morais = {}
        if hasattr(senciante, "moralidade") and senciante.moralidade:
            valores_morais = senciante.moralidade.valores
        
        return {
            "sentimentos_basicos": sentimentos_basicos,
            "necessidades": necessidades,
            "valores_morais": valores_morais,
            "posicao": senciante.posicao
        }
    
    def avaliar_diversidade_genetica(self, tempo_atual):
        """
        Avalia a diversidade genética da população de Senciantes.
        
        Args:
            tempo_atual (float): Tempo atual da simulação.
            
        Returns:
            dict: Análise da diversidade genética.
        """
        # Verificar se o cache está atualizado (recalcular a cada 48 horas simuladas)
        if tempo_atual - self.ultimo_calculo["diversidade_genetica"] >= 48.0:
            # Coletar genes de todos os Senciantes
            genes_populacao = {}
            mutacoes_populacao = {}
            
            for senciante in self.senciantes.values():
                # Coletar genes
                for gene, valor in senciante.genoma.genes.items():
                    if gene not in genes_populacao:
                        genes_populacao[gene] = []
                    genes_populacao[gene].append(valor)
                
                # Coletar mutações
                for mutacao in senciante.genoma.mutacoes:
                    mutacoes_populacao[mutacao] = mutacoes_populacao.get(mutacao, 0) + 1
            
            # Calcular estatísticas para cada gene
            estatisticas_genes = {}
            for gene, valores in genes_populacao.items():
                estatisticas_genes[gene] = {
                    "media": np.mean(valores),
                    "desvio_padrao": np.std(valores),
                    "min": min(valores),
                    "max": max(valores)
                }
            
            # Calcular índice de diversidade genética
            indice_diversidade = 0.0
            for gene, stats in estatisticas_genes.items():
                # Usar o coeficiente de variação como medida de diversidade
                if stats["media"] > 0:
                    indice_diversidade += stats["desvio_padrao"] / stats["media"]
            
            # Normalizar
            if estatisticas_genes:
                indice_diversidade /= len(estatisticas_genes)
            
            # Calcular frequência de mutações
            total_senciantes = len(self.senciantes)
            frequencia_mutacoes = {mutacao: count / total_senciantes for mutacao, count in mutacoes_populacao.items()}
            
            # Atualizar cache
            self.cache_diversidade_genetica = {
                "indice_diversidade": indice_diversidade,
                "estatisticas_genes": estatisticas_genes,
                "frequencia_mutacoes": frequencia_mutacoes,
                "total_senciantes": total_senciantes
            }
            
            self.ultimo_calculo["diversidade_genetica"] = tempo_atual
        
        return self.cache_diversidade_genetica
    
    def avaliar_equilibrio_ecologico(self, tempo_atual, fauna=None, flora=None):
        """
        Avalia o equilíbrio ecológico do mundo.
        
        Args:
            tempo_atual (float): Tempo atual da simulação.
            fauna (dict, optional): Dicionário de fauna para referência.
            flora (dict, optional): Dicionário de flora para referência.
            
        Returns:
            dict: Análise do equilíbrio ecológico.
        """
        # Verificar se o cache está atualizado (recalcular a cada 24 horas simuladas)
        if tempo_atual - self.ultimo_calculo["equilibrio_ecologico"] >= 24.0:
            # Contagem de recursos por tipo
            recursos_por_tipo = {}
            for recurso in self.mundo.recursos.values():
                if recurso.tipo not in recursos_por_tipo:
                    recursos_por_tipo[recurso.tipo] = 0
                recursos_por_tipo[recurso.tipo] += recurso.quantidade
            
            # Análise de biomas
            biomas = {}
            for x in range(0, self.mundo.tamanho[0], 5):  # Amostragem a cada 5 unidades
                for y in range(0, self.mundo.tamanho[1], 5):
                    bioma = self.mundo.obter_bioma([x, y])
                    biomas[bioma] = biomas.get(bioma, 0) + 1
            
            # Normalizar contagem de biomas
            total_amostras = sum(biomas.values())
            distribuicao_biomas = {bioma: count / total_amostras for bioma, count in biomas.items()}
            
            # Análise de fauna (se fornecida)
            analise_fauna = {}
            if fauna:
                especies_fauna = {}
                for animal in fauna.values():
                    especies_fauna[animal.especie] = especies_fauna.get(animal.especie, 0) + 1
                
                # Calcular proporção de predadores vs. presas
                predadores = sum(especies_fauna.get(esp, 0) for esp in ["carnívoro_pequeno", "carnívoro_grande"])
                presas = sum(especies_fauna.get(esp, 0) for esp in ["herbívoro_pequeno", "herbívoro_grande", "onívoro"])
                
                if presas > 0:
                    razao_predador_presa = predadores / presas
                else:
                    razao_predador_presa = 0.0
                
                analise_fauna = {
                    "contagem_especies": especies_fauna,
                    "total_animais": len(fauna),
                    "razao_predador_presa": razao_predador_presa
                }
            
            # Análise de flora (se fornecida)
            analise_flora = {}
            if flora:
                especies_flora = {}
                for planta in flora.values():
                    especies_flora[planta.especie] = especies_flora.get(planta.especie, 0) + 1
                
                analise_flora = {
                    "contagem_especies": especies_flora,
                    "total_plantas": len(flora)
                }
            
            # Calcular índice de equilíbrio ecológico
            # Simplificação: baseado na diversidade de recursos e biomas
            diversidade_recursos = len(recursos_por_tipo)
            diversidade_biomas = len(biomas)
            
            indice_equilibrio = (diversidade_recursos / 10.0 + diversidade_biomas / 5.0) / 2.0
            indice_equilibrio = min(1.0, indice_equilibrio)
            
            # Atualizar cache
            self.cache_equilibrio_ecologico = {
                "indice_equilibrio": indice_equilibrio,
                "recursos_por_tipo": recursos_por_tipo,
                "distribuicao_biomas": distribuicao_biomas,
                "analise_fauna": analise_fauna,
                "analise_flora": analise_flora
            }
            
            self.ultimo_calculo["equilibrio_ecologico"] = tempo_atual
        
        return self.cache_equilibrio_ecologico
    
    def gerar_logs(self, tempo_inicio, tempo_fim):
        """
        Gera logs de eventos ocorridos em um período.
        
        Args:
            tempo_inicio (float): Tempo inicial do período.
            tempo_fim (float): Tempo final do período.
            
        Returns:
            list: Lista de eventos no período.
        """
        # Obter eventos do histórico
        eventos = self.mundo.historico.obter_eventos_por_periodo(tempo_inicio, tempo_fim)
        
        # Organizar por tipo
        eventos_por_tipo = {}
        for evento in eventos:
            tipo = evento["tipo"]
            if tipo not in eventos_por_tipo:
                eventos_por_tipo[tipo] = []
            eventos_por_tipo[tipo].append(evento)
        
        return {
            "eventos": eventos,
            "eventos_por_tipo": eventos_por_tipo,
            "total_eventos": len(eventos),
            "periodo": [tempo_inicio, tempo_fim]
        }
    
    def gerar_graficos(self, tipo, dados=None):
        """
        Gera dados para gráficos de análise.
        
        Args:
            tipo (str): Tipo de gráfico ("populacao", "recursos", "saude", "felicidade", "tecnologia").
            dados (dict, optional): Dados adicionais para o gráfico.
            
        Returns:
            dict: Dados para o gráfico.
        """
        if tipo == "populacao":
            # Dados de população ao longo do tempo
            return {
                "tipo": "linha",
                "titulo": "Evolução da População",
                "eixo_x": "Tempo (horas)",
                "eixo_y": "Número de Senciantes",
                "dados": self.mundo.historico.estatisticas["populacao"]
            }
        
        elif tipo == "recursos":
            # Dados de recursos ao longo do tempo
            return {
                "tipo": "linha",
                "titulo": "Evolução dos Recursos",
                "eixo_x": "Tempo (horas)",
                "eixo_y": "Quantidade",
                "dados": self.mundo.historico.estatisticas["recursos"]
            }
        
        elif tipo == "saude":
            # Distribuição de saúde atual
            saude = [s.estado["saude"] for s in self.senciantes.values()]
            
            return {
                "tipo": "histograma",
                "titulo": "Distribuição de Saúde",
                "eixo_x": "Nível de Saúde",
                "eixo_y": "Número de Senciantes",
                "dados": saude
            }
        
        elif tipo == "felicidade":
            # Distribuição de felicidade atual
            felicidade = [s.estado["felicidade"] for s in self.senciantes.values()]
            
            return {
                "tipo": "histograma",
                "titulo": "Distribuição de Felicidade",
                "eixo_x": "Nível de Felicidade",
                "eixo_y": "Número de Senciantes",
                "dados": felicidade
            }
        
        elif tipo == "tecnologia":
            # Evolução tecnológica ao longo do tempo
            return {
                "tipo": "dispersao",
                "titulo": "Evolução Tecnológica",
                "eixo_x": "Tempo (horas)",
                "eixo_y": "Tecnologia",
                "dados": self.mundo.historico.estatisticas["tecnologias"]
            }
        
        elif tipo == "personalizado" and dados:
            # Gráfico personalizado com dados fornecidos
            return dados
        
        else:
            return {"erro": "Tipo de gráfico não suportado"}
    
    def modo_debug_divino(self, opcoes=None):
        """
        Ativa o modo "debug divino" com opções específicas.
        
        Args:
            opcoes (dict, optional): Opções de debug.
            
        Returns:
            dict: Informações de debug.
        """
        resultado = {}
        
        # Opções padrão
        opcoes_padrao = {
            "redes_sociais": True,
            "sentimentos": True,
            "diversidade_genetica": True,
            "equilibrio_ecologico": True
        }
        
        # Usar opções fornecidas ou padrão
        opcoes_ativas = opcoes if opcoes else opcoes_padrao
        
        # Tempo atual (simplificado)
        tempo_atual = 0.0
        
        # Coletar informações solicitadas
        if opcoes_ativas.get("redes_sociais", False):
            resultado["redes_sociais"] = self.visualizar_redes_sociais(tempo_atual)
        
        if opcoes_ativas.get("sentimentos", False):
            resultado["sentimentos"] = self.visualizar_sentimentos()
        
        if opcoes_ativas.get("diversidade_genetica", False):
            resultado["diversidade_genetica"] = self.avaliar_diversidade_genetica(tempo_atual)
        
        if opcoes_ativas.get("equilibrio_ecologico", False):
            resultado["equilibrio_ecologico"] = self.avaliar_equilibrio_ecologico(tempo_atual)
        
        return resultado

