import unittest
from unittest.mock import MagicMock
from modelos.senciante import Senciante
from modelos.genoma import Genoma
from modelos.memoria import Memoria

class TestSenciante(unittest.TestCase):
    """
    Testes para a classe Senciante.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.posicao = [10.0, 10.0]
        self.senciante = Senciante(self.posicao)
    
    def test_inicializacao(self):
        """
        Testa a inicialização de um Senciante.
        """
        # Verificar atributos básicos
        self.assertIsNotNone(self.senciante.id)
        self.assertEqual(self.senciante.posicao, self.posicao)
        self.assertIsInstance(self.senciante.genoma, Genoma)
        
        # Verificar necessidades
        for necessidade in ["fome", "sede", "sono", "higiene", "social"]:
            self.assertIn(necessidade, self.senciante.necessidades)
            self.assertEqual(self.senciante.necessidades[necessidade], 0.0)
        
        # Verificar estado
        self.assertEqual(self.senciante.estado["idade"], 0.0)
        self.assertEqual(self.senciante.estado["saude"], 1.0)
        self.assertEqual(self.senciante.estado["energia"], 1.0)
        
        # Verificar habilidades
        for habilidade in ["coleta", "construcao", "comunicacao", "combate", "aprendizado"]:
            self.assertIn(habilidade, self.senciante.habilidades)
            self.assertEqual(self.senciante.habilidades[habilidade], 0.1)
    
    def test_atualizar_necessidades(self):
        """
        Testa a atualização das necessidades do Senciante.
        """
        # Estado inicial
        for necessidade in self.senciante.necessidades:
            self.assertEqual(self.senciante.necessidades[necessidade], 0.0)
        
        # Atualizar necessidades
        self.senciante._atualizar_necessidades(1.0)
        
        # Verificar se as necessidades aumentaram
        for necessidade in self.senciante.necessidades:
            self.assertGreater(self.senciante.necessidades[necessidade], 0.0)
    
    def test_verificar_morte(self):
        """
        Testa a verificação de morte do Senciante.
        """
        # Inicialmente vivo
        self.assertFalse(self.senciante._verificar_morte())
        
        # Morte por idade
        self.senciante.estado["idade"] = 100.0
        self.assertTrue(self.senciante._verificar_morte())
        
        # Resetar idade
        self.senciante.estado["idade"] = 0.0
        
        # Morte por saúde
        self.senciante.estado["saude"] = 0.0
        self.assertTrue(self.senciante._verificar_morte())
        
        # Resetar saúde
        self.senciante.estado["saude"] = 1.0
        
        # Morte por fome
        self.senciante.necessidades["fome"] = 1.0
        self.assertTrue(self.senciante._verificar_morte())
    
    def test_consumir_recurso(self):
        """
        Testa o consumo de recursos pelo Senciante.
        """
        # Adicionar recursos ao inventário
        self.senciante.inventario["comida"] = 2.0
        self.senciante.inventario["agua"] = 1.5
        
        # Consumir comida
        quantidade_consumida = self.senciante._consumir_recurso("comida", 1.0)
        self.assertEqual(quantidade_consumida, 1.0)
        self.assertEqual(self.senciante.inventario["comida"], 1.0)
        
        # Consumir água (toda)
        quantidade_consumida = self.senciante._consumir_recurso("agua", 2.0)
        self.assertEqual(quantidade_consumida, 1.5)
        self.assertNotIn("agua", self.senciante.inventario)
        
        # Tentar consumir recurso inexistente
        quantidade_consumida = self.senciante._consumir_recurso("pedra", 1.0)
        self.assertEqual(quantidade_consumida, 0.0)
    
    def test_ganhar_experiencia(self):
        """
        Testa o ganho de experiência em habilidades.
        """
        # Valor inicial
        self.assertEqual(self.senciante.habilidades["coleta"], 0.1)
        
        # Ganhar experiência
        self.senciante._ganhar_experiencia("coleta", 0.2)
        
        # Verificar aumento
        self.assertGreater(self.senciante.habilidades["coleta"], 0.1)
        
        # Verificar limite
        self.senciante._ganhar_experiencia("coleta", 1.0)
        self.assertLessEqual(self.senciante.habilidades["coleta"], 1.0)
    
    def test_adicionar_memoria(self):
        """
        Testa a adição de memórias ao Senciante.
        """
        # Estado inicial
        self.assertEqual(len(self.senciante.memoria), 0)
        
        # Adicionar memória
        self.senciante._adicionar_memoria("teste", "Conteúdo de teste", 0.5)
        
        # Verificar adição
        self.assertEqual(len(self.senciante.memoria), 1)
        self.assertIsInstance(self.senciante.memoria[0], Memoria)
        self.assertEqual(self.senciante.memoria[0].tipo, "teste")
        self.assertEqual(self.senciante.memoria[0].conteudo, "Conteúdo de teste")
        self.assertEqual(self.senciante.memoria[0].importancia, 0.5)
    
    def test_estabelecer_relacao(self):
        """
        Testa o estabelecimento de relações com outros Senciantes.
        """
        # Estado inicial
        self.assertEqual(len(self.senciante.relacoes), 0)
        
        # Estabelecer relação
        self.senciante.estabelecer_relacao("outro_id", "conhecido", 0.5)
        
        # Verificar relação
        self.assertIn("outro_id", self.senciante.relacoes)
        self.assertEqual(self.senciante.relacoes["outro_id"]["tipo"], "conhecido")
        self.assertEqual(self.senciante.relacoes["outro_id"]["forca"], 0.5)
        
        # Atualizar relação existente
        self.senciante.estabelecer_relacao("outro_id", "amigo", 0.7)
        
        # Verificar atualização
        self.assertEqual(self.senciante.relacoes["outro_id"]["tipo"], "amigo")
        self.assertEqual(self.senciante.relacoes["outro_id"]["forca"], 0.7)
    
    def test_pode_reproduzir(self):
        """
        Testa a verificação de capacidade de reprodução.
        """
        # Inicialmente não pode (idade insuficiente)
        self.assertFalse(self.senciante.pode_reproduzir())
        
        # Definir idade suficiente
        self.senciante.estado["idade"] = 10.0
        
        # Agora deve poder
        self.assertTrue(self.senciante.pode_reproduzir())
        
        # Testar com energia insuficiente
        self.senciante.estado["energia"] = 0.3
        self.assertFalse(self.senciante.pode_reproduzir())
    
    def test_to_dict(self):
        """
        Testa a conversão do Senciante para dicionário.
        """
        # Converter para dicionário
        senciante_dict = self.senciante.to_dict()
        
        # Verificar estrutura do dicionário
        self.assertIsNotNone(senciante_dict)
        self.assertIsInstance(senciante_dict, dict)
        
        # Verificar campos principais
        campos = [
            "id", "posicao", "genoma", "necessidades", "estado",
            "habilidades", "memoria", "relacoes", "inventario"
        ]
        
        for campo in campos:
            self.assertIn(campo, senciante_dict)

if __name__ == "__main__":
    unittest.main()


