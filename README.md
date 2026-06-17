# Pomodoro Assistant

Aplicativo desktop de produtividade baseado na técnica Pomodoro, desenvolvido com PyQt6. Projetado para rodar de forma discreta como uma janela flutuante e sempre visível (*always on top*), com visual minimalista em tema escuro.

## Funcionalidades

- **Timer Pomodoro** com ciclo completo de fases (foco → pausa curta → pausa longa) e barra de progresso visual
- **Cronômetro livre** com registro de voltas
- **To-Do List** com múltiplas abas e persistência automática
- **Estatísticas** com heatmap mensal, cartões de métricas e aba de Analytics com gráficos interativos (barras, drill-down por dia, linha de tendência e média de horários ativos)
- **Configurações** persistentes: duração das fases, sons customizados e diretórios de dados
- **Sistema de áudio** com sons padrão gerados automaticamente e suporte a WAV customizados
- Persistência local via **SQLite** para histórico de ciclos

---

## Pré-requisitos

| Ferramenta | Versão mínima | Uso |
|---|---|---|
| [Python](https://www.python.org/downloads/) | 3.14+ | Runtime |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | qualquer | Gerenciador de pacotes e ambiente virtual |
| [VS Code](https://code.visualstudio.com/) | qualquer | Editor recomendado |
| [Inno Setup](https://jrsoftware.org/isinfo.php) | 6.x | Apenas para gerar o instalador `.exe` |

---

## Como rodar localmente (VS Code)

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd pomodoro-assistant
```

### 2. Criar e ativar o ambiente virtual

O `uv` cria e gerencia o `.venv` automaticamente. Basta instalar as dependências:

```bash
uv sync
```

Para ativar o ambiente manualmente no terminal do VS Code:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat
```

> **Dica:** No VS Code, selecione o interpretador Python em `Ctrl+Shift+P` → `Python: Select Interpreter` e aponte para `.venv\Scripts\python.exe`. O terminal integrado já ativará o ambiente automaticamente.

### 3. Executar o aplicativo

```bash
uv run python main.py
```

---

## Build e Instalador

O processo de empacotamento usa **PyInstaller** (para gerar o executável) e **Inno Setup** (para gerar o instalador `.exe`).

### Dependências de build

As ferramentas de build estão no grupo `dev` do `pyproject.toml` e já são instaladas via:

```bash
uv sync --group dev
```

### Passo 1 — Gerar o executável (PyInstaller)

O arquivo `pomodoro.spec` na raiz contém todas as configurações de empacotamento (assets incluídos, imports ocultos, ícone, etc.).

```bash
uv run pyinstaller pomodoro.spec --clean
```

O executável e seus arquivos serão gerados em `dist/PomodoroAssistant/`.

### Passo 2 — Gerar o instalador (Inno Setup)

Com o Inno Setup instalado, compile o script `installer/pomodoro_assistant.iss`:

**Via interface gráfica:**
1. Abra o Inno Setup Compiler
2. `File` → `Open` → selecione `installer/pomodoro_assistant.iss`
3. Clique em `Build` → `Compile` (ou pressione `F9`)

**Via linha de comando** (requer `iscc.exe` no PATH):

```bash
iscc installer/pomodoro_assistant.iss
```

O instalador será gerado em `installer/output/PomodoroAssistant_Setup.exe`.

> **Atenção:** O Passo 1 (PyInstaller) deve ser executado **antes** do Passo 2. O script `.iss` aponta para `dist/PomodoroAssistant/` como fonte dos arquivos.

---

## Estrutura do Projeto

```
main.py                     # Ponto de entrada e orquestrador (GerenciadorDeTelas)
pomodoro.spec               # Configuração de build do PyInstaller
assets/
  icon.ico / icon.png       # Ícone do aplicativo
  sons/                     # Sons WAV (gerados automaticamente, não versionados)
installer/
  pomodoro_assistant.iss    # Script do Inno Setup
src/
  backend/
    timer_core.py           # Motor do Pomodoro (PyQt6 QObject + sinais)
    stopwatch_core.py       # Motor do cronômetro livre
    database.py             # Persistência SQLite (ciclos e estatísticas)
    settings_manager.py     # Singleton de configurações (settings.json)
    audio_manager.py        # Reprodução e geração de sons WAV
    todo_manager.py         # Persistência da To-Do List (JSON)
  frontend/
    PillWidget.py           # Janela compacta em pílula (always on top)
    pomodoro_ui.py          # Janela expandida do timer
    DrawerWidget.py         # Gaveta animada de navegação
    settings_ui.py          # Painel de configurações
    todo_ui.py              # Janela da To-Do List com abas
    stats_ui.py             # Estatísticas: heatmap + aba Analytics (matplotlib)
    stopwatch_ui.py         # Janela do cronômetro livre
    components.py           # Componentes reutilizáveis (CustomSpinBox)
  styles/
    theme.py                # Paleta de cores e funções de stylesheet (QSS)
```

---

## Tecnologias utilizadas

| Biblioteca | Finalidade |
|---|---|
| [PyQt6](https://pypi.org/project/PyQt6/) | Framework de UI (janelas, sinais, widgets) |
| [qtawesome](https://github.com/spyder-ide/qtawesome) | Ícones vetoriais (Phosphor Icons via `ph.*`) |
| [matplotlib](https://matplotlib.org/) | Gráficos interativos na aba Analytics |
| [pandas](https://pandas.pydata.org/) | Suporte a análise de dados |
| [markdown](https://pypi.org/project/Markdown/) | Suporte a notas Markdown (módulo planejado) |
| [PyInstaller](https://pyinstaller.org/) | Empacotamento em executável Windows |
| [uv](https://docs.astral.sh/uv/) | Gerenciamento de dependências e ambiente virtual |
