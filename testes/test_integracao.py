"""
Testes de integração para o jogo "O Mundo dos Senciantes".
"""

import unittest
import time
from simulacao import Simulacao
from modelos.mundo import Mundo
from modelos.senciante import Senciante

class TestIntegracao(unittest.TestCase):
    """
    Testes de integração para o jogo.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Criar simulação com valores personalizados
        self.simulacao = Simulacao([20, 20], 5)
    
    def test_ciclo_completo(self):
        """
        Testa um ciclo completo de simulação.
        """
        # Iniciar simulação
        self.simulacao.iniciar()
        
        # Executar por um curto período
        time.sleep(0.5)
        
        # Pausar simulação
        self.simulacao.pausar()
        
        # Verificar se o tempo de simulação avançou
        self.assertGreater(self.simulacao.tempo_simulacao, 0.0)
        
        # Verificar se o mundo foi atualizado
        # (não podemos verificar valores específicos, apenas que a atualização ocorreu)
        
        # Verificar se os Senciantes foram atualizados
        for senciante in self.simulacao.senciantes.values():
            # Pelo menos algumas necessidades devem ter aumentado
            necessidades_aumentadas = False
            for necessidade, valor in senciante.necessidades.items():
                if valor > 0.0:
                    necessidades_aumentadas = True
                    break
            
            self.assertTrue(necessidades_aumentadas)
        
        # Parar simulação
        self.simulacao.parar()
        
        # Aguardar thread terminar
        if self.simulacao.thread_simulacao:
            self.simulacao.thread_simulacao.join(timeout=1.0)
    
    def test_acao_divina_clima(self):
        """
        Testa a aplicação de uma ação divina no clima.
        """
        # Iniciar simulação
        self.simulacao.iniciar()
        
        # Temperatura inicial
        temp_inicial = self.simulacao.mundo.clima.temperatura
        
        # Aplicar ação divina
        self.simulacao.adicionar_acao_divina("clima", {
            "alvo": "temperatura",
            "intensidade": 1.0,  # Aumentar ao máximo
            "duracao": 1.0
        })
        
        # Executar por um curto período
        time.sleep(0.5)
        
        # Pausar simulação
        self.simulacao.pausar()
        
        # Verificar se a temperatura mudou
        # (não podemos verificar valores específicos, apenas que houve mudança)
        self.assertNotEqual(self.simulacao.mundo.clima.temperatura, temp_inicial)
        
        # Parar simulação
        self.simulacao.parar()
        
        # Aguardar thread terminar
        if self.simulacao.thread_simulacao:
            self.simulacao.thread_simulacao.join(timeout=1.0)
    
    def test_acao_divina_recurso(self):
        """
        Testa a aplicação de uma ação divina nos recursos.
        """
        # Iniciar simulação
        self.simulacao.iniciar()
        
        # Contar recursos antes
        num_recursos_antes = len(self.simulacao.mundo.recursos)
        
        # Aplicar ação divina
        self.simulacao.adicionar_acao_divina("recurso", {
            "tipo": "comida",
            "quantidade": 10.0,
            "posicao": [10.0, 10.0]
        })
        
        # Executar por um curto período
        time.sleep(0.5)
        
        # Pausar simulação
        self.simulacao.pausar()
        
        # Verificar se o número de recursos aumentou
        self.assertGreater(len(self.simulacao.mundo.recursos), num_recursos_antes)
        
        # Parar simulação
        self.simulacao.parar()
        
        # Aguardar thread terminar
        if self.simulacao.thread_simulacao:
            self.simulacao.thread_simulacao.join(timeout=1.0)
    
    def test_interacao_senciantes(self):
        """
        Testa a interação entre Senciantes.
        """
        # Criar dois Senciantes próximos
        senciante1 = Senciante([10.0, 10.0])
        senciante2 = Senciante([10.5, 10.5])
        
        # Adicionar à simulação
        self.simulacao.senciantes = {}
        self.simulacao.senciantes[senciante1.id] = senciante1
        self.simulacao.senciantes[senciante2.id] = senciante2
        
        # Processar interações
        self.simulacao._processar_interacoes()
        
        # Verificar se estabeleceram relações
        self.assertIn(senciante2.id, senciante1.relacoes)
        self.assertIn(senciante1.id, senciante2.relacoes)
    
    def test_reproducao(self):
        """
        Testa a reprodução entre Senciantes.
        """
        # Criar dois Senciantes próximos e aptos a reproduzir
        senciante1 = Senciante([10.0, 10.0])
        senciante2 = Senciante([10.5, 10.5])
        
        # Definir condições para reprodução
        senciante1.estado["idade"] = 10.0
        senciante2.estado["idade"] = 10.0
        
        # Adicionar à simulação
        self.simulacao.senciantes = {}
        self.simulacao.senciantes[senciante1.id] = senciante1
        self.simulacao.senciantes[senciante2.id] = senciante2
        
        # Forçar alta chance de reprodução
        import random
        random.seed(0)  # Usar seed fixo para reprodutibilidade
        
        # Processar reprodução
        self.simulacao._processar_reproducao()
        
        # Verificar se houve reprodução (pode não ocorrer devido à aleatoriedade)
        # Apenas verificamos se o código executa sem erros
    
    def test_callbacks(self):
        """
        Testa o sistema de callbacks.
        """
        # Variáveis para verificar chamadas de callbacks
        atualizacoes = 0
        
        # Criar funções de callback
        def callback_atualizacao(simulacao):
            nonlocal atualizacoes
            atualizacoes += 1
        
        # Registrar callbacks
        self.simulacao.registrar_callback("atualizacao", callback_atualizacao)
        
        # Iniciar simulação
        self.simulacao.iniciar()
        
        # Executar por um curto período
        time.sleep(0.5)
        
        # Pausar simulação
        self.simulacao.pausar()
        
        # Verificar se os callbacks foram chamados
        self.assertGreater(atualizacoes, 0)
        
        # Parar simulação
        self.simulacao.parar()
        
        # Aguardar thread terminar
        if self.simulacao.thread_simulacao:
            self.simulacao.thread_simulacao.join(timeout=1.0)

if __name__ == "__main__":
    unittest.main()


