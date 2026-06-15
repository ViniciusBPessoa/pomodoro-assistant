import qtawesome as qta
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame
from src.frontend.DrawerWidget import DrawerWidget
from PyQt6.QtCore import Qt
import sys


class PillWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.WindowMinimizeButtonHint | 
            Qt.WindowType.WindowSystemMenuHint
        )        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(190, 70)

        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        self.pill_frame = QFrame(self)
        self.pill_frame.setObjectName("pillBackground")

        layout_interno = QVBoxLayout(self.pill_frame)
        layout_interno.setContentsMargins(15, 8, 15, 8) 
        layout_interno.setSpacing(2) 

        cor_icone = '#8E8E93'

        linha_superior = QHBoxLayout()
        linha_superior.setContentsMargins(0, 0, 0, 0)

        self.btn_gaveta = QPushButton()
        self.btn_gaveta.setIcon(qta.icon('ph.caret-up-bold', color=cor_icone))
        self.btn_gaveta.setFixedSize(24, 24)

        self.lbl_tempo = QLabel("25:30")
        self.lbl_tempo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_ampliar = QPushButton()
        self.btn_ampliar.setIcon(qta.icon('ph.corners-out-bold', color=cor_icone))
        self.btn_ampliar.setFixedSize(24, 24)

        linha_superior.addWidget(self.btn_gaveta)
        linha_superior.addWidget(self.lbl_tempo)
        linha_superior.addWidget(self.btn_ampliar)

        linha_play = QHBoxLayout()
        linha_play.setContentsMargins(0, 0, 0, 0)

        self.btn_play = QPushButton()
        self.btn_play.setIcon(qta.icon('ph.play-fill', color=cor_icone))
        self.btn_play.setFixedSize(20, 20)

        linha_play.addStretch()
        linha_play.addWidget(self.btn_play)
        linha_play.addStretch()

        layout_interno.addLayout(linha_superior)
        layout_interno.addLayout(linha_play)
        layout_principal.addWidget(self.pill_frame)

        self.setStyleSheet("""
            QFrame#pillBackground {
                background-color: #1C1C1E; 
                border-radius: 20px;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 26px; 
                font-weight: 500;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 15);
            }
        """)

        self.pos_antiga = None

        # --- AQUI ESTÁ A INTEGRAÇÃO COM A GAVETA ---
        self.gaveta = DrawerWidget(self)
        
        # Conecta o clique do botão à função de abrir/fechar da gaveta
        self.btn_gaveta.clicked.connect(self.alternar_gaveta)

    def alternar_gaveta(self):
        # Opcional: Anima o ícone girando (Caret-up vira Caret-down)
        cor_icone = '#8E8E93'
        if self.gaveta.aberta:
            self.btn_gaveta.setIcon(qta.icon('ph.caret-up-bold', color=cor_icone))
        else:
            self.btn_gaveta.setIcon(qta.icon('ph.caret-down-bold', color=cor_icone))
            
        self.gaveta.toggle()

    # --- Lógica de clique e arraste atualizada para arrastar a gaveta junto ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.pos_antiga = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.pos_antiga:
            return
        delta = event.globalPosition().toPoint() - self.pos_antiga
        self.move(self.pos() + delta)
        self.pos_antiga = event.globalPosition().toPoint()
        
        # Atualiza a posição da gaveta enquanto arrasta a pílula!
        self.gaveta.atualizar_posicao()

# Bloco para testar rodando o script diretamente
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PillWidget()
    ex.show()
    sys.exit(app.exec())