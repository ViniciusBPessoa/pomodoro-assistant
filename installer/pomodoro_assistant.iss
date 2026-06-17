; Script Inno Setup — Pomodoro Assistant
; Pré-requisito: rodar "uv run pyinstaller pomodoro.spec --clean" antes de compilar

[Setup]
AppName=Pomodoro Assistant
AppVersion=1.0.0
AppPublisher=ViniciusBPessoa
DefaultDirName={autopf}\PomodoroAssistant
DefaultGroupName=Pomodoro Assistant
OutputDir=output
OutputBaseFilename=PomodoroAssistant_Setup
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\PomodoroAssistant.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Files]
Source: "..\dist\PomodoroAssistant\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Pomodoro Assistant";    Filename: "{app}\PomodoroAssistant.exe"; IconFilename: "{app}\assets\icon.ico"
Name: "{commondesktop}\Pomodoro Assistant"; Filename: "{app}\PomodoroAssistant.exe"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos adicionais:"

[Run]
Filename: "{app}\PomodoroAssistant.exe"; Description: "Iniciar Pomodoro Assistant"; Flags: nowait postinstall skipifsilent
