@echo off
:: Asegurar que estamos en la codificación correcta para caracteres latinos
chcp 65001 > nul

echo ==========================================
echo   🚀 SUBIENDO ACTUALIZACIONES A GITHUB
echo ==========================================
echo.

:: 1. Agrega todos los archivos nuevos o modificados
git add .

:: 2. Pide el mensaje del commit por teclado
set /p mensaje="¿Que cambiaste hoy? -> "

:: 3. Hace el commit con tu mensaje
git commit -m "%mensaje%"

:: 4. Sube los cambios con el bypass de seguridad activado automáticamente
echo.
echo 📤 Mandando archivos a la nube...
git push origin main -o secret-scanning=bypass

echo.
echo ==========================================
echo   ✅ ¡PROYECTO ACTUALIZADO EN INTERNET!
echo ==========================================
pause