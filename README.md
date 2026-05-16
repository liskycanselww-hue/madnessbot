# madnessbot

Madness RPG desktop client на Python + PyQt5.

## Полная инструкция по установке и запуску (Windows)

### Шаг 1: Установка Python

1. Перейди на https://www.python.org/downloads/
2. Скачай **Python 3.11** или новее (нажми на большую синюю кнопку)
3. Запусти установщик `.exe`
4. **ВАЖНО!** Поставь галочку на `Add Python to PATH`
5. Нажми `Install Now` и дождись завершения

**Проверка:** Открой PowerShell и введи:
```powershell
python --version
```
Должно вывести что-то вроде `Python 3.14.0`

### Шаг 2: Установка Git

1. Перейди на https://git-scm.com/
2. Скачай и установи Git для Windows
3. При установке нажимай `Next` во всех окнах (стандартные настройки подойдут)

**Проверка:** Открой PowerShell и введи:
```powershell
git --version
```
Должно вывести версию Git

### Шаг 3: Клонирование репозитория

Открой PowerShell **как администратор** (правый клик по PowerShell → "Запуск от имени администратора")

Введи команды одну за другой:

```powershell
cd Desktop
mkdir madnessbot
cd madnessbot
git clone https://github.com/liskycanselww-hue/madnessbot .
```

После этого в папке `Desktop/madnessbot` будут все файлы проекта.

### Шаг 4: Создание виртуального окружения

В этой же PowerShell введи:

```powershell
python -m venv venv
```

Это создаст папку `venv` с изолированным окружением Python.

### Шаг 5: Активация виртуального окружения

Введи:

```powershell
.\venv\Scripts\Activate.ps1
```

**Если PowerShell ругается на политику выполнения:**

Введи:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

PowerShell спросит подтверждение — введи `Y` и нажми Enter.

Потом повтори:
```powershell
.\venv\Scripts\Activate.ps1
```

**Проверка активации:** В начале строки должно появиться `(venv)`:
```
(venv) PS C:\Users\...\madnessbot>
```

### Шаг 6: Установка зависимостей

В активированном окружении (когда видно `(venv)` в начале) введи:

```powershell
pip install -r requirements.txt
```

Это установит все необходимые библиотеки. Может занять 1-2 минуты.

**Проверка:** Когда завершится, введи:
```powershell
pip list
```
Должны быть видны `PyQt5`, `httpx`, `qasync` и другие пакеты

### Шаг 7: Запуск приложения

Введи:

```powershell
python main.py
```

**Должно произойти:**
- Откроется окно приложения Madness RPG Desktop Client
- Слева будут полосы HP и Energy
- Справа поле для логов
- Внизу кнопки `START` и `STOP`

### Шаг 8: Вход в приложение

1. В поле "Telegram auth" вставь свой `initData` (получи его из Telegram бота)
2. Нажми кнопку `START`
3. Приложение начнёт искать рейды и подключаться к ним

## Быстрые команды (если всё установлено)

Каждый раз для запуска:

```powershell
cd Desktop\madnessbot
.\venv\Scripts\Activate.ps1
python main.py
```

## Решение проблем

### "source: command not found"
Это Linux-команда. На Windows используй: `.\venv\Scripts\Activate.ps1`

### "Невозможно загрузить файл Activate.ps1"
Выполни один раз:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "python: command not found"
Python не установлен или не добавлен в PATH. Переустанови Python, выбери опцию "Add Python to PATH".

### "git: command not found"
Git не установлен. Скачай и установи с https://git-scm.com/

### Приложение не запускается
Убедись, что:
- Python 3.11+
- Все зависимости установлены: `pip list | findstr PyQt5`
- Виртуальное окружение активировано (видно `(venv)` в строке)

## Linux/macOS

Для Linux/macOS команды похожи, но используй:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Запуск без GUI (для проверки)

Если нет графического окружения:

```powershell
python main.py --headless --init-data "<your telegram initData>"
```

