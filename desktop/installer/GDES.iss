; ============================================================================
;  GDES Windows installer
;  Per-user, no admin, no Program Files. Installs the PyInstaller onedir build
;  into %LOCALAPPDATA%\GDES, preserves local data on upgrades, seeds OneDrive
;  backup/media/update folders when OneDrive is detected, and bundles WebView2.
;
;  Build:
;    iscc /DAppVersion=7.3.0 desktop\installer\GDES.iss
; ============================================================================

#define AppName "GDES Registry"
#define AppPublisher "BIRDEM - Department of Nephrology"
#ifndef AppVersion
  #define AppVersion "7.3.5"
#endif
#define AppExeName "GDES.exe"
#define DistDir "..\..\dist\GDES"

[Setup]
AppId={{B9D2F0A1-GDES-4C7E-9A11-BGDDRPILOT01}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
DefaultDirName={localappdata}\GDES
DisableProgramGroupPage=yes
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
OutputDir=..\..\dist\installer
OutputBaseFilename=Setup_GDES_{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "MicrosoftEdgeWebview2Setup.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall ignoreversion skipifsourcedoesntexist

[Dirs]
; Local live data is preserved on uninstall/upgrade. Backups are seeded to OneDrive
; in bgddr_paths.json below when OneDrive is available.
Name: "{app}\Data"; Flags: uninsneveruninstall
Name: "{app}\Data\Logs"; Flags: uninsneveruninstall

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{tmp}\MicrosoftEdgeWebview2Setup.exe"; Parameters: "/silent /install"; \
  Flags: runhidden waituntilterminated skipifdoesntexist; Check: WebView2Missing
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName} now"; \
  Flags: nowait postinstall skipifsilent

[Code]
function WebView2Missing: Boolean;
var
  v: String;
begin
  Result := not (
    RegQueryStringValue(HKLM,
      'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', v)
    or RegQueryStringValue(HKLM,
      'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', v)
    or RegQueryStringValue(HKCU,
      'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', v)
  );
end;

function JsonEscape(Value: String): String;
begin
  Result := Value;
  StringChangeEx(Result, '\', '\\', True);
  StringChangeEx(Result, '"', '\"', True);
end;

function OneDriveRoot: String;
begin
  Result := GetEnv('OneDriveCommercial');
  if Result = '' then
    Result := GetEnv('OneDrive');
  if Result = '' then
    Result := GetEnv('OneDriveConsumer');
end;

procedure SeedOneDrivePaths;
var
  Base: String;
  BackupDir: String;
  MediaDir: String;
  UpdateDir: String;
  ConfigPath: String;
  Json: String;
begin
  ConfigPath := ExpandConstant('{app}\Data\bgddr_paths.json');
  if FileExists(ConfigPath) then
    exit;

  Base := OneDriveRoot;
  if Base = '' then
    exit;

  BackupDir := AddBackslash(Base) + 'GDES-Backups';
  MediaDir := AddBackslash(Base) + 'GDES-Media';
  UpdateDir := AddBackslash(Base) + 'GDES-Update';

  ForceDirectories(BackupDir);
  ForceDirectories(MediaDir);
  ForceDirectories(UpdateDir);

  Json := '{'#13#10 +
    '  "backup_dir": "' + JsonEscape(BackupDir) + '",'#13#10 +
    '  "media_dir": "' + JsonEscape(MediaDir) + '",'#13#10 +
    '  "update_dir": "' + JsonEscape(UpdateDir) + '"'#13#10 +
    '}'#13#10;

  SaveStringToFile(ConfigPath, Json, False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    SeedOneDrivePaths;
end;
