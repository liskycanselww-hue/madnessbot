# madnessbot

Madness RPG desktop client на Python + PyQt5.

## Установка

### Linux/macOS

1. Убедитесь, что установлен Python 3.11+
2. Клонируйте репозиторий:

```bash
git clone https://github.com/liskycanselww-hue/madnessbot
cd madnessbot
```

3. Создайте виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate  # На macOS: source venv/bin/activate
```

4. Установите зависимости:

```bash
pip install -r requirements.txt
```

### Windows

1. Убедитесь, что установлены:
   - Python 3.11+ (скачайте с https://www.python.org/downloads/)
   - Git (скачайте с https://git-scm.com/)

2. Откройте PowerShell как администратор и клонируйте репозиторий:

```powershell
git clone https://github.com/liskycanselww-hue/madnessbot
cd madnessbot
```

3. Создайте виртуальное окружение:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

4. Установите зависимости:

```powershell
pip install -r requirements.txt
```

## Запуск

### На компьютере

```bash
python main.py
```

Откроется окно приложения. Вставьте свой Telegram `initData` в поле логина и нажмите `START`.

### Headless режим (без GUI)

```bash
python main.py --headless --init-data "<your telegram initData>"
```

## Описание

Проект содержит:

- `main.py` — запуск Qt + qasync
- `gui.py` — полноэкранный интерфейс с логами, прогресс-барами и настройками
- `api.py` — асинхронный клиент для Madness RPG backend
- `battle_manager.py` — цикл рейдов, атаки, проверка HP и получение наград
- `config.py` — базовые настройки и URL API

## Как работать

1. Вставьте Telegram `initData` в поле логина
2. Нажмите `START`
3. Бот будет искать рейды, подключаться, атаковать и получать награды
4. `STOP` остановит цикл, но не выйдет из Qt-приложения
