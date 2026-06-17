from PyQt6.QtCore import QObject, QTimer, pyqtSignal


def _fmt(cs: int) -> str:
    total_s  = cs // 100
    centis   = cs % 100
    minutos  = total_s // 60
    segundos = total_s % 60
    if minutos >= 60:
        horas    = minutos // 60
        minutos %= 60
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    return f"{minutos:02d}:{segundos:02d}.{centis:02d}"


class StopwatchCore(QObject):
    tempo_atualizado = pyqtSignal(str)           # "MM:SS.cs"
    estado_alterado  = pyqtSignal(bool)          # True = rodando
    volta_registrada = pyqtSignal(int, str, str) # (numero, total, delta)

    def __init__(self) -> None:
        super().__init__()
        self._cs        = 0   # centisegundos totais
        self._cs_ultima = 0   # cs no último lap
        self._n_voltas  = 0
        self._rodando   = False

        self._timer = QTimer()
        self._timer.setInterval(10)   # 10 ms ≈ 1 centisegundo
        self._timer.timeout.connect(self._tick)

    def alternar(self) -> None:
        self.pausar() if self._rodando else self.iniciar()

    def iniciar(self) -> None:
        if self._rodando:
            return
        self._rodando = True
        self._timer.start()
        self.estado_alterado.emit(True)

    def pausar(self) -> None:
        if not self._rodando:
            return
        self._rodando = False
        self._timer.stop()
        self.estado_alterado.emit(False)

    def resetar(self) -> None:
        self._timer.stop()
        self._rodando   = False
        self._cs        = 0
        self._cs_ultima = 0
        self._n_voltas  = 0
        self.estado_alterado.emit(False)
        self.tempo_atualizado.emit("00:00.00")

    def registrar_volta(self) -> None:
        if self._cs == 0:
            return
        self._n_voltas += 1
        delta           = self._cs - self._cs_ultima
        self._cs_ultima = self._cs
        self.volta_registrada.emit(self._n_voltas, _fmt(self._cs), _fmt(delta))

    def _tick(self) -> None:
        self._cs += 1
        self.tempo_atualizado.emit(_fmt(self._cs))
