import qtawesome as qta
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QScrollArea,
)

from src.styles.theme import ICON_COLOR, estilo_stopwatch


class StopwatchUI(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._pos_antiga = None
        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(240, 340)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("swBackground")
        layout_f = QVBoxLayout(self.main_frame)
        layout_f.setContentsMargins(14, 12, 14, 12)
        layout_f.setSpacing(8)

        # Header
        header = QHBoxLayout()
        lbl_titulo = QLabel("Cronômetro")
        lbl_titulo.setObjectName("swTitulo")
        btn_fechar = QPushButton()
        btn_fechar.setIcon(qta.icon("ph.x-bold", color=ICON_COLOR))
        btn_fechar.setFixedSize(24, 24)
        btn_fechar.setObjectName("swBtnFechar")
        btn_fechar.clicked.connect(self.hide)
        header.addWidget(lbl_titulo)
        header.addStretch()
        header.addWidget(btn_fechar)
        layout_f.addLayout(header)

        # Exibição do tempo
        self.lbl_tempo = QLabel("00:00.00")
        self.lbl_tempo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tempo.setObjectName("swTempo")
        layout_f.addWidget(self.lbl_tempo)

        # Botões: reset | play | volta
        linha_btns = QHBoxLayout()
        self.btn_reset = QPushButton()
        self.btn_reset.setIcon(qta.icon("ph.arrow-counter-clockwise-bold", color=ICON_COLOR))
        self.btn_reset.setFixedSize(36, 36)
        self.btn_reset.setObjectName("swBtnAcao")
        self.btn_reset.setToolTip("Zerar")

        self.btn_play = QPushButton()
        self.btn_play.setIcon(qta.icon("ph.play-fill", color=ICON_COLOR))
        self.btn_play.setFixedSize(48, 48)
        self.btn_play.setObjectName("swBtnPlay")

        self.btn_lap = QPushButton()
        self.btn_lap.setIcon(qta.icon("ph.flag-bold", color=ICON_COLOR))
        self.btn_lap.setFixedSize(36, 36)
        self.btn_lap.setObjectName("swBtnAcao")
        self.btn_lap.setToolTip("Registrar Volta")

        linha_btns.addWidget(self.btn_reset)
        linha_btns.addStretch()
        linha_btns.addWidget(self.btn_play)
        linha_btns.addStretch()
        linha_btns.addWidget(self.btn_lap)
        layout_f.addLayout(linha_btns)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("swSep")
        layout_f.addWidget(sep)

        # Lista de voltas
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container.setObjectName("swContainerVoltas")
        self._layout_voltas = QVBoxLayout(self._container)
        self._layout_voltas.setContentsMargins(0, 0, 0, 0)
        self._layout_voltas.setSpacing(2)

        self._lbl_vazio = QLabel("Nenhuma volta registrada")
        self._lbl_vazio.setObjectName("swLblVazio")
        self._lbl_vazio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout_voltas.addWidget(self._lbl_vazio)
        self._layout_voltas.addStretch()

        self._scroll.setWidget(self._container)
        layout_f.addWidget(self._scroll)

        layout.addWidget(self.main_frame)
        self.setStyleSheet(estilo_stopwatch())

    # ------------------------------------------------------------------

    def atualizar_icone_play(self, rodando: bool) -> None:
        icone = "ph.pause-fill" if rodando else "ph.play-fill"
        self.btn_play.setIcon(qta.icon(icone, color=ICON_COLOR))

    def adicionar_volta(self, numero: int, total: str, delta: str) -> None:
        if self._lbl_vazio.isVisible():
            self._lbl_vazio.hide()

        item = QFrame()
        item.setObjectName("swItemVolta")
        linha = QHBoxLayout(item)
        linha.setContentsMargins(4, 3, 4, 3)
        linha.setSpacing(6)

        lbl_num   = QLabel(f"#{numero}")
        lbl_delta = QLabel(delta)
        lbl_total = QLabel(total)
        lbl_num.setObjectName("swVoltaNum")
        lbl_delta.setObjectName("swVoltaDelta")
        lbl_total.setObjectName("swVoltaTotal")

        linha.addWidget(lbl_num)
        linha.addStretch()
        linha.addWidget(lbl_delta)
        linha.addSpacing(8)
        linha.addWidget(lbl_total)

        # Insere após o lbl_vazio (índice 0) para que o mais recente fique no topo
        self._layout_voltas.insertWidget(1, item)
        QTimer.singleShot(0, lambda: self._scroll.verticalScrollBar().setValue(0))

    def limpar_voltas(self) -> None:
        to_remove = [
            self._layout_voltas.itemAt(i).widget()
            for i in range(self._layout_voltas.count())
            if (w := self._layout_voltas.itemAt(i).widget())
            and w.objectName() == "swItemVolta"
        ]
        for w in to_remove:
            self._layout_voltas.removeWidget(w)
            w.deleteLater()
        self._lbl_vazio.show()

    # ------------------------------------------------------------------
    # Arrastar
    # ------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pos_antiga = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event) -> None:
        if not self._pos_antiga:
            return
        delta = event.globalPosition().toPoint() - self._pos_antiga
        self.move(self.pos() + delta)
        self._pos_antiga = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, _event) -> None:
        self._pos_antiga = None
