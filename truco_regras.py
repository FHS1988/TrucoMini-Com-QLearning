import random

ORDEM_VALORES = ["4", "5", "6", "7", "Q", "J", "K", "A", "2", "3"]

VALOR_BASE = {
    "4": 1, "5": 2, "6": 3, "7": 4, "Q": 5,
    "J": 6, "K": 7, "A": 8, "2": 9, "3": 10
}

# Hierarquia Paulista: Zape (♣) > Copas (♥) > Espada (♠) > Ouro (♦)
FORCA_NAIPES = {
    "♦": 101,
    "♠": 102,
    "♥": 103,
    "♣": 104
}

NAIPES = ["♦", "♠", "♥", "♣"]

def nova_mao():
    baralho = [f"{v}{n}" for v in ORDEM_VALORES for n in NAIPES]
    random.shuffle(baralho)

    jogador = [baralho.pop() for _ in range(3)]
    cpu = [baralho.pop() for _ in range(3)]
    tombo = baralho.pop()

    return jogador, cpu, tombo

def e_manilha(carta_str, tombo_str):
    if not carta_str or carta_str == "OCULTA":
        return False
    valor_carta = carta_str[:-1]
    valor_tombo = tombo_str[:-1]

    idx_tombo = ORDEM_VALORES.index(valor_tombo)
    idx_manilha = (idx_tombo + 1) % len(ORDEM_VALORES)
    valor_manilha = ORDEM_VALORES[idx_manilha]

    return valor_carta == valor_manilha

def obter_valor_carta(carta_dict, tombo_str):
    if not carta_dict or carta_dict["coberta"]:
        return 0 

    carta_str = carta_dict["str"]
    valor_carta = carta_str[:-1]
    naipe_carta = carta_str[-1]

    if e_manilha(carta_str, tombo_str):
        return FORCA_NAIPES[naipe_carta]
    
    return VALOR_BASE[valor_carta]

def proximo_valor_truco(valor_atual):
    if valor_atual == 1: return 3
    if valor_atual == 3: return 6
    if valor_atual == 6: return 9
    if valor_atual == 9: return 12
    return 12

def nome_pedido(valor_alvo):
    nomes = {3: "TRUCO (3 pts)", 6: "SEIS (6 pts)", 9: "NOVE (9 pts)", 12: "DOZE (12 pts)"}
    return nomes.get(valor_alvo, "TRUCO")

def cor_do_naipe(carta_str):
    if not carta_str or carta_str == "OCULTA":
        return (50, 50, 50)
    naipe = carta_str[-1]
    return (200, 20, 20) if naipe in ["♥", "♦"] else (20, 20, 20)

def criar_estado_ia(cpu_cartas, carta_mesa_jogador, tombo_str, vaza_atual, valor_mao):
    """Cria uma assinatura simplificada da mesa para a IA entender a situação."""
    forca_mao = tuple(sorted([obter_valor_carta({"str": c, "coberta": False}, tombo_str) for c in cpu_cartas]))
    val_jog = obter_valor_carta(carta_mesa_jogador, tombo_str) if carta_mesa_jogador else -1
    return (forca_mao, val_jog, vaza_atual, valor_mao)