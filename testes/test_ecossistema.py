import unittest
import os
import sys
from unittest.mock import MagicMock, patch
from contextlib import ExitStack

# Adicionar diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos a serem testados
from mecanicas.ecossistema import MecanicaEcossistema
from modelos.mundo import Mundo
from modelos.fauna import Fauna
from modelos.flora import Flora
from modelos.senciante import Senciante

class TestMecanicaEcossistema(unittest.TestCase):
    """
    Classe de testes para o módulo MecanicaEcossistema.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.mundo_mock = MagicMock(spec=Mundo)
        self.mundo_mock.historico.eventos = []
        self.mecanica_ecossistema = MecanicaEcossistema(self.mundo_mock)
        
        self.senciante_mock = MagicMock(spec=Senciante)
        self.senciante_mock.id = "s1"
        self.senciante_mock.nome = "Senciante Teste"
        self.senciante_mock.posicao = (50, 50)
        self.senciante_mock.inventario = {}
        
        self.fauna_mock = MagicMock(spec=Fauna)
        self.fauna_mock.id = "f1"
        self.fauna_mock.nome = "Coelho"
        self.fauna_mock.tipo = "herbivoro"
        self.fauna_mock.populacao = 100
        self.fauna_mock.predador = False
        self.fauna_mock.dieta = ["vegetacao"]
        
        self.flora_mock = MagicMock(spec=Flora)
        self.flora_mock.id = "fl1"
        self.flora_mock.nome = "Arbusto"
        self.flora_mock.tipo = "vegetacao"
        self.flora_mock.populacao = 200
        self.flora_mock.comestivel = True
        self.flora_mock.medicinal = False

    def test_inicializacao(self):
        """
        Testa a inicialização da MecanicaEcossistema.
        """
        self.assertEqual(self.mecanica_ecossistema.mundo, self.mundo_mock)
        self.assertIsInstance(self.mecanica_ecossistema.fauna, dict)
        self.assertIsInstance(self.mecanica_ecossistema.flora, dict)
        self.assertIsInstance(self.mecanica_ecossistema.relacoes_simbioticas, list)
        self.assertIsInstance(self.mecanica_ecossistema.animais_domesticados, dict)
        self.assertIsInstance(self.mecanica_ecossistema.plantas_cultivadas, dict)

    def test_atualizar_ecossistema(self):
        """
        Testa a atualização do ecossistema.
        """
        self.mecanica_ecossistema.fauna["f1"] = self.fauna_mock
        self.mecanica_ecossistema.flora["fl1"] = self.flora_mock
        
        with ExitStack() as stack:
            mock_crescimento = stack.enter_context(patch.object(self.mecanica_ecossistema, 
                                                                "_simular_crescimento_populacional"))
            mock_interacoes = stack.enter_context(patch.object(self.mecanica_ecossistema, 
                                                               "_simular_interacoes_especies"))
            mock_eventos = stack.enter_context(patch.object(self.mecanica_ecossistema, 
                                                            "_simular_eventos_ecologicos"))
            
            self.mecanica_ecossistema.atualizar_ecossistema(1.0)
            
            mock_crescimento.assert_called_once()
            mock_interacoes.assert_called_once()
            mock_eventos.assert_called_once()

    def test_simular_crescimento_populacional(self):
        """
        Testa a simulação de crescimento populacional.
        """
        self.mecanica_ecossistema.fauna["f1"] = self.fauna_mock
        self.mecanica_ecossistema.flora["fl1"] = self.flora_mock
        
        initial_fauna_pop = self.fauna_mock.populacao
        initial_flora_pop = self.flora_mock.populacao
        
        self.mecanica_ecossistema._simular_crescimento_populacional(1.0)
        
        self.assertNotEqual(self.fauna_mock.populacao, initial_fauna_pop)
        self.assertNotEqual(self.flora_mock.populacao, initial_flora_pop)

    def test_simular_interacoes_especies(self):
        """
        Testa a simulação de interações entre espécies.
        """
        predador_mock = MagicMock(spec=Fauna)
        predador_mock.id = "f2"
        predador_mock.nome = "Lobo"
        predador_mock.tipo = "carnivoro"
        predador_mock.populacao = 10
        predador_mock.predador = True
        predador_mock.dieta = ["Coelho"]
        
        self.mecanica_ecossistema.fauna["f1"] = self.fauna_mock
        self.mecanica_ecossistema.fauna["f2"] = predador_mock
        
        initial_fauna_pop = self.fauna_mock.populacao
        
        self.mecanica_ecossistema._simular_interacoes_especies(1.0)
        
        self.assertLess(self.fauna_mock.populacao, initial_fauna_pop)

    def test_simular_eventos_ecologicos(self):
        """
        Testa a simulação de eventos ecológicos.
        """
        with patch("backend.utils.helpers.chance", return_value=0.01):
            self.mecanica_ecossistema._simular_eventos_ecologicos(1.0)
            self.mundo_mock.historico.registrar_evento.assert_called_once()

    def test_estabelecer_relacao_simbiotica(self):
        """
        Testa o estabelecimento de uma relação simbiótica.
        """
        self.mecanica_ecossistema.estabelecer_relacao_simbiotica("Coelho", "Arbusto", "mutualismo")
        self.assertEqual(len(self.mecanica_ecossistema.relacoes_simbioticas), 1)
        self.mundo_mock.historico.registrar_evento.assert_called_once()

    def test_domesticar_animal(self):
        """
        Testa a domesticação de um animal.
        """
        self.mecanica_ecossistema.domesticar_animal(self.senciante_mock, self.fauna_mock)
        self.assertEqual(len(self.mecanica_ecossistema.animais_domesticados), 1)
        self.mundo_mock.historico.registrar_evento.assert_called_once()

    def test_cultivar_planta(self):
        """
        Testa o cultivo de uma planta.
        """
        self.mecanica_ecossistema.cultivar_planta(self.senciante_mock, self.flora_mock)
        self.assertEqual(len(self.mecanica_ecossistema.plantas_cultivadas), 1)
        self.mundo_mock.historico.registrar_evento.assert_called_once()

    def test_colheita_recursos_ecossistema(self):
        """
        Testa a colheita de recursos do ecossistema.
        """
        self.mecanica_ecossistema.flora["fl1"] = self.flora_mock
        initial_flora_pop = self.flora_mock.populacao
        
        self.mecanica_ecossistema.colheita_recursos_ecossistema(self.senciante_mock, "Arbusto", 10)
        
        self.assertLess(self.flora_mock.populacao, initial_flora_pop)
        self.assertIn("vegetacao", self.senciante_mock.inventario)
        self.assertEqual(self.senciante_mock.inventario["vegetacao"], 10)

    def test_introduzir_especie(self):
        """
        Testa a introdução de uma nova espécie.
        """
        nova_fauna = MagicMock(spec=Fauna)
        nova_fauna.id = "f3"
        nova_fauna.nome = "Urso"
        nova_fauna.tipo = "carnivoro"
        nova_fauna.populacao = 5
        nova_fauna.predador = True
        nova_fauna.dieta = ["Coelho"]
        
        self.mecanica_ecossistema.introduzir_especie(nova_fauna)
        self.assertIn("f3", self.mecanica_ecossistema.fauna)
        self.mundo_mock.historico.registrar_evento.assert_called_once()

    def test_remover_especie(self):
        """
        Testa a remoção de uma espécie.
        """
        self.mecanica_ecossistema.fauna["f1"] = self.fauna_mock
        self.mecanica_ecossistema.remover_especie("f1", "fauna")
        self.assertNotIn("f1", self.mecanica_ecossistema.fauna)
        self.mundo_mock.historico.registrar_evento.assert_called_once()

    def test_avaliar_equilibrio_ecologico(self):
        """
        Testa a avaliação do equilíbrio ecológico.
        """
        self.mecanica_ecossistema.fauna["f1"] = self.fauna_mock
        self.mecanica_ecossistema.flora["fl1"] = self.flora_mock
        
        equilibrio = self.mecanica_ecossistema.avaliar_equilibrio_ecologico()
        self.assertIsInstance(equilibrio, dict)
        self.assertIn("saude_geral", equilibrio)
        self.assertIn("diversidade_fauna", equilibrio)
        self.assertIn("diversidade_flora", equilibrio)

if __name__ == "__main__":
    unittest.main()


