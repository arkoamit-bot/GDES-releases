[Setup]
AppName=GDES
AppVersion=6.7.0
AppPublisher=GDES Clinical Team
DefaultDirName={autopf}\GDES
DefaultGroupName=GDES
OutputDir=..\dist\installer
OutputBaseFilename=GDES-6.7.0-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\GDES\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\GDES"; Filename: "{app}\GDES.exe"
Name: "{group}\Uninstall GDES"; Filename: "{uninstallexe}"
Name: "{autodesktop}\GDES"; Filename: "{app}\GDES.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\GDES.exe"; Description: "Launch GDES now"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    Exec(ExpandConstant('{app}\MicrosoftEdgeWebview2Setup.exe'), '/silent /install', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
