import unittest
import json
from unittest.mock import patch, MagicMock
from api_server import app

class TestAPI(unittest.TestCase):
    """
    Testes para a API RESTful.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        # Configurar cliente de teste
        self.app = app.test_client()
        self.app.testing = True
        
        # Mock para a simulação global
        self.mock_simulacao = MagicMock()
        
        # Configurar patch para a simulação global
        self.simulacao_patcher = patch("backend.api_server.simulacao", self.mock_simulacao)
        self.simulacao_patcher.start()
    
    def tearDown(self):
        """
        Limpeza após os testes.
        """
        # Parar patch
        self.simulacao_patcher.stop()
    
    def test_obter_status_nao_iniciada(self):
        """
        Testa a obtenção do status quando a simulação não está iniciada.
        """
        # Configurar mock
        patch("backend.api_server.simulacao", None).start()
        
        # Fazer requisição
        response = self.app.get("/api/estado")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["mensagem"], "Nenhuma simulação em execução")
    
    def test_obter_status_executando(self):
        """
        Testa a obtenção do status quando a simulação está em execução.
        """
        # Configurar mock
        self.mock_simulacao.executando = True
        self.mock_simulacao.pausada = False
        self.mock_simulacao.tempo_simulacao = 10.5
        self.mock_simulacao.velocidade = 1.5
        self.mock_simulacao.senciantes = {"id1": MagicMock(), "id2": MagicMock()}
        self.mock_simulacao.estatisticas = {"nascimentos": 5, "mortes": 2}
        
        # Fazer requisição
        response = self.app.get("/api/estado")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"]["executando"], True)
        self.assertEqual(data["status"]["pausada"], False)
        self.assertEqual(data["status"]["tempo_simulacao"], 10.5)
        self.assertEqual(data["status"]["velocidade"], 1.5)
        self.assertEqual(data["status"]["num_senciantes"], 2)
        self.assertEqual(data["status"]["estatisticas"]["nascimentos"], 5)
        self.assertEqual(data["status"]["estatisticas"]["mortes"], 2)
    
    def test_iniciar_simulacao(self):
        """
        Testa o início da simulação.
        """
        # Configurar mock
        self.mock_simulacao.iniciar.return_value = True
        
        # Fazer requisição
        response = self.app.post("/api/iniciar", 
                                json={"tamanho_mundo": [50, 50], "num_senciantes_iniciais": 10})
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["mensagem"], "Simulação iniciada com sucesso")
    
    def test_pausar_simulacao(self):
        """
        Testa a pausa da simulação.
        """
        # Configurar mock
        self.mock_simulacao.pausar.return_value = True
        
        # Fazer requisição
        response = self.app.post("/api/pausar")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["mensagem"], "Simulação pausada com sucesso")
    
    def test_retomar_simulacao(self):
        """
        Testa a retomada da simulação.
        """
        # Configurar mock
        self.mock_simulacao.retomar.return_value = True
        
        # Fazer requisição
        response = self.app.post("/api/retomar")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["mensagem"], "Simulação retomada com sucesso")
    
    def test_parar_simulacao(self):
        """
        Testa a parada da simulação.
        """
        # Configurar mock
        self.mock_simulacao.parar.return_value = True
        
        # Fazer requisição
        response = self.app.post("/api/parar")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["mensagem"], "Simulação parada com sucesso")
    
    def test_acelerar_simulacao(self):
        """
        Testa a aceleração da simulação.
        """
        # Configurar mock
        self.mock_simulacao.definir_velocidade.return_value = 2.5
        
        # Fazer requisição
        response = self.app.post("/api/acelerar", json={"fator": 2.5})
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["velocidade"], 2.5)
        self.assertEqual(data["mensagem"], "Simulação acelerada por um fator de 2.5")
    
    def test_obter_estado(self):
        """
        Testa a obtenção do estado da simulação.
        """
        # Configurar mock
        self.mock_simulacao.obter_estado.return_value = {
            "tempo_simulacao": 15.0,
            "executando": True,
            "pausada": False,
            "velocidade": 1.0,
            "estatisticas": {"nascimentos": 10, "mortes": 5},
            "num_senciantes": 15,
            "num_recursos": 20,
            "num_construcoes": 5,
            "clima": {"temperatura": 0.7, "umidade": 0.5}
        }
        
        # Fazer requisição
        response = self.app.get("/api/simulacao/estado")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["estado"]["tempo_simulacao"], 15.0)
        self.assertEqual(data["estado"]["executando"], True)
        self.assertEqual(data["estado"]["num_senciantes"], 15)
        self.assertEqual(data["estado"]["clima"]["temperatura"], 0.7)
    
    def test_obter_mundo(self):
        """
        Testa a obtenção dos dados do mundo.
        """
        # Configurar mock
        self.mock_simulacao.obter_mundo.return_value = {
            "tamanho": [50, 50],
            "clima": {"temperatura": 0.7, "umidade": 0.5},
            "recursos": {"id1": {"tipo": "comida", "quantidade": 10.0}},
            "construcoes": {"id1": {"tipo": "abrigo", "tamanho": 1.0}},
            "biomas": {"floresta": 0.3, "planicie": 0.5, "montanha": 0.2}
        }
        
        # Fazer requisição
        response = self.app.get("/api/mundo")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["mundo"]["tamanho"], [50, 50])
        self.assertEqual(data["mundo"]["clima"]["temperatura"], 0.7)
        self.assertEqual(data["mundo"]["recursos"]["id1"]["tipo"], "comida")
        self.assertEqual(data["mundo"]["construcoes"]["id1"]["tipo"], "abrigo")
        self.assertEqual(data["mundo"]["biomas"]["floresta"], 0.3)
    
    def test_obter_clima(self):
        """
        Testa a obtenção dos dados do clima.
        """
        # Configurar mock
        self.mock_simulacao.mundo.clima.to_dict.return_value = {
            "temperatura": 0.7,
            "umidade": 0.5,
            "precipitacao": 0.2,
            "vento": 0.3,
            "eventos_climaticos": [{"tipo": "chuva", "intensidade": 0.5}]
        }
        
        # Fazer requisição
        response = self.app.get("/api/mundo/clima")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["clima"]["temperatura"], 0.7)
        self.assertEqual(data["clima"]["umidade"], 0.5)
        self.assertEqual(data["clima"]["precipitacao"], 0.2)
        self.assertEqual(data["clima"]["vento"], 0.3)
        self.assertEqual(data["clima"]["eventos_climaticos"][0]["tipo"], "chuva")
    
    def test_obter_senciantes(self):
        """
        Testa a obtenção de todos os Senciantes.
        """
        # Configurar mock
        self.mock_simulacao.obter_todos_senciantes.return_value = {
            "id1": {
                "id": "id1",
                "posicao": [10.0, 10.0],
                "necessidades": {"fome": 0.3, "sede": 0.2},
                "estado": {"idade": 5.0, "saude": 0.9},
                "habilidades": {"coleta": 0.5, "construcao": 0.3}
            },
            "id2": {
                "id": "id2",
                "posicao": [15.0, 15.0],
                "necessidades": {"fome": 0.1, "sede": 0.1},
                "estado": {"idade": 2.0, "saude": 1.0},
                "habilidades": {"coleta": 0.2, "construcao": 0.1}
            }
        }
        
        # Fazer requisição
        response = self.app.get("/api/senciantes")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(len(data["senciantes"]), 2)
        self.assertEqual(data["senciantes"]["id1"]["posicao"], [10.0, 10.0])
        self.assertEqual(data["senciantes"]["id1"]["necessidades"]["fome"], 0.3)
        self.assertEqual(data["senciantes"]["id2"]["estado"]["idade"], 2.0)
    
    def test_obter_senciante(self):
        """
        Testa a obtenção de um Senciante específico.
        """
        # Configurar mock
        self.mock_simulacao.obter_senciante.return_value = {
            "id": "id1",
            "posicao": [10.0, 10.0],
            "necessidades": {"fome": 0.3, "sede": 0.2},
            "estado": {"idade": 5.0, "saude": 0.9},
            "habilidades": {"coleta": 0.5, "construcao": 0.3}
        }
        
        # Fazer requisição
        response = self.app.get("/api/senciantes/id1")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["senciante"]["id"], "id1")
        self.assertEqual(data["senciante"]["posicao"], [10.0, 10.0])
        self.assertEqual(data["senciante"]["necessidades"]["fome"], 0.3)
        self.assertEqual(data["senciante"]["estado"]["idade"], 5.0)
        self.assertEqual(data["senciante"]["habilidades"]["coleta"], 0.5)
    
    def test_obter_senciante_nao_encontrado(self):
        """
        Testa a obtenção de um Senciante que não existe.
        """
        # Configurar mock
        self.mock_simulacao.obter_senciante.return_value = None
        
        # Fazer requisição
        response = self.app.get("/api/senciantes/id_inexistente")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data["sucesso"])
        self.assertEqual(data["mensagem"], "Senciante não encontrado")
    
    def test_obter_recursos(self):
        """
        Testa a obtenção de todos os recursos.
        """
        # Configurar mock
        self.mock_simulacao.obter_todos_recursos.return_value = {
            "id1": {
                "id": "id1",
                "tipo": "comida",
                "posicao": [10.0, 10.0],
                "quantidade": 5.0
            },
            "id2": {
                "id": "id2",
                "tipo": "agua",
                "posicao": [15.0, 15.0],
                "quantidade": 10.0
            }
        }
        
        # Fazer requisição
        response = self.app.get("/api/recursos")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(len(data["recursos"]), 2)
        self.assertEqual(data["recursos"]["id1"]["tipo"], "comida")
        self.assertEqual(data["recursos"]["id1"]["quantidade"], 5.0)
        self.assertEqual(data["recursos"]["id2"]["tipo"], "agua")
    
    def test_obter_recurso(self):
        """
        Testa a obtenção de um recurso específico.
        """
        # Configurar mock
        self.mock_simulacao.obter_recurso.return_value = {
            "id": "id1",
            "tipo": "comida",
            "posicao": [10.0, 10.0],
            "quantidade": 5.0
        }
        
        # Fazer requisição
        response = self.app.get("/api/recursos/id1")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["recurso"]["id"], "id1")
        self.assertEqual(data["recurso"]["tipo"], "comida")
        self.assertEqual(data["recurso"]["posicao"], [10.0, 10.0])
        self.assertEqual(data["recurso"]["quantidade"], 5.0)
    
    def test_obter_recurso_nao_encontrado(self):
        """
        Testa a obtenção de um recurso que não existe.
        """
        # Configurar mock
        self.mock_simulacao.obter_recurso.return_value = None
        
        # Fazer requisição
        response = self.app.get("/api/recursos/id_inexistente")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data["sucesso"])
        self.assertEqual(data["mensagem"], "Recurso não encontrado")
    
    def test_obter_construcoes(self):
        """
        Testa a obtenção de todas as construções.
        """
        # Configurar mock
        self.mock_simulacao.obter_todas_construcoes.return_value = {
            "id1": {
                "id": "id1",
                "tipo": "abrigo",
                "posicao": [10.0, 10.0],
                "tamanho": 1.0,
                "proprietario_id": "senciante_id"
            },
            "id2": {
                "id": "id2",
                "tipo": "armazem",
                "posicao": [15.0, 15.0],
                "tamanho": 2.0,
                "proprietario_id": "senciante_id"
            }
        }
        
        # Fazer requisição
        response = self.app.get("/api/construcoes")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(len(data["construcoes"]), 2)
        self.assertEqual(data["construcoes"]["id1"]["tipo"], "abrigo")
        self.assertEqual(data["construcoes"]["id1"]["tamanho"], 1.0)
        self.assertEqual(data["construcoes"]["id2"]["tipo"], "armazem")
    
    def test_obter_construcao(self):
        """
        Testa a obtenção de uma construção específica.
        """
        # Configurar mock
        self.mock_simulacao.obter_construcao.return_value = {
            "id": "id1",
            "tipo": "abrigo",
            "posicao": [10.0, 10.0],
            "tamanho": 1.0,
            "proprietario_id": "senciante_id"
        }
        
        # Fazer requisição
        response = self.app.get("/api/construcoes/id1")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["construcao"]["id"], "id1")
        self.assertEqual(data["construcao"]["tipo"], "abrigo")
        self.assertEqual(data["construcao"]["posicao"], [10.0, 10.0])
        self.assertEqual(data["construcao"]["tamanho"], 1.0)
        self.assertEqual(data["construcao"]["proprietario_id"], "senciante_id")
    
    def test_obter_construcao_nao_encontrada(self):
        """
        Testa a obtenção de uma construção que não existe.
        """
        # Configurar mock
        self.mock_simulacao.obter_construcao.return_value = None
        
        # Fazer requisição
        response = self.app.get("/api/construcoes/id_inexistente")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data["sucesso"])
        self.assertEqual(data["mensagem"], "Construção não encontrada")
    
    def test_obter_historico(self):
        """
        Testa a obtenção do histórico do mundo.
        """
        # Configurar mock
        self.mock_simulacao.mundo.historico.to_dict.return_value = {
            "eventos": [
                {"tipo": "nascimento", "tempo": 0.0, "senciante_id": "s1"},
                {"tipo": "morte", "tempo": 10.0, "senciante_id": "s2"}
            ],
            "estatisticas": [
                {"tempo": 0.0, "num_senciantes": 10},
                {"tempo": 10.0, "num_senciantes": 8}
            ]
        }
        
        # Fazer requisição
        response = self.app.get("/api/historico")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(len(data["historico"]["eventos"]), 2)
        self.assertEqual(data["historico"]["eventos"][0]["tipo"], "nascimento")
        self.assertEqual(len(data["historico"]["estatisticas"]), 2)
        self.assertEqual(data["historico"]["estatisticas"][0]["num_senciantes"], 10)
    
    def test_acao_divina_clima(self):
        """
        Testa a ação divina de clima.
        """
        # Configurar mock
        self.mock_simulacao.adicionar_acao_divina.return_value = True
        
        # Fazer requisição
        response = self.app.post("/api/acoes/divina/clima", json={
            "alvo": "temperatura",
            "intensidade": 0.8,
            "duracao": 2.0
        })
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["mensagem"], "Ação divina adicionada com sucesso")
    
    def test_acao_divina_recurso(self):
        """
        Testa a ação divina de recurso.
        """
        # Configurar mock
        self.mock_simulacao.adicionar_acao_divina.return_value = True
        
        # Fazer requisição
        response = self.app.post("/api/acoes/divina/recurso", json={
            "tipo": "comida",
            "quantidade": 5.0,
            "posicao": [10.0, 10.0]
        })
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["mensagem"], "Ação divina adicionada com sucesso")
    
    def test_acao_divina_artefato(self):
        """
        Testa a ação divina de artefato.
        """
        # Configurar mock
        self.mock_simulacao.adicionar_acao_divina.return_value = True
        
        # Fazer requisição
        response = self.app.post("/api/acoes/divina/artefato", json={
            "tipo": "conhecimento",
            "posicao": [10.0, 10.0]
        })
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["mensagem"], "Ação divina adicionada com sucesso")
    
    def test_laboratorio_pausar(self):
        """
        Testa a pausa da simulação no modo laboratório.
        """
        # Configurar mock
        self.mock_simulacao.pausar.return_value = True
        
        # Fazer requisição
        response = self.app.post("/api/laboratorio/pausar")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["mensagem"], "Simulação pausada com sucesso")
    
    def test_laboratorio_retomar(self):
        """
        Testa a retomada da simulação no modo laboratório.
        """
        # Configurar mock
        self.mock_simulacao.retomar.return_value = True
        
        # Fazer requisição
        response = self.app.post("/api/laboratorio/retomar")
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["mensagem"], "Simulação retomada com sucesso")
    
    def test_laboratorio_acelerar(self):
        """
        Testa a aceleração da simulação no modo laboratório.
        """
        # Configurar mock
        self.mock_simulacao.definir_velocidade.return_value = 2.0
        
        # Fazer requisição
        response = self.app.post("/api/laboratorio/acelerar", json={"fator": 2.0})
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["velocidade"], 2.0)
        self.assertEqual(data["mensagem"], "Velocidade acelerada para 2.0")
    
    def test_laboratorio_desacelerar(self):
        """
        Testa a desaceleração da simulação no modo laboratório.
        """
        # Configurar mock
        self.mock_simulacao.definir_velocidade.return_value = 0.5
        
        # Fazer requisição
        response = self.app.post("/api/laboratorio/desacelerar", json={"fator": 2.0})
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["velocidade"], 0.5)
        self.assertEqual(data["mensagem"], "Velocidade desacelerada para 0.5")
    
    def test_laboratorio_alterar_variavel(self):
        """
        Testa a alteração de uma variável da simulação no modo laboratório.
        """
        # Configurar mock
        self.mock_simulacao.alterar_variavel.return_value = True
        
        # Fazer requisição
        response = self.app.post("/api/laboratorio/alterar_variavel", json={
            "categoria": "clima",
            "variavel": "temperatura",
            "valor": 0.8
        })
        
        # Verificar resposta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["sucesso"])
        self.assertEqual(data["mensagem"], "Variável clima.temperatura alterada para 0.8")

if __name__ == "__main__":
    unittest.main()


