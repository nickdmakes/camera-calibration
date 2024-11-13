; WARNING: Must define the following variables using /D command line option when compiling
; Name
; AppVersion
; ExeName
; SetupFileName

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{5BA1DACE-CDB5-4FC5-ABCC-37E6CC7AB0D6}
AppName={#Name}
AppVersion={#AppVersion}
;AppVerName={#Name} {#AppVersion}
DefaultDirName={autopf}\{#Name}
DisableDirPage=yes
DisableProgramGroupPage=yes
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
OutputDir=dist\exe
OutputBaseFilename={#SetupFileName}
SetupIconFile=assets\app_logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\AutoCC\{#ExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\AutoCC\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#Name}"; Filename: "{app}\{#ExeName}"
Name: "{autodesktop}\{#Name}"; Filename: "{app}\{#ExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#ExeName}"; Description: "{cm:LaunchProgram,{#StringChange(Name, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
