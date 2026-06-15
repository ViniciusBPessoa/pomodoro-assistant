import json
from pathlib import Path

class SettingsManager:
    def __init__(self):
        # Define onde o arquivo será salvo (na raiz do projeto)
        self.filepath = Path("settings.json")
        
        # As configurações padrão (caso seja a primeira vez abrindo o app)
        self.default_settings = {
            "tempo_foco": 25,
            "tempo_curta": 5,
            "tempo_longa": 15,
            "auto_iniciar_pausas": False,
            "auto_iniciar_foco": False
        }
        
        # Carrega as configurações assim que o gerente é chamado
        self.config = self._load_settings()

    def _load_settings(self):
        """Lê o arquivo JSON. Se não existir, cria um com os padrões."""
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    dados_salvos = json.load(f)
                    # Mescla os dados salvos com os padrões (evita erros se adicionarmos novas opções depois)
                    return {**self.default_settings, **dados_salvos}
            except json.JSONDecodeError:
                # Se o arquivo corromper, volta pro padrão
                pass
        
        return self.default_settings.copy()

    def save_settings(self):
        """Escreve as configurações atuais no arquivo JSON."""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    def get(self, chave):
        """Pega um valor específico."""
        return self.config.get(chave, self.default_settings.get(chave))

    def set(self, chave, valor):
        """Atualiza um valor e já salva no arquivo automaticamente."""
        self.config[chave] = valor
        self.save_settings()

# Instância global (Opcional, mas facilita para importar em várias telas)
settings = SettingsManager()