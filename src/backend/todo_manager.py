"""
Persistência da To-Do List em JSON.

Formato do arquivo:
{
  "tabs": [
    {
      "id": "<uuid>",
      "nome": "Geral",
      "tarefas": [
        {"id": "<uuid>", "texto": "...", "feita": false}
      ]
    }
  ]
}

Local padrão: data/todo.json na raiz do projeto.
Se settings["dir_todolist"] estiver configurado, usa esse diretório.
"""
import json
import uuid
from pathlib import Path

from src.backend.settings_manager import settings

_DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_TODO_FILENAME = "todo.json"


class TodoManager:
    def __init__(self) -> None:
        self._dados: dict = {"tabs": []}
        self.carregar()
        if not self._dados["tabs"]:
            self.adicionar_aba("Geral")

    # ------------------------------------------------------------------
    # Arquivo de persistência
    # ------------------------------------------------------------------

    @property
    def _filepath(self) -> Path:
        dir_cfg = settings.get("dir_todolist")
        base = Path(dir_cfg) if dir_cfg else _DEFAULT_DATA_DIR
        base.mkdir(parents=True, exist_ok=True)
        return base / _TODO_FILENAME

    def carregar(self) -> None:
        try:
            fp = self._filepath
            if fp.exists():
                with open(fp, "r", encoding="utf-8") as f:
                    self._dados = json.load(f)
        except (OSError, json.JSONDecodeError):
            self._dados = {"tabs": []}

    def salvar(self) -> None:
        try:
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump(self._dados, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Abas
    # ------------------------------------------------------------------

    def obter_abas(self) -> list[dict]:
        return self._dados.get("tabs", [])

    def adicionar_aba(self, nome: str = "Nova Aba") -> str:
        aba_id = str(uuid.uuid4())
        self._dados["tabs"].append({"id": aba_id, "nome": nome, "tarefas": []})
        self.salvar()
        return aba_id

    def renomear_aba(self, aba_id: str, novo_nome: str) -> None:
        for aba in self._dados["tabs"]:
            if aba["id"] == aba_id:
                aba["nome"] = novo_nome
                self.salvar()
                return

    def remover_aba(self, aba_id: str) -> None:
        self._dados["tabs"] = [a for a in self._dados["tabs"] if a["id"] != aba_id]
        self.salvar()

    # ------------------------------------------------------------------
    # Tarefas
    # ------------------------------------------------------------------

    def _aba(self, aba_id: str) -> dict | None:
        return next((a for a in self._dados["tabs"] if a["id"] == aba_id), None)

    def obter_tarefas(self, aba_id: str) -> list[dict]:
        aba = self._aba(aba_id)
        return aba["tarefas"] if aba else []

    def adicionar_tarefa(self, aba_id: str, texto: str) -> str | None:
        aba = self._aba(aba_id)
        if aba is None or not texto.strip():
            return None
        tarefa_id = str(uuid.uuid4())
        aba["tarefas"].append({"id": tarefa_id, "texto": texto.strip(), "feita": False})
        self.salvar()
        return tarefa_id

    def toggle_tarefa(self, aba_id: str, tarefa_id: str) -> None:
        aba = self._aba(aba_id)
        if aba is None:
            return
        for t in aba["tarefas"]:
            if t["id"] == tarefa_id:
                t["feita"] = not t["feita"]
                self.salvar()
                return

    def remover_tarefa(self, aba_id: str, tarefa_id: str) -> None:
        aba = self._aba(aba_id)
        if aba is None:
            return
        aba["tarefas"] = [t for t in aba["tarefas"] if t["id"] != tarefa_id]
        self.salvar()
