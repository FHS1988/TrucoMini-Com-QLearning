import json
import os
import random

ARQUIVO_Q_TABLE = "q_table.json"

class AgenteQLearning:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.15):
        self.alpha = alpha     # Taxa de aprendizado
        self.gamma = gamma     # Importância de recompensas futuras
        self.epsilon = epsilon # Taxa de exploração (tentar coisas novas)
        self.q_table = {}
        self.carregar_q_table()
        
        self.ultimo_estado = None
        self.ultima_acao = None

    def carregar_q_table(self):
        if os.path.exists(ARQUIVO_Q_TABLE):
            try:
                with open(ARQUIVO_Q_TABLE, "r") as f:
                    self.q_table = json.load(f)
            except Exception as e:
                print("Erro ao carregar Q-Table, iniciando nova:", e)
                self.q_table = {}

    def salvar_q_table(self):
        try:
            with open(ARQUIVO_Q_TABLE, "w") as f:
                json.dump(self.q_table, f)
        except Exception as e:
            print("Erro ao salvar Q-Table:", e)

    def obter_q(self, estado_str, acao):
        return self.q_table.get(estado_str, {}).get(str(acao), 0.0)

    def escolher_acao(self, estado_tuple, acoes_possiveis):
        estado_str = str(estado_tuple)

        if estado_str not in self.q_table:
            self.q_table[estado_str] = {str(a): 0.0 for a in acoes_possiveis}

        # Exploração (chuta uma jogada para testar resultado)
        if random.random() < self.epsilon:
            acao = random.choice(acoes_possiveis)
        else:
            # Explotação (escolhe a jogada de maior valor aprendido)
            q_valores = [self.obter_q(estado_str, a) for a in acoes_possiveis]
            max_q = max(q_valores)
            melhores = [a for a, q in zip(acoes_possiveis, q_valores) if q == max_q]
            acao = random.choice(melhores)

        self.ultimo_estado = estado_str
        self.ultima_acao = str(acao)
        return acao

    def aprender(self, novo_estado_tuple, recompensa, fim_mao=False):
        if self.ultimo_estado is None or self.ultima_acao is None:
            return

        q_antigo = self.obter_q(self.ultimo_estado, self.ultima_acao)

        if fim_mao:
            max_q_futuro = 0.0
        else:
            n_str = str(novo_estado_tuple)
            if n_str in self.q_table and self.q_table[n_str]:
                max_q_futuro = max(self.q_table[n_str].values())
            else:
                max_q_futuro = 0.0

        # Fórmula de atualização do Q-Learning
        novo_q = q_antigo + self.alpha * (recompensa + self.gamma * max_q_futuro - q_antigo)

        if self.ultimo_estado not in self.q_table:
            self.q_table[self.ultimo_estado] = {}

        self.q_table[self.ultimo_estado][self.ultima_acao] = novo_q
        self.salvar_q_table()