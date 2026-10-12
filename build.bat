@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM ============================================================
REM  Шаблон сборки проекта через PyInstaller (onedir).
REM
REM  ВАЖНО: замени <ProjectName> в строке ниже на имя проекта
REM  (например: set PROJECT_NAME=Sonolog).
REM  Имя должно совпадать с именем spec-файла в корне:
REM     set PROJECT_NAME=MyApp   ->   MyApp.spec
REM
REM  Результат: dist\<ProjectName>\<ProjectName>.exe
REM
REM  Перед сборкой:
REM    1) генерирует документацию (make_docs.py) -> md + docx + pdf,
REM    2) проверяет наличие <ProjectName>.spec,
REM    3) защищает папку данных, если она уже лежит в dist/.
REM ============================================================

set PROJECT_NAME=<ProjectName>
set SPEC_FILE=%PROJECT_NAME%.spec

REM Проверка: если имя не заменено — подскажем и остановимся.
if "%PROJECT_NAME%"=="<ProjectName>" (
    echo.
    echo ОШИБКА: в build.bat не заменён плейсхолдер ^<ProjectName^>.
    echo Открой build.bat и в строке
    echo     set PROJECT_NAME=^<ProjectName^>
    echo укажи имя проекта, например:
    echo     set PROJECT_NAME=Sonolog
    echo.
    pause
    exit /b 1
)

echo === Сборка %PROJECT_NAME% (через %SPEC_FILE%) ===
echo.

REM --- 1. Обновляем документацию и инструкции (md + docx + pdf) ---
if exist "service\docs\make_docs.py" (
    echo Обновляю документацию и инструкции...
    python service\docs\make_docs.py
    if errorlevel 1 echo ВНИМАНИЕ: make_docs.py завершился с ошибкой.
) else (
    echo ВНИМАНИЕ: service\docs\make_docs.py не найден — документация не обновлена.
)
echo.

REM --- 2. Проверки ---
if not exist "%SPEC_FILE%" goto :err_no_spec
if not exist "main.py" echo ВНИМАНИЕ: main.py не найден в корне проекта.
if not exist "requirements.txt" echo ВНИМАНИЕ: requirements.txt не найден.
if not exist "assets" echo ВНИМАНИЕ: папка assets не найдена.

REM --- 3. Защита данных, если папка данных уже лежит рядом с exe ---
if exist "dist\%PROJECT_NAME%\%PROJECT_NAME%Data" (
    echo.
    echo ВНИМАНИЕ! Найдена папка данных:
    echo    dist\%PROJECT_NAME%\%PROJECT_NAME%Data
    echo При пересборке она будет УДАЛЕНА.
    echo.
    choice /C YN /M "Сделать резервную копию и продолжить"
    if errorlevel 2 (
        echo Отменено.
        pause
        exit /b 1
    )
    echo Делаю резервную копию в backup_%PROJECT_NAME%Data\
    if not exist "backup_%PROJECT_NAME%Data" mkdir "backup_%PROJECT_NAME%Data"
    xcopy /E /I /Y "dist\%PROJECT_NAME%\%PROJECT_NAME%Data" "backup_%PROJECT_NAME%Data\%PROJECT_NAME%Data" >nul
    echo Копия: backup_%PROJECT_NAME%Data\%PROJECT_NAME%Data\
    echo.
)

REM --- 4. Очистка старых сборок ---
if exist "build" rmdir /s /q "build"
if exist "dist\%PROJECT_NAME%" rmdir /s /q "dist\%PROJECT_NAME%"

REM --- 5. Сборка ---
echo Собираю через %SPEC_FILE%...
python -m PyInstaller %SPEC_FILE% --clean --noconfirm

echo.
if exist "dist\%PROJECT_NAME%\%PROJECT_NAME%.exe" (
    echo ГОТОВО: dist\%PROJECT_NAME%\%PROJECT_NAME%.exe
    echo.
    echo Папку dist\%PROJECT_NAME%\ целиком переносим на другой ПК.
    echo Папка данных создастся при первом запуске.
) else (
    echo ОШИБКА СБОРКИ — смотри вывод выше.
)
pause
exit /b 0

:err_no_spec
echo.
echo ОШИБКА: %SPEC_FILE% не найден в корне проекта.
echo Если spec-файл называется иначе — поправь строку:
echo     set PROJECT_NAME=^<ProjectName^>
echo в этом build.bat, чтобы имя совпадало с именем spec-файла.
echo.
pause
exit /b 1