import qtawesome as qta
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt

class PomodoroUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 1. Configurações da Janela Flutuante
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Um tamanho maior e confortável para a tela expandida
        self.resize(260, 320)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        # 2. O "Corpo" Principal
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("pomodoroBackground")
        layout_interno = QVBoxLayout(self.main_frame)
        layout_interno.setContentsMargins(20, 20, 20, 20)

        cor_icone = '#8E8E93'

        # --- CABEÇALHO (Botão de encolher, Título da Fase, Vazio para alinhar) ---
        linha_topo = QHBoxLayout()
        
        self.btn_recolher = QPushButton()
        self.btn_recolher.setIcon(qta.icon('ph.corners-in-bold', color=cor_icone))
        self.btn_recolher.setFixedSize(28, 28)

        self.lbl_fase = QLabel("Foco - Ciclo 1/4")
        self.lbl_fase.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_fase.setObjectName("textoFase")

        # Um botão invisível só para manter o título centralizado perfeitamente
        spacer_btn = QPushButton()
        spacer_btn.setFixedSize(28, 28)
        spacer_btn.setStyleSheet("background: transparent;")
        spacer_btn.setEnabled(False)

        linha_topo.addWidget(self.btn_recolher)
        linha_topo.addWidget(self.lbl_fase)
        linha_topo.addWidget(spacer_btn)

        # --- CENTRO (O Relógio Gigante) ---
        self.lbl_tempo_gigante = QLabel("25:30")
        self.lbl_tempo_gigante.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tempo_gigante.setObjectName("textoGigante")

        # --- RODAPÉ (Botões de Ação) ---
        linha_base = QHBoxLayout()
        
        self.btn_reset = QPushButton()
        self.btn_reset.setIcon(qta.icon('ph.arrow-counter-clockwise-bold', color=cor_icone))
        self.btn_reset.setFixedSize(36, 36)

        self.btn_play_grande = QPushButton()
        self.btn_play_grande.setIcon(qta.icon('ph.play-fill', color=cor_icone))
        self.btn_play_grande.setFixedSize(48, 48)

        self.btn_avancar = QPushButton()
        self.btn_avancar.setIcon(qta.icon('ph.fast-forward-bold', color=cor_icone))
        self.btn_avancar.setFixedSize(36, 36)

        linha_base.addWidget(self.btn_reset)
        linha_base.addStretch()
        linha_base.addWidget(self.btn_play_grande)
        linha_base.addStretch()
        linha_base.addWidget(self.btn_avancar)

        # Montando tudo
        layout_interno.addLayout(linha_topo)
        layout_interno.addStretch() # Empurra o tempo pro centro
        layout_interno.addWidget(self.lbl_tempo_gigante)
        layout_interno.addStretch() # Empurra o tempo pro centro
        layout_interno.addLayout(linha_base)

        layout_principal.addWidget(self.main_frame)

        # 3. Estilização CSS
        self.setStyleSheet("""
            QFrame#pomodoroBackground {
                background-color: #1C1C1E; 
                border-radius: 24px;
            }
            QLabel#textoFase {
                color: #A1A1AA;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 14px;
                font-weight: 600;
            }
            QLabel#textoGigante {
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 56px; 
                font-weight: bold;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 15);
            }
        """)

        self.pos_antiga = None

    # --- LÓGICA DE ARRASTAR A TELA ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.pos_antiga = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.pos_antiga: return
        delta = event.globalPosition().toPoint() - self.pos_antiga
        self.move(self.pos() + delta)
        self.pos_antiga = event.globalPosition().toPoint()