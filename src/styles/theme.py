# ---------------------------------------------------------------------------
# Paleta de cores — Modo Foco Profundo
# ---------------------------------------------------------------------------
DARK_BG           = "#1C1C1E"
DARK_BG_SECONDARY = "#2C2C2E"
DARK_BG_TERTIARY  = "#3A3A3C"
DARK_BG_HOVER     = "#48484A"
ICON_COLOR        = "#8E8E93"
TEXT_PRIMARY      = "#FFFFFF"
TEXT_SECONDARY    = "#A1A1AA"
ACCENT_HOVER      = "rgba(255, 255, 255, 15)"
BORDER_SUBTLE     = "#2C2C2E"

# Cores por fase do Pomodoro (texto, fundo transparente)
CORES_FASE: dict[str, tuple[str, str]] = {
    "foco":        ("#1FC228", "rgba(76, 175, 80, 0.15)"),
    "pausa_curta": ("#FF9800", "rgba(255, 152, 0, 0.15)"),
    "pausa_longa": ("#0A84FF", "rgba(33, 150, 243, 0.15)"),
}

# ---------------------------------------------------------------------------
# Scrollbar compartilhada
# ---------------------------------------------------------------------------
_SCROLLBAR_QSS = f"""
    QScrollBar:vertical {{
        background: {DARK_BG};
        width: 6px;
        margin: 0;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: {DARK_BG_TERTIARY};
        border-radius: 3px;
        min-height: 30px;
        margin: 0px 1px;
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: none;
    }}
"""

# ---------------------------------------------------------------------------
# PillWidget
# ---------------------------------------------------------------------------
def estilo_pill() -> str:
    return f"""
        QFrame#pillBackground {{
            background-color: {DARK_BG};
            border-radius: 20px;
        }}
        QLabel {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 26px;
            font-weight: 500;
        }}
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_HOVER};
        }}
    """


# ---------------------------------------------------------------------------
# PomodoroUI
# ---------------------------------------------------------------------------
def estilo_pomodoro() -> str:
    return f"""
        QFrame#pomodoroBackground {{
            background-color: {DARK_BG};
            border-radius: 24px;
        }}
        QLabel#textoFase {{
            color: {TEXT_SECONDARY};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 14px;
            font-weight: 600;
        }}
        QLabel#textoModo {{
            color: #4CAF50;
            background-color: rgba(76, 175, 80, 0.15);
            padding: 6px 16px;
            border-radius: 12px;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 14px;
            font-weight: bold;
        }}
        QLabel#textoGigante {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 56px;
            font-weight: bold;
        }}
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_HOVER};
        }}
    """


# ---------------------------------------------------------------------------
# DrawerWidget
# ---------------------------------------------------------------------------
def estilo_drawer() -> str:
    return f"""
        QFrame#drawerBackground {{
            background-color: {DARK_BG};
            border-radius: 18px;
        }}
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_HOVER};
        }}
    """


# ---------------------------------------------------------------------------
# SettingsUI
# ---------------------------------------------------------------------------
def estilo_configuracoes() -> str:
    return f"""
        QFrame#settingsBackground {{
            background-color: {DARK_BG};
            border-radius: 20px;
            border: 1px solid {BORDER_SUBTLE};
        }}
        /* --- Área de scroll --- */
        QScrollArea, QScrollArea > QWidget > QWidget {{
            background: transparent;
            border: none;
        }}
        /* --- Textos gerais --- */
        QLabel {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 14px;
            background: transparent;
        }}
        QLabel#tituloTexto {{
            font-size: 18px;
            font-weight: bold;
        }}
        QLabel#secaoTexto {{
            color: {ICON_COLOR};
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }}
        /* --- CustomSpinBox --- */
        QLabel#spinValor {{
            color: {TEXT_PRIMARY};
            font-size: 15px;
            font-weight: 600;
            background-color: {DARK_BG_SECONDARY};
            border-radius: 6px;
            padding: 2px 0;
        }}
        QLineEdit#spinEdit {{
            color: {TEXT_PRIMARY};
            font-size: 15px;
            font-weight: 600;
            background-color: {DARK_BG_SECONDARY};
            border: 1px solid #4CAF50;
            border-radius: 6px;
            padding: 0;
        }}
        QPushButton#btnSpinAcao {{
            background-color: {DARK_BG_TERTIARY};
            border: none;
            border-radius: 6px;
        }}
        QPushButton#btnSpinAcao:hover {{
            background-color: {DARK_BG_HOVER};
        }}
        /* --- Slider de volume --- */
        QSlider#sliderVolume::groove:horizontal {{
            height: 4px;
            background: {DARK_BG_TERTIARY};
            border-radius: 2px;
        }}
        QSlider#sliderVolume::handle:horizontal {{
            background: #4CAF50;
            width: 14px;
            height: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }}
        QSlider#sliderVolume::sub-page:horizontal {{
            background: #4CAF50;
            border-radius: 2px;
        }}
        /* --- QLineEdit (diretórios) --- */
        QLineEdit {{
            background-color: {DARK_BG_SECONDARY};
            color: {TEXT_PRIMARY};
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 13px;
        }}
        /* --- QCheckBox (ativar sons) --- */
        QCheckBox {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 14px;
            spacing: 8px;
            background: transparent;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 5px;
            background-color: {DARK_BG_SECONDARY};
            border: 1px solid {DARK_BG_TERTIARY};
        }}
        QCheckBox::indicator:checked {{
            background-color: #4CAF50;
            border: 1px solid #4CAF50;
        }}
        /* --- QComboBox (seletor de sons) --- */
        QComboBox {{
            background-color: {DARK_BG_SECONDARY};
            color: {TEXT_PRIMARY};
            border: none;
            border-radius: 6px;
            padding: 4px 8px;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 13px;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox::down-arrow {{
            width: 0;
            height: 0;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {ICON_COLOR};
            margin-right: 6px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {DARK_BG_SECONDARY};
            color: {TEXT_PRIMARY};
            selection-background-color: {DARK_BG_TERTIARY};
            border: 1px solid {DARK_BG_TERTIARY};
            outline: none;
        }}
        /* --- Botões gerais --- */
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 8px;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_HOVER};
        }}
        QPushButton#btnAcao {{
            background-color: {DARK_BG_TERTIARY};
            border-radius: 6px;
        }}
        QPushButton#btnAcao:hover {{
            background-color: {DARK_BG_HOVER};
        }}
        QPushButton#btnSalvar {{
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 14px;
        }}
        QPushButton#btnSalvar:hover {{
            background-color: #45A049;
        }}
        /* --- Zona de perigo --- */
        QLabel#secaoPerigo {{
            color: #FF453A;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }}
        QPushButton#btnPerigo {{
            background-color: rgba(255, 69, 58, 0.12);
            color: #FF453A;
            border: 1px solid rgba(255, 69, 58, 0.35);
            border-radius: 8px;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton#btnPerigo:hover {{
            background-color: rgba(255, 69, 58, 0.22);
            border: 1px solid rgba(255, 69, 58, 0.65);
        }}
        {_SCROLLBAR_QSS}
    """


# ---------------------------------------------------------------------------
# TodoUI
# ---------------------------------------------------------------------------
def estilo_todo() -> str:
    return f"""
        QFrame#todoBackground {{
            background-color: {DARK_BG};
            border-radius: 20px;
            border: 1px solid {BORDER_SUBTLE};
        }}
        QFrame#todoHeader {{
            background: transparent;
            border-bottom: 1px solid {DARK_BG_SECONDARY};
        }}
        QLabel#todoTitulo {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 16px;
            font-weight: bold;
            background: transparent;
        }}
        /* --- Tab bar --- */
        QTabWidget#todoTabs {{
            background: transparent;
        }}
        QTabWidget#todoTabs::pane {{
            border: none;
            background: transparent;
        }}
        QTabBar::tab {{
            background: {DARK_BG_SECONDARY};
            color: {ICON_COLOR};
            padding: 5px 12px;
            border-radius: 6px;
            margin: 4px 2px 4px 2px;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 12px;
        }}
        QTabBar::tab:selected {{
            background: {DARK_BG_TERTIARY};
            color: {TEXT_PRIMARY};
        }}
        QTabBar::tab:hover:!selected {{
            background: {DARK_BG_TERTIARY};
            color: {TEXT_SECONDARY};
        }}
        QTabBar::close-button {{
            subcontrol-position: right;
        }}
        /* --- Conteúdo das abas --- */
        QWidget#containerTarefas, QScrollArea#areaScroll {{
            background: transparent;
            border: none;
        }}
        /* --- Item de tarefa --- */
        QFrame#itemTarefa {{
            background: transparent;
            border-radius: 6px;
        }}
        QFrame#itemTarefa:hover {{
            background-color: {DARK_BG_SECONDARY};
        }}
        QCheckBox#checkTarefa {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 14px;
            spacing: 8px;
            background: transparent;
        }}
        QCheckBox#checkTarefa::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            background-color: {DARK_BG_SECONDARY};
            border: 1px solid {DARK_BG_TERTIARY};
        }}
        QCheckBox#checkTarefa::indicator:checked {{
            background-color: #4CAF50;
            border: 1px solid #4CAF50;
        }}
        QPushButton#btnRemoverTarefa {{
            background: transparent;
            border: none;
            border-radius: 4px;
        }}
        QPushButton#btnRemoverTarefa:hover {{
            background-color: rgba(255, 59, 48, 0.2);
        }}
        /* --- Separador entre tab bar e lista --- */
        QFrame#sepTodo {{
            color: {DARK_BG_TERTIARY};
            background-color: {DARK_BG_TERTIARY};
            max-height: 1px;
            border: none;
        }}
        /* --- Input de nova tarefa --- */
        QFrame#frameInputTarefa {{
            background: {DARK_BG_SECONDARY};
            border-bottom-left-radius: 18px;
            border-bottom-right-radius: 18px;
        }}
        QLineEdit#inputTarefa {{
            background: transparent;
            color: {TEXT_PRIMARY};
            border: none;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 13px;
            padding: 2px 0;
        }}
        QLineEdit#inputTarefa::placeholder {{
            color: {ICON_COLOR};
        }}
        QPushButton#btnAdicionarTarefa {{
            background-color: {DARK_BG_TERTIARY};
            border: none;
            border-radius: 6px;
        }}
        QPushButton#btnAdicionarTarefa:hover {{
            background-color: {DARK_BG_HOVER};
        }}
        /* --- Botões de cabeçalho --- */
        QPushButton#btnCabecalho {{
            background: transparent;
            border: none;
            border-radius: 6px;
        }}
        QPushButton#btnCabecalho:hover {{
            background-color: {ACCENT_HOVER};
        }}
        {_SCROLLBAR_QSS}
    """


# ---------------------------------------------------------------------------
# StatsUI
# ---------------------------------------------------------------------------
def estilo_stats() -> str:
    return f"""
        QFrame#statsBackground {{
            background-color: {DARK_BG};
            border-radius: 20px;
            border: 1px solid {BORDER_SUBTLE};
        }}
        QLabel#statsTitulo {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        }}
        QLabel {{
            background: transparent;
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }}
        QPushButton#btnFecharStats,
        QPushButton#btnNavStats,
        QPushButton#btnRefreshStats {{
            background-color: transparent;
            border: none;
            border-radius: 6px;
        }}
        QPushButton#btnFecharStats:hover,
        QPushButton#btnNavStats:hover {{
            background-color: {ACCENT_HOVER};
        }}
        QLabel#lblMesStats {{
            color: {TEXT_PRIMARY};
            font-size: 15px;
            font-weight: 600;
            background: transparent;
        }}
        QLabel#lblDiaSemana {{
            color: {ICON_COLOR};
            font-size: 11px;
            font-weight: 600;
            background: transparent;
        }}
        QFrame#sepStats {{
            color: {DARK_BG_SECONDARY};
            background-color: {DARK_BG_SECONDARY};
            max-height: 1px;
        }}
        QFrame#cartaoStat {{
            background-color: {DARK_BG_SECONDARY};
            border-radius: 10px;
        }}
        QLabel#cartaoTitulo {{
            color: {ICON_COLOR};
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.3px;
            background: transparent;
        }}
        QLabel#cartaoValor {{
            color: {TEXT_PRIMARY};
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        }}
        /* ── QTabWidget ── */
        QTabWidget#statsTabWidget {{
            background: transparent;
        }}
        QTabWidget#statsTabWidget::pane {{
            border: none;
            background: transparent;
        }}
        QTabWidget#statsTabWidget QTabBar::tab {{
            background: {DARK_BG_SECONDARY};
            color: {ICON_COLOR};
            padding: 5px 16px;
            border-radius: 7px;
            margin: 0 3px 6px 0;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 500;
        }}
        QTabWidget#statsTabWidget QTabBar::tab:selected {{
            background: {DARK_BG_TERTIARY};
            color: {TEXT_PRIMARY};
        }}
        QTabWidget#statsTabWidget QTabBar::tab:hover:!selected {{
            background: {DARK_BG_HOVER};
            color: {TEXT_SECONDARY};
        }}
        /* ── Seletores de visão (Analytics) ── */
        QPushButton#btnVisaoAnalytics {{
            background-color: {DARK_BG_SECONDARY};
            color: {ICON_COLOR};
            border: none;
            border-radius: 7px;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 12px;
            font-weight: 500;
            padding: 4px 0;
        }}
        QPushButton#btnVisaoAnalytics:checked {{
            background-color: {DARK_BG_TERTIARY};
            color: {TEXT_PRIMARY};
        }}
        QPushButton#btnVisaoAnalytics:hover:!checked {{
            background-color: {DARK_BG_HOVER};
        }}
        /* ── Label de seção (Analytics) ── */
        QLabel#secaoAnalytics {{
            color: {ICON_COLOR};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 0.5px;
            background: transparent;
        }}
    """


# ---------------------------------------------------------------------------
# StopwatchUI
# ---------------------------------------------------------------------------
def estilo_stopwatch() -> str:
    return f"""
        QFrame#swBackground {{
            background-color: {DARK_BG};
            border-radius: 20px;
            border: 1px solid {BORDER_SUBTLE};
        }}
        QLabel#swTitulo {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        }}
        QLabel#swTempo {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 42px;
            font-weight: bold;
            letter-spacing: 1px;
            background: transparent;
        }}
        QPushButton#swBtnFechar {{
            background: transparent;
            border: none;
            border-radius: 6px;
        }}
        QPushButton#swBtnFechar:hover {{
            background-color: {ACCENT_HOVER};
        }}
        QPushButton#swBtnPlay {{
            background-color: {DARK_BG_SECONDARY};
            border: none;
            border-radius: 24px;
        }}
        QPushButton#swBtnPlay:hover {{
            background-color: {DARK_BG_TERTIARY};
        }}
        QPushButton#swBtnAcao {{
            background-color: {DARK_BG_SECONDARY};
            border: none;
            border-radius: 18px;
        }}
        QPushButton#swBtnAcao:hover {{
            background-color: {DARK_BG_TERTIARY};
        }}
        QFrame#swSep {{
            color: {DARK_BG_SECONDARY};
            background-color: {DARK_BG_SECONDARY};
            max-height: 1px;
            border: none;
        }}
        QWidget#swContainerVoltas {{
            background: transparent;
        }}
        QScrollArea, QScrollArea > QWidget > QWidget {{
            background: transparent;
            border: none;
        }}
        QLabel#swLblVazio {{
            color: {ICON_COLOR};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 12px;
            background: transparent;
        }}
        QFrame#swItemVolta {{
            background: transparent;
            border-radius: 5px;
        }}
        QFrame#swItemVolta:hover {{
            background-color: {DARK_BG_SECONDARY};
        }}
        QLabel#swVoltaNum {{
            color: {ICON_COLOR};
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-size: 12px;
            background: transparent;
        }}
        QLabel#swVoltaDelta {{
            color: #4CAF50;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            background: transparent;
        }}
        QLabel#swVoltaTotal {{
            color: {TEXT_PRIMARY};
            font-family: 'Consolas', monospace;
            font-size: 12px;
            background: transparent;
        }}
        {_SCROLLBAR_QSS}
    """


# ---------------------------------------------------------------------------
# Helper: estilo da barra de progresso (cor dinâmica por fase)
# ---------------------------------------------------------------------------
def estilo_progressbar(fase: str) -> str:
    cor_chunk = CORES_FASE.get(fase, CORES_FASE["foco"])[0]
    return (
        f"QProgressBar {{"
        f"  background-color: {DARK_BG_SECONDARY};"
        f"  border-radius: 3px;"
        f"  border: none;"
        f"}}"
        f"QProgressBar::chunk {{"
        f"  background-color: {cor_chunk};"
        f"  border-radius: 3px;"
        f"}}"
    )


# ---------------------------------------------------------------------------
# Helper: cor dinâmica do label de modo (por fase)
# ---------------------------------------------------------------------------
def estilo_label_modo(fase: str) -> str:
    """Retorna stylesheet inline para lbl_modo_atual, com cor dinâmica por fase."""
    cor_texto, cor_fundo = CORES_FASE.get(fase, CORES_FASE["foco"])
    return (
        f"color: {cor_texto};"
        f"background-color: {cor_fundo};"
        "padding: 6px 16px;"
        "border-radius: 12px;"
        "font-family: 'Segoe UI', 'Inter', sans-serif;"
        "font-size: 14px;"
        "font-weight: bold;"
    )
