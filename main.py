import pygame
import random
import sys

from agente import AgenteQLearning
from truco_regras import (
    nova_mao, e_manilha, obter_valor_carta,
    proximo_valor_truco, nome_pedido, cor_do_naipe,
    criar_estado_ia
)

pygame.init()

# ==========================
# CONFIGURAÇÕES DA TELA
# ==========================
LARGURA = 1000
ALTURA = 680

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mini Truco - Com IA que Aprende (Q-Learning)")

fonte_canto = pygame.font.SysFont("Arial", 11, bold=True)
fonte_pequena = pygame.font.SysFont("Arial", 13, bold=True)
fonte_media = pygame.font.SysFont("Arial", 19)
fonte_grande = pygame.font.SysFont("Arial", 26, bold=True)
fonte_destaque = pygame.font.SysFont("Arial", 36, bold=True)

clock = pygame.time.Clock()

TEMPO_PENSANDO_CPU = 800
TEMPO_RESULTADO = 2000

# Instância do Agente de IA
ia_agente = AgenteQLearning()

def desenhar_carta(surface, x, y, largura, altura, carta_info, tombo_str, selecionada=False, eh_tombo=False):
    if isinstance(carta_info, dict):
        carta_str = carta_info["str"]
        coberta = carta_info["coberta"]
    else:
        carta_str = carta_info
        coberta = False

    if coberta:
        pygame.draw.rect(surface, (50, 70, 120), (x, y, largura, altura), border_radius=6)
        pygame.draw.rect(surface, (255, 255, 255), (x, y, largura, altura), 2, border_radius=6)
        txt = fonte_pequena.render("COBERTA", True, (255, 255, 255))
        surface.blit(txt, (x + (largura - txt.get_width()) // 2, y + (altura - txt.get_height()) // 2))
        return

    pygame.draw.rect(surface, (255, 255, 255), (x, y, largura, altura), border_radius=6)

    eh_m = e_manilha(carta_str, tombo_str) and not eh_tombo
    cor_txt = cor_do_naipe(carta_str)

    if eh_m:
        pygame.draw.rect(surface, (255, 215, 0), (x, y, largura, altura), 3, border_radius=6)
        lbl_m = fonte_canto.render("MANILHA", True, (180, 100, 0))
        surface.blit(lbl_m, (x + (largura - lbl_m.get_width()) // 2, y + 14))
    else:
        cor_borda = (230, 50, 50) if selecionada else (0, 0, 0)
        pygame.draw.rect(surface, cor_borda, (x, y, largura, altura), 3 if selecionada else 2, border_radius=6)

    txt_centro = fonte_grande.render(carta_str, True, cor_txt)
    surface.blit(txt_centro, (x + (largura - txt_centro.get_width()) // 2, y + (altura - txt_centro.get_height()) // 2))

    txt_mini = fonte_canto.render(carta_str, True, cor_txt)
    pad = 4
    surface.blit(txt_mini, (x + pad, y + pad))
    surface.blit(txt_mini, (x + largura - txt_mini.get_width() - pad, y + pad))
    surface.blit(txt_mini, (x + pad, y + altura - txt_mini.get_height() - pad))
    surface.blit(txt_mini, (x + largura - txt_mini.get_width() - pad, y + altura - txt_mini.get_height() - pad))

# ==========================
# INICIALIZAÇÃO DO JOGO
# ==========================
pontos_j = 0
pontos_c = 0

jogador, cpu, tombo = nova_mao()
mao_da_vez = random.choice(["jogador", "cpu"])

valor_mao = 1
quem_trucou = None

rodadas_vencidas_j = 0
rodadas_vencidas_c = 0
vaza_atual = 1

selecionada = 0
tempo_estado = 0

carta_mesa_jogador = None
carta_mesa_cpu = None

if mao_da_vez == "jogador":
    estado = "jogador"
    mensagem = "Sua vez de jogar!"
else:
    estado = "cpu_inicia"
    mensagem = "CPU vai começar a rodada..."

# ==========================
# LOOP PRINCIPAL
# ==========================
while True:
    agora = pygame.time.get_ticks()

    # ======================
    # EVENTOS DE TECLADO
    # ======================
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ia_agente.salvar_q_table()
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_n:
                pontos_j, pontos_c = 0, 0
                jogador, cpu, tombo = nova_mao()
                mao_da_vez = random.choice(["jogador", "cpu"])
                valor_mao = 1
                quem_trucou = None
                rodadas_vencidas_j, rodadas_vencidas_c = 0, 0
                vaza_atual = 1
                selecionada = 0
                carta_mesa_jogador, carta_mesa_cpu = None, None

                if mao_da_vez == "jogador":
                    estado = "jogador"
                    mensagem = "Novo Jogo! Você começa."
                else:
                    estado = "cpu_inicia"
                    tempo_estado = agora
                    mensagem = "Novo Jogo! CPU começa."

            if evento.key == pygame.K_f and estado in ["jogador", "cpu_inicia", "jogador_decide_truco"] and estado != "fim_jogo":
                pontos_c += valor_mao
                ia_agente.aprender("FIM", recompensa=+valor_mao * 10, fim_mao=True)
                mensagem = f"Você fugiu! CPU ganha {valor_mao} pt(s)."
                estado = "prepara_proxima_mao"
                tempo_estado = agora

            if evento.key == pygame.K_t and estado in ["jogador", "cpu_inicia"] and quem_trucou != "jogador" and estado != "fim_jogo":
                if valor_mao < 12 and pontos_j < 11 and pontos_c < 11:
                    prox = proximo_valor_truco(valor_mao)
                    mensagem = f"Você pediu {nome_pedido(prox)}! CPU pensando..."
                    estado = "cpu_decide_truco"
                    tempo_estado = agora

            if estado == "jogador_decide_truco":
                if evento.key == pygame.K_a:
                    valor_mao = proximo_valor_truco(valor_mao)
                    mensagem = f"Você aceitou! A mão vale {valor_mao} pts."
                    estado = "jogador" if carta_mesa_jogador is None else "cpu_pensando"
                    tempo_estado = agora

                elif evento.key == pygame.K_r and valor_mao < 12:
                    prox = proximo_valor_truco(proximo_valor_truco(valor_mao))
                    quem_trucou = "jogador"
                    mensagem = f"Você pediu {nome_pedido(prox)}! CPU pensando..."
                    estado = "cpu_decide_truco"
                    tempo_estado = agora

            if estado == "jogador":
                if evento.key == pygame.K_LEFT:
                    selecionada = max(0, selecionada - 1)

                if evento.key == pygame.K_RIGHT:
                    selecionada = min(len(jogador) - 1, selecionada + 1)

                if evento.key == pygame.K_RETURN and jogador:
                    c_str = jogador.pop(selecionada)
                    carta_mesa_jogador = {"str": c_str, "coberta": False}

                    if carta_mesa_cpu is not None:
                        estado = "avaliar_rodada"
                    else:
                        estado = "cpu_pensando"
                        tempo_estado = agora
                        mensagem = "CPU pensando..."

                if evento.key == pygame.K_c and jogador:
                    if vaza_atual > 1:
                        c_str = jogador.pop(selecionada)
                        carta_mesa_jogador = {"str": c_str, "coberta": True}

                        if carta_mesa_cpu is not None:
                            estado = "avaliar_rodada"
                        else:
                            estado = "cpu_pensando"
                            tempo_estado = agora
                            mensagem = "CPU pensando..."
                    else:
                        mensagem = "Não é permitido cobrir carta na 1ª vaza!"

    # ======================
    # LÓGICA DO JOGO (IA)
    # ======================
    if estado == "cpu_inicia":
        if agora - tempo_estado >= TEMPO_PENSANDO_CPU:
            estado_ia = criar_estado_ia(cpu, carta_mesa_jogador, tombo, vaza_atual, valor_mao)
            opcoes_cartas = list(range(len(cpu)))
            
            idx_escolhido = ia_agente.escolher_acao(estado_ia, opcoes_cartas)
            c_str = cpu.pop(idx_escolhido)
            carta_mesa_cpu = {"str": c_str, "coberta": False}
            
            estado = "jogador"
            mensagem = "CPU jogou! Sua vez."

    elif estado == "cpu_pensando":
        if agora - tempo_estado >= TEMPO_PENSANDO_CPU:
            estado_ia = criar_estado_ia(cpu, carta_mesa_jogador, tombo, vaza_atual, valor_mao)
            opcoes_cartas = list(range(len(cpu)))
            
            idx_escolhido = ia_agente.escolher_acao(estado_ia, opcoes_cartas)
            c_str = cpu.pop(idx_escolhido)
            
            coberta = False
            if vaza_atual > 1 and random.random() < 0.2:
                coberta = True

            carta_mesa_cpu = {"str": c_str, "coberta": coberta}
            estado = "avaliar_rodada"

    elif estado == "cpu_decide_truco":
        if agora - tempo_estado >= TEMPO_PENSANDO_CPU:
            estado_ia = ("decisao_truco", tuple(sorted([obter_valor_carta({"str": c, "coberta": False}, tombo) for c in cpu])), valor_mao)
            decisao = ia_agente.escolher_acao(estado_ia, ["aceitar", "fugir"])

            if decisao == "aceitar":
                valor_mao = proximo_valor_truco(valor_mao)
                quem_trucou = "jogador"
                mensagem = f"CPU ACEITOU! A mão vale {valor_mao} pts."

                if carta_mesa_jogador is None and mao_da_vez == "jogador":
                    estado = "jogador"
                elif carta_mesa_jogador is None and mao_da_vez == "cpu":
                    estado = "cpu_inicia"
                else:
                    estado = "cpu_pensando"
                tempo_estado = agora

            else:
                pontos_j += valor_mao
                ia_agente.aprender("FIM", recompensa=-valor_mao * 10, fim_mao=True)
                mensagem = f"CPU FUGIU! Você ganhou {valor_mao} pt(s)."
                estado = "prepara_proxima_mao"
                tempo_estado = agora

    elif estado == "avaliar_rodada":
        v_j = obter_valor_carta(carta_mesa_jogador, tombo)
        v_c = obter_valor_carta(carta_mesa_cpu, tombo)

        txt_j = "Carta Coberta" if carta_mesa_jogador["coberta"] else carta_mesa_jogador["str"]
        txt_c = "Carta Coberta" if carta_mesa_cpu["coberta"] else carta_mesa_cpu["str"]

        estado_ia_atual = criar_estado_ia(cpu, carta_mesa_jogador, tombo, vaza_atual, valor_mao)

        if v_j > v_c:
            mensagem = f"Você venceu a vaza: {txt_j} x {txt_c}"
            rodadas_vencidas_j += 1
            mao_da_vez = "jogador"
            ia_agente.aprender(estado_ia_atual, recompensa=-5)
        elif v_c > v_j:
            mensagem = f"CPU venceu a vaza: {txt_c} x {txt_j}"
            rodadas_vencidas_c += 1
            mao_da_vez = "cpu"
            ia_agente.aprender(estado_ia_atual, recompensa=+5)
        else:
            mensagem = f"Empate na vaza!"
            rodadas_vencidas_j += 1
            rodadas_vencidas_c += 1

        vaza_atual += 1
        estado = "resultado_vaza"
        tempo_estado = agora

    elif estado == "resultado_vaza":
        if agora - tempo_estado >= TEMPO_RESULTADO:
            carta_mesa_jogador, carta_mesa_cpu = None, None

            if rodadas_vencidas_j >= 2 and rodadas_vencidas_c < 2:
                pontos_j += valor_mao
                ia_agente.aprender("FIM", recompensa=-valor_mao * 15, fim_mao=True)
                mensagem = f"VOCÊ GANHOU A MÃO! (+{valor_mao} pts)"
                estado = "prepara_proxima_mao"
                tempo_estado = agora

            elif rodadas_vencidas_c >= 2 and rodadas_vencidas_j < 2:
                pontos_c += valor_mao
                ia_agente.aprender("FIM", recompensa=+valor_mao * 15, fim_mao=True)
                mensagem = f"CPU GANHOU A MÃO! (+{valor_mao} pts)"
                estado = "prepara_proxima_mao"
                tempo_estado = agora

            elif len(jogador) == 0:
                if rodadas_vencidas_j > rodadas_vencidas_c:
                    pontos_j += valor_mao
                    ia_agente.aprender("FIM", recompensa=-valor_mao * 15, fim_mao=True)
                    mensagem = f"VOCÊ GANHOU A MÃO! (+{valor_mao} pts)"
                else:
                    pontos_c += valor_mao
                    ia_agente.aprender("FIM", recompensa=+valor_mao * 15, fim_mao=True)
                    mensagem = f"CPU GANHOU A MÃO! (+{valor_mao} pts)"
                estado = "prepara_proxima_mao"
                tempo_estado = agora
            else:
                selecionada = min(selecionada, len(jogador) - 1)
                if mao_da_vez == "jogador":
                    estado = "jogador"
                    mensagem = "Sua vez de jogar!"
                else:
                    estado = "cpu_inicia"
                    tempo_estado = agora
                    mensagem = "Vez da CPU..."

    elif estado == "prepara_proxima_mao":
        if agora - tempo_estado >= TEMPO_RESULTADO:
            if pontos_j >= 12 or pontos_c >= 12:
                estado = "fim_jogo"
            else:
                jogador, cpu, tombo = nova_mao()
                valor_mao = 1
                quem_trucou = None
                rodadas_vencidas_j, rodadas_vencidas_c = 0, 0
                vaza_atual = 1
                selecionada = 0

                mao_da_vez = "cpu" if mao_da_vez == "jogador" else "jogador"

                if mao_da_vez == "jogador":
                    estado = "jogador"
                    mensagem = "Nova Mão! Sua vez."
                else:
                    estado = "cpu_inicia"
                    tempo_estado = agora
                    mensagem = "Nova Mão! CPU começa..."

    # ======================
    # RENDERIZAÇÃO
    # ======================
    tela.fill((34, 112, 62))

    # 1. TOP BAR
    pygame.draw.rect(tela, (18, 60, 32), (0, 0, LARGURA, 65))
    pygame.draw.line(tela, (255, 255, 255), (0, 65), (LARGURA, 65), 2)

    titulo = fonte_grande.render("MINI TRUCO", True, (255, 255, 255))
    tela.blit(titulo, (20, 15))

    placar = fonte_media.render(f"Placar: Você {pontos_j} x {pontos_c} CPU (IA Memória: {len(ia_agente.q_table)})", True, (255, 220, 0))
    tela.blit(placar, (220, 22))

    val_txt = fonte_media.render(f"Mão Vale: {valor_mao} pt(s)", True, (100, 255, 100))
    tela.blit(val_txt, (750, 22))

    # 2. STATUS
    pygame.draw.rect(tela, (20, 45, 25), (LARGURA // 2 - 270, 75, 540, 32), border_radius=5)
    msg = fonte_media.render(mensagem, True, (255, 255, 255))
    tela.blit(msg, (LARGURA // 2 - msg.get_width() // 2, 80))

    largura_c, altura_c, espaco_c = 75, 110, 15

    # 3. CPU
    total_cpu = len(cpu)
    x_ini_cpu = (LARGURA - (total_cpu * largura_c + (total_cpu - 1) * espaco_c)) // 2

    for i in range(total_cpu):
        x = x_ini_cpu + i * (largura_c + espaco_c)
        y = 120
        pygame.draw.rect(tela, (40, 60, 150), (x, y, largura_c, altura_c), border_radius=6)
        pygame.draw.rect(tela, (255, 255, 255), (x, y, largura_c, altura_c), 2, border_radius=6)

    # 4. MESA & TOMBO
    y_mesa = 260

    x_tombo = 120
    lbl_tombo = fonte_pequena.render("TOMBO", True, (255, 220, 0))
    tela.blit(lbl_tombo, (x_tombo + (largura_c - lbl_tombo.get_width()) // 2, y_mesa - 18))
    desenhar_carta(tela, x_tombo, y_mesa, largura_c, altura_c, tombo, tombo, eh_tombo=True)

    if carta_mesa_jogador:
        x = LARGURA // 2 - largura_c - 15
        lbl = fonte_pequena.render("Você", True, (200, 255, 200))
        tela.blit(lbl, (x + (largura_c - lbl.get_width()) // 2, y_mesa - 18))
        desenhar_carta(tela, x, y_mesa, largura_c, altura_c, carta_mesa_jogador, tombo)

    if carta_mesa_cpu:
        x = LARGURA // 2 + 15
        lbl = fonte_pequena.render("CPU", True, (200, 255, 200))
        tela.blit(lbl, (x + (largura_c - lbl.get_width()) // 2, y_mesa - 18))
        desenhar_carta(tela, x, y_mesa, largura_c, altura_c, carta_mesa_cpu, tombo)

    # 5. JOGADOR
    total_jog = len(jogador)
    x_ini_jog = (LARGURA - (total_jog * largura_c + (total_jog - 1) * espaco_c)) // 2

    for i, carta in enumerate(jogador):
        x = x_ini_jog + i * (largura_c + espaco_c)
        y = 450 if (i == selecionada and estado == "jogador") else 470

        if i == selecionada and estado == "jogador":
            seta = fonte_pequena.render("▲", True, (255, 220, 0))
            tela.blit(seta, (x + (largura_c - seta.get_width()) // 2, y - 18))

        desenhar_carta(tela, x, y, largura_c, altura_c, carta, tombo, selecionada=(i == selecionada and estado == "jogador"))

    # 6. TELA FIM DE JOGO
    if estado == "fim_jogo":
        pygame.draw.rect(tela, (0, 0, 0, 210), (0, 0, LARGURA, ALTURA))
        vencedor_txt = "PARABÉNS! VOCÊ VENCEU O JOGO!" if pontos_j >= 12 else "FIM DE JOGO! CPU VENCEU!"
        cor_v = (255, 215, 0) if pontos_j >= 12 else (255, 80, 80)

        t_fim = fonte_destaque.render(vencedor_txt, True, cor_v)
        tela.blit(t_fim, (LARGURA // 2 - t_fim.get_width() // 2, ALTURA // 2 - 40))

        sub_fim = fonte_media.render("Pressione [N] para jogar novamente", True, (255, 255, 255))
        tela.blit(sub_fim, (LARGURA // 2 - sub_fim.get_width() // 2, ALTURA // 2 + 20))

    # 7. RODAPÉ DE OPÇÕES
    else:
        y_hud = 610
        pygame.draw.rect(tela, (15, 30, 20), (0, y_hud, LARGURA, ALTURA - y_hud))
        pygame.draw.line(tela, (80, 140, 90), (0, y_hud), (LARGURA, y_hud), 2)

        opcoes = []

        if estado == "jogador":
            opcoes.append(("[←/→]", "Escolher"))
            opcoes.append(("[ENTER]", "Jogar"))
            if vaza_atual > 1:
                opcoes.append(("[C]", "Tombar/Cobrir"))

        if estado in ["jogador", "cpu_inicia"] and valor_mao < 12 and quem_trucou != "jogador" and pontos_j < 11 and pontos_c < 11:
            opcoes.append(("[T]", f"Pedir {nome_pedido(proximo_valor_truco(valor_mao))}"))

        if estado in ["jogador", "cpu_inicia", "jogador_decide_truco"]:
            opcoes.append(("[F]", "Fugir"))

        if estado == "jogador_decide_truco":
            opcoes.append(("[A]", "ACEITAR"))
            if valor_mao < 12:
                prox_aumento = proximo_valor_truco(proximo_valor_truco(valor_mao))
                opcoes.append(("[R]", f"Pedir {nome_pedido(prox_aumento)}"))

        opcoes.append(("[N]", "Novo Jogo"))

        x_offset = 20
        for tecla, acao in opcoes:
            txt_t = fonte_pequena.render(tecla, True, (255, 255, 255))
            larg_box = txt_t.get_width() + 10

            pygame.draw.rect(tela, (40, 80, 50), (x_offset, y_hud + 18, larg_box, 26), border_radius=4)
            pygame.draw.rect(tela, (100, 200, 120), (x_offset, y_hud + 18, larg_box, 26), 1, border_radius=4)
            tela.blit(txt_t, (x_offset + 5, y_hud + 23))

            cor_acao = (255, 220, 0) if tecla in ["[T]", "[A]", "[F]", "[R]", "[C]"] else (210, 210, 210)
            txt_a = fonte_pequena.render(acao, True, cor_acao)
            tela.blit(txt_a, (x_offset + larg_box + 6, y_hud + 23))

            x_offset += larg_box + txt_a.get_width() + 20

    pygame.display.flip()
    clock.tick(60)