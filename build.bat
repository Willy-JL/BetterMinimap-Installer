@echo off

set wolvenkit_url=https://github.com/WolvenKit/WolvenKit/releases/download/8.5.3/WolvenKit.Console-1.6.5.zip
set dotnet_url=https://download.visualstudio.microsoft.com/download/pr/f3eaf689-f89a-40d0-9779-8c536dd9d2dc/924fd88b9c8d3622cb61112057c9ef47/dotnet-runtime-6.0.2-win-x64.exe

cxfreeze ^
    --base-name Win32GUI ^
    --target-name BetterMinimap-Installer ^
    --uac-admin ^
    --target-dir dist ^
    --compress ^
    --include-msvcr ^
    main.py
xcopy /E /I TclTheme dist\TclTheme

curl -Lo dist\WolvenKit.CLI.zip %wolvenkit_url%
tar -xf dist\WolvenKit.CLI.zip -C dist
move "dist\WolvenKit CLI" dist\WolvenKit.CLI
del dist\WolvenKit.CLI.zip

curl -Lo dist\dotnet-runtime.exe %dotnet_url%
