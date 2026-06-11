import qtawesome as qta
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QButtonGroup
from PyQt6.QtCore import Qt

class PomodoroUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 1. Configurações da Janela Flutuante
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Aumentei a altura de leve (340) para acomodar a nova linha com folga
        self.resize(260, 340)

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

        self.lbl_fase = QLabel("Ciclo 1/4")
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

        # --- SELETORES DE MODO (Foco, Pausa Curta, Pausa Longa) ---
        linha_modos = QHBoxLayout()
        linha_modos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        linha_modos.setSpacing(5)

        self.btn_modo_foco = QPushButton("Foco")
        self.btn_modo_foco.setObjectName("btnModo")
        self.btn_modo_foco.setCheckable(True)
        self.btn_modo_foco.setChecked(True) # Foco já vem selecionado por padrão

        self.btn_modo_curta = QPushButton("Curta")
        self.btn_modo_curta.setObjectName("btnModo")
        self.btn_modo_curta.setCheckable(True)

        self.btn_modo_longa = QPushButton("Longa")
        self.btn_modo_longa.setObjectName("btnModo")
        self.btn_modo_longa.setCheckable(True)

        # O QButtonGroup faz eles agirem como botões de rádio (só 1 ativo por vez)
        self.grupo_modos = QButtonGroup(self)
        self.grupo_modos.addButton(self.btn_modo_foco)
        self.grupo_modos.addButton(self.btn_modo_curta)
        self.grupo_modos.addButton(self.btn_modo_longa)

        linha_modos.addWidget(self.btn_modo_foco)
        linha_modos.addWidget(self.btn_modo_curta)
        linha_modos.addWidget(self.btn_modo_longa)

        # --- CENTRO (O Relógio Gigante com Ajuste Rápido) ---
        linha_tempo = QHBoxLayout()
        linha_tempo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        linha_tempo.setSpacing(10) # Espaço entre o relógio e os botões

        self.btn_menos = QPushButton()
        self.btn_menos.setIcon(qta.icon('ph.minus-bold', color=cor_icone))
        self.btn_menos.setFixedSize(36, 36)
        self.btn_menos.setToolTip("Diminuir 1 minuto")
        self.btn_menos.setObjectName("btnAjusteTempo") # Tag para o CSS

        self.lbl_tempo_gigante = QLabel("25:00")
        self.lbl_tempo_gigante.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tempo_gigante.setObjectName("textoGigante")

        self.btn_mais = QPushButton()
        self.btn_mais.setIcon(qta.icon('ph.plus-bold', color=cor_icone))
        self.btn_mais.setFixedSize(36, 36)
        self.btn_mais.setToolTip("Adicionar 1 minuto")
        self.btn_mais.setObjectName("btnAjusteTempo")

        linha_tempo.addWidget(self.btn_menos)
        linha_tempo.addWidget(self.lbl_tempo_gigante)
        linha_tempo.addWidget(self.btn_mais)

        # --- RODAPÉ (Botões de Ação) ---
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
        layout_interno.addSpacing(10)
        layout_interno.addLayout(linha_modos) # Adicionando os seletores de modo
        layout_interno.addStretch() 
        layout_interno.addLayout(linha_tempo) # Adiciona a linha com os botões +/-
        layout_interno.addStretch() 
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
            /* ESTILO DOS BOTÕES DE MODO */
            QPushButton#btnModo {
                color: #8E8E93;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 12px;
                font-weight: 600;
                padding: 6px 12px;
                border-radius: 12px;
            }
            QPushButton#btnModo:hover {
                color: #FFFFFF;
                background-color: rgba(255, 255, 255, 10);
            }
            QPushButton#btnModo:checked {
                color: #FFFFFF;
                background-color: rgba(255, 255, 255, 25);
            }
            /* ESTILO DOS BOTÕES DE AJUSTE (+ / -) */
            QPushButton#btnAjusteTempo {
                background-color: rgba(255, 255, 255, 5);
                border-radius: 18px; /* Fica redondinho */
            }
            QPushButton#btnAjusteTempo:hover {
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