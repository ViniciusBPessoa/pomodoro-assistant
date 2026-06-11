from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class PomodoroTimer(QObject):
    # Sinais (Signals) que o backend vai emitir para o frontend escutar
    tempo_atualizado = pyqtSignal(str)   # Vai enviar o texto "24:59"
    estado_alterado = pyqtSignal(bool)   # True se estiver rodando, False se pausado
    ciclo_concluido = pyqtSignal()       # Grita quando chega em 00:00

    def __init__(self, tempo_inicial_minutos=25):
        super().__init__()
        self.tempo_total_segundos = tempo_inicial_minutos * 60
        self.tempo_restante = self.tempo_total_segundos
        self.rodando = False

        # O QTimer é o coração que bate a cada 1 segundo
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

    def alternar(self):
        """Função do botão Play/Pause."""
        if self.rodando:
            self.pausar()
        else:
            self.iniciar()

    def iniciar(self):
        if not self.rodando and self.tempo_restante > 0:
            self.rodando = True
            self.timer.start(1000) # Pulsa a cada 1000 milissegundos (1 seg)
            self.estado_alterado.emit(True)

    def pausar(self):
        if self.rodando:
            self.rodando = False
            self.timer.stop()
            self.estado_alterado.emit(False)

    def resetar(self, minutos=None):
        self.pausar()
        if minutos is not None:
            self.tempo_total_segundos = minutos * 60
        self.tempo_restante = self.tempo_total_segundos
        self._emitir_tempo()

    def _tick(self):
        """Método interno chamado a cada 1 segundo pelo QTimer."""
        if self.tempo_restante > 0:
            self.tempo_restante -= 1
            self._emitir_tempo()
        else:
            self.pausar()
            self.ciclo_concluido.emit()
            self.resetar() # Por enquanto, ele apenas reseta ao terminar

    def _emitir_tempo(self):
        """Formata o tempo em MM:SS e emite o sinal."""
        minutos = self.tempo_restante // 60
        segundos = self.tempo_restante % 60
        texto = f"{minutos:02d}:{segundos:02d}"
        self.tempo_atualizado.emit(texto)