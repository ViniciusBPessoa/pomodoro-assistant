import qtawesome as qta
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame, QProgressBar
from PyQt6.QtCore import Qt

from src.frontend.DrawerWidget import DrawerWidget
from src.styles.theme import ICON_COLOR, estilo_pill


class PillWidget(QWidget):
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
        self.resize(190, 80)

        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        pill_frame = QFrame(self)
        pill_frame.setObjectName("pillBackground")

        layout_interno = QVBoxLayout(pill_frame)
        layout_interno.setContentsMargins(15, 8, 15, 8)
        layout_interno.setSpacing(2)

        # Linha superior: gaveta | tempo | ampliar
        linha_superior = QHBoxLayout()
        linha_superior.setContentsMargins(0, 0, 0, 0)

        self.btn_gaveta = QPushButton()
        self.btn_gaveta.setIcon(qta.icon("ph.caret-up-bold", color=ICON_COLOR))
        self.btn_gaveta.setFixedSize(24, 24)

        self.lbl_tempo = QLabel("25:00")
        self.lbl_tempo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_ampliar = QPushButton()
        self.btn_ampliar.setIcon(qta.icon("ph.corners-out-bold", color=ICON_COLOR))
        self.btn_ampliar.setFixedSize(24, 24)

        linha_superior.addWidget(self.btn_gaveta)
        linha_superior.addWidget(self.lbl_tempo)
        linha_superior.addWidget(self.btn_ampliar)

        # Linha do play
        linha_play = QHBoxLayout()
        linha_play.setContentsMargins(0, 0, 0, 0)

        self.btn_play = QPushButton()
        self.btn_play.setIcon(qta.icon("ph.play-fill", color=ICON_COLOR))
        self.btn_play.setFixedSize(20, 20)

        linha_play.addStretch()
        linha_play.addWidget(self.btn_play)
        linha_play.addStretch()

        # Barra de progresso fina no fundo da pílula
        self.barra_progresso = QProgressBar()
        self.barra_progresso.setObjectName("progressoPill")
        self.barra_progresso.setRange(0, 1000)
        self.barra_progresso.setValue(0)
        self.barra_progresso.setTextVisible(False)
        self.barra_progresso.setFixedHeight(4)

        layout_interno.addLayout(linha_superior)
        layout_interno.addLayout(linha_play)
        layout_interno.addWidget(self.barra_progresso)
        layout_principal.addWidget(pill_frame)

        self.setStyleSheet(estilo_pill())

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
        self.gaveta.atualizar_posicao()
