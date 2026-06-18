import qtawesome as qta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QLineEdit, QFileDialog,
    QCheckBox, QComboBox, QScrollArea, QSizePolicy, QSlider,
    QDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.backend.settings_manager import settings
from src.backend import audio_manager, database
from src.frontend.components import CustomSpinBox
from src.styles.theme import ICON_COLOR, DARK_BG, DARK_BG_SECONDARY, DARK_BG_TERTIARY, TEXT_PRIMARY, estilo_configuracoes


# ---------------------------------------------------------------------------
# Diálogo de confirmação destrutiva
# ---------------------------------------------------------------------------

class _DialogoConfirmarReset(QDialog):
    """Modal que exige digitar 'concordo' antes de zerar estatísticas."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        frame = QFrame()
        frame.setObjectName("dialogoBackground")
        frame.setStyleSheet(f"""
            QFrame#dialogoBackground {{
                background-color: {DARK_BG};
                border-radius: 16px;
                border: 1px solid #3A3A3C;
            }}
            QLabel {{ color: {TEXT_PRIMARY}; background: transparent;
                      font-family: 'Segoe UI', sans-serif; }}
            QLineEdit {{
                background-color: {DARK_BG_SECONDARY};
                color: {TEXT_PRIMARY};
                border: 1px solid #3A3A3C;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
            }}
            QLineEdit:focus {{ border: 1px solid #FF453A; }}
            QPushButton {{ border: none; border-radius: 8px;
                           font-family: 'Segoe UI', sans-serif;
                           font-size: 13px; font-weight: 500; }}
        """)

        layout_frame = QVBoxLayout(frame)
        layout_frame.setContentsMargins(20, 20, 20, 20)
        layout_frame.setSpacing(12)

        icone = QLabel("⚠")
        icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icone.setStyleSheet("font-size: 28px; color: #FF453A; background: transparent;")

        lbl_titulo = QLabel("Zerar Estatísticas")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF453A; background: transparent;")

        lbl_aviso = QLabel(
            "Esta ação é <b>irreversível</b>. Todo o histórico de Pomodoros, "
            "tempo de foco e sequências será permanentemente apagado.\n\n"
            "As configurações de tempo e som não serão afetadas."
        )
        lbl_aviso.setWordWrap(True)
        lbl_aviso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_aviso.setStyleSheet("font-size: 13px; color: #A1A1AA; background: transparent;")

        lbl_instrucao = QLabel('Digite <b style="color:#FFFFFF">concordo</b> para confirmar:')
        lbl_instrucao.setStyleSheet("font-size: 13px; color: #A1A1AA; background: transparent;")

        self._input = QLineEdit()
        self._input.setPlaceholderText("concordo")
        self._input.textChanged.connect(self._on_texto_alterado)

        linha_botoes = QHBoxLayout()
        self._btn_cancelar = QPushButton("Cancelar")
        self._btn_cancelar.setFixedHeight(36)
        self._btn_cancelar.setStyleSheet(
            f"background-color: {DARK_BG_TERTIARY}; color: {TEXT_PRIMARY};"
            "padding: 0 16px;"
        )
        self._btn_cancelar.clicked.connect(self.reject)

        self._btn_confirmar = QPushButton("Zerar Tudo")
        self._btn_confirmar.setFixedHeight(36)
        self._btn_confirmar.setEnabled(False)
        self._btn_confirmar.setStyleSheet(
            "background-color: rgba(255,69,58,0.15); color: #FF453A;"
            "border: 1px solid rgba(255,69,58,0.4); padding: 0 16px;"
        )
        self._btn_confirmar.clicked.connect(self.accept)

        linha_botoes.addWidget(self._btn_cancelar)
        linha_botoes.addWidget(self._btn_confirmar)

        layout_frame.addWidget(icone)
        layout_frame.addWidget(lbl_titulo)
        layout_frame.addWidget(lbl_aviso)
        layout_frame.addWidget(lbl_instrucao)
        layout_frame.addWidget(self._input)
        layout_frame.addLayout(linha_botoes)

        layout.addWidget(frame)
        self.adjustSize()

    def _on_texto_alterado(self, texto: str) -> None:
        ok = texto.strip().lower() == "concordo"
        self._btn_confirmar.setEnabled(ok)
        if ok:
            self._btn_confirmar.setStyleSheet(
                "background-color: rgba(255,69,58,0.3); color: #FF453A;"
                "border: 1px solid #FF453A; padding: 0 16px;"
            )
        else:
            self._btn_confirmar.setStyleSheet(
                "background-color: rgba(255,69,58,0.15); color: #FF453A;"
                "border: 1px solid rgba(255,69,58,0.4); padding: 0 16px;"
            )


class SettingsUI(QWidget):
    configuracoes_salvas = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._combos_sons: dict[str, QComboBox] = {}
        self._init_ui()
        self._carregar_configuracoes()

    # ------------------------------------------------------------------
    # Construção da interface
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(400, 480)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("settingsBackground")
        layout_frame = QVBoxLayout(self.main_frame)
        layout_frame.setContentsMargins(0, 0, 0, 0)
        layout_frame.setSpacing(0)

        layout_frame.addWidget(self._criar_cabecalho())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        conteudo = QWidget()
        conteudo.setObjectName("scrollConteudo")
        layout_conteudo = QVBoxLayout(conteudo)
        layout_conteudo.setContentsMargins(20, 10, 20, 10)
        layout_conteudo.setSpacing(6)

        layout_conteudo.addWidget(self._secao("TEMPOS (MINUTOS)"))
        layout_conteudo.addLayout(self._linha_spin("Foco:",        "spin_foco",  1, 120, 25))
        layout_conteudo.addLayout(self._linha_spin("Pausa Curta:", "spin_curta", 1,  60,  5))
        layout_conteudo.addLayout(self._linha_spin("Pausa Longa:", "spin_longa", 1,  60, 15))

        layout_conteudo.addSpacing(8)
        layout_conteudo.addWidget(self._secao("COMPORTAMENTO"))
        layout_conteudo.addLayout(self._linha_auto_reinicio())

        layout_conteudo.addSpacing(8)
        layout_conteudo.addWidget(self._secao("SOM E NOTIFICAÇÕES"))
        layout_conteudo.addLayout(self._linha_checkbox())
        layout_conteudo.addLayout(self._linha_volume())
        layout_conteudo.addLayout(self._linha_som("Início do Foco:",     "foco_inicio"))
        layout_conteudo.addLayout(self._linha_som("Início da Pausa:",    "pausa_inicio"))
        layout_conteudo.addLayout(self._linha_som("Ciclo Concluído:",    "ciclo_concluido"))

        layout_conteudo.addSpacing(8)
        layout_conteudo.addWidget(self._secao("DIRETÓRIOS DE SALVAMENTO"))
        self.input_todo, layout_todo = self._linha_pasta(
            "Todo List:", self._escolher_dir_todo
        )
        self.input_stats, layout_stats = self._linha_pasta(
            "Estatísticas (Sync):", self._escolher_dir_stats
        )
        layout_conteudo.addLayout(layout_todo)
        layout_conteudo.addLayout(layout_stats)

        layout_conteudo.addSpacing(12)
        layout_conteudo.addWidget(self._secao_perigo())
        layout_conteudo.addStretch()

        scroll.setWidget(conteudo)
        layout_frame.addWidget(scroll)

        wrapper_btn = QWidget()
        layout_btn = QHBoxLayout(wrapper_btn)
        layout_btn.setContentsMargins(20, 8, 20, 16)
        self.btn_salvar = QPushButton("Salvar Configurações")
        self.btn_salvar.setObjectName("btnSalvar")
        self.btn_salvar.setFixedHeight(40)
        self.btn_salvar.clicked.connect(self._salvar_configuracoes)
        layout_btn.addWidget(self.btn_salvar)
        layout_frame.addWidget(wrapper_btn)

        layout_principal.addWidget(self.main_frame)
        self.setStyleSheet(estilo_configuracoes())
        self._pos_antiga = None

    # ------------------------------------------------------------------
    # Helpers de criação de widgets
    # ------------------------------------------------------------------

    def _criar_cabecalho(self) -> QWidget:
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 16, 12, 12)

        self.lbl_titulo = QLabel("Configurações")
        self.lbl_titulo.setObjectName("tituloTexto")

        btn_fechar = QPushButton()
        btn_fechar.setIcon(qta.icon("ph.x-bold", color=ICON_COLOR))
        btn_fechar.setFixedSize(28, 28)
        btn_fechar.clicked.connect(self.hide)

        layout.addWidget(self.lbl_titulo)
        layout.addStretch()
        layout.addWidget(btn_fechar)
        return header

    @staticmethod
    def _secao(texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setObjectName("secaoTexto")
        return lbl

    def _linha_spin(self, label: str, attr: str, mn: int, mx: int, default: int) -> QHBoxLayout:
        spin = CustomSpinBox(mn, mx, default)
        setattr(self, attr, spin)
        linha = QHBoxLayout()
        linha.addWidget(QLabel(label))
        linha.addStretch()
        linha.addWidget(spin)
        return linha

    def _linha_auto_reinicio(self) -> QHBoxLayout:
        self.chk_auto_reinicio = QCheckBox("Reinício Automático")
        self.chk_auto_reinicio.setToolTip(
            "Inicia a próxima fase automaticamente ao término da fase atual"
        )
        linha = QHBoxLayout()
        linha.addWidget(self.chk_auto_reinicio)
        linha.addStretch()
        return linha

    def _linha_checkbox(self) -> QHBoxLayout:
        self.chk_sons = QCheckBox("Ativar sons de notificação")
        linha = QHBoxLayout()
        linha.addWidget(self.chk_sons)
        linha.addStretch()
        return linha

    def _linha_volume(self) -> QHBoxLayout:
        linha = QHBoxLayout()
        lbl = QLabel("Volume:")
        lbl.setFixedWidth(70)

        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setObjectName("sliderVolume")
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(settings.get("volume") or 70)
        self.slider_volume.setFixedHeight(20)

        self.lbl_volume_val = QLabel(f"{self.slider_volume.value()}%")
        self.lbl_volume_val.setFixedWidth(36)
        self.lbl_volume_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.slider_volume.valueChanged.connect(
            lambda v: self.lbl_volume_val.setText(f"{v}%")
        )

        btn_preview = QPushButton()
        btn_preview.setIcon(qta.icon("ph.speaker-high-fill", color="#FFFFFF"))
        btn_preview.setFixedSize(28, 28)
        btn_preview.setObjectName("btnAcao")
        btn_preview.setToolTip("Testar som com este volume")
        btn_preview.clicked.connect(self._preview_som)

        linha.addWidget(lbl)
        linha.addWidget(self.slider_volume)
        linha.addWidget(self.lbl_volume_val)
        linha.addWidget(btn_preview)
        return linha

    def _linha_som(self, label: str, chave: str) -> QHBoxLayout:
        linha = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(130)

        combo = QComboBox()
        combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._combos_sons[chave] = combo

        btn_play = QPushButton()
        btn_play.setIcon(qta.icon("ph.play-fill", color="#4CAF50"))
        btn_play.setFixedSize(28, 28)
        btn_play.setObjectName("btnAcao")
        btn_play.setToolTip("Testar este som")
        btn_play.clicked.connect(lambda: self._preview_som_chave(combo))

        btn_import = QPushButton()
        btn_import.setIcon(qta.icon("ph.folder-open-fill", color="#FFFFFF"))
        btn_import.setFixedSize(28, 28)
        btn_import.setObjectName("btnAcao")
        btn_import.setToolTip("Importar novo arquivo de som (.wav)")
        btn_import.clicked.connect(lambda: self._importar_som(combo))

        linha.addWidget(lbl)
        linha.addWidget(combo)
        linha.addWidget(btn_play)
        linha.addWidget(btn_import)
        return linha

    def _secao_perigo(self) -> QFrame:
        """Cria a seção 'ZONA DE PERIGO' com o botão de reset."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        lbl = QLabel("ZONA DE PERIGO")
        lbl.setObjectName("secaoPerigo")
        layout.addWidget(lbl)

        btn = QPushButton("Zerar Estatísticas")
        btn.setObjectName("btnPerigo")
        btn.setFixedHeight(36)
        btn.setToolTip("Apaga todo o histórico de Pomodoros e foco (irreversível)")
        btn.clicked.connect(self._confirmar_reset_stats)
        layout.addWidget(btn)
        return frame

    def _confirmar_reset_stats(self) -> None:
        dlg = _DialogoConfirmarReset(self)
        # Centraliza sobre a janela de configurações
        dlg.adjustSize()
        dlg.move(
            self.x() + (self.width()  - dlg.width())  // 2,
            self.y() + (self.height() - dlg.height()) // 2,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            database.zerar_estatisticas()

    def _linha_pasta(self, label: str, callback) -> tuple[QLineEdit, QVBoxLayout]:
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.addWidget(QLabel(label))

        linha = QHBoxLayout()
        campo = QLineEdit()
        campo.setReadOnly(True)
        campo.setPlaceholderText("Selecione a pasta...")

        btn = QPushButton()
        btn.setIcon(qta.icon("ph.folder-open-fill", color="#FFFFFF"))
        btn.setFixedSize(30, 30)
        btn.setObjectName("btnAcao")
        btn.clicked.connect(callback)

        linha.addWidget(campo)
        linha.addWidget(btn)
        layout.addLayout(linha)
        return campo, layout

    # ------------------------------------------------------------------
    # Lógica: sons
    # ------------------------------------------------------------------

    def _popular_combos_sons(self, selecionar: str | None = None, combo_alvo: QComboBox | None = None) -> None:
        sons = audio_manager.listar_sons()
        for chave, combo in self._combos_sons.items():
            valor_atual = combo.currentText() or settings.get(f"som_{chave}") or ""
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(sons)
            alvo = selecionar if (combo is combo_alvo and selecionar) else valor_atual
            idx = combo.findText(alvo)
            combo.setCurrentIndex(max(0, idx))
            combo.blockSignals(False)

    def _importar_som(self, combo: QComboBox) -> None:
        arquivo, _ = QFileDialog.getOpenFileName(
            self, "Selecionar arquivo de som", "", "Arquivos WAV (*.wav)"
        )
        if arquivo:
            nome = audio_manager.adicionar_som(arquivo)
            if nome:
                self._popular_combos_sons(selecionar=nome, combo_alvo=combo)

    def _preview_som_chave(self, combo: QComboBox) -> None:
        """Toca o som do combo especificado com o volume atual do slider."""
        nome_arquivo = combo.currentText()
        if not nome_arquivo:
            return
        from src.backend.audio_manager import SONS_DIR, _play
        caminho = SONS_DIR / nome_arquivo
        if not caminho.exists():
            return
        vol_anterior = settings.get("volume")
        settings.set("volume", self.slider_volume.value())
        _play(str(caminho))
        settings.set("volume", vol_anterior)

    def _preview_som(self) -> None:
        """Toca o primeiro som disponível como prévia do volume atual."""
        chave_combo = next(iter(self._combos_sons), None)
        if chave_combo:
            self._preview_som_chave(self._combos_sons[chave_combo])

    # ------------------------------------------------------------------
    # Lógica: diretórios
    # ------------------------------------------------------------------

    def _escolher_dir_todo(self) -> None:
        pasta = QFileDialog.getExistingDirectory(self, "Pasta para o Todo List")
        if pasta:
            self.input_todo.setText(pasta)

    def _escolher_dir_stats(self) -> None:
        pasta = QFileDialog.getExistingDirectory(self, "Pasta para Estatísticas (ex: Google Drive)")
        if pasta:
            self.input_stats.setText(pasta)

    # ------------------------------------------------------------------
    # Carregar / Salvar
    # ------------------------------------------------------------------

    def _carregar_configuracoes(self) -> None:
        self.spin_foco.setValue(settings.get("tempo_foco"))
        self.spin_curta.setValue(settings.get("tempo_curta"))
        self.spin_longa.setValue(settings.get("tempo_longa"))
        self.chk_auto_reinicio.setChecked(bool(settings.get("auto_reinicio")))
        self.chk_sons.setChecked(bool(settings.get("sons_ativados")))
        vol = settings.get("volume") or 70
        self.slider_volume.setValue(vol)
        self.lbl_volume_val.setText(f"{vol}%")
        self._popular_combos_sons()
        self.input_todo.setText(settings.get("dir_todolist") or "")
        self.input_stats.setText(settings.get("dir_stats") or "")

    def _salvar_configuracoes(self) -> None:
        settings.set("tempo_foco",       self.spin_foco.value())
        settings.set("tempo_curta",      self.spin_curta.value())
        settings.set("tempo_longa",      self.spin_longa.value())
        settings.set("auto_reinicio",    self.chk_auto_reinicio.isChecked())
        settings.set("sons_ativados",    self.chk_sons.isChecked())
        settings.set("volume",        self.slider_volume.value())
        for chave, combo in self._combos_sons.items():
            if combo.currentText():
                settings.set(f"som_{chave}", combo.currentText())
        settings.set("dir_todolist", self.input_todo.text())
        settings.set("dir_stats",    self.input_stats.text())
        self.configuracoes_salvas.emit()
        self.hide()

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
        self._popular_combos_sons()
        vol = settings.get("volume") or 70
        self.slider_volume.setValue(vol)
        self.lbl_volume_val.setText(f"{vol}%")
        super().showEvent(event)
