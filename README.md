# Backend Senciantes - Projeto Corrigido

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

### Opção 1: Script de inicialização (Recomendado)
```bash
python run_server.py
```

### Opção 2: Execução direta
```bash
python api_server.py
```

## Endpoints da API

O servidor roda na porta 5000 e oferece os seguintes endpoints:

### Controle da Simulação
- `POST /api/iniciar` - Inicia uma nova simulação
- `POST /api/parar` - Para a simulação
- `POST /api/pausar` - Pausa a simulação
- `POST /api/retomar` - Retoma a simulação pausada
- `POST /api/acelerar` - Acelera a simulação
- `POST /api/desacelerar` - Desacelera a simulação

### Consulta de Estado
- `GET /api/estado` - Obtém estado atual da simulação
- `GET /api/senciantes` - Lista todos os Senciantes
- `GET /api/senciante/<id>` - Obtém dados de um Senciante específico
- `GET /api/recursos` - Lista recursos do mundo
- `GET /api/construcoes` - Lista construções
- `GET /api/historico` - Obtém histórico da simulação
- `GET /api/clima` - Obtém informações do clima

### Interação
- `POST /api/acao_jogador` - Executa ação do jogador
- `POST /api/salvar` - Salva estado da simulação
- `POST /api/carregar` - Carrega estado salvo

## Correções Realizadas

1. **Imports corrigidos**: Removidos imports absolutos problemáticos
2. **Dependências**: Criado requirements.txt com Flask e Flask-CORS
3. **Script de inicialização**: Criado run_server.py para facilitar execução
4. **CORS habilitado**: Permite acesso de frontends web
5. **Host configurado**: Servidor escuta em 0.0.0.0 para acesso externo

## Estrutura do Projeto

```
backend_corrigido/
├── api_server.py          # Servidor Flask principal
├── run_server.py          # Script de inicialização
├── requirements.txt       # Dependências
├── simulacao.py          # Motor de simulação
├── simulacao_core.py     # Core da simulação
├── mecanicas/            # Mecânicas do jogo
├── modelos/              # Modelos de dados
├── testes/               # Testes unitários
└── utils/                # Utilitários
```

