# madnessbot

Madness RPG desktop client на Python + PyQt5.

## Установка

1. Убедитесь, что установлен Python 3.11+
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

### Headless режим для проверки

Если в среде нет графического дисплея, можно запустить тестовую проверку без GUI:

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
