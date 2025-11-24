; Script de Inno Setup para el Generador de Códigos de Carnet
; Este script crea un instalador profesional para Windows
; Requiere Inno Setup 6.0 o superior

; Incluir biblioteca para descargas (Inno Dependency Installer)
; Usa CodeDependencies.iss si está disponible en la carpeta InnoDependencyInstaller-master
#ifdef UNICODE
  #define DEPENDENCY_SUPPORT
  #ifexist "InnoDependencyInstaller-master\CodeDependencies.iss"
    #include "InnoDependencyInstaller-master\CodeDependencies.iss"
  #else
    #ifexist "CodeDependencies.iss"
      #include "CodeDependencies.iss"
    #endif
  #endif
#endif

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
; Templates de carnets (se instalarán en la ubicación seleccionada por el usuario)
Source: "..\data\templates_carnet\*"; DestDir: "{code:GetDataDir}\templates_carnet"; Flags: ignoreversion recursesubdirs createallsubdirs
; Base de datos vacía (si existe) - se instalará en la ubicación seleccionada por el usuario
Source: "..\data\codigos_barras.db"; DestDir: "{code:GetDataDir}"; Flags: ignoreversion onlyifdoesntexist
; Documentación
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
; Archivo .env de ejemplo
Source: "env.template"; DestDir: "{app}"; DestName: ".env"; Flags: ignoreversion
; Scripts de instalación de dependencias
Source: "..\script\install_poppler.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\script\verificar_poppler.bat"; DestDir: "{app}"; Flags: ignoreversion
; Poppler - empaquetado e instalado automáticamente en C:\Program Files\poppler
Source: "poppler-25.07.0\Library\bin\*"; DestDir: "{autopf}\poppler\bin"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "poppler-25.07.0\share\*"; DestDir: "{autopf}\poppler\share"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; Crear directorios de datos con permisos completos (en la ubicación seleccionada por el usuario)
Name: "{code:GetDataDir}"; Permissions: users-full
Name: "{code:GetDataDir}\codigos_generados"; Permissions: users-full
Name: "{code:GetDataDir}\carnets"; Permissions: users-full
Name: "{code:GetDataDir}\backups"; Permissions: users-full
Name: "{code:GetDataDir}\logs"; Permissions: users-full
Name: "{code:GetDataDir}\templates_carnet"; Permissions: users-full

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
  TesseractInstallerPath: String;
  
// URL del instalador de Tesseract OCR (versión 5.5.0)
// URL oficial desde GitHub: https://github.com/tesseract-ocr/tesseract/releases
// Si la descarga falla, el instalador permitirá continuar sin Tesseract
// El usuario puede instalarlo manualmente después si lo desea desde:
// https://github.com/UB-Mannheim/tesseract/wiki
const
  TESSERACT_DOWNLOAD_URL = 'https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe';
  
// URL de descarga de Poppler para Windows
// Poppler es necesario para la verificación OCR de archivos PDF
// Si la descarga falla, el usuario puede usar el script install_poppler.bat incluido
const
  POPPLER_DOWNLOAD_URL = 'https://github.com/oschwartz10612/poppler-windows/releases/download/v25.11.0-0/Release-25.11.0-0.zip';
  
// Rutas comunes donde Tesseract puede estar instalado
function GetTesseractPaths(): TArrayOfString;
var
  Paths: TArrayOfString;
begin
  SetArrayLength(Paths, 3);
  Paths[0] := ExpandConstant('{pf}\Tesseract-OCR\tesseract.exe');
  Paths[1] := ExpandConstant('{pf32}\Tesseract-OCR\tesseract.exe');
  Paths[2] := ExpandConstant('{localappdata}\Programs\Tesseract-OCR\tesseract.exe');
  Result := Paths;
end;

// Función para verificar si Tesseract está instalado
function IsTesseractInstalled(): Boolean;
var
  Paths: TArrayOfString;
  Path: String;
  I: Integer;
  VersionOutput: String;
  ErrorCode: Integer;
begin
  Result := False;
  
  // Primero, intentar ejecutar tesseract desde PATH
  if Exec('tesseract', '--version', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) then
  begin
    Result := True;
    Log('Tesseract encontrado en PATH');
    Exit;
  end;
  
  // Si no está en PATH, buscar en rutas comunes
  Paths := GetTesseractPaths();
  for I := 0 to GetArrayLength(Paths) - 1 do
  begin
    Path := Paths[I];
    if FileExists(Path) then
    begin
      Result := True;
      Log('Tesseract encontrado en: ' + Path);
      Exit;
    end;
  end;
  
  // También verificar en el registro de Windows
  if RegQueryStringValue(HKLM, 'SOFTWARE\Tesseract-OCR', 'Path', Path) then
  begin
    if FileExists(Path + '\tesseract.exe') then
    begin
      Result := True;
      Log('Tesseract encontrado en registro: ' + Path);
      Exit;
    end;
  end;
  
  Log('Tesseract no encontrado');
end;

// Función para verificar si Poppler está instalado
function IsPopplerInstalled(): Boolean;
var
  ErrorCode: Integer;
  PopplerPaths: TArrayOfString;
  Path: String;
  I: Integer;
begin
  Result := False;
  
  // Primero, intentar ejecutar pdftoppm desde PATH
  if Exec('pdftoppm', '-v', '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) then
  begin
    Result := True;
    Log('Poppler encontrado en PATH');
    Exit;
  end;
  
  // Si no está en PATH, buscar en rutas comunes
  SetArrayLength(PopplerPaths, 4);
  PopplerPaths[0] := 'C:\poppler\bin\pdftoppm.exe';
  PopplerPaths[1] := ExpandConstant('{pf}\poppler\bin\pdftoppm.exe');
  PopplerPaths[2] := ExpandConstant('{pf32}\poppler\bin\pdftoppm.exe');
  PopplerPaths[3] := 'C:\poppler\poppler-25.11.0\Library\bin\pdftoppm.exe';
  
  for I := 0 to GetArrayLength(PopplerPaths) - 1 do
  begin
    Path := PopplerPaths[I];
    if FileExists(Path) then
    begin
      Result := True;
      Log('Poppler encontrado en: ' + Path);
      Exit;
    end;
  end;
  
  Log('Poppler no encontrado');
end;

// Función para agregar Tesseract como dependencia usando CodeDependencies
function AddTesseractDependency(): Boolean;
begin
  Result := False;
  TesseractInstallerPath := 'tesseract-installer.exe';
  
  #ifdef DEPENDENCY_SUPPORT
  try
    // Agregar Tesseract como dependencia usando el sistema de CodeDependencies
    // Dependency_Add(Filename, Parameters, Title, URL, Checksum, ForceSuccess, RestartAfter)
    // NOTA: Con la URL correcta de GitHub, la descarga debería funcionar correctamente
    // ForceSuccess = False permite que el usuario elija si continuar si hay un error
    Dependency_Add(
      TesseractInstallerPath,
      '/S /COMPONENTS=base,spa,eng',
      'Tesseract OCR',
      TESSERACT_DOWNLOAD_URL,
      '', // Sin checksum por ahora
      False, // No forzar éxito - si falla, el usuario puede elegir omitir
      False  // No requiere reinicio
    );
    
    Result := True;
    Log('Tesseract OCR agregado como dependencia (con opción de omitir si falla la descarga)');
  except
    Log('Error al agregar Tesseract como dependencia: ' + GetExceptionMessage);
    Result := False;
  end;
  #else
  // CodeDependencies.iss no está disponible
  Log('CodeDependencies.iss no está disponible. La descarga automática de Tesseract no está disponible.');
  Result := False;
  #endif
end;

// Nota: La función InstallTesseract ya no es necesaria si usamos CodeDependencies
// CodeDependencies manejará la instalación automáticamente
// Esta función se mantiene como respaldo si CodeDependencies no está disponible
function InstallTesseract(): Boolean;
var
  ErrorCode: Integer;
  InstallParams: String;
  InstallerPath: String;
begin
  Result := False;
  InstallerPath := ExpandConstant('{tmp}\tesseract-installer.exe');
  
  if not FileExists(InstallerPath) then
  begin
    Log('Error: Archivo del instalador de Tesseract no encontrado: ' + InstallerPath);
    Exit;
  end;
  
  // Parámetros de instalación silenciosa:
  // /S = instalación silenciosa
  // /COMPONENTS = componentes a instalar (base, spa, eng)
  InstallParams := '/S /COMPONENTS=base,spa,eng';
  
  Log('Instalando Tesseract OCR...');
  Log('Comando: ' + InstallerPath + ' ' + InstallParams);
  
  // Ejecutar el instalador
  if Exec(InstallerPath, InstallParams, '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) then
  begin
    if ErrorCode = 0 then
    begin
      Log('Tesseract OCR instalado exitosamente');
      Result := True;
      
      // Esperar un momento para que Windows actualice el PATH
      Sleep(2000);
      
      // Verificar que la instalación fue exitosa
      if IsTesseractInstalled() then
      begin
        Log('Verificación: Tesseract está correctamente instalado');
      end
      else
      begin
        Log('Advertencia: Tesseract instalado pero no se puede verificar. Puede requerir reinicio.');
        Result := True; // Aún así consideramos exitosa la instalación
      end;
    end
    else
    begin
      Log('Error al instalar Tesseract. Código de error: ' + IntToStr(ErrorCode));
      Result := False;
    end;
  end
  else
  begin
    Log('Error al ejecutar el instalador de Tesseract');
    Result := False;
  end;
end;

// Función InitializeSetup - se ejecuta al inicio del proceso de instalación
// Aquí es donde CodeDependencies espera que se agreguen las dependencias
function InitializeSetup: Boolean;
var
  TesseractNeedsInstall: Boolean;
  PopplerNeedsInstall: Boolean;
begin
  Result := True;
  
  // Verificar si Tesseract necesita instalación y agregarlo como dependencia
  TesseractNeedsInstall := not IsTesseractInstalled();
  if TesseractNeedsInstall then
  begin
    Log('Tesseract OCR no está instalado. Agregando como dependencia...');
    AddTesseractDependency();
  end
  else
  begin
    Log('Tesseract OCR ya está instalado. No se requiere instalación adicional.');
  end;
  
  // Verificar Poppler (incluido en el paquete, se instalará automáticamente)
  PopplerNeedsInstall := not IsPopplerInstalled();
  if PopplerNeedsInstall then
  begin
    Log('Poppler no está instalado. Se instalará automáticamente desde el paquete incluido.');
  end
  else
  begin
    Log('Poppler ya está instalado en el sistema. El paquete incluido no se instalará.');
  end;
end;

procedure InitializeWizard;
begin
  // Crear página personalizada para seleccionar directorio de datos
  DataDirPage := CreateInputDirPage(wpSelectDir,
    'Seleccionar Ubicacion de Datos', 
    'Donde desea almacenar los datos de la aplicacion?',
    'Los datos incluyen: codigos generados, carnets, backups y logs.'#13#10#13#10 +
    'Seleccione la carpeta donde desea almacenar los datos, luego haga clic en Siguiente.'#13#10#13#10 +
    'NOTA: Se recomienda mantener la ubicacion predeterminada (AppData del usuario).',
    False, '');
  DataDirPage.Add('');
  // Usar AppData del usuario en lugar de ProgramData (más fácil de acceder y no requiere permisos de admin)
  DataDirPage.Values[0] := ExpandConstant('{userappdata}\{#MyAppName}');
  
  // Inicializar variable
  TesseractInstallerPath := '';
end;

function GetDataDir(Param: String): String;
begin
  Result := DataDirPage.Values[0];
end;

// Función que se ejecuta antes de la instalación
// Nota: Si CodeDependencies está disponible, las dependencias se instalarán automáticamente
// a través de Dependency_PrepareToInstall que se ejecuta como evento
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  TesseractNeedsInstall: Boolean;
  PopplerNeedsInstall: Boolean;
begin
  Result := '';
  
  // Verificar si Tesseract está instalado
  TesseractNeedsInstall := not IsTesseractInstalled();
  PopplerNeedsInstall := not IsPopplerInstalled();
  
  if TesseractNeedsInstall then
  begin
    #ifdef DEPENDENCY_SUPPORT
    // CodeDependencies manejará la descarga e instalación automáticamente
    // Si la descarga falla, el usuario puede omitirla y continuar
    Log('Tesseract OCR será instalado automáticamente por CodeDependencies (si la descarga es exitosa)');
    #else
    // CodeDependencies no está disponible, mostrar mensaje informativo
    Log('Tesseract OCR no está instalado y CodeDependencies no está disponible');
    Result := 'Tesseract OCR no está instalado y no se pudo configurar la instalación automática.'#13#10#13#10 +
              'La aplicación se instalará correctamente, pero la verificación OCR estará deshabilitada.'#13#10#13#10 +
              'Para habilitar la verificación OCR, puede instalar Tesseract manualmente desde:'#13#10 +
              'https://github.com/UB-Mannheim/tesseract/wiki'#13#10#13#10 +
              'Durante la instalación, asegúrese de seleccionar los idiomas "Spanish" y "English".';
    #endif
  end
  else
  begin
    Log('Tesseract OCR ya está instalado. No se requiere instalación adicional.');
  end;
  
  // Información sobre Poppler (incluido en el paquete)
  if PopplerNeedsInstall then
  begin
    Log('Poppler no está instalado. Se instalará automáticamente desde el paquete incluido.');
    // No agregar mensaje de advertencia ya que Poppler se instalará automáticamente
  end
  else
  begin
    Log('Poppler ya está instalado en el sistema. El paquete incluido no se instalará.');
  end;
end;

// Función para agregar Poppler al PATH del sistema
function AddPopplerToPath(): Boolean;
var
  PopplerBinPath: String;
  CurrentPath: String;
  NewPath: String;
begin
  Result := False;
  PopplerBinPath := ExpandConstant('{autopf}\poppler\bin');
  
  // Verificar que el directorio existe
  if not DirExists(PopplerBinPath) then
  begin
    Log('Error: Directorio de Poppler no existe: ' + PopplerBinPath);
    Exit;
  end;
  
  // Obtener el PATH actual del sistema
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', CurrentPath) then
  begin
    Log('Error: No se pudo leer el PATH del sistema');
    Exit;
  end;
  
  // Verificar si ya está en el PATH
  if Pos(PopplerBinPath, CurrentPath) > 0 then
  begin
    Log('Poppler ya está en el PATH del sistema');
    Result := True;
    Exit;
  end;
  
  // Agregar Poppler al PATH
  NewPath := CurrentPath + ';' + PopplerBinPath;
  if RegWriteStringValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', NewPath) then
  begin
    Log('Poppler agregado al PATH del sistema: ' + PopplerBinPath);
    Result := True;
  end
  else
  begin
    Log('Error: No se pudo agregar Poppler al PATH del sistema');
  end;
end;

// Función que se ejecuta después de la instalación
procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvFile: String;
  EnvContent: String;
  PopplerInstalled: Boolean;
begin
  if CurStep = ssPostInstall then
  begin
    // Crear archivo .env con la ruta de datos
    EnvFile := ExpandConstant('{app}\.env');
    EnvContent := 'DATA_DIR=' + DataDirPage.Values[0] + #13#10 +
                  'ADMIN_PASSWORD=admin123' + #13#10;
    SaveStringToFile(EnvFile, EnvContent, False);
    
    // Limpiar el instalador de Tesseract si existe
    if (TesseractInstallerPath <> '') and FileExists(TesseractInstallerPath) then
    begin
      DeleteFile(TesseractInstallerPath);
      Log('Instalador temporal de Tesseract eliminado');
    end;
    
    // Configurar Poppler si no está instalado
    PopplerInstalled := IsPopplerInstalled();
    if not PopplerInstalled then
    begin
      Log('Configurando Poppler desde el paquete incluido...');
      // Poppler ya fue copiado a {autopf}\poppler\bin durante la instalación
      // Solo necesitamos agregarlo al PATH
      if AddPopplerToPath() then
      begin
        Log('Poppler configurado exitosamente');
      end
      else
      begin
        Log('Advertencia: Poppler fue instalado pero no se pudo agregar al PATH. Puede requerir reinicio.');
      end;
    end
    else
    begin
      Log('Poppler ya está instalado en el sistema. No se requiere configuración adicional.');
    end;
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

// Función para obtener la ruta de datos desde el archivo .env o del registro
function GetDataDirPath(): String;
var
  EnvFile: String;
  EnvContent: TArrayOfString;
  I: Integer;
  Line: String;
  DataDir: String;
begin
  Result := '';
  
  // Primero, intentar leer desde el archivo .env
  EnvFile := ExpandConstant('{app}\.env');
  if FileExists(EnvFile) then
  begin
    if LoadStringsFromFile(EnvFile, EnvContent) then
    begin
      for I := 0 to GetArrayLength(EnvContent) - 1 do
      begin
        Line := Trim(EnvContent[I]);
        if Pos('DATA_DIR=', Line) = 1 then
        begin
          DataDir := Copy(Line, Length('DATA_DIR=') + 1, MaxInt);
          Result := Trim(DataDir);
          Log('Ruta de datos encontrada en .env: ' + Result);
          Exit;
        end;
      end;
    end;
  end;
  
  // Si no se encuentra en .env, usar la ruta predeterminada (AppData)
  Result := ExpandConstant('{userappdata}\{#MyAppName}');
  Log('Usando ruta predeterminada de datos: ' + Result);
end;

// Función que se ejecuta durante la desinstalación
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataDir: String;
  Response: Integer;
begin
  // Cuando el desinstalador está a punto de finalizar
  if CurUninstallStep = usUninstall then
  begin
    // Obtener la ruta de datos
    DataDir := GetDataDirPath();
    
    // Verificar si la carpeta de datos existe
    if DirExists(DataDir) then
    begin
      // Preguntar al usuario si quiere eliminar todos los datos
      Response := SuppressibleMsgBox(
        '¿Desea eliminar todos los datos de la aplicación?' + #13#10#13#10 +
        'Esto incluye:' + #13#10 +
        '- Base de datos (códigos de barras, empleados, usuarios)' + #13#10 +
        '- Códigos de barras generados' + #13#10 +
        '- Carnets generados' + #13#10 +
        '- Backups' + #13#10 +
        '- Logs' + #13#10 +
        '- Templates personalizados' + #13#10#13#10 +
        'Ubicación: ' + DataDir + #13#10#13#10 +
        'Esta acción NO se puede deshacer.',
        mbConfirmation,
        MB_YESNO or MB_DEFBUTTON2,
        IDNO
      );
      
      if Response = IDYES then
      begin
        // El usuario quiere eliminar todos los datos
        Log('Usuario eligió eliminar todos los datos');
        Log('Eliminando carpeta de datos: ' + DataDir);
        
        try
          // Eliminar la carpeta completa de datos
          if DelTree(DataDir, True, True, True) then
          begin
            Log('Carpeta de datos eliminada exitosamente');
            SuppressibleMsgBox(
              'Todos los datos de la aplicación han sido eliminados.',
              mbInformation,
              MB_OK,
              IDOK
            );
          end
          else
          begin
            Log('Advertencia: No se pudo eliminar completamente la carpeta de datos');
            SuppressibleMsgBox(
              'No se pudieron eliminar todos los archivos de datos.' + #13#10 +
              'Puede eliminarlos manualmente desde:' + #13#10 + DataDir,
              mbError,
              MB_OK,
              IDOK
            );
          end;
        except
          Log('Error al intentar eliminar la carpeta de datos: ' + GetExceptionMessage);
          SuppressibleMsgBox(
            'Error al eliminar los datos.' + #13#10 +
            'Puede eliminarlos manualmente desde:' + #13#10 + DataDir,
            mbError,
            MB_OK,
            IDOK
          );
        end;
      end
      else
      begin
        // El usuario NO quiere eliminar los datos
        Log('Usuario eligió conservar los datos');
        SuppressibleMsgBox(
          'Los datos de la aplicación se han conservado.' + #13#10#13#10 +
          'Ubicación: ' + DataDir + #13#10#13#10 +
          'Puede eliminarlos manualmente si lo desea.',
          mbInformation,
          MB_OK,
          IDOK
        );
      end;
    end
    else
    begin
      Log('Carpeta de datos no encontrada: ' + DataDir);
    end;
  end;
end;

