; ============================================================================
;  GDES / BGDDR — Inno Setup installer (P2-2)
;  Per-user, NO admin, NO Program Files. Installs the onedir PyInstaller build
;  into %LOCALAPPDATA%\GDES, creates shortcuts, and installs the Edge WebView2
;  Evergreen runtime if it is missing. Upgrades never touch the patient DB
;  (that lives under %LOCALAPPDATA%\GDES\Data and is handled at launch).
;
;  Build:  iscc desktop\installer\GDES.iss
;  Prereq: build the app first (desktop\build_exe.ps1 -> dist\BGDDR\), and place
;          MicrosoftEdgeWebview2Setup.exe next to this .iss (or in dist\BGDDR\).
; ============================================================================

#define AppName "GDES Registry"
#define AppPublisher "BIRDEM — Department of Nephrology"
#ifndef AppVersion
  #define AppVersion "6.6.1"
#endif
#define AppExeName "BGDDR.exe"
; Path to the onedir build output (relative to this .iss).
#define DistDir "..\..\dist\BGDDR"

[Setup]
AppId={{B9D2F0A1-GDES-4C7E-9A11-BGDDRPILOT01}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
; ---- Per-user install: no admin rights, not in Program Files ----
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
; Never show a console window; this is a GUI app.
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
; The entire onedir build (BGDDR.exe + _internal/ + runtime folders).
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
; WebView2 Evergreen bootstrapper (bundled so clean machines can install it).
Source: "MicrosoftEdgeWebview2Setup.exe"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Dirs]
; Local (non-synced) data root — created once, preserved across upgrades.
Name: "{app}\Data"; Flags: uninsneveruninstall
Name: "{app}\Data\Logs"; Flags: uninsneveruninstall
Name: "{app}\Data\Backups"; Flags: uninsneveruninstall

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
; Install WebView2 silently (per-user, no admin) only if it is absent.
Filename: "{app}\MicrosoftEdgeWebview2Setup.exe"; Parameters: "/silent /install"; \
  Flags: runhidden waituntilterminated skipifdoesntexist; Check: WebView2Missing
; Offer to launch after install.
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName} now"; \
  Flags: nowait postinstall skipifsilent

[Environment]
; Pin the data directory to a LOCAL, non-synced location for this user.
; (The launcher also defaults to %LOCALAPPDATA%\GDES\Data if unset.)

[Code]
function WebView2Missing: Boolean;
var
  v: String;
begin
  { Present if the Evergreen runtime client key exists (HKLM or HKCU). }
  Result := not (
    RegQueryStringValue(HKLM,
      'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', v)
    or RegQueryStringValue(HKCU,
      'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', v)
  );
end;
