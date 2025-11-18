; Script de Inno Setup para el Generador de Códigos de Carnet
; Este script crea un instalador profesional para Windows
; Requiere Inno Setup 6.0 o superior

#define MyAppName "Generador de Codigos de Carnet"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "YoquelvisDev"
#define MyAppURL "https://github.com/yoquelvisdev"
#define MyAppExeName "GeneradorCodigosCarnet.exe"
#define MyAppAssocName "Archivo de Codigos de Carnet"
#define MyAppAssocExt ".gcdb"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; Información básica de la aplicación
AppId={{8F3C4E2D-9B5A-4C7E-8D6F-1A2B3C4D5E6F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Configuración de instalación
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README_INSTALLER.txt
OutputDir=output_installer
OutputBaseFilename=GeneradorCodigosCarnet_Setup_v{#MyAppVersion}
SetupIconFile=..\assets\logo.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

; Privilegios
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Arquitectura
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Configuración visual
; WizardImageFile=..\assets\logo_256x256.png
; WizardSmallImageFile=..\assets\logo_64x64.png

; Desinstalación
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Archivos del ejecutable principal
Source: "..\dist\GeneradorCodigosCarnet\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Archivos de assets
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
; Archivos de configuración
Source: "..\config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs
; Templates de carnets
Source: "..\data\templates_carnet\*"; DestDir: "{commonappdata}\{#MyAppName}\templates_carnet"; Flags: ignoreversion recursesubdirs createallsubdirs
; Base de datos vacía (si existe)
Source: "..\data\codigos_barras.db"; DestDir: "{commonappdata}\{#MyAppName}"; Flags: ignoreversion onlyifdoesntexist
; Documentación
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
; Archivo .env de ejemplo
Source: "env.template"; DestDir: "{app}"; DestName: ".env"; Flags: ignoreversion

[Dirs]
; Crear directorios de datos con permisos completos
Name: "{commonappdata}\{#MyAppName}"; Permissions: users-full
Name: "{commonappdata}\{#MyAppName}\codigos_generados"; Permissions: users-full
Name: "{commonappdata}\{#MyAppName}\carnets"; Permissions: users-full
Name: "{commonappdata}\{#MyAppName}\backups"; Permissions: users-full
Name: "{commonappdata}\{#MyAppName}\logs"; Permissions: users-full
Name: "{commonappdata}\{#MyAppName}\templates_carnet"; Permissions: users-full

[Icons]
; Accesos directos en el menú de inicio
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\Manual de Usuario"; Filename: "{app}\README.md"
; Acceso directo en el escritorio
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; WorkingDir: "{app}"
; Acceso directo en inicio rápido
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; WorkingDir: "{app}"

[Run]
; Ejecutar la aplicación después de la instalación
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Asociar extensión de archivo con la aplicación
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".gcdb"; ValueData: ""

; Agregar al registro de Windows para desinstalación
Root: HKA; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: "Path"; ValueData: "{app}"

[Code]
var
  DataDirPage: TInputDirWizardPage;
  
procedure InitializeWizard;
begin
  // Crear página personalizada para seleccionar directorio de datos
  DataDirPage := CreateInputDirPage(wpSelectDir,
    'Seleccionar Ubicacion de Datos', 
    'Donde desea almacenar los datos de la aplicacion?',
    'Los datos incluyen: codigos generados, carnets, backups y logs.'#13#10#13#10 +
    'Seleccione la carpeta donde desea almacenar los datos, luego haga clic en Siguiente.'#13#10#13#10 +
    'NOTA: Se recomienda mantener la ubicacion predeterminada.',
    False, '');
  DataDirPage.Add('');
  DataDirPage.Values[0] := ExpandConstant('{commonappdata}\{#MyAppName}');
end;

function GetDataDir(Param: String): String;
begin
  Result := DataDirPage.Values[0];
end;

// Funcion para verificar si .NET Framework esta instalado (si es necesario)
function IsDotNetInstalled(): Boolean;
begin
  Result := True;  // Por ahora siempre True, PyInstaller incluye todo
end;

// Funcion que se ejecuta antes de la instalacion
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
end;

// Funcion que se ejecuta despues de la instalacion
procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvFile: String;
  EnvContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Crear archivo .env con la ruta de datos
    EnvFile := ExpandConstant('{app}\.env');
    EnvContent := 'DATA_DIR=' + DataDirPage.Values[0] + #13#10 +
                  'ADMIN_PASSWORD=admin123' + #13#10;
    SaveStringToFile(EnvFile, EnvContent, False);
  end;
end;

// Funcion para mostrar mensaje final
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    // Mostrar informacion adicional al finalizar
    Log('Instalacion completada exitosamente');
  end;
end;

