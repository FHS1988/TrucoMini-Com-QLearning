import time
from agente import AgenteQLearning
from truco_regras import nova_mao, obter_valor_carta, criar_estado_ia

def simular_mao(agente_1, agente_2):
    """
    Simula 1 mão completa de Truco entre duas IAs (sem Pygame).
    """
    jogador_1, jogador_2, tombo = nova_mao()
    
    # 0 = Agente 1, 1 = Agente 2
    mao_da_vez = 0 
    
    vazas_1 = 0
    vazas_2 = 0
    vaza_atual = 1
    
    # Mão simples rodando para treino rápido (valor fixo)
    valor_mao = 1 

    while vazas_1 < 2 and vazas_2 < 2 and len(jogador_1) > 0:
        carta_1 = None
        carta_2 = None

        if mao_da_vez == 0:
            # Vez do Agente 1 jogar
            est1 = criar_estado_ia(jogador_1, None, tombo, vaza_atual, valor_mao)
            idx1 = agente_1.escolher_acao(est1, list(range(len(jogador_1))))
            carta_1 = {"str": jogador_1.pop(idx1), "coberta": False}

            # Vez do Agente 2 responder
            est2 = criar_estado_ia(jogador_2, carta_1, tombo, vaza_atual, valor_mao)
            idx2 = agente_2.escolher_acao(est2, list(range(len(jogador_2))))
            carta_2 = {"str": jogador_2.pop(idx2), "coberta": False}
        else:
            # Vez do Agente 2 jogar
            est2 = criar_estado_ia(jogador_2, None, tombo, vaza_atual, valor_mao)
            idx2 = agente_2.escolher_acao(est2, list(range(len(jogador_2))))
            carta_2 = {"str": jogador_2.pop(idx2), "coberta": False}

            # Vez do Agente 1 responder
            est1 = criar_estado_ia(jogador_1, carta_2, tombo, vaza_atual, valor_mao)
            idx1 = agente_1.escolher_acao(est1, list(range(len(jogador_1))))
            carta_1 = {"str": jogador_1.pop(idx1), "coberta": False}

        # Avaliar vaza
        v1 = obter_valor_carta(carta_1, tombo)
        v2 = obter_valor_carta(carta_2, tombo)

        if v1 > v2:
            vazas_1 += 1
            mao_da_vez = 0
            agente_1.aprender(est1, recompensa=+5)
            agente_2.aprender(est2, recompensa=-5)
        elif v2 > v1:
            vazas_2 += 1
            mao_da_vez = 1
            agente_1.aprender(est1, recompensa=-5)
            agente_2.aprender(est2, recompensa=+5)
        else:
            # Empate
            vazas_1 += 1
            vazas_2 += 1

        vaza_atual += 1

    # Recompensa Final da Mão
    if vazas_1 > vazas_2:
        agente_1.aprender("FIM", recompensa=+15, fim_mao=True)
        agente_2.aprender("FIM", recompensa=-15, fim_mao=True)
    elif vazas_2 > vazas_1:
        agente_1.aprender("FIM", recompensa=-15, fim_mao=True)
        agente_2.aprender("FIM", recompensa=+15, fim_mao=True)

def treinar_agente(total_partidas=50000):
    print(f"--- INICIANDO TREINAMENTO AUTOMÁTICO DE {total_partidas} PARTIDAS ---")
    
    # Criamos dois agentes com taxa de exploração alta para testarem estratégias
    agente_principal = AgenteQLearning(alpha=0.1, gamma=0.9, epsilon=0.2)
    agente_oponente = AgenteQLearning(alpha=0.1, gamma=0.9, epsilon=0.2)

    inicio = time.time()

    for i in range(1, total_partidas + 1):
        simular_mao(agente_principal, agente_oponente)

        # Mostra o progresso a cada 10% do treino
        if i % (total_partidas // 10) == 0:
            pct = (i / total_partidas) * 100
            qtd_estados = len(agente_principal.q_table)
            print(f"Progresso: {pct:.0f}% | Mãos Simuladas: {i} | Estados Aprendidos (Q-Table): {qtd_estados}")

    # Salva o aprendizado consolidado
    agente_principal.salvar_q_table()
    
    tempo_total = time.time() - inicio
    print("--------------------------------------------------")
    print(f"✅ Treinamento concluído em {tempo_total:.2f} segundos!")
    print(f"🧠 Total de situações salvas no arquivo 'q_table.json': {len(agente_principal.q_table)}")

if __name__ == "__main__":
    # Altere a quantidade de simulações se quiser (ex: 10000, 50000, 100000)
    treinar_agente(total_partidas=2000)