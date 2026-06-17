# CLAUDE.md

Este arquivo fornece orientações ao Claude Code (claude.ai/code) ao trabalhar neste repositório.

## Visão Geral do Projeto

Sistema modular de produtividade desktop com janelas flutuantes e sempre visíveis (Always on Top). O design segue o conceito **"Pill Design / Modo Foco Profundo"**: janelas frameless, tema escuro (`#1C1C1E`), ícones via Phosphor Icons (prefixo `ph.` no `qtawesome`).

**Módulos implementados:** Pomodoro ✅, To-Do List ✅, Persistência SQLite ✅, Sistema de Áudio ✅.
**Módulos planejados:** Notas Markdown, Dashboard de relatórios.
**Empacotamento final previsto:** PyInstaller para gerar `.exe`.

## Como Executar

```bash
uv run python main.py
```

## Estrutura do Projeto

```
main.py                         # Ponto de entrada e orquestrador (GerenciadorDeTelas)
assets/
  sons/                         # Sons WAV (gerados automaticamente no primeiro run)
    foco_inicio.wav             # Som ao iniciar fase de foco
    pausa_inicio.wav            # Som ao iniciar pausa
    ciclo_concluido.wav         # Som ao concluir ciclo
data/
  todo.json                     # Persistência da To-Do List (gerado em runtime)
src/
  styles/
    theme.py                    # Paleta de cores e funções de stylesheet (QSS)
  backend/
    settings_manager.py         # Singleton `settings` — persistência em settings.json
    timer_core.py               # PomodoroTimer com sinais PyQt e ciclo de fases
    database.py                 # SQLite — log de ciclos concluídos (pomodoro.db)
    audio_manager.py            # Gerência de sons WAV e geração de sons padrão
    todo_manager.py             # Persistência JSON da To-Do List
  frontend/
    components.py               # Componentes reutilizáveis (CustomSpinBox)
    PillWidget.py               # Janela compacta em pílula (190×70)
    pomodoro_ui.py              # Janela expandida do timer (260×280)
    DrawerWidget.py             # Gaveta animada com botões de ferramentas
    settings_ui.py              # Painel de configurações (320×480)
    todo_ui.py                  # Janela da To-Do List com abas (300×400)
settings.json                   # Configurações do usuário (gerado em runtime)
pomodoro.db                     # Banco SQLite (gerado em runtime)
```

## Arquitetura

### Orquestrador (`main.py`)

`GerenciadorDeTelas` possui todas as instâncias e faz **todas** as conexões de sinais. Regras:
- Toda lógica de sincronização entre frontend e backend mora aqui.
- Frontend nunca importa backend diretamente (exceto `settings` singleton e `audio_manager` dentro de `settings_ui`).
- Backend nunca importa frontend.

### Backend (`src/backend/`)

**`timer_core.py` — `PomodoroTimer(QObject)`**

Motor do cronômetro com ciclo completo de fases:
- Ciclo: `"foco"` → `"pausa_curta"` → `"foco"` → ... → (a cada 4 focos) → `"pausa_longa"` → `"foco"`
- Sinais emitidos:
  - `tempo_atualizado(str)` — texto `"MM:SS"` a cada segundo
  - `estado_alterado(bool)` — `True` se rodando
  - `ciclo_concluido()` — disparado ao zerar o tempo naturalmente (antes de avançar a fase)
  - `fase_alterada(str, int)` — `(fase_key, ciclo_atual 1–4)` ao mudar de fase
- Métodos públicos: `alternar()`, `iniciar()`, `pausar()`, `resetar()`, `avancar_fase()`, `atualizar_configuracoes(foco, curta, longa)`

**`settings_manager.py` — singleton `settings`**

```python
from src.backend.settings_manager import settings
settings.get("tempo_foco")      # leitura
settings.set("tempo_foco", 30)  # escrita + salva automaticamente
```

Chaves: `tempo_foco`, `tempo_curta`, `tempo_longa`, `auto_iniciar_pausas`, `auto_iniciar_foco`, `sons_ativados`, `som_foco_inicio`, `som_pausa_inicio`, `som_ciclo_concluido`, `dir_todolist`, `dir_markdown`.

**`database.py`**

```python
from src.backend import database
database.inicializar()               # chamado uma vez no startup
database.registrar_ciclo(fase, min)  # chamado ao ciclo_concluido
database.buscar_ciclos(limite=100)   # retorna list[dict]
```

**`audio_manager.py`**

```python
from src.backend import audio_manager
audio_manager.inicializar()           # cria pasta e gera WAVs padrão se ausentes
audio_manager.tocar("foco_inicio")    # toca o som se sons_ativados=True
audio_manager.listar_sons()           # lista arquivos .wav disponíveis
audio_manager.adicionar_som(caminho)  # copia um WAV externo para assets/sons/
```

Sons ficam em `assets/sons/`. Sons padrão são gerados automaticamente via síntese senoidal (sem dependências externas). Para adicionar sons customizados: copie arquivos `.wav` para `assets/sons/` ou use o seletor na tela de configurações.

**`todo_manager.py` — `TodoManager`**

Gerencia abas e tarefas persistidas em `data/todo.json` (ou `dir_todolist/todo.json`):
```python
manager.adicionar_aba("Nome")
manager.adicionar_tarefa(aba_id, "Texto da tarefa")
manager.toggle_tarefa(aba_id, tarefa_id)
manager.remover_tarefa(aba_id, tarefa_id)
```

### Frontend (`src/frontend/`)

Todas as janelas são frameless, always-on-top e arrastáveis via `mousePressEvent` / `mouseMoveEvent`.

- **`PillWidget`** — View padrão (190×70). Contém `gaveta: DrawerWidget`.
- **`PomodoroUI`** — View expandida (260×280) com `lbl_fase`, `lbl_modo_atual`, `lbl_tempo_gigante`, `btn_reset`, `btn_play_grande`, `btn_avancar`. Contém `gaveta: DrawerWidget`.
- **`DrawerWidget`** — Gaveta animada (QPropertyAnimation). Botões: `btn_modo`, `btn_todos`, `btn_markdown`, `btn_stats`, `btn_config`.
- **`SettingsUI`** — Painel scrollável (320×480). Usa `CustomSpinBox`, `QComboBox` para sons e `QCheckBox`. Emite `configuracoes_salvas` ao salvar. Nunca fechar com `close()` — apenas `hide()`.
- **`TodoUI`** — Janela com abas (300×400). Duplo clique em aba para renomear; botão `×` para deletar (mantém ao menos 1). Tarefas auto-salvas a cada mudança.
- **`components.py` — `CustomSpinBox`** — Substitui `QSpinBox` para evitar colisão de hitbox. API idêntica: `value()`, `setValue()`, `valueChanged`.

### Estilos (`src/styles/theme.py`)

**Regra:** Todo QSS fica aqui. Widgets nunca definem `setStyleSheet` com hex colors literais.

Funções disponíveis:
- `estilo_pill()`, `estilo_pomodoro()`, `estilo_drawer()`, `estilo_configuracoes()`, `estilo_todo()`
- `estilo_label_modo(fase: str)` → stylesheet inline para `lbl_modo_atual`, com cor dinâmica por fase

Cores de fase (`CORES_FASE`): foco = verde `#4CAF50`, pausa curta = laranja `#FF9800`, pausa longa = azul `#2196F3`.

### Fluxo de Sinais (resumo)

```
Clique em play (PillWidget ou PomodoroUI)
  → motor.alternar()
    → estado_alterado(bool)   → GerenciadorDeTelas._atualizar_icone_play()
    → tempo_atualizado(str)   → lbl_tempo (pill) + lbl_tempo_gigante (expandido)

Ciclo completa naturalmente:
  → ciclo_concluido()         → GerenciadorDeTelas._registrar_ciclo() → database
  → fase_alterada(str, int)   → GerenciadorDeTelas._atualizar_fase()  → labels + cor
                              → GerenciadorDeTelas._tocar_som_fase()   → audio_manager

Salvar configurações:
  → configuracoes_salvas()    → GerenciadorDeTelas._aplicar_configuracoes()
                              → motor.atualizar_configuracoes(...)
```

## Regras de Desenvolvimento

1. **Estilos centralizados:** Toda cor e QSS devem estar em `src/styles/theme.py`. Não hardcodar hex colors em widgets.
2. **Separação de camadas:** Backend não importa de frontend. O orquestrador (`main.py`) faz a ponte via sinais.
3. **Sinais PyQt para comunicação:** Preferir sinais/slots ao invés de referências diretas entre widgets.
4. **Componentes sem colisão de hitbox:** Usar `CustomSpinBox` (de `components.py`) em vez de `QSpinBox` nativo em todos os formulários.
5. **Caminhos absolutos:** Usar `Path(__file__).resolve().parent...` para localizar arquivos de dados — nunca `Path("arquivo")` relativo ao CWD.
6. **Novos módulos:** Ao criar um novo módulo (ex: Markdown), seguir o padrão: classe backend pura + classe frontend widget + conexão no `GerenciadorDeTelas`. Adicionar o botão correspondente na `DrawerWidget`.
7. **Sons:** Tocar via `audio_manager.tocar(chave)` — nunca diretamente via `winsound`. Chaves disponíveis: `foco_inicio`, `pausa_inicio`, `ciclo_concluido`.

## Dependências

Gerenciadas com `uv`. Para adicionar: `uv add <pacote>`.

Principais: `pyqt6`, `qtawesome` (ícones Phosphor `ph.*`), `matplotlib`, `pandas`, `markdown`.
