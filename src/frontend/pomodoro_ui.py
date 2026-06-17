import qtawesome as qta
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QProgressBar
from PyQt6.QtCore import Qt

from src.frontend.DrawerWidget import DrawerWidget
from src.styles.theme import ICON_COLOR, estilo_pomodoro


class PomodoroUI(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowSystemMenuHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(260, 280)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("pomodoroBackground")
        layout_interno = QVBoxLayout(self.main_frame)
        layout_interno.setContentsMargins(20, 20, 20, 20)

        # --- Cabeçalho ---
        linha_topo = QHBoxLayout()

        self.btn_gaveta = QPushButton()
        self.btn_gaveta.setIcon(qta.icon("ph.caret-up-bold", color=ICON_COLOR))
        self.btn_gaveta.setFixedSize(24, 24)

        self.lbl_fase = QLabel("Ciclo 1/4")
        self.lbl_fase.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_fase.setObjectName("textoFase")

        self.btn_recolher = QPushButton()
        self.btn_recolher.setIcon(qta.icon("ph.corners-in-bold", color=ICON_COLOR))
        self.btn_recolher.setFixedSize(28, 28)

        linha_topo.addWidget(self.btn_gaveta)
        linha_topo.addWidget(self.lbl_fase)
        linha_topo.addWidget(self.btn_recolher)

        # --- Indicador de modo ---
        linha_modos = QHBoxLayout()
        linha_modos.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_modo_atual = QLabel("Em Foco")
        self.lbl_modo_atual.setObjectName("textoModo")
        linha_modos.addWidget(self.lbl_modo_atual)

        # --- Relógio gigante ---
        linha_tempo = QHBoxLayout()
        linha_tempo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_tempo_gigante = QLabel("25:00")
        self.lbl_tempo_gigante.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tempo_gigante.setObjectName("textoGigante")

        linha_tempo.addWidget(self.lbl_tempo_gigante)

        # --- Barra de progresso ---
        self.barra_progresso = QProgressBar()
        self.barra_progresso.setObjectName("progressoPomodoro")
        self.barra_progresso.setRange(0, 1000)
        self.barra_progresso.setValue(0)
        self.barra_progresso.setTextVisible(False)
        self.barra_progresso.setFixedHeight(6)

        # --- Rodapé: reset | play | skip ---
        linha_base = QHBoxLayout()

        self.btn_reset = QPushButton()
        self.btn_reset.setIcon(qta.icon("ph.arrow-counter-clockwise-bold", color=ICON_COLOR))
        self.btn_reset.setFixedSize(36, 36)
        self.btn_reset.setToolTip("Reiniciar")

        self.btn_play_grande = QPushButton()
        self.btn_play_grande.setIcon(qta.icon("ph.play-fill", color=ICON_COLOR))
        self.btn_play_grande.setFixedSize(48, 48)

        self.btn_avancar = QPushButton()
        self.btn_avancar.setIcon(qta.icon("ph.fast-forward-bold", color=ICON_COLOR))
        self.btn_avancar.setFixedSize(36, 36)
        self.btn_avancar.setToolTip("Pular Fase")

        linha_base.addWidget(self.btn_reset)
        linha_base.addStretch()
        linha_base.addWidget(self.btn_play_grande)
        linha_base.addStretch()
        linha_base.addWidget(self.btn_avancar)

        layout_interno.addLayout(linha_topo)
        layout_interno.addSpacing(15)
        layout_interno.addLayout(linha_modos)
        layout_interno.addStretch()
        layout_interno.addLayout(linha_tempo)
        layout_interno.addSpacing(10)
        layout_interno.addWidget(self.barra_progresso)
        layout_interno.addStretch()
        layout_interno.addLayout(linha_base)

        layout_principal.addWidget(self.main_frame)

        self.setStyleSheet(estilo_pomodoro())

        self._pos_antiga = None

        self.gaveta = DrawerWidget(self)
        self.btn_gaveta.clicked.connect(self._alternar_gaveta)

    def _alternar_gaveta(self) -> None:
        icone = "ph.caret-down-bold" if not self.gaveta.aberta else "ph.caret-up-bold"
        self.btn_gaveta.setIcon(qta.icon(icone, color=ICON_COLOR))
        self.gaveta.toggle()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pos_antiga = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event) -> None:
        if not self._pos_antiga:
            return
        delta = event.globalPosition().toPoint() - self._pos_antiga
        self.move(self.pos() + delta)
        self._pos_antiga = event.globalPosition().toPoint()
        if hasattr(self, "gaveta"):
            self.gaveta.atualizar_posicao()
