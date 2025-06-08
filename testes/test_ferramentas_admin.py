import unittest
import os
import sys
import json
from unittest.mock import MagicMock, patch
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Usar backend não interativo para testes

# Adicionar diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos a serem testados
from mecanicas.ferramentas_admin import FerramentasAdmin
from modelos.mundo import Mundo
from simulacao import Simulacao

class TestFerramentasAdmin(unittest.TestCase):
    """
    Classe de testes para o módulo FerramentasAdmin.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Criar diretórios temporários para testes
        os.makedirs("logs_test", exist_ok=True)
        os.makedirs("graficos_test", exist_ok=True)
        
        # Criar mocks
        self.mundo_mock = MagicMock(spec=Mundo)
        self.mundo_mock.tamanho = [100, 100]
        self.mundo_mock.historico.eventos = []
        
        self.simulacao_mock = MagicMock(spec=Simulacao)
        self.simulacao_mock.tempo_atual = 24.0  # 1 dia
        
        # Criar objeto de ferramentas de administração
        self.ferramentas_admin = FerramentasAdmin(self.mundo_mock, self.simulacao_mock)
        self.ferramentas_admin.diretorio_logs = "logs_test"
        self.ferramentas_admin.diretorio_graficos = "graficos_test"
        
        # Inicializar histórico de métricas com alguns dados
        self.ferramentas_admin.historico_metricas = {
            "tempo": [0.0, 12.0, 24.0],
            "populacao_total": [10, 12, 15],
            "media_saude": [0.8, 0.75, 0.7],
            "media_felicidade": [0.7, 0.65, 0.6],
            "media_estresse": [0.2, 0.3, 0.4],
            "diversidade_genetica": [0.5, 0.55, 0.6],
            "equilibrio_ecologico": [0.8, 0.75, 0.7],
            "numero_grupos": [2, 3, 4],
            "numero_conflitos": [0, 1, 2],
            "numero_tratados": [0, 0, 1],
            "numero_construcoes": [0, 2, 5],
            "numero_tecnologias": [0, 1, 3],
            "numero_doencas": [0, 1, 2]
        }
    
    def tearDown(self):
        """
        Limpeza após os testes.
        """
        # Remover arquivos e diretórios de teste
        for diretorio in ["logs_test", "graficos_test"]:
            for arquivo in os.listdir(diretorio):
                os.remove(os.path.join(diretorio, arquivo))
            os.rmdir(diretorio)
    
    def test_inicializacao(self):
        """
        Testa a inicialização da classe FerramentasAdmin.
        """
        self.assertEqual(self.ferramentas_admin.mundo, self.mundo_mock)
        self.assertEqual(self.ferramentas_admin.simulacao, self.simulacao_mock)
        self.assertEqual(self.ferramentas_admin.diretorio_logs, "logs_test")
        self.assertEqual(self.ferramentas_admin.diretorio_graficos, "graficos_test")
        
        # Verificar se o histórico de métricas foi inicializado corretamente
        self.assertIn("tempo", self.ferramentas_admin.historico_metricas)
        self.assertIn("populacao_total", self.ferramentas_admin.historico_metricas)
        self.assertIn("media_saude", self.ferramentas_admin.historico_metricas)
    
    def test_calcular_metricas(self):
        """
        Testa o cálculo de métricas.
        """
        # Criar senciantes mock
        senciante1 = MagicMock()
        senciante1.estado = {"saude": 0.8, "felicidade": 0.7, "estresse": 0.2}
        
        senciante2 = MagicMock()
        senciante2.estado = {"saude": 0.6, "felicidade": 0.5, "estresse": 0.4}
        
        senciantes = {"s1": senciante1, "s2": senciante2}
        
        # Calcular métricas
        metricas = self.ferramentas_admin._calcular_metricas(24.0, senciantes)
        
        # Verificar resultados
        self.assertEqual(metricas["tempo"], 24.0)
        self.assertEqual(metricas["populacao_total"], 2)
        self.assertAlmostEqual(metricas["media_saude"], 0.7)
        self.assertAlmostEqual(metricas["media_felicidade"], 0.6)
        self.assertAlmostEqual(metricas["media_estresse"], 0.3)
    
    def test_calcular_diversidade_genetica(self):
        """
        Testa o cálculo de diversidade genética.
        """
        # Criar senciantes mock com genoma
        senciante1 = MagicMock()
        senciante1.genoma.genes = {"forca": 0.8, "inteligencia": 0.7, "carisma": 0.6}
        
        senciante2 = MagicMock()
        senciante2.genoma.genes = {"forca": 0.4, "inteligencia": 0.9, "carisma": 0.2}
        
        senciantes = {"s1": senciante1, "s2": senciante2}
        
        # Calcular diversidade genética
        diversidade = self.ferramentas_admin._calcular_diversidade_genetica(senciantes)
        
        # Verificar resultado
        self.assertGreater(diversidade, 0.0)
        self.assertLessEqual(diversidade, 1.0)
    
    def test_calcular_equilibrio_ecologico(self):
        """
        Testa o cálculo de equilíbrio ecológico.
        """
        # Configurar mock do ecossistema
        fauna1 = MagicMock()
        fauna1.predador = True
        fauna1.populacao = 10
        
        fauna2 = MagicMock()
        fauna2.predador = False
        fauna2.populacao = 50
        
        flora1 = MagicMock()
        flora1.populacao = 100
        
        flora2 = MagicMock()
        flora2.populacao = 200
        
        self.simulacao_mock.mecanica_ecossistema.fauna = {"f1": fauna1, "f2": fauna2}
        self.simulacao_mock.mecanica_ecossistema.flora = {"fl1": flora1, "fl2": flora2}
        
        # Calcular equilíbrio ecológico
        equilibrio = self.ferramentas_admin._calcular_equilibrio_ecologico()
        
        # Verificar resultado
        self.assertGreaterEqual(equilibrio, 0.0)
        self.assertLessEqual(equilibrio, 1.0)
    
    def test_registrar_logs(self):
        """
        Testa o registro de logs.
        """
        # Criar senciantes mock
        senciante1 = MagicMock()
        senciante1.estado = {"saude": 0.8, "felicidade": 0.7, "estresse": 0.2}
        senciante1.idade = 12.0
        senciante1.genero = "masculino"
        
        senciante2 = MagicMock()
        senciante2.estado = {"saude": 0.6, "felicidade": 0.5, "estresse": 0.4}
        senciante2.idade = 24.0
        senciante2.genero = "feminino"
        
        senciantes = {"s1": senciante1, "s2": senciante2}
        
        # Calcular métricas
        metricas = self.ferramentas_admin._calcular_metricas(24.0, senciantes)
        
        # Registrar logs
        self.ferramentas_admin._registrar_logs(24.0, metricas, senciantes)
        
        # Verificar se o arquivo de log foi criado
        log_files = os.listdir("logs_test")
        self.assertGreater(len(log_files), 0)
        
        # Verificar conteúdo do arquivo de log
        log_file = os.path.join("logs_test", log_files[0])
        with open(log_file, "r") as f:
            log_data = json.load(f)
        
        self.assertEqual(log_data["tempo"]["valor"], 24.0)
        self.assertEqual(log_data["tempo"]["dia"], 2)  # Dia 2 (começa em 1)
        self.assertEqual(log_data["tempo"]["hora"], 0)  # Hora 0
        self.assertEqual(log_data["metricas"]["populacao_total"], 2)
    
    def test_gerar_grafico_populacao(self):
        """
        Testa a geração do gráfico de população.
        """
        # Gerar gráfico
        caminho = self.ferramentas_admin.gerar_grafico_populacao()
        
        # Verificar se o arquivo foi criado
        self.assertIsNotNone(caminho)
        self.assertTrue(os.path.exists(caminho))
    
    def test_gerar_grafico_estados(self):
        """
        Testa a geração do gráfico de estados.
        """
        # Gerar gráfico
        caminho = self.ferramentas_admin.gerar_grafico_estados()
        
        # Verificar se o arquivo foi criado
        self.assertIsNotNone(caminho)
        self.assertTrue(os.path.exists(caminho))
    
    def test_gerar_rede_social(self):
        """
        Testa a geração da rede social.
        """
        # Criar senciantes mock com relações
        senciante1 = MagicMock()
        senciante1.nome = "Senciante 1"
        senciante1.relacoes = {
            "s2": {"afinidade": 0.8},
            "s3": {"afinidade": 0.6}
        }
        
        senciante2 = MagicMock()
        senciante2.nome = "Senciante 2"
        senciante2.relacoes = {
            "s1": {"afinidade": 0.7},
            "s3": {"afinidade": 0.5}
        }
        
        senciante3 = MagicMock()
        senciante3.nome = "Senciante 3"
        senciante3.relacoes = {
            "s1": {"afinidade": 0.6},
            "s2": {"afinidade": 0.4}
        }
        
        senciantes = {"s1": senciante1, "s2": senciante2, "s3": senciante3}
        
        # Gerar rede social
        caminho = self.ferramentas_admin.gerar_rede_social(senciantes)
        
        # Verificar se o arquivo foi criado
        self.assertIsNotNone(caminho)
        self.assertTrue(os.path.exists(caminho))
    
    def test_visualizar_rede_influencia_social(self):
        """
        Testa a visualização da rede de influência social.
        """
        # Criar senciantes mock com relações e influência
        senciante1 = MagicMock()
        senciante1.nome = "Senciante 1"
        senciante1.genoma.genes = {"carisma": 0.8}
        senciante1.habilidades = {"comunicacao": 0.7, "lideranca": 0.6}
        senciante1.relacoes = {
            "s2": {"influencia": 0.8},
            "s3": {"influencia": 0.6}
        }
        
        senciante2 = MagicMock()
        senciante2.nome = "Senciante 2"
        senciante2.genoma.genes = {"carisma": 0.6}
        senciante2.habilidades = {"comunicacao": 0.5, "lideranca": 0.4}
        senciante2.relacoes = {
            "s1": {"influencia": 0.3},
            "s3": {"influencia": 0.5}
        }
        
        senciante3 = MagicMock()
        senciante3.nome = "Senciante 3"
        senciante3.genoma.genes = {"carisma": 0.4}
        senciante3.habilidades = {"comunicacao": 0.3, "lideranca": 0.2}
        senciante3.relacoes = {
            "s1": {"influencia": 0.2},
            "s2": {"influencia": 0.4}
        }
        
        senciantes = {"s1": senciante1, "s2": senciante2, "s3": senciante3}
        
        # Visualizar rede de influência social
        img_base64 = self.ferramentas_admin.visualizar_rede_influencia_social(senciantes)
        
        # Verificar se a imagem foi gerada
        self.assertIsNotNone(img_base64)
        self.assertIsInstance(img_base64, str)
        self.assertTrue(img_base64.startswith("iVBORw0KGgo"))  # Início típico de base64 de imagem PNG
    
    def test_visualizar_sentimentos_tempo_real(self):
        """
        Testa a visualização de sentimentos em tempo real.
        """
        # Criar senciantes mock
        senciante1 = MagicMock()
        senciante1.nome = "Senciante 1"
        senciante1.estado = {"saude": 0.8, "felicidade": 0.7, "estresse": 0.2}
        
        senciante2 = MagicMock()
        senciante2.nome = "Senciante 2"
        senciante2.estado = {"saude": 0.6, "felicidade": 0.5, "estresse": 0.4}
        
        senciantes = {"s1": senciante1, "s2": senciante2}
        
        # Visualizar sentimentos em tempo real
        img_base64 = self.ferramentas_admin.visualizar_sentimentos_tempo_real(senciantes)
        
        # Verificar se a imagem foi gerada
        self.assertIsNotNone(img_base64)
        self.assertIsInstance(img_base64, str)
        self.assertTrue(img_base64.startswith("iVBORw0KGgo"))  # Início típico de base64 de imagem PNG
    
    def test_avaliar_equilibrio_ecologico(self):
        """
        Testa a avaliação detalhada do equilíbrio ecológico.
        """
        # Configurar mock do ecossistema
        fauna1 = MagicMock()
        fauna1.predador = True
        fauna1.populacao = 10
        
        fauna2 = MagicMock()
        fauna2.predador = False
        fauna2.populacao = 50
        
        flora1 = MagicMock()
        flora1.populacao = 100
        
        flora2 = MagicMock()
        flora2.populacao = 200
        
        self.simulacao_mock.mecanica_ecossistema.fauna = {"f1": fauna1, "f2": fauna2}
        self.simulacao_mock.mecanica_ecossistema.flora = {"fl1": flora1, "fl2": flora2}
        
        # Avaliar equilíbrio ecológico
        avaliacao = self.ferramentas_admin.avaliar_equilibrio_ecologico()
        
        # Verificar resultado
        self.assertIn("equilibrio_geral", avaliacao)
        self.assertIn("status_geral", avaliacao)
        self.assertIn("detalhes", avaliacao)
        self.assertIn("recomendacoes", avaliacao)
        
        self.assertGreaterEqual(avaliacao["equilibrio_geral"], 0.0)
        self.assertLessEqual(avaliacao["equilibrio_geral"], 1.0)
    
    def test_avaliar_diversidade_genetica(self):
        """
        Testa a avaliação detalhada da diversidade genética.
        """
        # Criar senciantes mock com genoma
        senciante1 = MagicMock()
        senciante1.genoma.genes = {"forca": 0.8, "inteligencia": 0.7, "carisma": 0.6}
        
        senciante2 = MagicMock()
        senciante2.genoma.genes = {"forca": 0.4, "inteligencia": 0.9, "carisma": 0.2}
        
        senciantes = {"s1": senciante1, "s2": senciante2}
        
        # Avaliar diversidade genética
        avaliacao = self.ferramentas_admin.avaliar_diversidade_genetica(senciantes)
        
        # Verificar resultado
        self.assertIn("diversidade_geral", avaliacao)
        self.assertIn("status_geral", avaliacao)
        self.assertIn("detalhes", avaliacao)
        self.assertIn("recomendacoes", avaliacao)
        
        self.assertGreaterEqual(avaliacao["diversidade_geral"], 0.0)
        self.assertLessEqual(avaliacao["diversidade_geral"], 1.0)
    
    def test_exportar_dados_csv(self):
        """
        Testa a exportação de dados para CSV.
        """
        # Exportar dados
        caminhos = self.ferramentas_admin.exportar_dados_csv()
        
        # Verificar se os arquivos foram criados
        self.assertIsNotNone(caminhos)
        self.assertGreater(len(caminhos), 0)
        
        for caminho in caminhos:
            self.assertTrue(os.path.exists(caminho))
    
    def test_obter_metricas_atuais(self):
        """
        Testa a obtenção das métricas atuais.
        """
        # Obter métricas atuais
        metricas = self.ferramentas_admin.obter_metricas_atuais()
        
        # Verificar resultado
        self.assertIsNotNone(metricas)
        self.assertIn("tempo", metricas)
        self.assertIn("populacao_total", metricas)
        self.assertIn("media_saude", metricas)
        self.assertIn("media_felicidade", metricas)
        self.assertIn("media_estresse", metricas)
        
        self.assertEqual(metricas["tempo"], 24.0)
        self.assertEqual(metricas["populacao_total"], 15)
    
    def test_obter_graficos_base64(self):
        """
        Testa a obtenção de gráficos em formato base64.
        """
        # Criar senciantes mock
        senciante1 = MagicMock()
        senciante1.nome = "Senciante 1"
        senciante1.estado = {"saude": 0.8, "felicidade": 0.7, "estresse": 0.2}
        senciante1.relacoes = {}
        
        senciante2 = MagicMock()
        senciante2.nome = "Senciante 2"
        senciante2.estado = {"saude": 0.6, "felicidade": 0.5, "estresse": 0.4}
        senciante2.relacoes = {}
        
        senciantes = {"s1": senciante1, "s2": senciante2}
        
        # Obter gráficos base64
        graficos = self.ferramentas_admin.obter_graficos_base64(senciantes)
        
        # Verificar resultado
        self.assertIsNotNone(graficos)
        self.assertIn("populacao", graficos)
        self.assertIn("sentimentos", graficos)


if __name__ == "__main__":
    unittest.main()


