from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class PomodoroTimer(QObject):
    tempo_atualizado    = pyqtSignal(str)       # "MM:SS"
    estado_alterado     = pyqtSignal(bool)      # True = rodando
    ciclo_concluido     = pyqtSignal()          # fase completou naturalmente
    ciclo_parcial       = pyqtSignal(str, int)  # (fase, segundos_decorridos) ao pular
    fase_alterada       = pyqtSignal(str, int)  # (fase, ciclo_atual 1-4)
    progresso_atualizado = pyqtSignal(int)      # 0–1000: progresso dentro da fase

    _FOCOS_PARA_PAUSA_LONGA = 4

    def __init__(
        self,
        tempo_foco: int = 25,
        tempo_curta: int = 5,
        tempo_longa: int = 15,
    ) -> None:
        super().__init__()
        self.tempo_foco   = tempo_foco
        self.tempo_curta  = tempo_curta
        self.tempo_longa  = tempo_longa

        self.fase_atual        = "foco"
        self.ciclo_atual       = 1
        self.focos_concluidos  = 0

        self.tempo_total_segundos = tempo_foco * 60
        self.tempo_restante       = self.tempo_total_segundos
        self.rodando              = False

        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def alternar(self) -> None:
        self.pausar() if self.rodando else self.iniciar()

    def iniciar(self) -> None:
        if not self.rodando and self.tempo_restante > 0:
            self.rodando = True
            self._timer.start(1000)
            self.estado_alterado.emit(True)

    def pausar(self) -> None:
        if self.rodando:
            self.rodando = False
            self._timer.stop()
            self.estado_alterado.emit(False)

    def resetar(self) -> None:
        """Reinicia o cronômetro no início da fase atual."""
        self.pausar()
        self.tempo_total_segundos = self._duracao_fase_atual() * 60
        self.tempo_restante       = self.tempo_total_segundos
        self._emitir_tempo()

    def avancar_fase(self) -> None:
        """Pula para a próxima fase. Registra o tempo decorrido se havia progresso."""
        segundos_decorridos = self.tempo_total_segundos - self.tempo_restante
        if segundos_decorridos > 0 and self.fase_atual == "foco":
            self.ciclo_parcial.emit(self.fase_atual, segundos_decorridos)
        self.pausar()
        self._proxima_fase()
        self.tempo_total_segundos = self._duracao_fase_atual() * 60
        self.tempo_restante       = self.tempo_total_segundos
        self._emitir_tempo()

    def atualizar_configuracoes(
        self,
        tempo_foco: int,
        tempo_curta: int,
        tempo_longa: int,
    ) -> None:
        """Aplica novos tempos. Só afeta a fase atual se o timer não estiver rodando."""
        self.tempo_foco  = tempo_foco
        self.tempo_curta = tempo_curta
        self.tempo_longa = tempo_longa
        if not self.rodando:
            self.resetar()

    # ------------------------------------------------------------------
    # Lógica de ciclo
    # ------------------------------------------------------------------

    def _duracao_fase_atual(self) -> int:
        return {
            "foco":        self.tempo_foco,
            "pausa_curta": self.tempo_curta,
            "pausa_longa": self.tempo_longa,
        }[self.fase_atual]

    def _proxima_fase(self) -> None:
        if self.fase_atual == "foco":
            self.focos_concluidos += 1
            if self.focos_concluidos % self._FOCOS_PARA_PAUSA_LONGA == 0:
                self.fase_atual = "pausa_longa"
            else:
                self.fase_atual = "pausa_curta"
        else:
            self.fase_atual  = "foco"
            self.ciclo_atual = (self.focos_concluidos % self._FOCOS_PARA_PAUSA_LONGA) + 1

        self.fase_alterada.emit(self.fase_atual, self.ciclo_atual)

    # ------------------------------------------------------------------
    # Loop interno
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        if self.tempo_restante > 0:
            self.tempo_restante -= 1
            self._emitir_tempo()
        else:
            self.pausar()
            self.ciclo_concluido.emit()
            self._proxima_fase()
            self.tempo_total_segundos = self._duracao_fase_atual() * 60
            self.tempo_restante       = self.tempo_total_segundos
            self._emitir_tempo()

    def _emitir_tempo(self) -> None:
        m, s = divmod(self.tempo_restante, 60)
        self.tempo_atualizado.emit(f"{m:02d}:{s:02d}")
        if self.tempo_total_segundos > 0:
            progresso = int((1 - self.tempo_restante / self.tempo_total_segundos) * 1000)
        else:
            progresso = 1000
        self.progresso_atualizado.emit(progresso)
