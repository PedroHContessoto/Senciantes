from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import threading
import json
from simulacao import Simulacao
app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

# Instância global da simulação
simulacao = None
thread_simulacao = None
executando = False

import time

def executar_simulacao():
    """Função para executar a simulação em uma thread separada."""
    global simulacao, executando

    ultimo_tempo = time.time()

    while executando:
        # Calcula o tempo real decorrido
        tempo_atual = time.time()
        delta_tempo_real = tempo_atual - ultimo_tempo
        ultimo_tempo = tempo_atual

        # Converte o tempo real em tempo da simulação (com base na velocidade)
        delta_tempo_simulacao = delta_tempo_real * simulacao.velocidade

        # Limita para evitar saltos grandes
        delta_tempo_simulacao = min(delta_tempo_simulacao, 0.1)

        # Atualiza o tempo total da simulação
        simulacao.tempo_simulacao += delta_tempo_simulacao

        # Chama o método correto
        simulacao._atualizar(delta_tempo_simulacao)
        simulacao._processar_eventos_pendentes()
        simulacao._processar_acoes_divinas_pendentes()

        # (Opcional) Chama callbacks de atualização, se necessário
        for callback in simulacao.callbacks["atualizacao"]:
            try:
                callback(simulacao)
            except Exception as e:
                print(f"Erro em callback de atualização: {e}")

        time.sleep(simulacao.intervalo_atualizacao)


@app.route('/api/iniciar', methods=['POST'])
def iniciar_simulacao():
    """Inicia uma nova simulação."""
    global simulacao, thread_simulacao, executando

    # Parar simulação existente, se houver
    if executando:
        executando = False
        if thread_simulacao:
            thread_simulacao.join()

    # Obter parâmetros da requisição
    dados = request.json
    tamanho_mundo = dados.get('tamanho_mundo', (100, 100))
    num_senciantes_iniciais = dados.get('num_senciantes_iniciais', 10)

    # Criar nova simulação
    simulacao = Simulacao(tamanho_mundo=tamanho_mundo, num_senciantes_inicial=num_senciantes_iniciais)

    # Iniciar thread de simulação
    executando = True
    thread_simulacao = threading.Thread(target=executar_simulacao)
    thread_simulacao.daemon = True
    thread_simulacao.start()

    return jsonify({"status": "success", "mensagem": "Simulação iniciada com sucesso"})

@app.route('/api/parar', methods=['POST'])
def parar_simulacao():
    """Para a simulação em execução."""
    global executando

    if executando:
        executando = False
        return jsonify({"status": "success", "mensagem": "Simulação parada com sucesso"})
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/pausar', methods=['POST'])
def pausar_simulacao():
    """Pausa a simulação em execução."""
    global simulacao

    if simulacao:
        simulacao.pausar()
        return jsonify({"status": "success", "mensagem": "Simulação pausada com sucesso"})
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/retomar', methods=['POST'])
def retomar_simulacao():
    """Retoma a simulação pausada."""
    global simulacao

    if simulacao:
        simulacao.retomar()
        return jsonify({"status": "success", "mensagem": "Simulação retomada com sucesso"})
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/acelerar', methods=['POST'])
def acelerar_simulacao():
    """Acelera a simulação."""
    global simulacao

    if simulacao:
        fator = request.json.get('fator', 2)
        simulacao.acelerar(fator)
        return jsonify({"status": "success", "mensagem": f"Simulação acelerada por um fator de {fator}"})
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/desacelerar', methods=['POST'])
def desacelerar_simulacao():
    """Desacelera a simulação."""
    global simulacao

    if simulacao:
        fator = request.json.get('fator', 2)
        simulacao.desacelerar(fator)
        return jsonify({"status": "success", "mensagem": f"Simulação desacelerada por um fator de {fator}"})
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/estado', methods=['GET'])
def obter_estado():
    """Obtém o estado atual da simulação."""
    global simulacao

    if simulacao:
        return jsonify(simulacao.to_dict())
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/senciantes', methods=['GET'])
def obter_senciantes():
    """Obtém informações sobre os Senciantes."""
    global simulacao

    if simulacao:
        return jsonify({k: v.to_dict() for k, v in simulacao.senciantes.items()})
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/senciante/<id_senciante>', methods=['GET'])
def obter_senciante(id_senciante):
    """Obtém informações sobre um Senciante específico."""
    global simulacao

    if simulacao and id_senciante in simulacao.ambiente.senciantes:
        return jsonify(simulacao.senciantes[id_senciante].to_dict())
    else:
        return jsonify({"status": "error", "mensagem": "Senciante não encontrado"})

@app.route('/api/recursos', methods=['GET'])
def obter_recursos():
    """Obtém informações sobre os recursos."""
    global simulacao

    if simulacao:
        return jsonify({k: v.to_dict() for k, v in simulacao.mundo.recursos.items()})
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/construcoes', methods=['GET'])
def obter_construcoes():
    """Obtém informações sobre as construções."""
    global simulacao

    if simulacao:
        return jsonify([c.to_dict() for c in simulacao.mundo.construcoes.values()])
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/historico', methods=['GET'])
def obter_historico():
    """Obtém o histórico da simulação."""
    global simulacao

    if simulacao:
        return jsonify(simulacao.mundo.historico.to_dict())
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/clima', methods=['GET'])
def obter_clima():
    """Obtém informações sobre o clima."""
    global simulacao

    if simulacao:
        return jsonify(simulacao.mundo.clima.to_dict())
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/acao_jogador', methods=['POST'])
def executar_acao_jogador():
    """Executa uma ação do jogador."""
    global simulacao

    if simulacao:
        dados = request.json
        tipo = dados.get('tipo')
        alvo = dados.get('alvo')
        intensidade = dados.get('intensidade', 0.5)
        duracao = dados.get('duracao', 10)

        id_acao = simulacao.adicionar_acao_jogador(tipo, alvo, intensidade, duracao)
        return jsonify({"status": "success", "id_acao": id_acao})
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/salvar', methods=['POST'])
def salvar_estado():
    """Salva o estado atual da simulação."""
    global simulacao

    if simulacao:
        caminho = request.json.get('caminho', 'simulacao_estado.json')

        try:
            with open(caminho, 'w') as f:
                json.dump(simulacao.to_dict(), f, indent=2)
            return jsonify({"status": "success", "mensagem": f"Estado salvo em {caminho}"})
        except Exception as e:
            return jsonify({"status": "error", "mensagem": f"Erro ao salvar estado: {str(e)}"})
    else:
        return jsonify({"status": "error", "mensagem": "Nenhuma simulação em execução"})

@app.route('/api/carregar', methods=['POST'])
def carregar_estado():
    """Carrega um estado salvo da simulação."""
    global simulacao, thread_simulacao, executando

    # Parar simulação existente, se houver
    if executando:
        executando = False
        if thread_simulacao:
            thread_simulacao.join()

    caminho = request.json.get('caminho', 'simulacao_estado.json')

    try:
        # Em uma implementação completa, reconstruiríamos a simulação a partir dos dados
        # Por simplicidade, criamos uma nova simulação
        simulacao = Simulacao()

        # Iniciar thread de simulação
        executando = True
        thread_simulacao = threading.Thread(target=executar_simulacao)
        thread_simulacao.daemon = True
        thread_simulacao.start()

        return jsonify({"status": "success", "mensagem": f"Estado carregado de {caminho}"})
    except Exception as e:
        return jsonify({"status": "error", "mensagem": f"Erro ao carregar estado: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

