import unittest
import os
import sys
from unittest.mock import MagicMock, patch
from contextlib import ExitStack

# Adicionar diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos a serem testados
from mecanicas.consciencia_moralidade import MecanicaConscienciaMoralidade
from modelos.moralidade import Moralidade
from modelos.senciante import Senciante
from modelos.mundo import Mundo
from utils.helpers import chance

class TestMecanicaMoralidade(unittest.TestCase):
    """
    Classe de testes para o módulo MecanicaMoralidade.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Criar mocks
        self.mundo_mock = MagicMock(spec=Mundo)
        self.mundo_mock.historico.eventos = []
        
        # Criar objeto de mecânica de moralidade
        self.mecanica_moralidade = MecanicaConscienciaMoralidade(self.mundo_mock)
        
        # Criar senciantes mock
        self.senciante1 = MagicMock(spec=Senciante)
        self.senciante1.id = "s1"
        self.senciante1.nome = "Senciante 1"
        self.senciante1.idade = 24.0
        self.senciante1.genero = "masculino"
        self.senciante1.estado = {"saude": 0.8, "felicidade": 0.7, "estresse": 0.2}
        self.senciante1.habilidades = {"comunicacao": 0.7, "empatia": 0.6}
        self.senciante1.memoria = []
        self.senciante1.conhecimento = {}
        
        self.senciante2 = MagicMock(spec=Senciante)
        self.senciante2.id = "s2"
        self.senciante2.nome = "Senciante 2"
        self.senciante2.idade = 36.0
        self.senciante2.genero = "feminino"
        self.senciante2.estado = {"saude": 0.6, "felicidade": 0.5, "estresse": 0.4}
        self.senciante2.habilidades = {"comunicacao": 0.5, "empatia": 0.8}
        self.senciante2.memoria = []
        self.senciante2.conhecimento = {}
        
        # Adicionar moralidade aos senciantes
        self.senciante1.moralidade = Moralidade()
        self.senciante2.moralidade = Moralidade()
        
        # Inicializar valores morais
        self.senciante1.moralidade.valores = {
            "lealdade": 0.7,
            "justica": 0.6,
            "cuidado": 0.5,
            "liberdade": 0.8,
            "autoridade": 0.4
        }
        
        self.senciante2.moralidade.valores = {
            "lealdade": 0.5,
            "justica": 0.8,
            "cuidado": 0.7,
            "liberdade": 0.6,
            "autoridade": 0.3
        }
        
        # Adicionar senciantes à simulação
        self.senciantes = {"s1": self.senciante1, "s2": self.senciante2}
    
    def test_inicializacao(self):
        """
        Testa a inicialização da classe MecanicaMoralidade.
        """
        self.assertEqual(self.mecanica_moralidade.mundo, self.mundo_mock)
        self.assertEqual(len(self.mecanica_moralidade.valores_morais), 6)
        self.assertEqual(len(self.mecanica_moralidade.dilemas_morais), 5)
    
    def test_atualizar_senciante(self):
        """
        Testa a atualização de um Senciante.
        """
        # Mockar a função chance para controlar o comportamento
        with patch("backend.utils.helpers.chance", return_value=0.001):
            self.mecanica_moralidade.atualizar_senciante(self.senciante1, 1.0)
            # Verificar se o dilema foi apresentado
            self.mundo_mock.historico.registrar_evento.assert_called_once()

    def test_apresentar_dilema_moral(self):
        """
        Testa a apresentação de um dilema moral.
        """
        with patch("backend.utils.helpers.chance", return_value=0.5):
            resultado = self.mecanica_moralidade._apresentar_dilema_moral(self.senciante1)
            self.assertIsNotNone(resultado)
            self.assertIn("dilema", resultado)
            self.assertIn("escolha", resultado)
            self.assertIn("consequencias", resultado)

    def test_tomar_decisao_moral(self):
        """
        Testa a tomada de decisão moral.
        """
        dilema = self.mecanica_moralidade.dilemas_morais[0]
        escolha = self.mecanica_moralidade._tomar_decisao_moral(self.senciante1, dilema)
        self.assertIn(escolha, dilema["opcoes"])

    def test_aplicar_consequencias_dilema(self):
        """
        Testa a aplicação de consequências de um dilema moral.
        """
        dilema = self.mecanica_moralidade.dilemas_morais[0]
        escolha = dilema["opcoes"][0]
        initial_felicidade = self.senciante1.estado["felicidade"]
        initial_estresse = self.senciante1.estado["estresse"]
        
        consequencias = self.mecanica_moralidade._aplicar_consequencias_dilema(self.senciante1, dilema, escolha)
        self.assertIn("descricao", consequencias)
        self.assertIn("efeito_felicidade", consequencias)
        self.assertIn("efeito_estresse", consequencias)
        self.assertNotEqual(self.senciante1.estado["felicidade"], initial_felicidade)
        self.assertNotEqual(self.senciante1.estado["estresse"], initial_estresse)

    def test_formar_principio_etico(self):
        """
        Testa a formação de um princípio ético.
        """
        # Garantir que o senciante tem um valor moral forte para formar um princípio
        self.senciante1.moralidade.valores["lealdade"] = 0.8
        
        with patch("backend.utils.helpers.chance", return_value=0.001):
            principio = self.mecanica_moralidade._formar_principio_etico(self.senciante1)
            if principio:
                self.assertIsNotNone(principio)
                self.mundo_mock.historico.registrar_evento.assert_called_once()

    def test_desenvolver_conceito_filosofico(self):
        """
        Testa o desenvolvimento de um conceito filosófico.
        """
        self.senciante1.habilidades["aprendizado"] = 0.8 # Habilidade alta para desenvolver conceito
        with patch("backend.utils.helpers.chance", return_value=0.001):
            conceito = self.mecanica_moralidade._desenvolver_conceito_filosofico(self.senciante1)
            self.assertIsNotNone(conceito)
            self.mundo_mock.historico.registrar_conceito_filosofico.assert_called_once()

    def test_avaliar_compatibilidade_moral(self):
        """
        Testa a avaliação de compatibilidade moral entre dois Senciantes.
        """
        compatibilidade = self.mecanica_moralidade.avaliar_compatibilidade_moral(self.senciante1, self.senciante2)
        self.assertIsInstance(compatibilidade, float)
        self.assertGreaterEqual(compatibilidade, 0.0)
        self.assertLessEqual(compatibilidade, 1.0)

    def test_avaliar_acao_moral(self):
        """
        Testa a avaliação de uma ação moral.
        """
        avaliacao = self.mecanica_moralidade.avaliar_acao_moral(self.senciante1, "ajudar", {"impacto": "positivo"})
        self.assertIsInstance(avaliacao, float)
        self.assertGreaterEqual(avaliacao, -1.0)
        self.assertLessEqual(avaliacao, 1.0)

    def test_gerar_conflito_etico(self):
        """
        Testa a geração de um conflito ético.
        """
        grupo1 = [self.senciante1]
        grupo2 = [self.senciante2]
        conflito = self.mecanica_moralidade.gerar_conflito_etico(grupo1, grupo2)
        self.assertIsInstance(conflito, dict)
        self.assertIn("descricao", conflito)
        self.assertIn("valor_divergente", conflito)

    def test_calcular_valores_medios(self):
        """
        Testa o cálculo de valores morais médios de um grupo.
        """
        grupo = [self.senciante1, self.senciante2]
        valores_medios = self.mecanica_moralidade._calcular_valores_medios(grupo)
        self.assertIsInstance(valores_medios, dict)
        self.assertIn("lealdade", valores_medios)

if __name__ == "__main__":
    unittest.main()


