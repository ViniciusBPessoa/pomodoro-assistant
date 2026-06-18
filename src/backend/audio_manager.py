"""
Gerencia sons de notificação do app.

Diretório de sons: assets/sons/ na raiz do projeto.
Sons padrão são gerados automaticamente via síntese de onda senoidal (WAV puro,
sem dependências externas). Novos sons podem ser adicionados via interface de
configurações ou copiando arquivos .wav diretamente para assets/sons/.
"""
import math
import struct
import sys
import wave
from pathlib import Path
from shutil import copy2

from src.backend.settings_manager import settings

SONS_DIR: Path = Path(__file__).resolve().parent.parent.parent / "assets" / "sons"

_SONS_PADRAO: dict[str, tuple[float, float]] = {
    "foco_inicio":     (880.0,  0.45),
    "pausa_inicio":    (528.0,  0.45),
    "ciclo_concluido": (1047.0, 0.70),
}

# Lista de efeitos sonoros vivos (evita garbage collection antes de terminar)
_efeitos_ativos: list = []


# ---------------------------------------------------------------------------
# Inicialização
# ---------------------------------------------------------------------------

def inicializar() -> None:
    """Cria o diretório de sons e gera WAVs padrão caso não existam."""
    SONS_DIR.mkdir(parents=True, exist_ok=True)
    for nome, (freq, dur) in _SONS_PADRAO.items():
        caminho = SONS_DIR / f"{nome}.wav"
        if not caminho.exists():
            _gerar_wav(caminho, freq, dur)


def _gerar_wav(caminho: Path, frequencia: float, duracao: float, volume: float = 0.55) -> None:
    """Gera arquivo WAV monocanal com onda senoidal e envelope suave."""
    taxa = 44100
    n = int(taxa * duracao)
    ataque    = int(taxa * 0.015)
    decaimento = int(taxa * 0.1)

    with wave.open(str(caminho), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(taxa)
        for i in range(n):
            restante = n - i
            if i < ataque:
                env = i / ataque
            elif restante < decaimento:
                env = restante / decaimento
            else:
                env = 1.0
            amostra = int(volume * env * 32767 * math.sin(2 * math.pi * frequencia * i / taxa))
            wf.writeframes(struct.pack("<h", amostra))


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def listar_sons() -> list[str]:
    if not SONS_DIR.exists():
        return []
    return sorted(p.name for p in SONS_DIR.glob("*.wav"))


def adicionar_som(caminho_origem: str) -> str | None:
    src = Path(caminho_origem)
    if not src.exists() or src.suffix.lower() != ".wav":
        return None
    dst = SONS_DIR / src.name
    try:
        copy2(src, dst)
    except OSError:
        return None
    return dst.name


def tocar(chave: str) -> None:
    """Toca o som da chave dada respeitando volume e flag sons_ativados."""
    if not settings.get("sons_ativados"):
        return
    arquivo = settings.get(f"som_{chave}") or f"{chave}.wav"
    caminho = SONS_DIR / arquivo
    if caminho.exists():
        _play(str(caminho))


# ---------------------------------------------------------------------------
# Backend de playback com suporte a volume
# ---------------------------------------------------------------------------

def _play(caminho: str) -> None:
    volume = max(0.0, min(1.0, (settings.get("volume") or 70) / 100.0))
    try:
        from PyQt6.QtMultimedia import QSoundEffect
        from PyQt6.QtCore import QUrl, QTimer

        efeito = QSoundEffect()
        _efeitos_ativos.append(efeito)

        def _ao_status_mudar():
            status = efeito.status()
            if status == QSoundEffect.Status.Ready:
                efeito.play()
                QTimer.singleShot(5000, lambda: _efeitos_ativos.remove(efeito)
                                  if efeito in _efeitos_ativos else None)
            elif status == QSoundEffect.Status.Error:
                if efeito in _efeitos_ativos:
                    _efeitos_ativos.remove(efeito)
                _play_winsound(caminho)

        efeito.statusChanged.connect(_ao_status_mudar)
        efeito.setVolume(volume)
        efeito.setSource(QUrl.fromLocalFile(caminho))

        # Se já estava Ready antes de conectar o sinal, dispara manualmente
        if efeito.status() == QSoundEffect.Status.Ready:
            efeito.play()
            QTimer.singleShot(5000, lambda: _efeitos_ativos.remove(efeito)
                              if efeito in _efeitos_ativos else None)

    except Exception:
        _play_winsound(caminho)


def _play_winsound(caminho: str) -> None:
    if sys.platform == "win32":
        try:
            import winsound
            winsound.PlaySound(
                caminho,
                winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
            )
        except Exception:
            pass
