import qtawesome as qta
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve

class DrawerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Tool e Frameless garantem que ela não crie um ícone extra na barra de tarefas e flutue
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.parent_widget = parent
        self.largura = 44
        self.altura_aberta = 220

        # Começa com altura 0 (escondida)
        self.resize(self.largura, 0)

        # O corpo da gaveta
        self.frame = QFrame(self)
        self.frame.setObjectName("drawerBackground")
        self.frame.resize(self.largura, self.altura_aberta)

        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(5, 10, 5, 10)
        layout.setSpacing(8)

        # --- CRIANDO OS BOTÕES DA GAVETA ---
        cor_icone = '#8E8E93'

        self.btn_modo = QPushButton()
        self.btn_modo.setIcon(qta.icon('ph.hourglass-high', color=cor_icone))
        self.btn_modo.setToolTip("Modos de Foco")
        
        self.btn_todos = QPushButton()
        self.btn_todos.setIcon(qta.icon('ph.check-square', color=cor_icone))
        self.btn_todos.setToolTip("ToDos")
        
        self.btn_markdown = QPushButton()
        self.btn_markdown.setIcon(qta.icon('ph.pencil-simple', color=cor_icone))
        self.btn_markdown.setToolTip("Notas / Markdown")
        
        self.btn_stats = QPushButton()
        self.btn_stats.setIcon(qta.icon('ph.chart-bar', color=cor_icone))
        self.btn_stats.setToolTip("Estatísticas")

        self.btn_config = QPushButton()
        self.btn_config.setIcon(qta.icon('ph.sliders-horizontal', color=cor_icone))
        self.btn_config.setToolTip("Configurações")

        for btn in [self.btn_modo, self.btn_todos, self.btn_markdown, self.btn_stats, self.btn_config]:
            btn.setFixedSize(34, 34)
            layout.addWidget(btn)

        # CSS da Gaveta
        self.setStyleSheet("""
            QFrame#drawerBackground {
                background-color: #1C1C1E; 
                border-radius: 18px;
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

        # Configuração da Animação
        self.animacao = QPropertyAnimation(self, b"geometry")
        self.animacao.setEasingCurve(QEasingCurve.Type.InOutQuad) # Suavidade no movimento
        self.animacao.setDuration(250) # Velocidade em ms
        self.aberta = False

    def atualizar_posicao(self):
        """Mantém a gaveta colada na pílula quando arrastada"""
        if self.parent_widget:
            # Alinhado com o botão esquerdo da pílula
            x = self.parent_widget.x() + 10 
            y_base = self.parent_widget.y() - 10 
            
            if self.aberta:
                self.setGeometry(x, y_base - self.altura_aberta, self.largura, self.altura_aberta)
            else:
                self.setGeometry(x, y_base, self.largura, 0)

    def toggle(self):
        """Aciona o abrir/fechar"""
        if not self.parent_widget:
            return

        x = self.parent_widget.x() + 10
        y_base = self.parent_widget.y() - 10

        self.animacao.setStartValue(self.geometry())

        if self.aberta:
            # Fechando: altura vai para 0, Y desce
            self.animacao.setEndValue(QRect(x, y_base, self.largura, 0))
        else:
            # Abrindo: altura aumenta, Y sobe
            self.animacao.setEndValue(QRect(x, y_base - self.altura_aberta, self.largura, self.altura_aberta))

        self.aberta = not self.aberta
        self.show()
        self.animacao.start()
