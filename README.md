# VK Tarot Bot Fixed

Минимальный бот для VK Callback API.

## Что делает

- Подтверждает Callback API VK.
- Ловит новые комментарии к постам.
- Ищет ключевые слова.
- Выбирает случайное послание из JSON.
- Отвечает под комментарием.
- Отправляет такое же послание в ЛС, если VK разрешает.

## Render Environment Variables

Добавить в Render:

- VK_TOKEN
- CONFIRMATION_CODE
- SECRET_KEY

## Callback URL для VK

https://YOUR-RENDER-URL.onrender.com/callback

## Проверка

Открой:
https://YOUR-RENDER-URL.onrender.com/health
