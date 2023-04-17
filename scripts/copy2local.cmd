@echo off
CALL :copy2 sma-em-dev,\\192.168.1.8\addons\sma-em-dev\

EXIT /B %ERRORLEVEL%

:copy2
echo # Copy '%~1' to '%~2'
xcopy /Y %~1 %~2

cp %~1\config.yaml config.tmp
sed -i 's/name: /name: LOCAL /' config.tmp
xcopy /Y config.tmp %~2\config.yaml
rm config.tmp

EXIT /B 0
