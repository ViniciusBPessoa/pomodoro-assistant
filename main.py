import sys
import ctypes
from pathlib import Path
import qtawesome as qta

from PyQt6.QtCore import QObject, QEvent, Qt, QPoint
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget

# Resolve asset path corretamente tanto em desenvolvimento quanto no exe empacotado
_BASE_PATH = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
_ICON_PATH = _BASE_PATH / "assets" / "icon.ico"

from src.frontend.PillWidget import PillWidget
from src.frontend.pomodoro_ui import PomodoroUI
from src.frontend.settings_ui import SettingsUI
from src.frontend.todo_ui import TodoUI
from src.frontend.stats_ui import StatsUI
from src.frontend.stopwatch_ui import StopwatchUI
from src.backend.timer_core import PomodoroTimer
from src.backend.stopwatch_core import StopwatchCore
from src.backend.settings_manager import settings
from src.backend import database
from src.backend import audio_manager
from src.styles.theme import ICON_COLOR, estilo_label_modo, estilo_progressbar

_NOMES_MODO = {
    "foco":        "Em Foco",
    "pausa_curta": "Pausa Curta",
    "pausa_longa": "Pausa Longa",
}


# ---------------------------------------------------------------------------
# Event filter para sincronizar minimize / restore entre janelas
# ---------------------------------------------------------------------------

class _FiltroJanela(QObject):
    """Detecta minimize e restore nas janelas principais e notifica o gerenciador."""

    def __init__(self, gerenciador: "GerenciadorDeTelas") -> None:
        super().__init__()
        self._ger = gerenciador

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.WindowStateChange:
            estado = obj.windowState() if hasattr(obj, "windowState") else Qt.WindowState.WindowNoState
            if estado & Qt.WindowState.WindowMinimized:
                self._ger._on_minimizar()
            else:
                self._ger._on_restaurar()
        return False  # não consome o evento


# ---------------------------------------------------------------------------
# Orquestrador
# ---------------------------------------------------------------------------

class GerenciadorDeTelas:
    def __init__(self) -> None:
        database.inicializar()
        audio_manager.inicializar()

        self.pilula             = PillWidget()
        self.pomodoro_expandido = PomodoroUI()
        self.tela_config        = SettingsUI()
        self.tela_todo          = TodoUI()
        self.tela_stats         = StatsUI()
        self.tela_stopwatch     = StopwatchUI()

        self.motor    = PomodoroTimer(
            tempo_foco  = settings.get("tempo_foco"),
            tempo_curta = settings.get("tempo_curta"),
            tempo_longa = settings.get("tempo_longa"),
        )
        self.motor_sw = StopwatchCore()

        self._conectar_sinais()

        # Estado inicial de UI
        self.motor._emitir_tempo()
        self._atualizar_fase("foco", 1)

        # Sincronização de janelas (minimize/restore)
        self._esta_minimizado = False
        self._janelas_visiveis: set[str] = set()
        self._filtro = _FiltroJanela(self)
        self.pilula.installEventFilter(self._filtro)
        self.pomodoro_expandido.installEventFilter(self._filtro)

        self.pilula.show()

    # ------------------------------------------------------------------
    # Conexões de sinais
    # ------------------------------------------------------------------

    def _conectar_sinais(self) -> None:
        # Transição entre telas
        self.pilula.btn_ampliar.clicked.connect(self._abrir_pomodoro)
        self.pomodoro_expandido.btn_recolher.clicked.connect(self._abrir_pilula)

        # Comandos ao motor
        self.pilula.btn_play.clicked.connect(self.motor.alternar)
        self.pomodoro_expandido.btn_play_grande.clicked.connect(self.motor.alternar)
        self.pomodoro_expandido.btn_reset.clicked.connect(self.motor.resetar)
        self.pomodoro_expandido.btn_avancar.clicked.connect(self.motor.avancar_fase)

        # Respostas do motor → UI
        self.motor.tempo_atualizado.connect(self.pilula.lbl_tempo.setText)
        self.motor.tempo_atualizado.connect(self.pomodoro_expandido.lbl_tempo_gigante.setText)
        self.motor.progresso_atualizado.connect(self.pilula.barra_progresso.setValue)
        self.motor.progresso_atualizado.connect(self.pomodoro_expandido.barra_progresso.setValue)
        self.motor.estado_alterado.connect(self._atualizar_icone_play)
        self.motor.fase_alterada.connect(self._atualizar_fase)
        self.motor.fase_alterada.connect(self._tocar_som_fase)
        self.motor.ciclo_concluido.connect(self._registrar_ciclo)
        self.motor.ciclo_parcial.connect(self._registrar_ciclo_parcial)

        # Gavetas → telas secundárias
        self.pilula.gaveta.btn_config.clicked.connect(self._abrir_configuracoes)
        self.pomodoro_expandido.gaveta.btn_config.clicked.connect(self._abrir_configuracoes)
        self.pilula.gaveta.btn_todos.clicked.connect(self._abrir_todo)
        self.pomodoro_expandido.gaveta.btn_todos.clicked.connect(self._abrir_todo)
        self.pilula.gaveta.btn_stats.clicked.connect(self._abrir_stats)
        self.pomodoro_expandido.gaveta.btn_stats.clicked.connect(self._abrir_stats)
        self.pilula.gaveta.btn_stopwatch.clicked.connect(self._abrir_stopwatch)
        self.pomodoro_expandido.gaveta.btn_stopwatch.clicked.connect(self._abrir_stopwatch)

        # Cronômetro livre
        self.tela_stopwatch.btn_play.clicked.connect(self.motor_sw.alternar)
        self.tela_stopwatch.btn_reset.clicked.connect(self.motor_sw.resetar)
        self.tela_stopwatch.btn_reset.clicked.connect(self.tela_stopwatch.limpar_voltas)
        self.tela_stopwatch.btn_lap.clicked.connect(self.motor_sw.registrar_volta)
        self.motor_sw.tempo_atualizado.connect(self.tela_stopwatch.lbl_tempo.setText)
        self.motor_sw.estado_alterado.connect(self.tela_stopwatch.atualizar_icone_play)
        self.motor_sw.volta_registrada.connect(self.tela_stopwatch.adicionar_volta)

        # Salvar configurações → atualiza motor
        self.tela_config.configuracoes_salvas.connect(self._aplicar_configuracoes)

    # ------------------------------------------------------------------
    # Sincronização minimize / restore
    # ------------------------------------------------------------------

    def _on_minimizar(self) -> None:
        if self._esta_minimizado:
            return
        self._esta_minimizado = True
        self._janelas_visiveis.clear()
        for nome, janela in self._janelas_secundarias():
            if janela.isVisible():
                self._janelas_visiveis.add(nome)
                janela.hide()

    def _on_restaurar(self) -> None:
        if not self._esta_minimizado:
            return
        self._esta_minimizado = False
        for nome, janela in self._janelas_secundarias():
            if nome in self._janelas_visiveis:
                janela.show()
        self._janelas_visiveis.clear()

    def _janelas_secundarias(self) -> list[tuple[str, QWidget]]:
        return [
            ("config",     self.tela_config),
            ("todo",       self.tela_todo),
            ("stats",      self.tela_stats),
            ("stopwatch",  self.tela_stopwatch),
        ]

    # ------------------------------------------------------------------
    # Slots de UI
    # ------------------------------------------------------------------

    def _atualizar_icone_play(self, rodando: bool) -> None:
        icone = qta.icon(
            "ph.pause-fill" if rodando else "ph.play-fill",
            color=ICON_COLOR,
        )
        self.pilula.btn_play.setIcon(icone)
        self.pomodoro_expandido.btn_play_grande.setIcon(icone)

    def _atualizar_fase(self, fase: str, ciclo: int) -> None:
        texto_ciclo = "Pausa Longa" if fase == "pausa_longa" else f"Ciclo {ciclo}/4"
        self.pomodoro_expandido.lbl_fase.setText(texto_ciclo)
        self.pomodoro_expandido.lbl_modo_atual.setText(_NOMES_MODO.get(fase, fase))
        self.pomodoro_expandido.lbl_modo_atual.setStyleSheet(estilo_label_modo(fase))
        estilo_barra = estilo_progressbar(fase)
        self.pilula.barra_progresso.setStyleSheet(estilo_barra)
        self.pomodoro_expandido.barra_progresso.setStyleSheet(estilo_barra)

    # ------------------------------------------------------------------
    # Áudio
    # ------------------------------------------------------------------

    def _tocar_som_fase(self, fase: str, _ciclo: int) -> None:  # noqa: ARG002
        if fase == "foco":
            audio_manager.tocar("foco_inicio")
        else:
            audio_manager.tocar("pausa_inicio")

    # ------------------------------------------------------------------
    # Banco de dados
    # ------------------------------------------------------------------

    def _registrar_ciclo(self) -> None:
        try:
            seg = self.motor.tempo_total_segundos
            database.registrar_ciclo(
                fase        = self.motor.fase_atual,
                duracao_min = seg // 60,
                duracao_seg = seg,
                concluido   = True,
            )
        except Exception:
            pass

    def _registrar_ciclo_parcial(self, fase: str, segundos: int) -> None:
        try:
            database.registrar_ciclo(
                fase        = fase,
                duracao_min = segundos // 60,
                duracao_seg = segundos,
                concluido   = False,
            )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Navegação entre telas
    # ------------------------------------------------------------------

    def _posicao_ao_lado(self, janela: QWidget) -> QPoint:
        """Coordenadas à direita da janela ativa, clamped para dentro da tela disponível."""
        janela_ativa = (
            self.pomodoro_expandido if self.pomodoro_expandido.isVisible() else self.pilula
        )
        geo    = janela_ativa.geometry()
        screen = QApplication.primaryScreen().availableGeometry()
        w      = max(janela.width(),  1)
        h      = max(janela.height(), 1)
        x = min(geo.right() + 10, screen.right()  - w)
        y = min(max(geo.top(), screen.top()), screen.bottom() - h)
        x = max(x, screen.left())
        return QPoint(x, y)

    def _abrir_configuracoes(self) -> None:
        self.tela_config.move(self._posicao_ao_lado(self.tela_config))
        self.tela_config.show()

    def _aplicar_configuracoes(self) -> None:
        self.motor.atualizar_configuracoes(
            tempo_foco  = settings.get("tempo_foco"),
            tempo_curta = settings.get("tempo_curta"),
            tempo_longa = settings.get("tempo_longa"),
        )
        database.inicializar()  # garante tabela no diretório de stats recém-configurado

    def _abrir_todo(self) -> None:
        if not self.tela_todo.isVisible():
            self.tela_todo.move(self._posicao_ao_lado(self.tela_todo))
        self.tela_todo.show()
        self.tela_todo.raise_()

    def _abrir_stats(self) -> None:
        if not self.tela_stats.isVisible():
            self.tela_stats.move(self._posicao_ao_lado(self.tela_stats))
        self.tela_stats.show()
        self.tela_stats.raise_()

    def _abrir_stopwatch(self) -> None:
        if not self.tela_stopwatch.isVisible():
            self.tela_stopwatch.move(self._posicao_ao_lado(self.tela_stopwatch))
        self.tela_stopwatch.show()
        self.tela_stopwatch.raise_()

    def _abrir_pomodoro(self) -> None:
        if self.pilula.gaveta.aberta:
            self.pilula._alternar_gaveta()

        geo_atual = self.pilula.geometry()
        nova_geo  = self.pomodoro_expandido.frameGeometry()
        nova_geo.moveCenter(geo_atual.center())
        nova_geo.moveBottom(geo_atual.bottom())

        self.pomodoro_expandido.move(nova_geo.topLeft())
        self.pilula.hide()
        self.pomodoro_expandido.show()

    def _abrir_pilula(self) -> None:
        if self.pomodoro_expandido.gaveta.aberta:
            self.pomodoro_expandido._alternar_gaveta()

        geo_atual = self.pomodoro_expandido.geometry()
        nova_geo  = self.pilula.frameGeometry()
        nova_geo.moveCenter(geo_atual.center())
        nova_geo.moveBottom(geo_atual.bottom())

        self.pilula.move(nova_geo.topLeft())
        self.pomodoro_expandido.hide()
        self.pilula.show()


def main() -> None:
    # Necessário no Windows para que a barra de tarefas use o ícone correto
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Pomodoro.Assistant.App.1")
    except Exception:
        pass

    app = QApplication(sys.argv)
    if _ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(_ICON_PATH)))
    gerenciador = GerenciadorDeTelas()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
