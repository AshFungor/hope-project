# Hope Project

Проект для лагеря Надежда

## Установка

```
alias python=python3
python -m venv ./venv --symlinks --clear
venv/bin/pip -V && venv/bin/pip install -r requirements.txt
```

## Запуск

Все бинари должны лежать в **venv/bin**! И запускать их надо оттуда

```
venv/bin/flask run
```

## Таски в CI

Пока доступен один раннер и простая таска