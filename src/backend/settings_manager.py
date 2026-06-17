import json
from pathlib import Path

# Raiz do projeto — dois níveis acima de src/backend/
_RAIZ_PROJETO = Path(__file__).resolve().parent.parent.parent


class SettingsManager:
    _DEFAULTS: dict = {
        # Tempos do Pomodoro (em minutos)
        "tempo_foco":   25,
        "tempo_curta":  5,
        "tempo_longa":  15,
        # Comportamento automático
        "auto_iniciar_pausas": False,
        "auto_iniciar_foco":   False,
        "auto_reinicio":       False,
        # Áudio
        "sons_ativados":       True,
        "volume":              70,
        "som_foco_inicio":     "foco_inicio.wav",
        "som_pausa_inicio":    "pausa_inicio.wav",
        "som_ciclo_concluido": "ciclo_concluido.wav",
        # Diretórios de módulos externos
        "dir_todolist":  "",
        "dir_stats":     "",
    }

    def __init__(self) -> None:
        self.filepath = _RAIZ_PROJETO / "settings.json"
        self.config = self._carregar()

    def _carregar(self) -> dict:
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    dados_salvos = json.load(f)
                return {**self._DEFAULTS, **dados_salvos}
            except (json.JSONDecodeError, OSError):
                pass
        return self._DEFAULTS.copy()

    def salvar(self) -> None:
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except OSError:
            pass

    def get(self, chave: str):
        return self.config.get(chave, self._DEFAULTS.get(chave))

    def set(self, chave: str, valor) -> None:
        self.config[chave] = valor
        self.salvar()

    # Compatibilidade retroativa
    def save_settings(self) -> None:
        self.salvar()


settings = SettingsManager()
