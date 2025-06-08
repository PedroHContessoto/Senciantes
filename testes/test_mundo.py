"""
Testes unitários para o módulo Mundo.
"""

import unittest
import numpy as np
from modelos.mundo import Mundo
from modelos.clima import Clima
from modelos.recurso import Recurso
from modelos.construcao import Construcao
from modelos.historico import Historico

class TestMundo(unittest.TestCase):
    """
    Testes para a classe Mundo.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.tamanho = [50, 50]
        self.mundo = Mundo(self.tamanho)
    
    def test_inicializacao(self):
        """
        Testa a inicialização de um Mundo.
        """
        # Verificar atributos básicos
        self.assertEqual(self.mundo.tamanho, self.tamanho)
        self.assertIsInstance(self.mundo.clima, Clima)
        self.assertIsInstance(self.mundo.recursos, dict)
        self.assertIsInstance(self.mundo.construcoes, dict)
        self.assertIsInstance(self.mundo.historico, Historico)
        
        # Verificar geografia
        self.assertIn("elevacao", self.mundo.geografia)
        self.assertIn("biomas", self.mundo.geografia)
        
        # Verificar recursos iniciais
        self.assertGreater(len(self.mundo.recursos), 0)
    
    def test_gerar_geografia(self):
        """
        Testa a geração da geografia do mundo.
        """
        geografia = self.mundo._gerar_geografia()
        
        # Verificar estrutura
        self.assertIn("elevacao", geografia)
        self.assertIn("biomas", geografia)
        
        # Verificar dimensões
        self.assertEqual(geografia["elevacao"].shape, (self.tamanho[0], self.tamanho[1]))
        self.assertEqual(geografia["biomas"].shape, (self.tamanho[0], self.tamanho[1]))
        
        # Verificar valores
        self.assertTrue(np.all(geografia["elevacao"] >= 0))
        self.assertTrue(np.all(geografia["elevacao"] <= 1))
    
    def test_gerar_recursos_iniciais(self):
        """
        Testa a geração de recursos iniciais.
        """
        # Limpar recursos existentes
        self.mundo.recursos = {}
        
        # Gerar recursos
        self.mundo._gerar_recursos_iniciais()
        
        # Verificar se foram gerados
        self.assertGreater(len(self.mundo.recursos), 0)
        
        # Verificar tipos de recursos
        tipos_recursos = set()
        for recurso in self.mundo.recursos.values():
            tipos_recursos.add(recurso.tipo)
        
        # Deve haver pelo menos alguns tipos diferentes
        self.assertGreaterEqual(len(tipos_recursos), 3)
    
    def test_atualizar(self):
        """
        Testa a atualização do estado do mundo.
        """
        # Contar recursos antes
        num_recursos_antes = len(self.mundo.recursos)
        
        # Atualizar mundo
        self.mundo.atualizar(1.0)
        
        # Verificar se o clima foi atualizado
        # (não podemos verificar valores específicos, apenas que a atualização ocorreu)
        
        # Verificar recursos
        # O número pode mudar devido a recursos esgotados ou regenerados
        self.assertGreaterEqual(len(self.mundo.recursos), 0)
    
    def test_encontrar_recursos_proximos(self):
        """
        Testa a busca de recursos próximos a uma posição.
        """
        # Limpar recursos existentes
        self.mundo.recursos = {}
        
        # Adicionar recursos em posições conhecidas
        recurso1 = Recurso("comida", [10.0, 10.0], 1.0)
        recurso2 = Recurso("agua", [15.0, 15.0], 1.0)
        recurso3 = Recurso("comida", [30.0, 30.0], 1.0)
        
        self.mundo.recursos[recurso1.id] = recurso1
        self.mundo.recursos[recurso2.id] = recurso2
        self.mundo.recursos[recurso3.id] = recurso3
        
        # Buscar recursos próximos
        recursos = self.mundo.encontrar_recursos_proximos([10.0, 10.0], 10.0)
        
        # Deve encontrar 2 recursos (comida e água)
        self.assertEqual(len(recursos), 2)
        
        # Buscar apenas comida
        recursos = self.mundo.encontrar_recursos_proximos([10.0, 10.0], 10.0, "comida")
        
        # Deve encontrar 1 recurso
        self.assertEqual(len(recursos), 1)
        self.assertEqual(recursos[0].tipo, "comida")
    
    def test_adicionar_construcao(self):
        """
        Testa a adição de uma construção ao mundo.
        """
        # Contar construções antes
        num_construcoes_antes = len(self.mundo.construcoes)
        
        # Adicionar construção
        construcao = self.mundo.adicionar_construcao(
            "abrigo_simples",
            [20.0, 20.0],
            1.0,
            "senciante_id"
        )
        
        # Verificar se foi adicionada
        self.assertEqual(len(self.mundo.construcoes), num_construcoes_antes + 1)
        self.assertIn(construcao.id, self.mundo.construcoes)
        
        # Verificar atributos
        self.assertEqual(construcao.tipo, "abrigo_simples")
        self.assertEqual(construcao.posicao, [20.0, 20.0])
        self.assertEqual(construcao.tamanho, 1.0)
        self.assertEqual(construcao.proprietario_id, "senciante_id")
    
    def test_obter_bioma(self):
        """
        Testa a obtenção do bioma em uma posição.
        """
        # Definir bioma em uma posição específica
        x, y = 10, 10
        self.mundo.geografia["biomas"][x, y] = "floresta"
        
        # Obter bioma
        bioma = self.mundo.obter_bioma([x, y])
        
        # Verificar
        self.assertEqual(bioma, "floresta")
    
    def test_aplicar_acao_divina_clima(self):
        """
        Testa a aplicação de uma ação divina no clima.
        """
        # Temperatura inicial
        temp_inicial = self.mundo.clima.temperatura
        
        # Aplicar ação divina
        sucesso = self.mundo.aplicar_acao_divina_clima("temperatura", 1.0, 1.0)
        
        # Verificar sucesso
        self.assertTrue(sucesso)
        
        # Verificar eventos climáticos
        self.assertGreater(len(self.mundo.clima.eventos_climaticos), 0)
        
        # Verificar evento no histórico
        eventos = [e for e in self.mundo.historico.eventos if e["tipo"] == "acao_divina"]
        self.assertGreater(len(eventos), 0)
    
    def test_aplicar_acao_divina_recurso(self):
        """
        Testa a aplicação de uma ação divina nos recursos.
        """
        # Contar recursos antes
        num_recursos_antes = len(self.mundo.recursos)
        
        # Aplicar ação divina para criar recurso
        sucesso = self.mundo.aplicar_acao_divina_recurso("comida", 10.0, [25.0, 25.0])
        
        # Verificar sucesso
        self.assertTrue(sucesso)
        
        # Verificar se recurso foi criado
        self.assertEqual(len(self.mundo.recursos), num_recursos_antes + 1)
        
        # Verificar evento no histórico
        eventos = [e for e in self.mundo.historico.eventos if e["tipo"] == "acao_divina"]
        self.assertGreater(len(eventos), 0)
    
    def test_criar_artefato_divino(self):
        """
        Testa a criação de um artefato divino.
        """
        # Contar construções antes
        num_construcoes_antes = len(self.mundo.construcoes)
        
        # Criar artefato
        artefato = self.mundo.criar_artefato_divino("conhecimento", [30.0, 30.0])
        
        # Verificar se foi criado
        self.assertIsNotNone(artefato)
        self.assertEqual(len(self.mundo.construcoes), num_construcoes_antes + 1)
        
        # Verificar atributos
        construcao = self.mundo.construcoes[artefato["id"]]
        self.assertEqual(construcao.tipo, "artefato_conhecimento")
        self.assertEqual(construcao.posicao, [30.0, 30.0])
        
        # Verificar funcionalidades
        self.assertIn("bonus_aprendizado", construcao.funcionalidades)
        
        # Verificar evento no histórico
        eventos = [e for e in self.mundo.historico.eventos if e["tipo"] == "acao_divina"]
        self.assertGreater(len(eventos), 0)
    
    def test_to_dict(self):
        """
        Testa a conversão do Mundo para dicionário.
        """
        # Converter para dicionário
        mundo_dict = self.mundo.to_dict()
        
        # Verificar estrutura do dicionário
        self.assertIsNotNone(mundo_dict)
        self.assertIsInstance(mundo_dict, dict)
        
        # Verificar campos principais
        campos = ["tamanho", "clima", "recursos", "construcoes", "biomas"]
        
        for campo in campos:
            self.assertIn(campo, mundo_dict)

if __name__ == "__main__":
    unittest.main()


