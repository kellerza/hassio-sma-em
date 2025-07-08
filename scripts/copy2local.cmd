@echo off
CALL :copy2 sma-em,\\192.168.1.8\addons\sma-em\

EXIT /B %ERRORLEVEL%

:copy2
echo # Modify Config for local testing
set cf=%~1\config.localtest.yaml
cp %~1\config.yaml %cf%
sed -i 's/image:/# image:/' %cf%
sed -i 's/name: /name: A_LOCAL /' %cf%
xcopy /Y %cf% %~2\config.yaml

echo # Copy '%~1' to '%~2'
xcopy /Y /S /EXCLUDE:scripts\copyexclude.txt %~1 %~2

echo # Copy sma package
for %%f in (pyproject.toml,MANIFEST.in,LICENSE,README.md,uv.lock) do xcopy /Y "%%f" %~2\sma\
xcopy /Y /S /EXCLUDE:scripts\copyexclude.txt src %~2\sma\src\

EXIT /B 0
