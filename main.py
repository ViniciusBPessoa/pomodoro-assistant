import sys
import qtawesome as qta
from PyQt6.QtWidgets import QApplication
from src.frontend.PillWidget import PillWidget
from src.frontend.pomodoro_ui import PomodoroUI
from src.backend.timer_core import PomodoroTimer

class GerenciadorDeTelas:
    def __init__(self):
        self.pilula = PillWidget()
        self.pomodoro_expandido = PomodoroUI()
        
        # Instanciando o Motor do Tempo
        self.motor = PomodoroTimer(tempo_inicial_minutos=25)

        # Conectando a transição entre as Telas
        self.pilula.btn_ampliar.clicked.connect(self.abrir_pomodoro)
        self.pomodoro_expandido.btn_recolher.clicked.connect(self.abrir_pilula)

        # --- SINCRONIA: ENVIANDO COMANDOS PARA O MOTOR ---
        self.pilula.btn_play.clicked.connect(self.motor.alternar)
        self.pomodoro_expandido.btn_play_grande.clicked.connect(self.motor.alternar) # <-- AQUI
        
        # --- SINCRONIA: RECEBENDO RESPOSTAS DO MOTOR ---
        self.motor.tempo_atualizado.connect(self.pilula.lbl_tempo.setText)
        self.motor.tempo_atualizado.connect(self.pomodoro_expandido.lbl_tempo_gigante.setText) # <-- AQUI
        
        # Quando o motor rodar/pausar, muda o ícone nas DUAS telas
        self.motor.estado_alterado.connect(self.atualizar_icone_play)

        # Dá o "chute inicial" para a tela mostrar o 25:00 antes de dar play
        self.motor._emitir_tempo() 

        self.pilula.show()

    def atualizar_icone_play(self, rodando):
        """Troca o ícone nas duas telas dependendo do estado do cronômetro"""
        cor_icone = '#8E8E93'
        
        if rodando:
            icone = qta.icon('ph.pause-fill', color=cor_icone)
        else:
            icone = qta.icon('ph.play-fill', color=cor_icone)
            
        # Aplica o mesmo ícone nas duas telas!
        self.pilula.btn_play.setIcon(icone)
        self.pomodoro_expandido.btn_play_grande.setIcon(icone) # <-- AQUI

    def abrir_pomodoro(self):
        if self.pilula.gaveta.aberta:
            self.pilula.alternar_gaveta()

        geo_atual = self.pilula.geometry()
        nova_geometria = self.pomodoro_expandido.frameGeometry()
        
        nova_geometria.moveCenter(geo_atual.center())
        nova_geometria.moveBottom(geo_atual.bottom())
        
        self.pomodoro_expandido.move(nova_geometria.topLeft())
        self.pilula.hide()
        self.pomodoro_expandido.show()

    def abrir_pilula(self):
        geo_atual = self.pomodoro_expandido.geometry()
        nova_geometria = self.pilula.frameGeometry()
        
        nova_geometria.moveCenter(geo_atual.center())
        nova_geometria.moveBottom(geo_atual.bottom())
        
        self.pilula.move(nova_geometria.topLeft())
        self.pomodoro_expandido.hide()
        self.pilula.show()

def main():
    app = QApplication(sys.argv)
    gerenciador = GerenciadorDeTelas()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()