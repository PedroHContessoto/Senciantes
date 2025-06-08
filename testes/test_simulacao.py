"""
Testes unitários para o módulo Simulacao.
"""

import unittest
from unittest.mock import MagicMock, patch
import time
import threading
from simulacao import Simulacao
from modelos.mundo import Mundo
from modelos.senciante import Senciante

class TestSimulacao(unittest.TestCase):
    """
    Testes para a classe Simulacao.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Criar simulação com valores personalizados
        self.simulacao = Simulacao([20, 20], 5)
    
    def test_inicializacao(self):
        """
        Testa a inicialização de uma Simulação.
        """
        # Verificar atributos básicos
        self.assertEqual(self.simulacao.tamanho_mundo, [20, 20])
        self.assertEqual(self.simulacao.num_senciantes_inicial, 5)
        self.assertIsInstance(self.simulacao.mundo, Mundo)
        self.assertEqual(len(self.simulacao.senciantes), 5)
        
        # Verificar estado inicial
        self.assertFalse(self.simulacao.executando)
        self.assertFalse(self.simulacao.pausada)
        self.assertEqual(self.simulacao.tempo_simulacao, 0.0)
        self.assertIsNone(self.simulacao.tempo_real_inicio)
        
        # Verificar estatísticas iniciais
        for estatistica in ["nascimentos", "mortes", "construcoes", "tecnologias", "recursos_coletados"]:
            self.assertIn(estatistica, self.simulacao.estatisticas)
            self.assertEqual(self.simulacao.estatisticas[estatistica], 0)
    
    def test_criar_senciantes_iniciais(self):
        """
        Testa a criação de Senciantes iniciais.
        """
        # Limpar Senciantes existentes
        self.simulacao.senciantes = {}
        
        # Criar Senciantes
        self.simulacao._criar_senciantes_iniciais()
        
        # Verificar se foram criados
        self.assertEqual(len(self.simulacao.senciantes), 5)
        
        # Verificar tipos
        for senciante in self.simulacao.senciantes.values():
            self.assertIsInstance(senciante, Senciante)
    
    def test_iniciar_parar(self):
        """
        Testa o início e parada da simulação.
        """
        # Iniciar simulação
        sucesso = self.simulacao.iniciar()
        
        # Verificar se foi iniciada
        self.assertTrue(sucesso)
        self.assertTrue(self.simulacao.executando)
        self.assertFalse(self.simulacao.pausada)
        self.assertIsNotNone(self.simulacao.tempo_real_inicio)
        self.assertIsNotNone(self.simulacao.thread_simulacao)
        
        # Parar simulação
        sucesso = self.simulacao.parar()
        
        # Verificar se foi parada
        self.assertTrue(sucesso)
        self.assertFalse(self.simulacao.executando)
        self.assertFalse(self.simulacao.pausada)
        
        # Aguardar thread terminar
        if self.simulacao.thread_simulacao:
            self.simulacao.thread_simulacao.join(timeout=1.0)
    
    def test_pausar_retomar(self):
        """
        Testa a pausa e retomada da simulação.
        """
        # Iniciar simulação
        self.simulacao.iniciar()
        
        # Pausar simulação
        sucesso = self.simulacao.pausar()
        
        # Verificar se foi pausada
        self.assertTrue(sucesso)
        self.assertTrue(self.simulacao.executando)
        self.assertTrue(self.simulacao.pausada)
        
        # Retomar simulação
        sucesso = self.simulacao.retomar()
        
        # Verificar se foi retomada
        self.assertTrue(sucesso)
        self.assertTrue(self.simulacao.executando)
        self.assertFalse(self.simulacao.pausada)
        
        # Parar simulação
        self.simulacao.parar()
        
        # Aguardar thread terminar
        if self.simulacao.thread_simulacao:
            self.simulacao.thread_simulacao.join(timeout=1.0)
    
    def test_definir_velocidade(self):
        """
        Testa a definição da velocidade da simulação.
        """
        # Velocidade inicial
        self.assertEqual(self.simulacao.velocidade, 1.0)
        
        # Definir velocidade
        velocidade = self.simulacao.definir_velocidade(2.5)
        
        # Verificar se foi definida
        self.assertEqual(velocidade, 2.5)
        self.assertEqual(self.simulacao.velocidade, 2.5)
        
        # Testar limite inferior
        velocidade = self.simulacao.definir_velocidade(0.05)
        self.assertEqual(velocidade, 0.1)
        
        # Testar limite superior
        velocidade = self.simulacao.definir_velocidade(15.0)
        self.assertEqual(velocidade, 10.0)
    
    @patch("backend.simulacao.Simulacao._atualizar")
    def test_loop_simulacao(self, mock_atualizar):
        """
        Testa o loop principal da simulação.
        """
        # Configurar simulação para parar após algumas iterações
        def parar_apos_iteracoes():
            time.sleep(0.3)
            self.simulacao.executando = False
        
        # Iniciar thread para parar a simulação
        thread_parada = threading.Thread(target=parar_apos_iteracoes)
        thread_parada.daemon = True
        thread_parada.start()
        
        # Executar loop
        self.simulacao.executando = True
        self.simulacao._loop_simulacao()
        
        # Verificar se _atualizar foi chamado
        self.assertTrue(mock_atualizar.called)
        
        # Aguardar thread terminar
        thread_parada.join(timeout=1.0)
    
    def test_determinar_causa_morte(self):
        """
        Testa a determinação da causa de morte de um Senciante.
        """
        # Criar Senciante
        senciante = Senciante([0, 0])
        
        # Testar morte por velhice
        senciante.estado["idade"] = 50.0
        causa = self.simulacao._determinar_causa_morte(senciante)
        self.assertEqual(causa, "velhice")
        
        # Testar morte por fome
        senciante.estado["idade"] = 10.0
        senciante.necessidades["fome"] = 0.95
        causa = self.simulacao._determinar_causa_morte(senciante)
        self.assertEqual(causa, "fome")
        
        # Testar morte por sede
        senciante.necessidades["fome"] = 0.5
        senciante.necessidades["sede"] = 0.95
        causa = self.simulacao._determinar_causa_morte(senciante)
        self.assertEqual(causa, "sede")
        
        # Testar morte por doença
        senciante.necessidades["sede"] = 0.5
        senciante.estado["saude"] = 0.05
        causa = self.simulacao._determinar_causa_morte(senciante)
        self.assertEqual(causa, "doença")
    
    def test_adicionar_evento(self):
        """
        Testa a adição de eventos à lista de eventos pendentes.
        """
        # Estado inicial
        self.assertEqual(len(self.simulacao.eventos_pendentes), 0)
        
        # Adicionar evento de construção
        sucesso = self.simulacao.adicionar_evento("construcao", {
            "tipo": "abrigo_simples",
            "posicao": [10.0, 10.0],
            "tamanho": 1.0,
            "proprietario_id": "senciante_id"
        })
        
        # Verificar se foi adicionado
        self.assertTrue(sucesso)
        self.assertEqual(len(self.simulacao.eventos_pendentes), 1)
        self.assertEqual(self.simulacao.eventos_pendentes[0]["tipo"], "construcao")
        
        # Adicionar evento de tecnologia
        sucesso = self.simulacao.adicionar_evento("tecnologia", {
            "tecnologia": "fogo",
            "inventor_id": "senciante_id"
        })
        
        # Verificar se foi adicionada
        self.assertTrue(sucesso)
        self.assertEqual(len(self.simulacao.eventos_pendentes), 2)
        
        # Tentar adicionar evento inválido
        sucesso = self.simulacao.adicionar_evento("invalido", {})
        
        # Verificar que não foi adicionado
        self.assertFalse(sucesso)
        self.assertEqual(len(self.simulacao.eventos_pendentes), 2)
    
    def test_adicionar_acao_divina(self):
        """
        Testa a adição de ações divinas à lista de ações pendentes.
        """
        # Estado inicial
        self.assertEqual(len(self.simulacao.acoes_divinas_pendentes), 0)
        
        # Adicionar ação divina de clima
        sucesso = self.simulacao.adicionar_acao_divina("clima", {
            "alvo": "temperatura",
            "intensidade": 0.8,
            "duracao": 2.0
        })
        
        # Verificar se foi adicionada
        self.assertTrue(sucesso)
        self.assertEqual(len(self.simulacao.acoes_divinas_pendentes), 1)
        self.assertEqual(self.simulacao.acoes_divinas_pendentes[0]["tipo"], "clima")
        
        # Adicionar ação divina de recurso
        sucesso = self.simulacao.adicionar_acao_divina("recurso", {
            "tipo": "comida",
            "quantidade": 5.0,
            "posicao": [15.0, 15.0]
        })
        
        # Verificar se foi adicionada
        self.assertTrue(sucesso)
        self.assertEqual(len(self.simulacao.acoes_divinas_pendentes), 2)
        
        # Tentar adicionar ação inválida
        sucesso = self.simulacao.adicionar_acao_divina("invalida", {})
        
        # Verificar que não foi adicionada
        self.assertFalse(sucesso)
        self.assertEqual(len(self.simulacao.acoes_divinas_pendentes), 2)
    
    def test_registrar_callback(self):
        """
        Testa o registro de callbacks para eventos.
        """
        # Criar função de callback
        def callback_teste(simulacao):
            pass
        
        # Estado inicial
        self.assertEqual(len(self.simulacao.callbacks["atualizacao"]), 0)
        
        # Registrar callback
        sucesso = self.simulacao.registrar_callback("atualizacao", callback_teste)
        
        # Verificar se foi registrado
        self.assertTrue(sucesso)
        self.assertEqual(len(self.simulacao.callbacks["atualizacao"]), 1)
        
        # Tentar registrar para evento inválido
        sucesso = self.simulacao.registrar_callback("invalido", callback_teste)
        
        # Verificar que não foi registrado
        self.assertFalse(sucesso)
    
    def test_remover_callback(self):
        """
        Testa a remoção de callbacks registrados.
        """
        # Criar função de callback
        def callback_teste(simulacao):
            pass
        
        # Registrar callback
        self.simulacao.registrar_callback("atualizacao", callback_teste)
        
        # Verificar registro
        self.assertEqual(len(self.simulacao.callbacks["atualizacao"]), 1)
        
        # Remover callback
        sucesso = self.simulacao.remover_callback("atualizacao", callback_teste)
        
        # Verificar remoção
        self.assertTrue(sucesso)
        self.assertEqual(len(self.simulacao.callbacks["atualizacao"]), 0)
        
        # Tentar remover callback não registrado
        sucesso = self.simulacao.remover_callback("atualizacao", callback_teste)
        
        # Verificar que não foi removido
        self.assertFalse(sucesso)
    
    def test_obter_estado(self):
        """
        Testa a obtenção do estado atual da simulação.
        """
        # Obter estado
        estado = self.simulacao.obter_estado()
        
        # Verificar estrutura
        self.assertIsNotNone(estado)
        self.assertIsInstance(estado, dict)
        
        # Verificar campos principais
        campos = [
            "tempo_simulacao", "executando", "pausada", "velocidade",
            "estatisticas", "num_senciantes", "num_recursos", "num_construcoes", "clima"
        ]
        
        for campo in campos:
            self.assertIn(campo, estado)
    
    def test_to_dict(self):
        """
        Testa a conversão da Simulação para dicionário.
        """
        # Converter para dicionário
        simulacao_dict = self.simulacao.to_dict()
        
        # Verificar estrutura
        self.assertIsNotNone(simulacao_dict)
        self.assertIsInstance(simulacao_dict, dict)
        
        # Verificar campos principais
        campos = ["estado", "mundo", "senciantes", "historico"]
        
        for campo in campos:
            self.assertIn(campo, simulacao_dict)

if __name__ == "__main__":
    unittest.main()


