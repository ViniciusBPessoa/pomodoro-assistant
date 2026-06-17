import qtawesome as qta
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve

from src.styles.theme import ICON_COLOR, estilo_drawer


class DrawerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.parent_widget = parent
        self.largura       = 44
        self.altura_aberta = 180  # 4 botões × 34 + 3 espaços × 8 + margens 20 = 180

        self.resize(self.largura, 0)

        self.frame = QFrame(self)
        self.frame.setObjectName("drawerBackground")
        self.frame.resize(self.largura, self.altura_aberta)

        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(5, 10, 5, 10)
        layout.setSpacing(8)

        self.btn_todos      = self._criar_botao("ph.check-square",        "To-Do List")
        self.btn_stopwatch  = self._criar_botao("ph.timer-bold",         "Cronômetro")
        self.btn_stats      = self._criar_botao("ph.chart-bar",          "Estatísticas")
        self.btn_config     = self._criar_botao("ph.sliders-horizontal", "Configurações")

        for btn in (self.btn_todos, self.btn_stopwatch, self.btn_stats, self.btn_config):
            btn.setFixedSize(34, 34)
            layout.addWidget(btn)

        self.setStyleSheet(estilo_drawer())

        self._animacao = QPropertyAnimation(self, b"geometry")
        self._animacao.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animacao.setDuration(250)
        self.aberta = False

    def _criar_botao(self, icone: str, tooltip: str) -> QPushButton:
        btn = QPushButton()
        btn.setIcon(qta.icon(icone, color=ICON_COLOR))
        btn.setToolTip(tooltip)
        return btn

    def atualizar_posicao(self) -> None:
        if not self.parent_widget:
            return
        x      = self.parent_widget.x() + 10
        y_base = self.parent_widget.y() - 10
        if self.aberta:
            self.setGeometry(x, y_base - self.altura_aberta, self.largura, self.altura_aberta)
        else:
            self.setGeometry(x, y_base, self.largura, 0)

    def toggle(self) -> None:
        if not self.parent_widget:
            return
        x      = self.parent_widget.x() + 10
        y_base = self.parent_widget.y() - 10

        self._animacao.setStartValue(self.geometry())

        if self.aberta:
            self._animacao.setEndValue(QRect(x, y_base, self.largura, 0))
        else:
            self._animacao.setEndValue(
                QRect(x, y_base - self.altura_aberta, self.largura, self.altura_aberta)
            )

        self.aberta = not self.aberta
        self.show()
        self._animacao.start()
