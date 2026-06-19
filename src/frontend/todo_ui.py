import qtawesome as qta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QTabWidget, QTabBar, QScrollArea, QLineEdit, QCheckBox,
    QInputDialog, QSizePolicy, QSizeGrip
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QTimer

from src.backend.todo_manager import TodoManager
from src.styles.theme import ICON_COLOR, TEXT_SECONDARY, estilo_todo


# ---------------------------------------------------------------------------
# Widget de item individual de tarefa
# ---------------------------------------------------------------------------

class _ItemTarefa(QFrame):
    alternada = pyqtSignal(str)
    removida  = pyqtSignal(str)
    editada   = pyqtSignal(str, str)  # (tarefa_id, novo_texto)

    def __init__(self, tarefa_id: str, texto: str, feita: bool, parent=None) -> None:
        super().__init__(parent)
        self.tarefa_id = tarefa_id
        self._feita = feita
        self.setObjectName("itemTarefa")

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(6, 3, 6, 3)
        self._layout.setSpacing(8)

        self.chk = QCheckBox()
        self.chk.setChecked(feita)
        self.chk.setObjectName("checkTarefa")

        self.lbl = QLabel(texto)
        self.lbl.setObjectName("textoTarefa")
        self.lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.lbl.setWordWrap(True)
        self._aplicar_estilo_texto(feita)

        self._edit = QLineEdit(texto)
        self._edit.setObjectName("inputTarefa")
        self._edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._edit.setVisible(False)
        self._edit.returnPressed.connect(self._confirmar_edicao)
        self._edit.installEventFilter(self)

        self.btn_remover = QPushButton()
        self.btn_remover.setIcon(qta.icon("ph.x-bold", color="#8E8E93"))
        self.btn_remover.setFixedSize(20, 20)
        self.btn_remover.setObjectName("btnRemoverTarefa")
        self.btn_remover.setVisible(False)

        self._layout.addWidget(self.chk)
        self._layout.addWidget(self.lbl)
        self._layout.addWidget(self._edit)
        self._layout.addWidget(self.btn_remover)

        self.chk.toggled.connect(self._on_toggle)
        self.btn_remover.clicked.connect(lambda: self.removida.emit(self.tarefa_id))
        self.lbl.mouseDoubleClickEvent = lambda _: self._iniciar_edicao()

    def _on_toggle(self, feita: bool) -> None:
        self._feita = feita
        self._aplicar_estilo_texto(feita)
        self.alternada.emit(self.tarefa_id)

    def _aplicar_estilo_texto(self, feita: bool) -> None:
        cor = "#5A5A5E" if feita else "#FFFFFF"
        strike = "line-through" if feita else "none"
        self.lbl.setStyleSheet(
            f"color: {cor}; text-decoration: {strike};"
            "font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px;"
            "background: transparent;"
        )

    def _iniciar_edicao(self) -> None:
        self._edit.setText(self.lbl.text())
        self.lbl.setVisible(False)
        self._edit.setVisible(True)
        self._edit.setFocus()
        self._edit.selectAll()

    def _confirmar_edicao(self) -> None:
        novo = self._edit.text().strip()
        if novo and novo != self.lbl.text():
            self.lbl.setText(novo)
            self._aplicar_estilo_texto(self._feita)
            self.editada.emit(self.tarefa_id, novo)
        self._edit.setVisible(False)
        self.lbl.setVisible(True)

    def _cancelar_edicao(self) -> None:
        self._edit.setVisible(False)
        self.lbl.setVisible(True)

    def eventFilter(self, obj, event) -> bool:
        if obj is self._edit and event.type() == QEvent.Type.FocusOut:
            self._confirmar_edicao()
            return False
        return super().eventFilter(obj, event)

    def enterEvent(self, event) -> None:
        self.btn_remover.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.btn_remover.setVisible(False)
        super().leaveEvent(event)


# ---------------------------------------------------------------------------
# Conteúdo de uma aba (lista de tarefas + input)
# ---------------------------------------------------------------------------

class _ConteudoAba(QWidget):
    def __init__(self, manager: TodoManager, aba_id: str) -> None:
        super().__init__()
        self._manager = manager
        self._aba_id  = aba_id
        self.setProperty("aba_id", aba_id)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Separador sutil no topo
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("sepTodo")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # Área scrollável
        self._scroll = QScrollArea()
        self._scroll.setObjectName("areaScroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container.setObjectName("containerTarefas")
        self._layout_tarefas = QVBoxLayout(self._container)
        self._layout_tarefas.setContentsMargins(8, 6, 8, 6)
        self._layout_tarefas.setSpacing(2)
        self._layout_tarefas.addStretch()

        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

        # Input de nova tarefa
        frame_input = QFrame()
        frame_input.setObjectName("frameInputTarefa")
        layout_input = QHBoxLayout(frame_input)
        layout_input.setContentsMargins(10, 8, 10, 8)
        layout_input.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Nova tarefa… (Enter para adicionar)")
        self._input.setObjectName("inputTarefa")
        self._input.returnPressed.connect(self._adicionar_tarefa)

        btn_add = QPushButton()
        btn_add.setIcon(qta.icon("ph.plus-bold", color=ICON_COLOR))
        btn_add.setFixedSize(28, 28)
        btn_add.setObjectName("btnAdicionarTarefa")
        btn_add.clicked.connect(self._adicionar_tarefa)

        layout_input.addWidget(self._input)
        layout_input.addWidget(btn_add)
        layout.addWidget(frame_input)

        self._carregar_tarefas()

    def _carregar_tarefas(self) -> None:
        while self._layout_tarefas.count() > 1:
            item = self._layout_tarefas.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for t in self._manager.obter_tarefas(self._aba_id):
            self._inserir_item(t["id"], t["texto"], t["feita"])

    def _inserir_item(self, tarefa_id: str, texto: str, feita: bool) -> None:
        item = _ItemTarefa(tarefa_id, texto, feita)
        item.alternada.connect(lambda tid: self._manager.toggle_tarefa(self._aba_id, tid))
        item.removida.connect(self._remover_tarefa_ui)
        item.editada.connect(lambda tid, txt: self._manager.editar_tarefa(self._aba_id, tid, txt))
        self._layout_tarefas.insertWidget(self._layout_tarefas.count() - 1, item)

    def _adicionar_tarefa(self) -> None:
        texto = self._input.text().strip()
        if not texto:
            return
        tarefa_id = self._manager.adicionar_tarefa(self._aba_id, texto)
        if tarefa_id:
            self._inserir_item(tarefa_id, texto, False)
            self._input.clear()
            self._scroll.verticalScrollBar().setValue(
                self._scroll.verticalScrollBar().maximum()
            )

    def _remover_tarefa_ui(self, tarefa_id: str) -> None:
        self._manager.remover_tarefa(self._aba_id, tarefa_id)
        for i in range(self._layout_tarefas.count()):
            item = self._layout_tarefas.itemAt(i)
            if item and isinstance(item.widget(), _ItemTarefa):
                if item.widget().tarefa_id == tarefa_id:
                    w = self._layout_tarefas.takeAt(i).widget()
                    w.deleteLater()
                    break

    def focar_input(self) -> None:
        self._input.setFocus()


# ---------------------------------------------------------------------------
# Janela principal da Todo List
# ---------------------------------------------------------------------------

class TodoUI(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._manager = TodoManager()
        self._plus_tab_idx = -1
        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(300, 400)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("todoBackground")
        layout_interno = QVBoxLayout(self.main_frame)
        layout_interno.setContentsMargins(0, 0, 0, 0)
        layout_interno.setSpacing(0)

        # Cabeçalho (só título + fechar)
        header = QFrame()
        header.setObjectName("todoHeader")
        layout_header = QHBoxLayout(header)
        layout_header.setContentsMargins(14, 10, 8, 10)
        layout_header.setSpacing(6)

        lbl_titulo = QLabel("To-Do List")
        lbl_titulo.setObjectName("todoTitulo")

        btn_fechar = QPushButton()
        btn_fechar.setIcon(qta.icon("ph.x-bold", color=ICON_COLOR))
        btn_fechar.setFixedSize(24, 24)
        btn_fechar.setObjectName("btnCabecalho")
        btn_fechar.clicked.connect(self.hide)

        layout_header.addWidget(lbl_titulo)
        layout_header.addStretch()
        layout_header.addWidget(btn_fechar)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("todoTabs")
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._remover_aba)
        self.tabs.currentChanged.connect(self._on_current_changed)
        self.tabs.tabBar().installEventFilter(self)

        layout_interno.addWidget(header)
        layout_interno.addWidget(self.tabs)

        # --- CÓDIGO NOVO: Área de redimensionamento (Size Grip) ---
        layout_rodape = QHBoxLayout()
        layout_rodape.setContentsMargins(0, 0, 0, 0)
        
        # O stretch empurra o ícone de redimensionamento totalmente para a direita
        layout_rodape.addStretch() 
        
        # Cria o grip passando a janela principal (self) como referência
        grip = QSizeGrip(self)
        grip.setFixedSize(16, 16) 
        
        layout_rodape.addWidget(grip)
        layout_interno.addLayout(layout_rodape)
        # ----------------------------------------------------------

        layout_principal.addWidget(self.main_frame)

        self.setStyleSheet(estilo_todo())
        self._carregar_abas()
        self._pos_antiga = None

    # ------------------------------------------------------------------
    # Filtro de evento (duplo clique na tab bar para renomear)
    # ------------------------------------------------------------------

    def eventFilter(self, obj, event) -> bool:
        if obj is self.tabs.tabBar() and event.type() == QEvent.Type.MouseButtonDblClick:
            idx = self.tabs.tabBar().tabAt(event.position().toPoint())
            if idx >= 0 and idx != self._plus_tab_idx:
                self._renomear_aba(idx)
                return True
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    # Gerenciamento de abas
    # ------------------------------------------------------------------

    def _carregar_abas(self) -> None:
        for aba in self._manager.obter_abas():
            self._criar_aba_na_ui(aba["id"], aba["nome"])
        self._adicionar_plus_tab()

    def _adicionar_plus_tab(self) -> None:
        """Adiciona a pseudo-aba '+' no final (não é removível)."""
        placeholder = QWidget()
        self._plus_tab_idx = self.tabs.addTab(placeholder, "+")
        self.tabs.tabBar().setTabButton(
            self._plus_tab_idx, QTabBar.ButtonPosition.RightSide, None
        )

    def _criar_aba_na_ui(self, aba_id: str, nome: str) -> None:
        conteudo = _ConteudoAba(self._manager, aba_id)
        # Insere antes da aba "+"
        idx = self._plus_tab_idx if self._plus_tab_idx >= 0 else self.tabs.count()
        self.tabs.insertTab(idx, conteudo, nome)
        self._plus_tab_idx = self.tabs.count() - 1

    def _on_current_changed(self, idx: int) -> None:
        """Impede selecionar a aba '+' — abre diálogo em vez disso."""
        if idx == self._plus_tab_idx:
            prev = max(0, idx - 1)
            self.tabs.setCurrentIndex(prev)
            QTimer.singleShot(0, self._adicionar_aba)

    def _adicionar_aba(self) -> None:
        nome, ok = QInputDialog.getText(self, "Nova Aba", "Nome da aba:")
        if ok and nome.strip():
            aba_id = self._manager.adicionar_aba(nome.strip())
            self._criar_aba_na_ui(aba_id, nome.strip())
            self.tabs.setCurrentIndex(self._plus_tab_idx - 1)

    def _remover_aba(self, index: int) -> None:
        if index == self._plus_tab_idx:
            return
        if self.tabs.count() <= 2:  # 1 aba real + aba "+"
            return
        widget = self.tabs.widget(index)
        aba_id = widget.property("aba_id")
        self._manager.remover_aba(aba_id)
        self.tabs.removeTab(index)
        self._plus_tab_idx = self.tabs.count() - 1

    def _renomear_aba(self, index: int) -> None:
        nome_atual = self.tabs.tabText(index)
        novo_nome, ok = QInputDialog.getText(
            self, "Renomear Aba", "Novo nome:", text=nome_atual
        )
        if ok and novo_nome.strip():
            widget = self.tabs.widget(index)
            aba_id = widget.property("aba_id")
            self._manager.renomear_aba(aba_id, novo_nome.strip())
            self.tabs.setTabText(index, novo_nome.strip())

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

    def showEvent(self, event) -> None:
        super().showEvent(event)
        widget_atual = self.tabs.currentWidget()
        if isinstance(widget_atual, _ConteudoAba):
            widget_atual.focar_input()
