"""
Módulo que define a classe Clima para o jogo "O Mundo dos Senciantes".
O Clima representa as condições climáticas do mundo e seus efeitos.
"""

import random
from utils.config import (
    CLIMATE_BASE_TEMPERATURE, CLIMATE_TEMPERATURE_RANGE,
    CLIMATE_HUMIDITY_RANGE, CLIMATE_PRECIPITATION_RANGE,
    CLIMATE_WIND_RANGE, CLIMATE_CHANGE_RATE
)
from utils.helpers import limitar_valor, chance

class Clima:
    """
    Classe que representa o clima do mundo.
    Controla temperatura, umidade, precipitação, vento e eventos climáticos.
    """
    
    def __init__(self):
        """
        Inicializa um novo Clima com valores padrão.
        """
        self.temperatura = CLIMATE_BASE_TEMPERATURE  # Celsius
        self.umidade = 0.5  # 0-1
        self.precipitacao = 0.0  # 0-1
        self.vento = 5.0  # km/h
        self.eventos_climaticos = []  # Lista de eventos ativos
        self.ciclo_dia_noite = 0.0  # 0-24 (horas)
    
    def atualizar(self, delta_tempo):
        """
        Atualiza o clima com base no tempo decorrido.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Atualizar ciclo dia/noite
        self.ciclo_dia_noite = (self.ciclo_dia_noite + delta_tempo) % 24
        
        # Variações naturais
        self.temperatura += random.uniform(-0.1, 0.1) * delta_tempo * CLIMATE_CHANGE_RATE
        self.umidade += random.uniform(-0.02, 0.02) * delta_tempo * CLIMATE_CHANGE_RATE
        self.precipitacao += random.uniform(-0.05, 0.05) * delta_tempo * CLIMATE_CHANGE_RATE
        self.vento += random.uniform(-0.5, 0.5) * delta_tempo * CLIMATE_CHANGE_RATE
        
        # Limitar valores
        self.temperatura = limitar_valor(self.temperatura, CLIMATE_TEMPERATURE_RANGE[0], CLIMATE_TEMPERATURE_RANGE[1])
        self.umidade = limitar_valor(self.umidade, CLIMATE_HUMIDITY_RANGE[0], CLIMATE_HUMIDITY_RANGE[1])
        self.precipitacao = limitar_valor(self.precipitacao, CLIMATE_PRECIPITATION_RANGE[0], CLIMATE_PRECIPITATION_RANGE[1])
        self.vento = limitar_valor(self.vento, CLIMATE_WIND_RANGE[0], CLIMATE_WIND_RANGE[1])
        
        # Gerar eventos climáticos
        self._gerar_eventos_climaticos(delta_tempo)
        
        # Atualizar eventos ativos
        self._atualizar_eventos_climaticos(delta_tempo)
    
    def _gerar_eventos_climaticos(self, delta_tempo):
        """
        Gera eventos climáticos aleatórios com base nas condições atuais.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        # Chance de chuva baseada na umidade
        if self.umidade > 0.7 and self.precipitacao < 0.3 and chance(0.05 * delta_tempo):
            self.eventos_climaticos.append({
                "tipo": "chuva",
                "intensidade": random.uniform(0.3, 0.8),
                "duracao_restante": random.uniform(1.0, 3.0)  # Horas
            })
            self.precipitacao = 0.5  # Aumentar precipitação
        
        # Chance de tempestade baseada na umidade e vento
        if self.umidade > 0.8 and self.vento > 20.0 and chance(0.02 * delta_tempo):
            self.eventos_climaticos.append({
                "tipo": "tempestade",
                "intensidade": random.uniform(0.6, 1.0),
                "duracao_restante": random.uniform(0.5, 2.0)  # Horas
            })
            self.precipitacao = 0.8  # Aumentar precipitação
            self.vento += 10.0  # Aumentar vento
        
        # Chance de nevasca baseada na temperatura
        if self.temperatura < 0 and self.umidade > 0.6 and chance(0.01 * delta_tempo):
            self.eventos_climaticos.append({
                "tipo": "nevasca",
                "intensidade": random.uniform(0.4, 0.9),
                "duracao_restante": random.uniform(2.0, 6.0)  # Horas
            })
            self.precipitacao = 0.7  # Aumentar precipitação
        
        # Chance de onda de calor baseada na temperatura
        if self.temperatura > 30 and chance(0.01 * delta_tempo):
            self.eventos_climaticos.append({
                "tipo": "onda_de_calor",
                "intensidade": random.uniform(0.5, 0.9),
                "duracao_restante": random.uniform(12.0, 48.0)  # Horas
            })
            self.temperatura += 5.0  # Aumentar temperatura
            self.umidade -= 0.2  # Diminuir umidade
    
    def _atualizar_eventos_climaticos(self, delta_tempo):
        """
        Atualiza os eventos climáticos ativos, removendo os que terminaram.
        
        Args:
            delta_tempo (float): Tempo decorrido desde a última atualização em horas.
        """
        eventos_ativos = []
        
        for evento in self.eventos_climaticos:
            # Reduzir duração restante
            evento["duracao_restante"] -= delta_tempo
            
            # Manter apenas eventos não expirados
            if evento["duracao_restante"] > 0:
                eventos_ativos.append(evento)
            else:
                # Reverter alguns efeitos quando o evento termina
                if evento["tipo"] == "onda_de_calor":
                    self.temperatura -= 3.0  # Reduzir temperatura
                    self.umidade += 0.1  # Aumentar umidade
        
        self.eventos_climaticos = eventos_ativos
    
    def aplicar_acao_divina(self, alvo, intensidade, duracao):
        """
        Aplica uma ação divina ao clima.
        
        Args:
            alvo (str): Alvo da ação ("temperatura", "precipitacao", "vento").
            intensidade (float): Intensidade da ação (0.0 a 1.0).
            duracao (float): Duração da ação em horas.
        """
        if alvo == "temperatura":
            # Calcular mudança de temperatura (-20 a +20 graus)
            mudanca = (intensidade * 2 - 1) * 20
            
            # Aplicar mudança gradualmente
            def efeito(dt):
                self.temperatura += mudanca * min(1.0, dt / duracao)
            
            # Registrar evento climático
            self.eventos_climaticos.append({
                "tipo": "alteracao_temperatura",
                "intensidade": intensidade,
                "duracao_restante": duracao,
                "efeito": efeito
            })
        
        elif alvo == "precipitacao":
            # Calcular mudança de precipitação
            mudanca = intensidade - self.precipitacao
            
            # Aplicar mudança gradualmente
            def efeito(dt):
                self.precipitacao += mudanca * min(1.0, dt / duracao)
            
            # Registrar evento climático
            self.eventos_climaticos.append({
                "tipo": "alteracao_precipitacao",
                "intensidade": intensidade,
                "duracao_restante": duracao,
                "efeito": efeito
            })
        
        elif alvo == "vento":
            # Calcular mudança de vento (0 a 100 km/h)
            mudanca = intensidade * 100 - self.vento
            
            # Aplicar mudança gradualmente
            def efeito(dt):
                self.vento += mudanca * min(1.0, dt / duracao)
            
            # Registrar evento climático
            self.eventos_climaticos.append({
                "tipo": "alteracao_vento",
                "intensidade": intensidade,
                "duracao_restante": duracao,
                "efeito": efeito
            })
    
    def obter_estado_atual(self):
        """
        Obtém o estado atual do clima.
        
        Returns:
            dict: Estado atual do clima.
        """
        # Determinar período do dia
        if 6 <= self.ciclo_dia_noite < 18:
            periodo = "dia"
        else:
            periodo = "noite"
        
        # Determinar condição climática
        condicao = "limpo"
        for evento in self.eventos_climaticos:
            if evento["tipo"] in ["chuva", "tempestade", "nevasca"]:
                condicao = evento["tipo"]
                break
        
        return {
            "temperatura": self.temperatura,
            "umidade": self.umidade,
            "precipitacao": self.precipitacao,
            "vento": self.vento,
            "ciclo_dia_noite": self.ciclo_dia_noite,
            "periodo": periodo,
            "condicao": condicao,
            "eventos_ativos": [
                {
                    "tipo": e["tipo"],
                    "intensidade": e["intensidade"],
                    "duracao_restante": e["duracao_restante"]
                } for e in self.eventos_climaticos
            ]
        }
    
    def to_dict(self):
        """
        Converte o clima para um dicionário.
        
        Returns:
            dict: Representação do clima como dicionário.
        """
        return self.obter_estado_atual()


