"""
Módulo de utilitários para o jogo "O Mundo dos Senciantes".
Contém funções auxiliares usadas em várias partes do sistema.
"""

import random
import uuid
import math
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mundo_senciantes.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def gerar_id():
    """
    Gera um ID único para entidades do jogo.
    
    Returns:
        str: ID único no formato de string.
    """
    return str(uuid.uuid4())

def calcular_distancia(pos1, pos2):
    """
    Calcula a distância euclidiana entre duas posições.
    
    Args:
        pos1 (list): Posição 1 [x, y].
        pos2 (list): Posição 2 [x, y].
        
    Returns:
        float: Distância entre as posições.
    """
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def posicao_aleatoria(tamanho_mundo):
    """
    Gera uma posição aleatória dentro dos limites do mundo.
    
    Args:
        tamanho_mundo (list): Tamanho do mundo [largura, altura].
        
    Returns:
        list: Posição aleatória [x, y].
    """
    return [
        random.uniform(0, tamanho_mundo[0]),
        random.uniform(0, tamanho_mundo[1])
    ]

def limitar_valor(valor, minimo, maximo):
    """
    Limita um valor dentro de um intervalo.
    
    Args:
        valor (float): Valor a ser limitado.
        minimo (float): Valor mínimo permitido.
        maximo (float): Valor máximo permitido.
        
    Returns:
        float: Valor limitado.
    """
    return max(minimo, min(maximo, valor))

def chance(probabilidade):
    """
    Determina se um evento ocorre com base em uma probabilidade.
    
    Args:
        probabilidade (float): Probabilidade do evento ocorrer (0.0 a 1.0).
        
    Returns:
        bool: True se o evento ocorre, False caso contrário.
    """
    return random.random() < probabilidade

def valor_aleatorio_entre(minimo, maximo):
    """
    Gera um valor aleatório entre um mínimo e um máximo.
    
    Args:
        minimo (float): Valor mínimo.
        maximo (float): Valor máximo.
        
    Returns:
        float: Valor aleatório entre minimo e maximo.
    """
    return random.uniform(minimo, maximo)

def mover_em_direcao(posicao_atual, posicao_alvo, velocidade):
    """
    Move uma entidade em direção a uma posição alvo.
    
    Args:
        posicao_atual (list): Posição atual [x, y].
        posicao_alvo (list): Posição alvo [x, y].
        velocidade (float): Velocidade de movimento.
        
    Returns:
        list: Nova posição [x, y].
    """
    distancia = calcular_distancia(posicao_atual, posicao_alvo)
    
    # Se já está no alvo ou muito próximo
    if distancia < 0.1:
        return posicao_alvo
    
    # Calcular direção
    direcao = [
        (posicao_alvo[0] - posicao_atual[0]) / distancia,
        (posicao_alvo[1] - posicao_atual[1]) / distancia
    ]
    
    # Calcular nova posição
    movimento = min(velocidade, distancia)
    nova_posicao = [
        posicao_atual[0] + direcao[0] * movimento,
        posicao_atual[1] + direcao[1] * movimento
    ]
    
    return nova_posicao

def timestamp_atual():
    """
    Obtém o timestamp atual.
    
    Returns:
        str: Timestamp atual no formato ISO.
    """
    return datetime.now().isoformat()

def registrar_evento(tipo, descricao, tempo, envolvidos=None):
    """
    Cria um objeto de evento para registro no histórico.
    
    Args:
        tipo (str): Tipo do evento.
        descricao (str): Descrição do evento.
        tempo (float): Tempo da simulação em que o evento ocorreu.
        envolvidos (list, optional): Lista de IDs de entidades envolvidas no evento.
        
    Returns:
        dict: Objeto de evento.
    """
    if envolvidos is None:
        envolvidos = []
        
    return {
        "id": gerar_id(),
        "tipo": tipo,
        "descricao": descricao,
        "tempo": tempo,
        "timestamp": timestamp_atual(),
        "envolvidos": envolvidos
    }

def calcular_compatibilidade_genetica(genoma1, genoma2):
    """
    Calcula a compatibilidade genética entre dois genomas.
    Usado para determinar se dois Senciantes podem se reproduzir.
    
    Args:
        genoma1 (dict): Genoma do primeiro Senciante.
        genoma2 (dict): Genoma do segundo Senciante.
        
    Returns:
        float: Valor de compatibilidade entre 0.0 e 1.0.
    """
    # Implementação simples: média da diferença entre genes
    diferenca_total = 0
    num_genes = 0
    
    for gene in genoma1["genes"]:
        if gene in genoma2["genes"]:
            diferenca = abs(genoma1["genes"][gene] - genoma2["genes"][gene])
            diferenca_total += diferenca
            num_genes += 1
    
    # Se não há genes em comum, retorna compatibilidade mínima
    if num_genes == 0:
        return 0.0
    
    # Quanto menor a diferença, maior a compatibilidade
    diferenca_media = diferenca_total / num_genes
    compatibilidade = 1.0 - min(1.0, diferenca_media)
    
    return compatibilidade

def determinar_complexidade_comunicacao(assunto):
    """
    Determina a complexidade de um assunto para comunicação entre Senciantes.
    
    Args:
        assunto (dict): Informações sobre o assunto a ser comunicado.
        
    Returns:
        float: Valor de complexidade entre 0.0 e 1.0.
    """
    complexidades = {
        "necessidade": 0.1,  # Comunicar fome, sede, etc.
        "localizacao": 0.2,  # Comunicar onde há recursos
        "perigo": 0.3,       # Comunicar sobre ameaças
        "tecnologia": 0.5,   # Comunicar sobre ferramentas ou construções
        "social": 0.4,       # Comunicar sobre relações sociais
        "abstrato": 0.8      # Comunicar conceitos abstratos
    }
    
    tipo = assunto.get("tipo", "necessidade")
    complexidade_base = complexidades.get(tipo, 0.5)
    
    # Ajustar com base em outros fatores
    if "detalhes" in assunto:
        complexidade_base += len(assunto["detalhes"]) * 0.05
    
    return min(1.0, complexidade_base)

def log_info(mensagem):
    """
    Registra uma mensagem de informação no log.
    
    Args:
        mensagem (str): Mensagem a ser registrada.
    """
    logger.info(mensagem)

def log_warning(mensagem):
    """
    Registra uma mensagem de aviso no log.
    
    Args:
        mensagem (str): Mensagem a ser registrada.
    """
    logger.warning(mensagem)

def log_error(mensagem):
    """
    Registra uma mensagem de erro no log.
    
    Args:
        mensagem (str): Mensagem a ser registrada.
    """
    logger.error(mensagem)

