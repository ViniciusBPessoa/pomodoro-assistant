"""Componentes reutilizáveis de UI."""
import qtawesome as qta
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit, QStackedWidget,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIntValidator

from src.styles.theme import ICON_COLOR


class CustomSpinBox(QWidget):
    """
    Controle numérico com botões [-] e [+] explícitos.
    Clicar no número central ativa edição manual pelo teclado.
    API compatível com QSpinBox: value(), setValue(), valueChanged.
    """
    valueChanged = pyqtSignal(int)

    def __init__(
        self,
        minimo: int = 1,
        maximo: int = 120,
        valor: int = 25,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._min = minimo
        self._max = maximo
        self._valor = max(minimo, min(maximo, valor))
        self._editando = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.btn_menos = QPushButton()
        self.btn_menos.setIcon(qta.icon("ph.minus-bold", color=ICON_COLOR))
        self.btn_menos.setFixedSize(28, 28)
        self.btn_menos.setObjectName("btnSpinAcao")
        self.btn_menos.clicked.connect(self._decrementar)

        # Stack: QLabel (exibição) / QLineEdit (edição)
        self._stack = QStackedWidget()
        self._stack.setFixedSize(44, 28)

        self.lbl_valor = QLabel(str(self._valor))
        self.lbl_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_valor.setObjectName("spinValor")
        self.lbl_valor.setCursor(Qt.CursorShape.IBeamCursor)
        self.lbl_valor.mousePressEvent = self._iniciar_edicao

        self._edit = QLineEdit(str(self._valor))
        self._edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._edit.setObjectName("spinEdit")
        self._edit.setValidator(QIntValidator(minimo, maximo))
        self._edit.editingFinished.connect(self._confirmar_edicao)

        self._stack.addWidget(self.lbl_valor)  # índice 0
        self._stack.addWidget(self._edit)       # índice 1

        self.btn_mais = QPushButton()
        self.btn_mais.setIcon(qta.icon("ph.plus-bold", color=ICON_COLOR))
        self.btn_mais.setFixedSize(28, 28)
        self.btn_mais.setObjectName("btnSpinAcao")
        self.btn_mais.clicked.connect(self._incrementar)

        layout.addWidget(self.btn_menos)
        layout.addWidget(self._stack)
        layout.addWidget(self.btn_mais)

        # Tamanho fixo garante alinhamento perfeito em qualquer layout
        self.setFixedSize(28 + 4 + 44 + 4 + 28, 28)  # = 108 × 28

    # ------------------------------------------------------------------

    def _iniciar_edicao(self, _event=None) -> None:
        self._editando = True
        self._edit.setText(str(self._valor))
        self._edit.selectAll()
        self._stack.setCurrentIndex(1)
        self._edit.setFocus()

    def _confirmar_edicao(self) -> None:
        if not self._editando:
            return
        self._editando = False
        self._stack.setCurrentIndex(0)
        try:
            self.setValue(int(self._edit.text()))
        except ValueError:
            self.lbl_valor.setText(str(self._valor))

    def _decrementar(self) -> None:
        if self._editando:
            self._confirmar_edicao()
        self.setValue(self._valor - 1)

    def _incrementar(self) -> None:
        if self._editando:
            self._confirmar_edicao()
        self.setValue(self._valor + 1)

    # ------------------------------------------------------------------

    def value(self) -> int:
        return self._valor

    def setValue(self, valor: int) -> None:
        novo = max(self._min, min(self._max, valor))
        self._valor = novo
        self.lbl_valor.setText(str(novo))
        self.valueChanged.emit(novo)
