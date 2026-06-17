import calendar
from datetime import date, timedelta

import qtawesome as qta
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QGridLayout, QTabWidget,
)

from src.backend import database
from src.styles.theme import ICON_COLOR, estilo_stats

# ── Paleta do matplotlib (espelha o dark theme do app) ────────────────────
_BG        = "#1C1C1E"
_AX_BG     = "#242426"
_GRID_C    = "#2C2C2E"
_TEXT_C    = "#8E8E93"
_BAR_C     = "#1FC228"
_BAR_EMPTY = "#252527"
_TREND_C   = "#FF9800"
_DPI       = 80

_NOMES_MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
_NOMES_DIAS_SEMANA_ABREV = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
_NOMES_DIAS_SEMANA_COMPLETO = [
    "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo",
]


def _formatar_tempo(segundos: int) -> str:
    if segundos <= 0:
        return "0 min"
    minutos = segundos // 60
    if minutos < 60:
        return f"{minutos} min"
    horas = minutos // 60
    mins_resto = minutos % 60
    return f"{horas}h {mins_resto:02d}min" if mins_resto else f"{horas}h"


def _cor_para_segundos(segundos: int) -> str:
    if segundos <= 0:
        return "#2A2A2C"
    if segundos < 1800:
        return "#1A3D1C"
    if segundos < 3600:
        return "#2D6131"
    if segundos < 7200:
        return "#3D8B42"
    return "#4CAF50"


def _regressao_linear(x: list[int], y: list[float]) -> tuple[float, float]:
    """Retorna (slope, intercept) sem depender de numpy."""
    n = len(x)
    if n < 2:
        return 0.0, 0.0
    sum_x  = sum(x)
    sum_y  = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi * xi for xi in x)
    denom  = n * sum_x2 - sum_x ** 2
    if denom == 0:
        return 0.0, sum_y / n
    slope     = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept


# ---------------------------------------------------------------------------
# Botão de refresh discreto
# ---------------------------------------------------------------------------

class _BotaoRefresh(QPushButton):
    _COR_IDLE  = "#2E2E30"
    _COR_HOVER = "#8E8E93"

    def __init__(self, callback) -> None:
        super().__init__()
        self.setFixedSize(22, 22)
        self.setToolTip("Atualizar dados")
        self.clicked.connect(callback)
        self._set_icone(self._COR_IDLE)
        self.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 5px; }"
            "QPushButton:hover { background-color: rgba(255,255,255,12); }"
        )

    def _set_icone(self, cor: str) -> None:
        self.setIcon(qta.icon("ph.arrow-clockwise-bold", color=cor))

    def enterEvent(self, event) -> None:
        self._set_icone(self._COR_HOVER)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._set_icone(self._COR_IDLE)
        super().leaveEvent(event)


# ---------------------------------------------------------------------------
# Célula individual do calendário (heatmap)
# ---------------------------------------------------------------------------

class _CelulaDia(QFrame):
    def __init__(self, dia: int | None, data_str: str | None, segundos: int) -> None:
        super().__init__()
        self.setFixedSize(32, 32)
        if dia is None:
            self.setStyleSheet("background: transparent; border: none;")
            return
        cor = _cor_para_segundos(segundos)
        self.setStyleSheet(f"background-color: {cor}; border-radius: 5px; border: none;")
        tooltip = (
            f"{data_str}: {_formatar_tempo(segundos)} de foco"
            if segundos > 0
            else f"{data_str}: sem atividade"
        )
        self.setToolTip(tooltip)
        cor_texto = (
            "#FFFFFF" if segundos >= 3600
            else "#BBBBBB" if segundos > 0
            else "#555558"
        )
        lbl = QLabel(str(dia), self)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setGeometry(0, 0, 32, 32)
        lbl.setStyleSheet(
            f"color: {cor_texto}; font-size: 10px; font-weight: 500; "
            "background: transparent; border: none; font-family: 'Segoe UI', sans-serif;"
        )


# ---------------------------------------------------------------------------
# Heatmap mensal
# ---------------------------------------------------------------------------

class _Heatmap(QWidget):
    def __init__(self) -> None:
        super().__init__()
        hoje = date.today()
        self._ano = hoje.year
        self._mes = hoje.month

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        nav = QHBoxLayout()
        self.btn_anterior = QPushButton()
        self.btn_anterior.setIcon(qta.icon("ph.caret-left-bold", color=ICON_COLOR))
        self.btn_anterior.setFixedSize(28, 28)
        self.btn_anterior.setObjectName("btnNavStats")
        self.btn_anterior.clicked.connect(self._mes_anterior)

        self.lbl_mes = QLabel()
        self.lbl_mes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mes.setObjectName("lblMesStats")

        self.btn_proximo = QPushButton()
        self.btn_proximo.setIcon(qta.icon("ph.caret-right-bold", color=ICON_COLOR))
        self.btn_proximo.setFixedSize(28, 28)
        self.btn_proximo.setObjectName("btnNavStats")
        self.btn_proximo.clicked.connect(self._mes_proximo)

        nav.addWidget(self.btn_anterior)
        nav.addStretch()
        nav.addWidget(self.lbl_mes)
        nav.addStretch()
        nav.addWidget(self.btn_proximo)
        layout.addLayout(nav)

        header_dias = QHBoxLayout()
        header_dias.setSpacing(4)
        for nome in _NOMES_DIAS_SEMANA_ABREV:
            lbl = QLabel(nome)
            lbl.setFixedWidth(32)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setObjectName("lblDiaSemana")
            header_dias.addWidget(lbl)
        layout.addLayout(header_dias)

        self._grid_widget = QWidget()
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(4)
        self._grid.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._grid_widget)

        self._atualizar()

    def _atualizar(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.lbl_mes.setText(f"{_NOMES_MESES[self._mes - 1]} {self._ano}")
        dados = database.buscar_segundos_por_dia(self._ano, self._mes)
        primeiro = date(self._ano, self._mes, 1)
        inicio_col = primeiro.weekday()
        _, num_dias = calendar.monthrange(self._ano, self._mes)
        for c in range(inicio_col):
            self._grid.addWidget(_CelulaDia(None, None, 0), 0, c)
        row, col = 0, inicio_col
        for dia_num in range(1, num_dias + 1):
            d = date(self._ano, self._mes, dia_num)
            seg = dados.get(d.isoformat(), 0)
            self._grid.addWidget(_CelulaDia(dia_num, d.strftime("%d/%m/%Y"), seg), row, col)
            col += 1
            if col > 6:
                col = 0
                row += 1

    def _mes_anterior(self) -> None:
        if self._mes == 1:
            self._mes, self._ano = 12, self._ano - 1
        else:
            self._mes -= 1
        self._atualizar()

    def _mes_proximo(self) -> None:
        hoje = date.today()
        if (self._ano, self._mes) >= (hoje.year, hoje.month):
            return
        if self._mes == 12:
            self._mes, self._ano = 1, self._ano + 1
        else:
            self._mes += 1
        self._atualizar()


# ---------------------------------------------------------------------------
# Cartão de métrica
# ---------------------------------------------------------------------------

class _CartaoStat(QFrame):
    def __init__(self, titulo: str, valor: str = "—") -> None:
        super().__init__()
        self.setObjectName("cartaoStat")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("cartaoTitulo")
        self._lbl_valor = QLabel(valor)
        self._lbl_valor.setObjectName("cartaoValor")
        layout.addWidget(lbl_titulo)
        layout.addWidget(self._lbl_valor)

    def atualizar(self, valor: str) -> None:
        self._lbl_valor.setText(valor)


# ---------------------------------------------------------------------------
# Aba de Analytics (gráficos interativos)
# ---------------------------------------------------------------------------

def _estilo_eixo(ax, fig) -> None:
    """Aplica o tema escuro a um eixo matplotlib."""
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_AX_BG)
    ax.tick_params(colors=_TEXT_C, labelsize=6, length=2)
    ax.yaxis.label.set_color(_TEXT_C)
    ax.grid(axis="y", color=_GRID_C, linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_edgecolor(_GRID_C)


class _TabAnalytics(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._visao    = "semana"
        self._data_ref = date.today()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 0)
        layout.setSpacing(6)

        # ── Seletores de visão ──────────────────────────────────────────
        sel_row = QHBoxLayout()
        sel_row.setSpacing(4)
        self._btns_visao: dict[str, QPushButton] = {}
        for key, label in [("dia", "Dia"), ("semana", "Semana"), ("mes", "Mês")]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(28)
            btn.setObjectName("btnVisaoAnalytics")
            btn.clicked.connect(lambda _checked, k=key: self._set_visao(k))
            self._btns_visao[key] = btn
            sel_row.addWidget(btn)
        layout.addLayout(sel_row)

        # ── Navegação temporal ──────────────────────────────────────────
        nav_row = QHBoxLayout()
        self._btn_ant = QPushButton()
        self._btn_ant.setIcon(qta.icon("ph.caret-left-bold", color=ICON_COLOR))
        self._btn_ant.setFixedSize(28, 28)
        self._btn_ant.setObjectName("btnNavStats")
        self._btn_ant.clicked.connect(self._navegar_anterior)

        self._lbl_periodo = QLabel()
        self._lbl_periodo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_periodo.setObjectName("lblMesStats")

        self._btn_prox = QPushButton()
        self._btn_prox.setIcon(qta.icon("ph.caret-right-bold", color=ICON_COLOR))
        self._btn_prox.setFixedSize(28, 28)
        self._btn_prox.setObjectName("btnNavStats")
        self._btn_prox.clicked.connect(self._navegar_proximo)

        nav_row.addWidget(self._btn_ant)
        nav_row.addStretch()
        nav_row.addWidget(self._lbl_periodo)
        nav_row.addStretch()
        nav_row.addWidget(self._btn_prox)
        layout.addLayout(nav_row)

        # ── Gráfico principal ────────────────────────────────────────────
        self._fig_main = Figure(dpi=_DPI, constrained_layout=True)
        self._canvas_main = FigureCanvasQTAgg(self._fig_main)
        self._canvas_main.setFixedHeight(185)
        self._canvas_main.mpl_connect("button_press_event", self._on_click_barra)
        self._ax_main = self._fig_main.add_subplot(111)
        layout.addWidget(self._canvas_main)

        # ── Gráfico secundário ───────────────────────────────────────────
        lbl_sec = QLabel("MÉDIA DE HORÁRIOS ATIVOS")
        lbl_sec.setObjectName("secaoAnalytics")
        layout.addWidget(lbl_sec)

        self._fig_sec = Figure(dpi=_DPI, constrained_layout=True)
        self._canvas_sec = FigureCanvasQTAgg(self._fig_sec)
        self._canvas_sec.setFixedHeight(148)
        self._ax_sec = self._fig_sec.add_subplot(111)
        layout.addWidget(self._canvas_sec)

        self._set_visao("semana")

    # ── Visão e período ─────────────────────────────────────────────────

    def _set_visao(self, visao: str) -> None:
        self._visao = visao
        for key, btn in self._btns_visao.items():
            btn.setChecked(key == visao)
        self._atualizar_periodo_label()
        self._desenhar_principal()

    def _atualizar_periodo_label(self) -> None:
        if self._visao == "dia":
            mes = _NOMES_MESES[self._data_ref.month - 1]
            self._lbl_periodo.setText(
                f"{self._data_ref.day} de {mes} de {self._data_ref.year}"
            )
        elif self._visao == "semana":
            inicio = self._data_ref - timedelta(days=self._data_ref.weekday())
            fim    = inicio + timedelta(days=6)
            if inicio.month == fim.month:
                self._lbl_periodo.setText(
                    f"{inicio.day}–{fim.day} de {_NOMES_MESES[inicio.month-1]} {inicio.year}"
                )
            else:
                self._lbl_periodo.setText(
                    f"{inicio.day}/{inicio.month} – {fim.day}/{fim.month} {fim.year}"
                )
        else:
            self._lbl_periodo.setText(
                f"{_NOMES_MESES[self._data_ref.month-1]} {self._data_ref.year}"
            )

    def _navegar_anterior(self) -> None:
        if self._visao == "dia":
            self._data_ref -= timedelta(days=1)
        elif self._visao == "semana":
            self._data_ref -= timedelta(weeks=1)
        else:
            if self._data_ref.month == 1:
                self._data_ref = self._data_ref.replace(year=self._data_ref.year - 1, month=12)
            else:
                self._data_ref = self._data_ref.replace(month=self._data_ref.month - 1)
        self._set_visao(self._visao)

    def _navegar_proximo(self) -> None:
        hoje = date.today()
        if self._visao == "dia":
            novo = self._data_ref + timedelta(days=1)
            if novo <= hoje:
                self._data_ref = novo
        elif self._visao == "semana":
            novo = self._data_ref + timedelta(weeks=1)
            if (novo - timedelta(days=novo.weekday())) <= hoje:
                self._data_ref = novo
        else:
            if (self._data_ref.year, self._data_ref.month) >= (hoje.year, hoje.month):
                return
            if self._data_ref.month == 12:
                self._data_ref = self._data_ref.replace(year=self._data_ref.year + 1, month=1)
            else:
                self._data_ref = self._data_ref.replace(month=self._data_ref.month + 1)
        self._set_visao(self._visao)

    # ── Drill-down por clique ────────────────────────────────────────────

    def _on_click_barra(self, event) -> None:
        if self._visao == "dia" or event.inaxes != self._ax_main:
            return
        if event.xdata is None:
            return
        idx  = int(round(event.xdata))
        hoje = date.today()

        if self._visao == "semana":
            inicio = self._data_ref - timedelta(days=self._data_ref.weekday())
            datas  = [inicio + timedelta(days=i) for i in range(7)]
            if 0 <= idx < len(datas) and datas[idx] <= hoje:
                self._data_ref = datas[idx]
                self._set_visao("dia")

        else:  # mes
            _, num_dias = calendar.monthrange(self._data_ref.year, self._data_ref.month)
            if 0 <= idx < num_dias:
                data_clicada = date(self._data_ref.year, self._data_ref.month, idx + 1)
                if data_clicada <= hoje:
                    self._data_ref = data_clicada
                    self._set_visao("dia")

    # ── Gráfico principal ────────────────────────────────────────────────

    def _desenhar_principal(self) -> None:
        self._ax_main.clear()
        _estilo_eixo(self._ax_main, self._fig_main)

        hoje          = date.today()
        datas_lista: list[date] = []

        if self._visao == "dia":
            dados   = database.buscar_segundos_por_hora(self._data_ref.isoformat())
            x       = list(range(24))
            valores = [dados.get(h, 0) / 60 for h in x]
            labels  = [f"{h:02d}" for h in x]
            cores   = [_BAR_C if v > 0 else _BAR_EMPTY for v in valores]
            ylabel  = "min"
            show_trend = False

        elif self._visao == "semana":
            inicio      = self._data_ref - timedelta(days=self._data_ref.weekday())
            datas_lista = [inicio + timedelta(days=i) for i in range(7)]
            dados       = database.buscar_segundos_por_dia_range(
                datas_lista[0].isoformat(), datas_lista[-1].isoformat()
            )
            x       = list(range(7))
            valores = [dados.get(d.isoformat(), 0) / 3600 for d in datas_lista]
            labels  = [
                f"{_NOMES_DIAS_SEMANA_ABREV[i]}\n{datas_lista[i].day}/{datas_lista[i].month}"
                for i in range(7)
            ]
            cores      = [_BAR_EMPTY if datas_lista[i] > hoje else _BAR_C for i in range(7)]
            ylabel     = "horas"
            show_trend = True

        else:  # mes
            _, num_dias = calendar.monthrange(self._data_ref.year, self._data_ref.month)
            datas_lista = [
                date(self._data_ref.year, self._data_ref.month, d)
                for d in range(1, num_dias + 1)
            ]
            dados   = database.buscar_segundos_por_dia_range(
                datas_lista[0].isoformat(), datas_lista[-1].isoformat()
            )
            x       = list(range(num_dias))
            valores = [dados.get(d.isoformat(), 0) / 3600 for d in datas_lista]
            labels  = [str(d.day) for d in datas_lista]
            cores   = [
                _BAR_EMPTY if datas_lista[i] > hoje else _BAR_C
                for i in range(num_dias)
            ]
            ylabel     = "horas"
            show_trend = True

        # Barras
        self._ax_main.bar(x, valores, color=cores, width=0.55, zorder=2)

        # Linha de tendência (apenas semana/mês)
        if show_trend and datas_lista:
            passados = [i for i, d in enumerate(datas_lista) if d <= hoje]
            x_fit    = passados
            y_fit    = [valores[i] for i in passados]
            if len(x_fit) >= 2 and any(v > 0 for v in y_fit):
                slope, intercept = _regressao_linear(x_fit, y_fit)
                trend_y = [slope * xi + intercept for xi in x]
                self._ax_main.plot(
                    x, trend_y,
                    color=_TREND_C, linewidth=1.5, linestyle="--",
                    alpha=0.85, zorder=3, label="Tendência",
                )
                self._ax_main.legend(
                    loc="upper left", fontsize=6,
                    facecolor="#2C2C2E", edgecolor="none", labelcolor=_TEXT_C,
                )

        # Labels do eixo X — mês com muitos dias: mostra a cada 5
        if self._visao == "mes" and len(x) > 15:
            show_x = [i for i in x if (i + 1) % 5 == 1 or i == len(x) - 1]
            self._ax_main.set_xticks(show_x)
            self._ax_main.set_xticklabels([labels[i] for i in show_x])
        else:
            self._ax_main.set_xticks(x)
            self._ax_main.set_xticklabels(labels)

        self._ax_main.set_ylabel(ylabel, color=_TEXT_C, fontsize=7)
        self._ax_main.set_xlim(-0.5, len(x) - 0.5)
        self._ax_main.set_ylim(bottom=0)

        if self._visao in ("semana", "mes"):
            self._ax_main.set_title(
                "Clique em uma barra para detalhar o dia",
                color="#504E53", fontsize=6, pad=3,
            )

        self._canvas_main.draw_idle()

    # ── Gráfico secundário ────────────────────────────────────────────────

    def _desenhar_secundario(self) -> None:
        self._ax_sec.clear()
        _estilo_eixo(self._ax_sec, self._fig_sec)

        dados   = database.buscar_media_horaria_global()
        horas   = list(range(24))
        valores = [dados.get(h, 0) / 60 for h in horas]   # → minutos/dia
        max_val = max(valores) if any(v > 0 for v in valores) else 1.0

        def _cor(v: float) -> str:
            if v <= 0:
                return _BAR_EMPTY
            r = min(v / max_val, 1.0)
            if r < 0.25:  return "#1A3D1C"
            if r < 0.50:  return "#2D6131"
            if r < 0.75:  return "#3D8B42"
            return _BAR_C

        self._ax_sec.bar(horas, valores, color=[_cor(v) for v in valores], width=0.6, zorder=2)
        self._ax_sec.set_ylabel("min/dia", color=_TEXT_C, fontsize=6)
        self._ax_sec.tick_params(colors=_TEXT_C, labelsize=5, length=2)
        show_x = [0, 4, 8, 12, 16, 20, 23]
        self._ax_sec.set_xticks(show_x)
        self._ax_sec.set_xticklabels([f"{h:02d}h" for h in show_x])
        self._ax_sec.set_xlim(-0.5, 23.5)
        self._ax_sec.set_ylim(bottom=0)
        self._canvas_sec.draw_idle()

    # ── API pública ────────────────────────────────────────────────────────

    def atualizar(self) -> None:
        self._atualizar_periodo_label()
        self._desenhar_principal()
        self._desenhar_secundario()


# ---------------------------------------------------------------------------
# Janela principal de Estatísticas
# ---------------------------------------------------------------------------

class StatsUI(QWidget):
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
        self.resize(320, 580)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)

        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("statsBackground")
        layout_frame = QVBoxLayout(self.main_frame)
        layout_frame.setContentsMargins(16, 14, 16, 16)
        layout_frame.setSpacing(10)

        # ── Cabeçalho ────────────────────────────────────────────────────
        header = QHBoxLayout()
        lbl_titulo = QLabel("Estatísticas")
        lbl_titulo.setObjectName("statsTitulo")
        self._btn_refresh = _BotaoRefresh(self._atualizar_tudo)
        btn_fechar = QPushButton()
        btn_fechar.setIcon(qta.icon("ph.x-bold", color=ICON_COLOR))
        btn_fechar.setFixedSize(28, 28)
        btn_fechar.setObjectName("btnFecharStats")
        btn_fechar.clicked.connect(self.hide)
        header.addWidget(lbl_titulo)
        header.addStretch()
        header.addWidget(self._btn_refresh)
        header.addWidget(btn_fechar)
        layout_frame.addLayout(header)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setObjectName("sepStats")
        layout_frame.addWidget(sep1)

        # ── QTabWidget ────────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setObjectName("statsTabWidget")
        self._tabs.currentChanged.connect(self._on_tab_change)

        # ── Tab 1: Calendário ─────────────────────────────────────────────
        tab_cal = QWidget()
        layout_cal = QVBoxLayout(tab_cal)
        layout_cal.setContentsMargins(0, 8, 0, 0)
        layout_cal.setSpacing(10)

        self._heatmap = _Heatmap()
        layout_cal.addWidget(self._heatmap)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setObjectName("sepStats")
        layout_cal.addWidget(sep2)

        grid = QGridLayout()
        grid.setSpacing(8)
        self._card_hoje      = _CartaoStat("HOJE")
        self._card_total     = _CartaoStat("TOTAL DE FOCO")
        self._card_streak    = _CartaoStat("SEQUÊNCIA")
        self._card_pomodoros = _CartaoStat("POMODOROS")
        self._card_melhor    = _CartaoStat("MELHOR DIA DA SEMANA")
        grid.addWidget(self._card_hoje,      0, 0)
        grid.addWidget(self._card_total,     0, 1)
        grid.addWidget(self._card_streak,    1, 0)
        grid.addWidget(self._card_pomodoros, 1, 1)
        grid.addWidget(self._card_melhor,    2, 0, 1, 2)
        layout_cal.addLayout(grid)
        layout_cal.addStretch()

        # ── Tab 2: Analytics ──────────────────────────────────────────────
        self._tab_analytics = _TabAnalytics()

        self._tabs.addTab(tab_cal,               "Calendário")
        self._tabs.addTab(self._tab_analytics,   "Analytics")
        layout_frame.addWidget(self._tabs)
        layout_principal.addWidget(self.main_frame)

        self.setStyleSheet(estilo_stats())

    # ------------------------------------------------------------------

    def _on_tab_change(self, idx: int) -> None:
        if idx == 1:
            self._tab_analytics.atualizar()

    def _atualizar_stats(self) -> None:
        try:
            s = database.buscar_estatisticas()
            self._card_hoje.atualizar(_formatar_tempo(s["seg_hoje"]))
            self._card_total.atualizar(_formatar_tempo(s["total_seg"]))
            streak = s["streak_dias"]
            self._card_streak.atualizar(f"{streak} {'dia' if streak == 1 else 'dias'}")
            self._card_pomodoros.atualizar(str(s["total_focos"]))
            dow = s["melhor_dia_semana"]
            if dow is not None:
                py_idx = (int(dow) - 1) % 7
                self._card_melhor.atualizar(_NOMES_DIAS_SEMANA_COMPLETO[py_idx])
            else:
                self._card_melhor.atualizar("—")
        except Exception:
            pass

    def _atualizar_tudo(self) -> None:
        self._heatmap._atualizar()
        self._atualizar_stats()
        if self._tabs.currentIndex() == 1:
            self._tab_analytics.atualizar()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._atualizar_tudo()

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

    def mouseReleaseEvent(self, event) -> None:
        self._pos_antiga = None
