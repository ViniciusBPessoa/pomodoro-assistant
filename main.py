import sys
from PyQt6.QtWidgets import QApplication
from src.frontend.pill_widget import PillWidget
from src.frontend.pomodoro_ui import PomodoroUI

class GerenciadorDeTelas:
    def __init__(self):
        self.pilula = PillWidget()
        self.pomodoro_expandido = PomodoroUI()

        self.pilula.btn_ampliar.clicked.connect(self.abrir_pomodoro)
        self.pomodoro_expandido.btn_recolher.clicked.connect(self.abrir_pilula)

        self.pilula.show()

    def abrir_pomodoro(self):
        # 1. Pega a geometria (caixa) de onde a pílula está
        geo_atual = self.pilula.geometry()
        
        # 2. Pega a caixa da tela que vai abrir
        nova_geometria = self.pomodoro_expandido.frameGeometry()
        
        # 3. Alinha pelo centro primeiro e depois fixa o chão (bottom)
        nova_geometria.moveCenter(geo_atual.center())
        nova_geometria.moveBottom(geo_atual.bottom())
        
        # 4. Aplica a nova posição e troca as telas
        self.pomodoro_expandido.move(nova_geometria.topLeft())
        self.pilula.hide()
        self.pomodoro_expandido.show()

    def abrir_pilula(self):
        # Faz exatamente o inverso na volta
        geo_atual = self.pomodoro_expandido.geometry()
        
        nova_geometria = self.pilula.frameGeometry()
        
        nova_geometria.moveCenter(geo_atual.center())
        nova_geometria.moveBottom(geo_atual.bottom())
        
        self.pilula.move(nova_geometria.topLeft())
        self.pomodoro_expandido.hide()
        self.pilula.show()

def main():
    app = QApplication(sys.argv)
    gerenciador = GerenciadorDeTelas()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()