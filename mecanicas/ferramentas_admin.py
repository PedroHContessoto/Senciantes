"""
Implementação das ferramentas de administração e observação avançadas para o jogo "O Mundo dos Senciantes".
"""

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import json
import os
from datetime import datetime
import pandas as pd
from io import BytesIO
import base64

class FerramentasAdmin:
    """
    Classe que implementa as ferramentas de administração e observação avançadas.
    """
    
    def __init__(self, mundo, simulacao):
        """
        Inicializa as ferramentas de administração.
        
        Args:
            mundo (Mundo): Objeto mundo para referência.
            simulacao (Simulacao): Objeto simulação para referência.
        """
        self.mundo = mundo
        self.simulacao = simulacao
        self.diretorio_logs = "logs"
        self.diretorio_graficos = "graficos"
        
        # Criar diretórios se não existirem
        os.makedirs(self.diretorio_logs, exist_ok=True)
        os.makedirs(self.diretorio_graficos, exist_ok=True)
        
        # Inicializar histórico de métricas
        self.historico_metricas = {
            "tempo": [],
            "populacao_total": [],
            "media_saude": [],
            "media_felicidade": [],
            "media_estresse": [],
            "diversidade_genetica": [],
            "equilibrio_ecologico": [],
            "numero_grupos": [],
            "numero_conflitos": [],
            "numero_tratados": [],
            "numero_construcoes": [],
            "numero_tecnologias": [],
            "numero_doencas": []
        }
    
    def atualizar(self, tempo_atual, senciantes):
        """
        Atualiza as métricas e logs.
        
        Args:
            tempo_atual (float): Tempo atual da simulação em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Calcular métricas
        metricas = self._calcular_metricas(tempo_atual, senciantes)
        
        # Atualizar histórico de métricas
        for chave, valor in metricas.items():
            if chave in self.historico_metricas:
                self.historico_metricas[chave].append(valor)
        
        # Registrar logs a cada 24 horas (1 dia)
        if int(tempo_atual) % 24 == 0:
            self._registrar_logs(tempo_atual, metricas, senciantes)
    
    def _calcular_metricas(self, tempo_atual, senciantes):
        """
        Calcula métricas da simulação.
        
        Args:
            tempo_atual (float): Tempo atual da simulação em horas.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            dict: Dicionário com métricas calculadas.
        """
        # Inicializar métricas
        metricas = {
            "tempo": tempo_atual,
            "populacao_total": len(senciantes),
            "media_saude": 0.0,
            "media_felicidade": 0.0,
            "media_estresse": 0.0,
            "diversidade_genetica": 0.0,
            "equilibrio_ecologico": 0.0,
            "numero_grupos": 0,
            "numero_conflitos": 0,
            "numero_tratados": 0,
            "numero_construcoes": 0,
            "numero_tecnologias": 0,
            "numero_doencas": 0
        }
        
        # Calcular médias de estado
        if senciantes:
            soma_saude = sum(s.estado["saude"] for s in senciantes.values())
            soma_felicidade = sum(s.estado["felicidade"] for s in senciantes.values())
            soma_estresse = sum(s.estado["estresse"] for s in senciantes.values())
            
            metricas["media_saude"] = soma_saude / len(senciantes)
            metricas["media_felicidade"] = soma_felicidade / len(senciantes)
            metricas["media_estresse"] = soma_estresse / len(senciantes)
        
        # Calcular diversidade genética
        metricas["diversidade_genetica"] = self._calcular_diversidade_genetica(senciantes)
        
        # Calcular equilíbrio ecológico
        metricas["equilibrio_ecologico"] = self._calcular_equilibrio_ecologico()
        
        # Contar grupos
        metricas["numero_grupos"] = self._contar_grupos(senciantes)
        
        # Contar conflitos ativos
        metricas["numero_conflitos"] = self._contar_conflitos()
        
        # Contar tratados ativos
        metricas["numero_tratados"] = self._contar_tratados()
        
        # Contar construções
        metricas["numero_construcoes"] = self._contar_construcoes()
        
        # Contar tecnologias descobertas
        metricas["numero_tecnologias"] = self._contar_tecnologias()
        
        # Contar doenças ativas
        metricas["numero_doencas"] = self._contar_doencas()
        
        return metricas
    
    def _calcular_diversidade_genetica(self, senciantes):
        """
        Calcula a diversidade genética da população.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            float: Índice de diversidade genética (0.0 a 1.0).
        """
        if not senciantes:
            return 0.0
        
        # Coletar genes de todos os Senciantes
        todos_genes = []
        
        for senciante in senciantes.values():
            if hasattr(senciante, "genoma") and hasattr(senciante.genoma, "genes"):
                todos_genes.extend(list(senciante.genoma.genes.values()))
        
        if not todos_genes:
            return 0.0
        
        # Calcular variância dos genes
        variancia = np.var(todos_genes)
        
        # Normalizar para 0.0-1.0
        # Assumindo que a variância máxima teórica é 0.25 (para genes entre 0 e 1)
        diversidade = min(1.0, variancia * 4.0)
        
        return diversidade
    
    def _calcular_equilibrio_ecologico(self):
        """
        Calcula o equilíbrio ecológico do mundo.
        
        Returns:
            float: Índice de equilíbrio ecológico (0.0 a 1.0).
        """
        # Verificar se temos acesso ao ecossistema
        if not hasattr(self.simulacao, "mecanica_ecossistema"):
            return 0.5  # Valor padrão se não houver ecossistema
        
        ecossistema = self.simulacao.mecanica_ecossistema
        
        # Contar espécies de fauna e flora
        num_especies_fauna = len(ecossistema.fauna)
        num_especies_flora = len(ecossistema.flora)
        
        # Contar populações
        populacao_fauna = sum(fauna.populacao for fauna in ecossistema.fauna.values())
        populacao_flora = sum(flora.populacao for flora in ecossistema.flora.values())
        
        # Calcular proporção predadores/presas
        num_predadores = sum(1 for fauna in ecossistema.fauna.values() if fauna.predador)
        num_presas = num_especies_fauna - num_predadores
        
        if num_presas == 0:
            proporcao_predador_presa = 0.0
        else:
            proporcao_predador_presa = num_predadores / num_presas
        
        # Calcular equilíbrio ideal: proporção predador/presa entre 0.1 e 0.3
        if proporcao_predador_presa < 0.1:
            equilibrio_predador_presa = proporcao_predador_presa / 0.1
        elif proporcao_predador_presa > 0.3:
            equilibrio_predador_presa = 1.0 - min(1.0, (proporcao_predador_presa - 0.3) / 0.7)
        else:
            equilibrio_predador_presa = 1.0
        
        # Calcular equilíbrio fauna/flora (ideal: 1:5 a 1:10)
        if populacao_flora == 0:
            proporcao_fauna_flora = 0.0
        else:
            proporcao_fauna_flora = populacao_fauna / populacao_flora
        
        if proporcao_fauna_flora < 0.1:
            equilibrio_fauna_flora = proporcao_fauna_flora / 0.1
        elif proporcao_fauna_flora > 0.2:
            equilibrio_fauna_flora = 1.0 - min(1.0, (proporcao_fauna_flora - 0.2) / 0.8)
        else:
            equilibrio_fauna_flora = 1.0
        
        # Calcular diversidade de espécies
        diversidade_especies = min(1.0, (num_especies_fauna + num_especies_flora) / 30.0)
        
        # Calcular equilíbrio ecológico geral
        equilibrio = (equilibrio_predador_presa * 0.3 + 
                     equilibrio_fauna_flora * 0.3 + 
                     diversidade_especies * 0.4)
        
        return equilibrio
    
    def _contar_grupos(self, senciantes):
        """
        Conta o número de grupos sociais.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            int: Número de grupos.
        """
        # Verificar se temos acesso à mecânica social
        if not hasattr(self.simulacao, "mecanica_social"):
            return 0
        
        # Contar grupos
        return len(self.simulacao.mecanica_social.grupos)
    
    def _contar_conflitos(self):
        """
        Conta o número de conflitos ativos.
        
        Returns:
            int: Número de conflitos.
        """
        # Verificar se temos acesso à mecânica de conflito
        if not hasattr(self.simulacao, "mecanica_conflito"):
            return 0
        
        # Contar conflitos ativos
        return len([c for c in self.simulacao.mecanica_conflito.conflitos.values() if c["ativo"]])
    
    def _contar_tratados(self):
        """
        Conta o número de tratados ativos.
        
        Returns:
            int: Número de tratados.
        """
        # Verificar se temos acesso à mecânica de diplomacia
        if not hasattr(self.simulacao, "mecanica_diplomacia"):
            return 0
        
        # Contar tratados ativos
        return len([t for t in self.simulacao.mecanica_diplomacia.tratados.values() if t["ativo"]])
    
    def _contar_construcoes(self):
        """
        Conta o número de construções.
        
        Returns:
            int: Número de construções.
        """
        # Verificar se temos acesso às construções
        if not hasattr(self.mundo, "construcoes"):
            return 0
        
        # Contar construções
        return len(self.mundo.construcoes)
    
    def _contar_tecnologias(self):
        """
        Conta o número de tecnologias descobertas.
        
        Returns:
            int: Número de tecnologias.
        """
        # Verificar se temos acesso à mecânica de tecnologia
        if not hasattr(self.simulacao, "mecanica_tecnologia"):
            return 0
        
        # Contar tecnologias descobertas
        return len(self.simulacao.mecanica_tecnologia.tecnologias_descobertas)
    
    def _contar_doencas(self):
        """
        Conta o número de doenças ativas.
        
        Returns:
            int: Número de doenças.
        """
        # Verificar se temos acesso à mecânica de doença
        if not hasattr(self.simulacao, "mecanica_doenca"):
            return 0
        
        # Contar doenças ativas
        return len([d for d in self.simulacao.mecanica_doenca.doencas.values() if d["ativa"]])
    
    def _registrar_logs(self, tempo_atual, metricas, senciantes):
        """
        Registra logs da simulação.
        
        Args:
            tempo_atual (float): Tempo atual da simulação em horas.
            metricas (dict): Métricas calculadas.
            senciantes (dict): Dicionário de Senciantes para referência.
        """
        # Formatar tempo
        dia = int(tempo_atual / 24) + 1
        hora = int(tempo_atual % 24)
        
        # Criar nome do arquivo de log
        nome_arquivo = f"{self.diretorio_logs}/log_dia_{dia:03d}_hora_{hora:02d}.json"
        
        # Criar log
        log = {
            "tempo": {
                "valor": tempo_atual,
                "dia": dia,
                "hora": hora
            },
            "metricas": metricas,
            "eventos_recentes": self._obter_eventos_recentes(10),
            "resumo_senciantes": self._criar_resumo_senciantes(senciantes)
        }
        
        # Salvar log
        with open(nome_arquivo, "w") as arquivo:
            json.dump(log, arquivo, indent=2)
    
    def _obter_eventos_recentes(self, limite=10):
        """
        Obtém os eventos mais recentes do histórico.
        
        Args:
            limite (int, optional): Número máximo de eventos. Defaults to 10.
            
        Returns:
            list: Lista de eventos recentes.
        """
        # Verificar se temos acesso ao histórico
        if not hasattr(self.mundo, "historico"):
            return []
        
        # Obter eventos recentes
        eventos = self.mundo.historico.eventos[-limite:] if self.mundo.historico.eventos else []
        
        return eventos
    
    def _criar_resumo_senciantes(self, senciantes):
        """
        Cria um resumo dos Senciantes.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            dict: Resumo dos Senciantes.
        """
        resumo = {
            "total": len(senciantes),
            "distribuicao_idade": self._calcular_distribuicao_idade(senciantes),
            "distribuicao_genero": self._calcular_distribuicao_genero(senciantes),
            "distribuicao_saude": self._calcular_distribuicao_estado(senciantes, "saude"),
            "distribuicao_felicidade": self._calcular_distribuicao_estado(senciantes, "felicidade"),
            "distribuicao_estresse": self._calcular_distribuicao_estado(senciantes, "estresse"),
            "top_habilidades": self._calcular_top_habilidades(senciantes, 5)
        }
        
        return resumo
    
    def _calcular_distribuicao_idade(self, senciantes):
        """
        Calcula a distribuição de idade dos Senciantes.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            dict: Distribuição de idade.
        """
        # Inicializar faixas etárias
        faixas = {
            "jovem": 0,
            "adulto": 0,
            "idoso": 0
        }
        
        # Contar Senciantes por faixa etária
        for senciante in senciantes.values():
            idade = senciante.idade
            
            if idade < 24:  # Menos de 1 dia
                faixas["jovem"] += 1
            elif idade < 36:  # Entre 1 e 1.5 dias
                faixas["adulto"] += 1
            else:  # Mais de 1.5 dias
                faixas["idoso"] += 1
        
        return faixas
    
    def _calcular_distribuicao_genero(self, senciantes):
        """
        Calcula a distribuição de gênero dos Senciantes.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            dict: Distribuição de gênero.
        """
        # Inicializar contagem
        generos = {}
        
        # Contar Senciantes por gênero
        for senciante in senciantes.values():
            genero = senciante.genero
            
            if genero not in generos:
                generos[genero] = 0
            
            generos[genero] += 1
        
        return generos
    
    def _calcular_distribuicao_estado(self, senciantes, estado):
        """
        Calcula a distribuição de um estado dos Senciantes.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            estado (str): Nome do estado a calcular.
            
        Returns:
            dict: Distribuição do estado.
        """
        # Inicializar faixas
        faixas = {
            "baixo": 0,
            "medio": 0,
            "alto": 0
        }
        
        # Contar Senciantes por faixa
        for senciante in senciantes.values():
            valor = senciante.estado[estado]
            
            if valor < 0.33:
                faixas["baixo"] += 1
            elif valor < 0.66:
                faixas["medio"] += 1
            else:
                faixas["alto"] += 1
        
        return faixas
    
    def _calcular_top_habilidades(self, senciantes, limite=5):
        """
        Calcula as habilidades mais comuns entre os Senciantes.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            limite (int, optional): Número máximo de habilidades. Defaults to 5.
            
        Returns:
            list: Lista de tuplas (habilidade, contagem).
        """
        # Inicializar contagem
        contagem = {}
        
        # Contar habilidades
        for senciante in senciantes.values():
            if hasattr(senciante, "habilidades"):
                for habilidade in senciante.habilidades:
                    if habilidade not in contagem:
                        contagem[habilidade] = 0
                    
                    contagem[habilidade] += 1
        
        # Ordenar por contagem
        top_habilidades = sorted(contagem.items(), key=lambda x: x[1], reverse=True)[:limite]
        
        return top_habilidades
    
    def gerar_grafico_populacao(self):
        """
        Gera um gráfico da evolução da população.
        
        Returns:
            str: Caminho para o arquivo de gráfico gerado.
        """
        # Verificar se temos dados suficientes
        if len(self.historico_metricas["tempo"]) < 2:
            return None
        
        # Converter tempo para dias
        dias = [t / 24 for t in self.historico_metricas["tempo"]]
        
        # Criar figura
        plt.figure(figsize=(10, 6))
        plt.plot(dias, self.historico_metricas["populacao_total"], 'b-', linewidth=2)
        plt.title("Evolução da População")
        plt.xlabel("Dias")
        plt.ylabel("Número de Senciantes")
        plt.grid(True)
        
        # Salvar figura
        caminho = f"{self.diretorio_graficos}/populacao_{int(dias[-1])}.png"
        plt.savefig(caminho)
        plt.close()
        
        return caminho
    
    def gerar_grafico_estados(self):
        """
        Gera um gráfico da evolução dos estados médios.
        
        Returns:
            str: Caminho para o arquivo de gráfico gerado.
        """
        # Verificar se temos dados suficientes
        if len(self.historico_metricas["tempo"]) < 2:
            return None
        
        # Converter tempo para dias
        dias = [t / 24 for t in self.historico_metricas["tempo"]]
        
        # Criar figura
        plt.figure(figsize=(10, 6))
        plt.plot(dias, self.historico_metricas["media_saude"], 'g-', linewidth=2, label="Saúde")
        plt.plot(dias, self.historico_metricas["media_felicidade"], 'b-', linewidth=2, label="Felicidade")
        plt.plot(dias, self.historico_metricas["media_estresse"], 'r-', linewidth=2, label="Estresse")
        plt.title("Evolução dos Estados Médios")
        plt.xlabel("Dias")
        plt.ylabel("Valor Médio")
        plt.legend()
        plt.grid(True)
        plt.ylim(0, 1)
        
        # Salvar figura
        caminho = f"{self.diretorio_graficos}/estados_{int(dias[-1])}.png"
        plt.savefig(caminho)
        plt.close()
        
        return caminho
    
    def gerar_grafico_equilibrio(self):
        """
        Gera um gráfico da evolução do equilíbrio ecológico e diversidade genética.
        
        Returns:
            str: Caminho para o arquivo de gráfico gerado.
        """
        # Verificar se temos dados suficientes
        if len(self.historico_metricas["tempo"]) < 2:
            return None
        
        # Converter tempo para dias
        dias = [t / 24 for t in self.historico_metricas["tempo"]]
        
        # Criar figura
        plt.figure(figsize=(10, 6))
        plt.plot(dias, self.historico_metricas["equilibrio_ecologico"], 'g-', linewidth=2, label="Equilíbrio Ecológico")
        plt.plot(dias, self.historico_metricas["diversidade_genetica"], 'b-', linewidth=2, label="Diversidade Genética")
        plt.title("Evolução do Equilíbrio Ecológico e Diversidade Genética")
        plt.xlabel("Dias")
        plt.ylabel("Valor")
        plt.legend()
        plt.grid(True)
        plt.ylim(0, 1)
        
        # Salvar figura
        caminho = f"{self.diretorio_graficos}/equilibrio_{int(dias[-1])}.png"
        plt.savefig(caminho)
        plt.close()
        
        return caminho
    
    def gerar_grafico_social(self):
        """
        Gera um gráfico da evolução de grupos, conflitos e tratados.
        
        Returns:
            str: Caminho para o arquivo de gráfico gerado.
        """
        # Verificar se temos dados suficientes
        if len(self.historico_metricas["tempo"]) < 2:
            return None
        
        # Converter tempo para dias
        dias = [t / 24 for t in self.historico_metricas["tempo"]]
        
        # Criar figura
        plt.figure(figsize=(10, 6))
        plt.plot(dias, self.historico_metricas["numero_grupos"], 'b-', linewidth=2, label="Grupos")
        plt.plot(dias, self.historico_metricas["numero_conflitos"], 'r-', linewidth=2, label="Conflitos")
        plt.plot(dias, self.historico_metricas["numero_tratados"], 'g-', linewidth=2, label="Tratados")
        plt.title("Evolução Social")
        plt.xlabel("Dias")
        plt.ylabel("Quantidade")
        plt.legend()
        plt.grid(True)
        
        # Salvar figura
        caminho = f"{self.diretorio_graficos}/social_{int(dias[-1])}.png"
        plt.savefig(caminho)
        plt.close()
        
        return caminho
    
    def gerar_grafico_tecnologia(self):
        """
        Gera um gráfico da evolução de tecnologias e construções.
        
        Returns:
            str: Caminho para o arquivo de gráfico gerado.
        """
        # Verificar se temos dados suficientes
        if len(self.historico_metricas["tempo"]) < 2:
            return None
        
        # Converter tempo para dias
        dias = [t / 24 for t in self.historico_metricas["tempo"]]
        
        # Criar figura
        plt.figure(figsize=(10, 6))
        plt.plot(dias, self.historico_metricas["numero_tecnologias"], 'b-', linewidth=2, label="Tecnologias")
        plt.plot(dias, self.historico_metricas["numero_construcoes"], 'g-', linewidth=2, label="Construções")
        plt.title("Evolução Tecnológica")
        plt.xlabel("Dias")
        plt.ylabel("Quantidade")
        plt.legend()
        plt.grid(True)
        
        # Salvar figura
        caminho = f"{self.diretorio_graficos}/tecnologia_{int(dias[-1])}.png"
        plt.savefig(caminho)
        plt.close()
        
        return caminho
    
    def gerar_grafico_doencas(self):
        """
        Gera um gráfico da evolução de doenças.
        
        Returns:
            str: Caminho para o arquivo de gráfico gerado.
        """
        # Verificar se temos dados suficientes
        if len(self.historico_metricas["tempo"]) < 2:
            return None
        
        # Converter tempo para dias
        dias = [t / 24 for t in self.historico_metricas["tempo"]]
        
        # Criar figura
        plt.figure(figsize=(10, 6))
        plt.plot(dias, self.historico_metricas["numero_doencas"], 'r-', linewidth=2)
        plt.title("Evolução de Doenças")
        plt.xlabel("Dias")
        plt.ylabel("Número de Doenças Ativas")
        plt.grid(True)
        
        # Salvar figura
        caminho = f"{self.diretorio_graficos}/doencas_{int(dias[-1])}.png"
        plt.savefig(caminho)
        plt.close()
        
        return caminho
    
    def gerar_rede_social(self, senciantes):
        """
        Gera um gráfico da rede social entre Senciantes.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: Caminho para o arquivo de gráfico gerado.
        """
        # Verificar se temos Senciantes suficientes
        if len(senciantes) < 2:
            return None
        
        # Criar grafo
        G = nx.Graph()
        
        # Adicionar nós (Senciantes)
        for senciante_id, senciante in senciantes.items():
            G.add_node(senciante_id, nome=senciante.nome)
        
        # Adicionar arestas (relações)
        for senciante_id, senciante in senciantes.items():
            if hasattr(senciante, "relacoes"):
                for outro_id, relacao in senciante.relacoes.items():
                    if outro_id in senciantes:
                        # Adicionar aresta com peso baseado na afinidade
                        G.add_edge(senciante_id, outro_id, weight=relacao["afinidade"])
        
        # Verificar se temos arestas
        if not G.edges():
            return None
        
        # Criar figura
        plt.figure(figsize=(12, 12))
        
        # Calcular posições dos nós
        pos = nx.spring_layout(G, seed=42)
        
        # Obter pesos das arestas
        edge_weights = [G[u][v]["weight"] * 5 for u, v in G.edges()]
        
        # Desenhar grafo
        nx.draw_networkx_nodes(G, pos, node_size=300, node_color="skyblue")
        nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.7, edge_color="gray")
        nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
        
        plt.title("Rede Social dos Senciantes")
        plt.axis("off")
        
        # Salvar figura
        caminho = f"{self.diretorio_graficos}/rede_social_{int(self.historico_metricas['tempo'][-1] / 24)}.png"
        plt.savefig(caminho)
        plt.close()
        
        return caminho
    
    def gerar_mapa_calor_sentimentos(self, senciantes):
        """
        Gera um mapa de calor dos sentimentos dos Senciantes no mundo.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: Caminho para o arquivo de gráfico gerado.
        """
        # Verificar se temos Senciantes suficientes
        if len(senciantes) < 2:
            return None
        
        # Obter tamanho do mundo
        tamanho_x, tamanho_y = self.mundo.tamanho
        
        # Criar grade para o mapa de calor
        resolucao = 20
        grade_x = np.linspace(0, tamanho_x, resolucao)
        grade_y = np.linspace(0, tamanho_y, resolucao)
        
        # Inicializar mapas de calor
        mapa_felicidade = np.zeros((resolucao, resolucao))
        mapa_estresse = np.zeros((resolucao, resolucao))
        
        # Preencher mapas de calor
        for senciante in senciantes.values():
            # Encontrar célula da grade
            x, y = senciante.posicao
            
            # Converter para índices da grade
            i = min(resolucao - 1, max(0, int(x / tamanho_x * resolucao)))
            j = min(resolucao - 1, max(0, int(y / tamanho_y * resolucao)))
            
            # Adicionar valores
            mapa_felicidade[j, i] += senciante.estado["felicidade"]
            mapa_estresse[j, i] += senciante.estado["estresse"]
        
        # Normalizar mapas
        for i in range(resolucao):
            for j in range(resolucao):
                if mapa_felicidade[j, i] > 0:
                    mapa_felicidade[j, i] = min(1.0, mapa_felicidade[j, i])
                if mapa_estresse[j, i] > 0:
                    mapa_estresse[j, i] = min(1.0, mapa_estresse[j, i])
        
        # Criar figura
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Mapa de calor de felicidade
        im1 = ax1.imshow(mapa_felicidade, cmap="YlGn", interpolation="bilinear", origin="lower",
                        extent=[0, tamanho_x, 0, tamanho_y])
        ax1.set_title("Mapa de Felicidade")
        ax1.set_xlabel("X")
        ax1.set_ylabel("Y")
        fig.colorbar(im1, ax=ax1, label="Nível de Felicidade")
        
        # Mapa de calor de estresse
        im2 = ax2.imshow(mapa_estresse, cmap="YlOrRd", interpolation="bilinear", origin="lower",
                        extent=[0, tamanho_x, 0, tamanho_y])
        ax2.set_title("Mapa de Estresse")
        ax2.set_xlabel("X")
        ax2.set_ylabel("Y")
        fig.colorbar(im2, ax=ax2, label="Nível de Estresse")
        
        # Adicionar posições dos Senciantes
        for senciante in senciantes.values():
            x, y = senciante.posicao
            ax1.plot(x, y, 'bo', markersize=3, alpha=0.5)
            ax2.plot(x, y, 'bo', markersize=3, alpha=0.5)
        
        plt.tight_layout()
        
        # Salvar figura
        caminho = f"{self.diretorio_graficos}/mapa_sentimentos_{int(self.historico_metricas['tempo'][-1] / 24)}.png"
        plt.savefig(caminho)
        plt.close()
        
        return caminho
    
    def gerar_mapa_recursos(self):
        """
        Gera um mapa dos recursos no mundo.
        
        Returns:
            str: Caminho para o arquivo de gráfico gerado.
        """
        # Obter tamanho do mundo
        tamanho_x, tamanho_y = self.mundo.tamanho
        
        # Criar figura
        plt.figure(figsize=(12, 10))
        
        # Desenhar recursos
        if hasattr(self.mundo, "recursos"):
            for recurso_id, recurso in self.mundo.recursos.items():
                x, y = recurso.posicao
                plt.plot(x, y, 'go', markersize=8, alpha=0.7)
                plt.text(x, y, recurso.tipo, fontsize=8)
        
        # Desenhar construções
        if hasattr(self.mundo, "construcoes"):
            for construcao_id, construcao in self.mundo.construcoes.items():
                x, y = construcao.posicao
                plt.plot(x, y, 'rs', markersize=8, alpha=0.7)
                plt.text(x, y, construcao.tipo, fontsize=8)
        
        # Configurar gráfico
        plt.title("Mapa de Recursos e Construções")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.xlim(0, tamanho_x)
        plt.ylim(0, tamanho_y)
        plt.grid(True)
        
        # Adicionar legenda
        plt.plot([], [], 'go', markersize=8, label="Recurso")
        plt.plot([], [], 'rs', markersize=8, label="Construção")
        plt.legend()
        
        # Salvar figura
        caminho = f"{self.diretorio_graficos}/mapa_recursos_{int(self.historico_metricas['tempo'][-1] / 24)}.png"
        plt.savefig(caminho)
        plt.close()
        
        return caminho
    
    def gerar_mapa_ecossistema(self):
        """
        Gera um mapa do ecossistema no mundo.
        
        Returns:
            str: Caminho para o arquivo de gráfico gerado.
        """
        # Verificar se temos acesso ao ecossistema
        if not hasattr(self.simulacao, "mecanica_ecossistema"):
            return None
        
        ecossistema = self.simulacao.mecanica_ecossistema
        
        # Obter tamanho do mundo
        tamanho_x, tamanho_y = self.mundo.tamanho
        
        # Criar figura
        plt.figure(figsize=(12, 10))
        
        # Desenhar grupos de fauna
        for fauna_id, fauna in ecossistema.fauna.items():
            if hasattr(fauna, "grupos"):
                for grupo in fauna.grupos:
                    x, y = grupo["posicao"]
                    
                    # Cor baseada no tipo
                    if "carnivoro" in fauna.tipo:
                        cor = 'r'
                    elif "herbivoro" in fauna.tipo:
                        cor = 'g'
                    else:
                        cor = 'b'
                    
                    # Tamanho baseado no tamanho do grupo
                    tamanho = min(20, max(5, grupo["tamanho"] / 5))
                    
                    plt.plot(x, y, cor+'o', markersize=tamanho, alpha=0.7)
        
        # Desenhar grupos de flora
        for flora_id, flora in ecossistema.flora.items():
            if hasattr(flora, "grupos"):
                for grupo in flora.grupos:
                    x, y = grupo["posicao"]
                    
                    # Cor baseada no tipo
                    if "frutifera" in flora.tipo or "frutas" in flora.tipo:
                        cor = 'm'
                    elif flora.tipo == "planta_medicinal":
                        cor = 'c'
                    else:
                        cor = 'g'
                    
                    # Tamanho baseado no tamanho do grupo
                    tamanho = min(15, max(3, grupo["tamanho"] / 10))
                    
                    plt.plot(x, y, cor+'^', markersize=tamanho, alpha=0.5)
        
        # Configurar gráfico
        plt.title("Mapa do Ecossistema")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.xlim(0, tamanho_x)
        plt.ylim(0, tamanho_y)
        plt.grid(True)
        
        # Adicionar legenda
        plt.plot([], [], 'ro', markersize=8, label="Carnívoros")
        plt.plot([], [], 'go', markersize=8, label="Herbívoros")
        plt.plot([], [], 'bo', markersize=8, label="Onívoros")
        plt.plot([], [], 'm^', markersize=8, label="Plantas Frutíferas")
        plt.plot([], [], 'c^', markersize=8, label="Plantas Medicinais")
        plt.plot([], [], 'g^', markersize=8, label="Outras Plantas")
        plt.legend()
        
        # Salvar figura
        caminho = f"{self.diretorio_graficos}/mapa_ecossistema_{int(self.historico_metricas['tempo'][-1] / 24)}.png"
        plt.savefig(caminho)
        plt.close()
        
        return caminho
    
    def gerar_relatorio_completo(self, senciantes):
        """
        Gera um relatório completo da simulação.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: Caminho para o arquivo de relatório gerado.
        """
        # Verificar se temos dados suficientes
        if len(self.historico_metricas["tempo"]) < 2:
            return None
        
        # Criar diretório para relatório
        diretorio_relatorio = f"{self.diretorio_graficos}/relatorio_{int(self.historico_metricas['tempo'][-1] / 24)}"
        os.makedirs(diretorio_relatorio, exist_ok=True)
        
        # Gerar gráficos
        graficos = {
            "populacao": self.gerar_grafico_populacao(),
            "estados": self.gerar_grafico_estados(),
            "equilibrio": self.gerar_grafico_equilibrio(),
            "social": self.gerar_grafico_social(),
            "tecnologia": self.gerar_grafico_tecnologia(),
            "doencas": self.gerar_grafico_doencas(),
            "rede_social": self.gerar_rede_social(senciantes),
            "mapa_sentimentos": self.gerar_mapa_calor_sentimentos(senciantes),
            "mapa_recursos": self.gerar_mapa_recursos(),
            "mapa_ecossistema": self.gerar_mapa_ecossistema()
        }
        
        # Criar HTML do relatório
        html = self._criar_html_relatorio(graficos, senciantes)
        
        # Salvar HTML
        caminho_html = f"{diretorio_relatorio}/relatorio.html"
        with open(caminho_html, "w") as arquivo:
            arquivo.write(html)
        
        return caminho_html
    
    def _criar_html_relatorio(self, graficos, senciantes):
        """
        Cria o HTML do relatório.
        
        Args:
            graficos (dict): Dicionário com caminhos para os gráficos.
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: HTML do relatório.
        """
        # Obter tempo atual
        tempo_atual = self.historico_metricas["tempo"][-1]
        dia = int(tempo_atual / 24) + 1
        hora = int(tempo_atual % 24)
        
        # Criar HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Relatório da Simulação - Dia {dia}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .container {{ display: flex; flex-wrap: wrap; }}
                .graph {{ margin: 10px; border: 1px solid #ddd; padding: 10px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h1>Relatório da Simulação - O Mundo dos Senciantes</h1>
            <p><strong>Dia:</strong> {dia} | <strong>Hora:</strong> {hora}</p>
            
            <h2>Resumo</h2>
            <table>
                <tr>
                    <th>Métrica</th>
                    <th>Valor</th>
                </tr>
                <tr>
                    <td>População Total</td>
                    <td>{self.historico_metricas["populacao_total"][-1]}</td>
                </tr>
                <tr>
                    <td>Saúde Média</td>
                    <td>{self.historico_metricas["media_saude"][-1]:.2f}</td>
                </tr>
                <tr>
                    <td>Felicidade Média</td>
                    <td>{self.historico_metricas["media_felicidade"][-1]:.2f}</td>
                </tr>
                <tr>
                    <td>Estresse Médio</td>
                    <td>{self.historico_metricas["media_estresse"][-1]:.2f}</td>
                </tr>
                <tr>
                    <td>Diversidade Genética</td>
                    <td>{self.historico_metricas["diversidade_genetica"][-1]:.2f}</td>
                </tr>
                <tr>
                    <td>Equilíbrio Ecológico</td>
                    <td>{self.historico_metricas["equilibrio_ecologico"][-1]:.2f}</td>
                </tr>
                <tr>
                    <td>Número de Grupos</td>
                    <td>{self.historico_metricas["numero_grupos"][-1]}</td>
                </tr>
                <tr>
                    <td>Conflitos Ativos</td>
                    <td>{self.historico_metricas["numero_conflitos"][-1]}</td>
                </tr>
                <tr>
                    <td>Tratados Ativos</td>
                    <td>{self.historico_metricas["numero_tratados"][-1]}</td>
                </tr>
                <tr>
                    <td>Construções</td>
                    <td>{self.historico_metricas["numero_construcoes"][-1]}</td>
                </tr>
                <tr>
                    <td>Tecnologias Descobertas</td>
                    <td>{self.historico_metricas["numero_tecnologias"][-1]}</td>
                </tr>
                <tr>
                    <td>Doenças Ativas</td>
                    <td>{self.historico_metricas["numero_doencas"][-1]}</td>
                </tr>
            </table>
            
            <h2>Gráficos</h2>
            <div class="container">
        """
        
        # Adicionar gráficos
        for nome, caminho in graficos.items():
            if caminho:
                html += f"""
                <div class="graph">
                    <h3>{nome.replace('_', ' ').title()}</h3>
                    <img src="{caminho}" alt="{nome}" style="max-width: 100%;">
                </div>
                """
        
        html += """
            </div>
            
            <h2>Eventos Recentes</h2>
            <table>
                <tr>
                    <th>Tipo</th>
                    <th>Descrição</th>
                    <th>Tempo</th>
                </tr>
        """
        
        # Adicionar eventos recentes
        eventos = self._obter_eventos_recentes(10)
        for evento in eventos:
            html += f"""
                <tr>
                    <td>{evento["tipo"]}</td>
                    <td>{evento["descricao"]}</td>
                    <td>{evento["tempo"]:.1f}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>Top Senciantes</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Nome</th>
                    <th>Idade</th>
                    <th>Saúde</th>
                    <th>Felicidade</th>
                    <th>Estresse</th>
                    <th>Habilidades</th>
                </tr>
        """
        
        # Adicionar top Senciantes (por saúde)
        top_senciantes = sorted(senciantes.values(), key=lambda s: s.estado["saude"], reverse=True)[:10]
        for senciante in top_senciantes:
            # Formatar habilidades
            if hasattr(senciante, "habilidades"):
                habilidades = ", ".join([f"{h}: {v:.2f}" for h, v in senciante.habilidades.items()])
            else:
                habilidades = "Nenhuma"
            
            html += f"""
                <tr>
                    <td>{senciante.id}</td>
                    <td>{senciante.nome}</td>
                    <td>{senciante.idade:.1f}</td>
                    <td>{senciante.estado["saude"]:.2f}</td>
                    <td>{senciante.estado["felicidade"]:.2f}</td>
                    <td>{senciante.estado["estresse"]:.2f}</td>
                    <td>{habilidades}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return html
    
    def visualizar_rede_influencia_social(self, senciantes):
        """
        Visualiza a rede de influência social entre Senciantes.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: Base64 da imagem gerada.
        """
        # Verificar se temos Senciantes suficientes
        if len(senciantes) < 2:
            return None
        
        # Criar grafo direcionado
        G = nx.DiGraph()
        
        # Adicionar nós (Senciantes)
        for senciante_id, senciante in senciantes.items():
            # Calcular influência baseada em carisma e habilidades sociais
            influencia = 0.5
            if hasattr(senciante, "genoma") and hasattr(senciante.genoma, "genes"):
                if "carisma" in senciante.genoma.genes:
                    influencia = senciante.genoma.genes["carisma"]
            
            if hasattr(senciante, "habilidades"):
                if "comunicacao" in senciante.habilidades:
                    influencia = max(influencia, senciante.habilidades["comunicacao"])
                if "lideranca" in senciante.habilidades:
                    influencia = max(influencia, senciante.habilidades["lideranca"])
            
            G.add_node(senciante_id, nome=senciante.nome, influencia=influencia)
        
        # Adicionar arestas (influências)
        for senciante_id, senciante in senciantes.items():
            if hasattr(senciante, "relacoes"):
                for outro_id, relacao in senciante.relacoes.items():
                    if outro_id in senciantes:
                        # Calcular influência
                        influencia = relacao.get("influencia", 0.0)
                        if influencia > 0.1:  # Apenas influências significativas
                            G.add_edge(senciante_id, outro_id, weight=influencia)
        
        # Verificar se temos arestas
        if not G.edges():
            return None
        
        # Criar figura
        plt.figure(figsize=(12, 12))
        
        # Calcular posições dos nós
        pos = nx.spring_layout(G, seed=42)
        
        # Calcular tamanhos dos nós baseados na influência
        node_sizes = [G.nodes[n]["influencia"] * 1000 for n in G.nodes()]
        
        # Calcular larguras das arestas baseadas no peso
        edge_widths = [G[u][v]["weight"] * 5 for u, v in G.edges()]
        
        # Desenhar grafo
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="skyblue", alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.6, edge_color="gray", 
                              arrowsize=15, connectionstyle="arc3,rad=0.1")
        nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
        
        plt.title("Rede de Influência Social")
        plt.axis("off")
        
        # Salvar em buffer
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        
        # Converter para base64
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_base64
    
    def visualizar_sentimentos_tempo_real(self, senciantes):
        """
        Visualiza os sentimentos dos Senciantes em tempo real.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            str: Base64 da imagem gerada.
        """
        # Verificar se temos Senciantes suficientes
        if len(senciantes) < 1:
            return None
        
        # Criar figura
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Preparar dados
        nomes = []
        saude = []
        felicidade = []
        estresse = []
        
        # Limitar a 20 Senciantes para melhor visualização
        for senciante in list(senciantes.values())[:20]:
            nomes.append(senciante.nome)
            saude.append(senciante.estado["saude"])
            felicidade.append(senciante.estado["felicidade"])
            estresse.append(senciante.estado["estresse"])
        
        # Gráfico de barras para saúde e felicidade
        x = range(len(nomes))
        width = 0.35
        
        ax1.bar(x, saude, width, label="Saúde", color="green")
        ax1.bar([i + width for i in x], felicidade, width, label="Felicidade", color="blue")
        
        ax1.set_ylabel("Valor")
        ax1.set_title("Saúde e Felicidade dos Senciantes")
        ax1.set_xticks([i + width/2 for i in x])
        ax1.set_xticklabels(nomes, rotation=45, ha="right")
        ax1.legend()
        ax1.set_ylim(0, 1)
        
        # Gráfico de barras para estresse
        ax2.bar(x, estresse, color="red")
        
        ax2.set_ylabel("Valor")
        ax2.set_title("Estresse dos Senciantes")
        ax2.set_xticks(x)
        ax2.set_xticklabels(nomes, rotation=45, ha="right")
        ax2.set_ylim(0, 1)
        
        plt.tight_layout()
        
        # Salvar em buffer
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        
        # Converter para base64
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        
        return img_base64
    
    def avaliar_equilibrio_ecologico(self):
        """
        Avalia o equilíbrio ecológico do mundo em detalhes.
        
        Returns:
            dict: Avaliação detalhada do equilíbrio ecológico.
        """
        # Verificar se temos acesso ao ecossistema
        if not hasattr(self.simulacao, "mecanica_ecossistema"):
            return {
                "equilibrio_geral": 0.5,
                "detalhes": "Ecossistema não disponível"
            }
        
        ecossistema = self.simulacao.mecanica_ecossistema
        
        # Contar espécies de fauna e flora
        num_especies_fauna = len(ecossistema.fauna)
        num_especies_flora = len(ecossistema.flora)
        
        # Contar populações
        populacao_fauna = sum(fauna.populacao for fauna in ecossistema.fauna.values())
        populacao_flora = sum(flora.populacao for flora in ecossistema.flora.values())
        
        # Calcular proporção predadores/presas
        num_predadores = sum(1 for fauna in ecossistema.fauna.values() if fauna.predador)
        num_presas = num_especies_fauna - num_predadores
        
        if num_presas == 0:
            proporcao_predador_presa = 0.0
        else:
            proporcao_predador_presa = num_predadores / num_presas
        
        # Calcular proporção fauna/flora
        if populacao_flora == 0:
            proporcao_fauna_flora = 0.0
        else:
            proporcao_fauna_flora = populacao_fauna / populacao_flora
        
        # Calcular diversidade de espécies
        diversidade_especies = (num_especies_fauna + num_especies_flora) / 30.0
        
        # Calcular equilíbrio predador/presa
        if proporcao_predador_presa < 0.1:
            equilibrio_predador_presa = proporcao_predador_presa / 0.1
            status_predador_presa = "Poucos predadores"
        elif proporcao_predador_presa > 0.3:
            equilibrio_predador_presa = 1.0 - min(1.0, (proporcao_predador_presa - 0.3) / 0.7)
            status_predador_presa = "Muitos predadores"
        else:
            equilibrio_predador_presa = 1.0
            status_predador_presa = "Equilibrado"
        
        # Calcular equilíbrio fauna/flora
        if proporcao_fauna_flora < 0.1:
            equilibrio_fauna_flora = proporcao_fauna_flora / 0.1
            status_fauna_flora = "Pouca fauna"
        elif proporcao_fauna_flora > 0.2:
            equilibrio_fauna_flora = 1.0 - min(1.0, (proporcao_fauna_flora - 0.2) / 0.8)
            status_fauna_flora = "Muita fauna"
        else:
            equilibrio_fauna_flora = 1.0
            status_fauna_flora = "Equilibrado"
        
        # Calcular equilíbrio ecológico geral
        equilibrio = (equilibrio_predador_presa * 0.3 + 
                     equilibrio_fauna_flora * 0.3 + 
                     min(1.0, diversidade_especies) * 0.4)
        
        # Determinar status geral
        if equilibrio < 0.33:
            status_geral = "Desequilibrado"
        elif equilibrio < 0.66:
            status_geral = "Parcialmente equilibrado"
        else:
            status_geral = "Bem equilibrado"
        
        # Criar avaliação detalhada
        avaliacao = {
            "equilibrio_geral": equilibrio,
            "status_geral": status_geral,
            "detalhes": {
                "especies_fauna": num_especies_fauna,
                "especies_flora": num_especies_flora,
                "populacao_fauna": populacao_fauna,
                "populacao_flora": populacao_flora,
                "predadores": num_predadores,
                "presas": num_presas,
                "proporcao_predador_presa": proporcao_predador_presa,
                "status_predador_presa": status_predador_presa,
                "proporcao_fauna_flora": proporcao_fauna_flora,
                "status_fauna_flora": status_fauna_flora,
                "diversidade_especies": diversidade_especies
            },
            "recomendacoes": []
        }
        
        # Adicionar recomendações
        if proporcao_predador_presa < 0.1:
            avaliacao["recomendacoes"].append("Introduzir mais predadores para controlar a população de presas")
        elif proporcao_predador_presa > 0.3:
            avaliacao["recomendacoes"].append("Reduzir o número de predadores ou introduzir mais presas")
        
        if proporcao_fauna_flora < 0.1:
            avaliacao["recomendacoes"].append("Introduzir mais fauna para equilibrar o ecossistema")
        elif proporcao_fauna_flora > 0.2:
            avaliacao["recomendacoes"].append("Introduzir mais flora para sustentar a fauna existente")
        
        if diversidade_especies < 0.5:
            avaliacao["recomendacoes"].append("Aumentar a diversidade de espécies para melhorar a resiliência do ecossistema")
        
        return avaliacao
    
    def avaliar_diversidade_genetica(self, senciantes):
        """
        Avalia a diversidade genética da população em detalhes.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            dict: Avaliação detalhada da diversidade genética.
        """
        if not senciantes:
            return {
                "diversidade_geral": 0.0,
                "detalhes": "Sem população"
            }
        
        # Coletar genes de todos os Senciantes
        genes_por_tipo = {}
        
        for senciante in senciantes.values():
            if hasattr(senciante, "genoma") and hasattr(senciante.genoma, "genes"):
                for gene, valor in senciante.genoma.genes.items():
                    if gene not in genes_por_tipo:
                        genes_por_tipo[gene] = []
                    
                    genes_por_tipo[gene].append(valor)
        
        if not genes_por_tipo:
            return {
                "diversidade_geral": 0.0,
                "detalhes": "Sem dados genéticos"
            }
        
        # Calcular diversidade por gene
        diversidade_por_gene = {}
        
        for gene, valores in genes_por_tipo.items():
            # Calcular variância
            variancia = np.var(valores)
            
            # Normalizar para 0.0-1.0
            diversidade = min(1.0, variancia * 4.0)
            
            diversidade_por_gene[gene] = diversidade
        
        # Calcular diversidade geral
        diversidade_geral = sum(diversidade_por_gene.values()) / len(diversidade_por_gene)
        
        # Determinar status geral
        if diversidade_geral < 0.33:
            status_geral = "Baixa diversidade"
        elif diversidade_geral < 0.66:
            status_geral = "Diversidade moderada"
        else:
            status_geral = "Alta diversidade"
        
        # Identificar genes com menor diversidade
        genes_baixa_diversidade = [gene for gene, div in diversidade_por_gene.items() if div < 0.33]
        
        # Criar avaliação detalhada
        avaliacao = {
            "diversidade_geral": diversidade_geral,
            "status_geral": status_geral,
            "detalhes": {
                "diversidade_por_gene": diversidade_por_gene,
                "genes_baixa_diversidade": genes_baixa_diversidade
            },
            "recomendacoes": []
        }
        
        # Adicionar recomendações
        if diversidade_geral < 0.33:
            avaliacao["recomendacoes"].append("Introduzir variação genética para evitar problemas de consanguinidade")
        
        if genes_baixa_diversidade:
            avaliacao["recomendacoes"].append(f"Focar em aumentar a diversidade dos genes: {', '.join(genes_baixa_diversidade)}")
        
        return avaliacao
    
    def exportar_dados_csv(self):
        """
        Exporta os dados históricos para arquivos CSV.
        
        Returns:
            list: Lista de caminhos para os arquivos CSV gerados.
        """
        # Criar diretório para dados
        diretorio_dados = f"{self.diretorio_logs}/dados"
        os.makedirs(diretorio_dados, exist_ok=True)
        
        # Exportar métricas gerais
        df_metricas = pd.DataFrame(self.historico_metricas)
        caminho_metricas = f"{diretorio_dados}/metricas.csv"
        df_metricas.to_csv(caminho_metricas, index=False)
        
        # Exportar eventos
        if hasattr(self.mundo, "historico") and hasattr(self.mundo.historico, "eventos"):
            eventos = self.mundo.historico.eventos
            
            if eventos:
                df_eventos = pd.DataFrame(eventos)
                caminho_eventos = f"{diretorio_dados}/eventos.csv"
                df_eventos.to_csv(caminho_eventos, index=False)
        
        return [caminho_metricas]
    
    def obter_metricas_atuais(self):
        """
        Obtém as métricas atuais da simulação.
        
        Returns:
            dict: Métricas atuais.
        """
        if not self.historico_metricas["tempo"]:
            return {}
        
        # Obter índice da última atualização
        indice = -1
        
        # Criar dicionário de métricas
        metricas = {}
        
        for chave in self.historico_metricas:
            if len(self.historico_metricas[chave]) > 0:
                metricas[chave] = self.historico_metricas[chave][indice]
        
        return metricas
    
    def obter_graficos_base64(self, senciantes):
        """
        Obtém os gráficos em formato base64 para exibição na API.
        
        Args:
            senciantes (dict): Dicionário de Senciantes para referência.
            
        Returns:
            dict: Dicionário com gráficos em base64.
        """
        graficos = {}
        
        # Gráfico de população
        plt.figure(figsize=(10, 6))
        if len(self.historico_metricas["tempo"]) >= 2:
            dias = [t / 24 for t in self.historico_metricas["tempo"]]
            plt.plot(dias, self.historico_metricas["populacao_total"], 'b-', linewidth=2)
            plt.title("Evolução da População")
            plt.xlabel("Dias")
            plt.ylabel("Número de Senciantes")
            plt.grid(True)
            
            buf = BytesIO()
            plt.savefig(buf, format="png")
            plt.close()
            
            buf.seek(0)
            graficos["populacao"] = base64.b64encode(buf.read()).decode("utf-8")
        
        # Rede social
        graficos["rede_social"] = self.visualizar_rede_influencia_social(senciantes)
        
        # Sentimentos
        graficos["sentimentos"] = self.visualizar_sentimentos_tempo_real(senciantes)
        
        return graficos

