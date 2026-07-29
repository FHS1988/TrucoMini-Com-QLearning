import unittest

from truco_regras import decidir_resposta_truco, decidir_resultado_vaza


class TestDecidirRespostaTruco(unittest.TestCase):
    def test_nao_retruca_com_mao_fraca(self):
        mao = ["4♥", "5♣", "7♦"]
        self.assertEqual(decidir_resposta_truco(3, mao, "A♠"), "fugir")

    def test_aceita_com_mao_intermediaria(self):
        mao = ["7♥", "A♠", "4♦"]
        self.assertEqual(decidir_resposta_truco(3, mao, "Q♣"), "aceitar")

    def test_retruca_com_mao_muito_forte(self):
        mao = ["3♥", "A♠", "K♦"]
        self.assertEqual(decidir_resposta_truco(3, mao, "Q♣"), "aumentar")

    def test_empate_na_vaza_nao_encerra_a_mao(self):
        self.assertEqual(decidir_resultado_vaza(0, 0, True), "continua")


if __name__ == "__main__":
    unittest.main()
