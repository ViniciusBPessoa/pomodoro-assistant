import qtawesome as qta
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt

class PillWidget(QWidget):
    def __init__(self):
        super().__init__()
        # O __init__ do widget DEVE ter apenas a chamada para montar a interface.
        self.init_ui()

    def init_ui(self):
        # 1. Configurações da Janela Flutuante
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Ajustei levemente a altura para acomodar os andares sem esmagar
        self.resize(190, 70)

        # 2. Layout Base
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        # 3. O "Corpo" da Pílula
        self.pill_frame = QFrame(self)
        self.pill_frame.setObjectName("pillBackground")

        # Layout interno VERTICAL
        layout_interno = QVBoxLayout(self.pill_frame)
        layout_interno.setContentsMargins(15, 8, 15, 8) 
        layout_interno.setSpacing(2) 

        # 4. CRIANDO OS ELEMENTOS
        cor_icone = '#8E8E93'

        # --- 1º ANDAR: LINHA SUPERIOR (Gaveta, Tempo, Ampliar) ---
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

        # --- 2º ANDAR: LINHA DO PLAY (Centralizado) ---
        linha_play = QHBoxLayout()
        linha_play.setContentsMargins(0, 0, 0, 0)

        self.btn_play = QPushButton()
        self.btn_play.setIcon(qta.icon('ph.play-fill', color=cor_icone))
        self.btn_play.setFixedSize(20, 20)

        linha_play.addStretch() # Empurra pro centro
        linha_play.addWidget(self.btn_play)
        linha_play.addStretch() # Empurra pro centro

        # Adiciona os andares na Pílula
        layout_interno.addLayout(linha_superior)
        layout_interno.addLayout(linha_play)
        
        layout_principal.addWidget(self.pill_frame)

        # 5. O CSS (QSS)
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

    # --- Lógica de clique e arraste mantida igual ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.pos_antiga = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.pos_antiga:
            return
        delta = event.globalPosition().toPoint() - self.pos_antiga
        self.move(self.pos() + delta)
        self.pos_antiga = event.globalPosition().toPoint()