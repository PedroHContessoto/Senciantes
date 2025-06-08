"""
Módulo de configuração para o jogo "O Mundo dos Senciantes".
Contém constantes e configurações globais para o motor de simulação.
"""

# Configurações do servidor
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5000

# Configurações da simulação
DEFAULT_WORLD_SIZE = [100, 100]  # Tamanho padrão do mundo [largura, altura]
DEFAULT_INITIAL_SENCIANTES = 10  # Número inicial de Senciantes
DEFAULT_SIMULATION_SPEED = 1.0   # Velocidade padrão da simulação (1.0 = tempo real)
DEFAULT_UPDATE_INTERVAL = 0.1    # Intervalo de atualização da simulação em segundos

# Configurações de Senciantes
SENCIANTE_MAX_AGE = 48.0         # Idade máxima em horas (2 dias)
SENCIANTE_REPRODUCTION_MIN_AGE = 5.0  # Idade mínima para reprodução em horas
SENCIANTE_NEEDS_DECAY_RATES = {
    "fome": 0.05,                # Taxa de aumento da fome por hora
    "sede": 0.1,                 # Taxa de aumento da sede por hora
    "sono": 0.03,                # Taxa de diminuição da energia por hora
    "higiene": 0.02,             # Taxa de aumento da necessidade de higiene por hora
    "social": 0.01               # Taxa de aumento da necessidade social por hora
}
SENCIANTE_NEEDS_CRITICAL_THRESHOLDS = {
    "fome": 0.9,                 # Limiar crítico para fome (morte)
    "sede": 0.9,                 # Limiar crítico para sede (morte)
    "sono": 0.95,                # Limiar crítico para sono (colapso)
    "higiene": 0.8,              # Limiar crítico para higiene (doença)
    "social": 0.9                # Limiar crítico para social (depressão)
}
SENCIANTE_NEEDS_URGENT_THRESHOLDS = {
    "fome": 0.7,                 # Limiar urgente para fome
    "sede": 0.6,                 # Limiar urgente para sede
    "sono": 0.7,                 # Limiar urgente para sono
    "higiene": 0.6,              # Limiar urgente para higiene
    "social": 0.7                # Limiar urgente para social
}
SENCIANTE_NEEDS_WEIGHTS = {
    "fome": 1.2,                 # Peso da fome na urgência
    "sede": 1.5,                 # Peso da sede na urgência
    "sono": 0.8,                 # Peso do sono na urgência
    "higiene": 0.6,              # Peso da higiene na urgência
    "social": 0.4                # Peso da necessidade social na urgência
}

# Configurações de recursos
RESOURCE_TYPES = [
    {
        "tipo": "comida",
        "renovavel": True,
        "taxa_renovacao": 0.1,   # Taxa de renovação por hora
        "quantidade_inicial": [5, 15],  # Intervalo para quantidade inicial
        "distribuicao": "agrupada"  # Distribuição no mundo: "uniforme", "agrupada", "aleatoria"
    },
    {
        "tipo": "agua",
        "renovavel": True,
        "taxa_renovacao": 0.2,
        "quantidade_inicial": [10, 20],
        "distribuicao": "agrupada"
    },
    {
        "tipo": "madeira",
        "renovavel": True,
        "taxa_renovacao": 0.05,
        "quantidade_inicial": [5, 10],
        "distribuicao": "uniforme"
    },
    {
        "tipo": "pedra",
        "renovavel": False,
        "taxa_renovacao": 0,
        "quantidade_inicial": [3, 8],
        "distribuicao": "aleatoria"
    },
    {
        "tipo": "fruta",
        "renovavel": True,
        "taxa_renovacao": 0.15,
        "quantidade_inicial": [5, 12],
        "distribuicao": "agrupada"
    }
]

# Configurações de clima
CLIMATE_BASE_TEMPERATURE = 20.0  # Temperatura base em Celsius
CLIMATE_TEMPERATURE_RANGE = [-10.0, 40.0]  # Intervalo de temperatura permitido
CLIMATE_HUMIDITY_RANGE = [0.0, 1.0]  # Intervalo de umidade permitido (0-1)
CLIMATE_PRECIPITATION_RANGE = [0.0, 1.0]  # Intervalo de precipitação permitido (0-1)
CLIMATE_WIND_RANGE = [0.0, 100.0]  # Intervalo de vento permitido (km/h)
CLIMATE_CHANGE_RATE = 0.01  # Taxa de mudança natural do clima por hora

# Configurações de genética
GENE_MUTATION_RATE = 0.1  # Probabilidade de mutação de um gene durante a reprodução
GENE_MUTATION_RANGE = [0.9, 1.1]  # Intervalo de multiplicador para mutação
GENE_INHERITANCE_RATE = 0.5  # Probabilidade de herdar um gene de um progenitor específico

# Configurações de aprendizado
LEARNING_BASE_RATE = 0.01  # Taxa base de aprendizado por hora
MEMORY_DECAY_RATE = 0.01  # Taxa de decaimento da importância da memória por hora
MEMORY_THRESHOLD = 0.1  # Limiar abaixo do qual a memória é esquecida

# Configurações de comunicação
COMMUNICATION_EVOLUTION_STAGES = [
    "grunhidos",  # Estágio inicial
    "gestos",     # Segundo estágio
    "pictografica",  # Terceiro estágio
    "simbolica",  # Quarto estágio
    "escrita"     # Estágio final
]
COMMUNICATION_EVOLUTION_THRESHOLDS = [0.2, 0.4, 0.6, 0.8]  # Limiares de habilidade para evolução

# Configurações de construção
CONSTRUCTION_TYPES = [
    {
        "tipo": "abrigo_simples",
        "recursos_necessarios": {"madeira": 3},
        "habilidade_minima": 0.2,
        "durabilidade": 24.0  # Horas
    },
    {
        "tipo": "abrigo_medio",
        "recursos_necessarios": {"madeira": 5, "pedra": 2},
        "habilidade_minima": 0.4,
        "durabilidade": 72.0
    },
    {
        "tipo": "abrigo_avancado",
        "recursos_necessarios": {"madeira": 8, "pedra": 5},
        "habilidade_minima": 0.6,
        "durabilidade": 168.0
    },
    {
        "tipo": "ferramenta_simples",
        "recursos_necessarios": {"madeira": 1, "pedra": 1},
        "habilidade_minima": 0.3,
        "durabilidade": 12.0
    },
    {
        "tipo": "ferramenta_avancada",
        "recursos_necessarios": {"madeira": 2, "pedra": 3},
        "habilidade_minima": 0.5,
        "durabilidade": 36.0
    }
]

# Configurações de relações sociais
RELATION_TYPES = [
    "desconhecido",
    "conhecido",
    "amigo",
    "parceiro",
    "familia",
    "inimigo"
]
RELATION_STRENGTH_DECAY_RATE = 0.01  # Taxa de decaimento da força da relação por hora
RELATION_STRENGTH_THRESHOLD = 0.1  # Limiar abaixo do qual a relação é esquecida

# Configurações de ações divinas
DIVINE_ACTION_TYPES = [
    "clima",
    "biologia",
    "manifestacao",
    "recurso",
    "artefato"
]
DIVINE_ACTION_TARGETS = {
    "clima": ["temperatura", "precipitacao", "vento"],
    "biologia": ["evolucao", "doenca", "extincao"],
    "manifestacao": ["sinal", "possessao", "profecia"],
    "recurso": ["criar", "destruir"],
    "artefato": ["conhecimento", "poder", "vida", "harmonia"]
}
DIVINE_ACTION_MAX_INTENSITY = 1.0
DIVINE_ACTION_MAX_DURATION = 24.0  # Horas

# Configurações de histórico
HISTORY_MAX_EVENTS = 1000  # Número máximo de eventos a serem armazenados

