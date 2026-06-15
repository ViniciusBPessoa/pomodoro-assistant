import qtawesome as qta
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt

from src.frontend.DrawerWidget import DrawerWidget 

class PomodoroUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 1. Configurações da Janela Flutuante
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.WindowMinimizeButtonHint | 
            Qt.WindowType.WindowSystemMenuHint
        )   
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # MUDANÇA: Reduzi a altura para 280, já que tiramos várias coisas
        self.resize(260, 280)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        # 2. O "Corpo" Principal
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("pomodoroBackground")
        layout_interno = QVBoxLayout(self.main_frame)
        layout_interno.setContentsMargins(20, 20, 20, 20)

        cor_icone = '#8E8E93'

        # --- CABEÇALHO ---
        linha_topo = QHBoxLayout()
        
        self.btn_recolher = QPushButton()
        self.btn_recolher.setIcon(qta.icon('ph.corners-in-bold', color=cor_icone))
        self.btn_recolher.setFixedSize(28, 28)

        self.lbl_fase = QLabel("Ciclo 1/4")
        self.lbl_fase.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_fase.setObjectName("textoFase")

        self.btn_gaveta = QPushButton()
        self.btn_gaveta.setIcon(qta.icon('ph.caret-up-bold', color=cor_icone))
        self.btn_gaveta.setFixedSize(24, 24)

        linha_topo.addWidget(self.btn_gaveta)
        linha_topo.addWidget(self.lbl_fase)
        linha_topo.addWidget(self.btn_recolher)

        # --- INDICADOR DE MODO (Substituiu os botões Foco/Curta/Longa) ---
        linha_modos = QHBoxLayout()
        linha_modos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_modo_atual = QLabel("Em Foco")
        self.lbl_modo_atual.setObjectName("textoModo")
        linha_modos.addWidget(self.lbl_modo_atual)

        # --- CENTRO (Relógio Gigante sem os botões +/-) ---
        linha_tempo = QHBoxLayout()
        linha_tempo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_tempo_gigante = QLabel("25:00")
        self.lbl_tempo_gigante.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tempo_gigante.setObjectName("textoGigante")

        linha_tempo.addWidget(self.lbl_tempo_gigante)

        # --- RODAPÉ ---
        linha_base = QHBoxLayout()
        
        self.btn_reset = QPushButton()
        self.btn_reset.setIcon(qta.icon('ph.arrow-counter-clockwise-bold', color=cor_icone))
        self.btn_reset.setFixedSize(36, 36)
        self.btn_reset.setToolTip("Reiniciar")

        self.btn_play_grande = QPushButton()
        self.btn_play_grande.setIcon(qta.icon('ph.play-fill', color=cor_icone))
        self.btn_play_grande.setFixedSize(48, 48)

        self.btn_avancar = QPushButton()
        self.btn_avancar.setIcon(qta.icon('ph.fast-forward-bold', color=cor_icone))
        self.btn_avancar.setFixedSize(36, 36)
        self.btn_avancar.setToolTip("Pular Fase")

        linha_base.addWidget(self.btn_reset)
        linha_base.addStretch()
        linha_base.addWidget(self.btn_play_grande)
        linha_base.addStretch()
        linha_base.addWidget(self.btn_avancar)

        # Montando tudo
        layout_interno.addLayout(linha_topo)
        layout_interno.addSpacing(15) # Um pouco mais de respiro
        layout_interno.addLayout(linha_modos) 
        layout_interno.addStretch() 
        layout_interno.addLayout(linha_tempo) 
        layout_interno.addStretch() 
        layout_interno.addLayout(linha_base)

        layout_principal.addWidget(self.main_frame)

        # 3. Estilização CSS Limpa
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
            /* Novo visual do indicador de modo */
            QLabel#textoModo {
                color: #4CAF50; /* Verde sutil para foco */
                background-color: rgba(76, 175, 80, 0.15); /* Fundo transparente */
                padding: 6px 16px;
                border-radius: 12px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 14px;
                font-weight: bold;
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

        self.gaveta = DrawerWidget(self)
        self.btn_gaveta.clicked.connect(self.alternar_gaveta)
    
    def alternar_gaveta(self):
        cor_icone = '#8E8E93'
        if self.gaveta.aberta:
            self.btn_gaveta.setIcon(qta.icon('ph.caret-up-bold', color=cor_icone))
        else:
            self.btn_gaveta.setIcon(qta.icon('ph.caret-down-bold', color=cor_icone))
            
        self.gaveta.toggle()

    # --- LÓGICA DE ARRASTAR A TELA ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.pos_antiga = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.pos_antiga: return
        delta = event.globalPosition().toPoint() - self.pos_antiga
        self.move(self.pos() + delta)
        self.pos_antiga = event.globalPosition().toPoint()

        if hasattr(self, 'gaveta'):
            self.gaveta.atualizar_posicao()