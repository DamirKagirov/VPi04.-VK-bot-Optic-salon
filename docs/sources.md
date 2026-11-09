# Источники, даты проверки и ограничения

**Дата проверки:** 10.11.2026.
**Регион сравнения цен:** Москва и Московская область.
**Принцип:** в документ попадают только те источники, которые были реально открыты. Если страница
недоступна, это фиксируется, а не маскируется пересказом по памяти.

## 1. Локальные документы проекта

| Источник | Что используется | Статус |
|---|---|---|
| `prompt.md` | требования к боту, состав документации, критерии §8 | прочитан 10.11.2026 |
| `.gitignore` | проверка исключения `.env`, `.env.*` | прочитан 10.11.2026 |
| `.env` | только факт существования; содержимое не читалось | не раскрывается |

## 2. Документация VKBottle

Все страницы открыты 10.11.2026. Используется раздел `ru/latest`; точная версия страницы
не зафиксирована, поэтому технические детали, влияющие на реализацию, дополнительно сверены
с исходным кодом тега `v4.11.0` (раздел 4).

| № | URL | Что проверено |
|---|---|---|
| VK-DOC-01 | https://vkbottle.readthedocs.io/ru/latest/ | структура документации, разделы high-level / low-level / tools |
| VK-DOC-02 | https://vkbottle.readthedocs.io/ru/latest/tutorial/ | порядок изучения, состав туториала |
| VK-DOC-03 | https://vkbottle.readthedocs.io/ru/latest/tutorial/first-bot/ | создание `Bot`, три декоратора сообщений, `message.answer`, `run_forever`, зависимость от настроек LongPoll |
| VK-DOC-04 | https://vkbottle.readthedocs.io/ru/latest/tutorial/rules/ | встроенные правила работают с `Message`, `ABCRule.check`, шорткаты правил |
| VK-DOC-05 | https://vkbottle.readthedocs.io/ru/latest/tutorial/keyboards-attachments/ | `Keyboard`, `add`, `row`, `get_json`, отправка клавиатуры, вложения, шаблоны |
| VK-DOC-06 | https://vkbottle.readthedocs.io/ru/latest/tutorial/code-separation/ | структура проекта, отдельные лейблеры, `labeler.load`, `Bot(...)`, `state_dispenser` |
| VK-DOC-07 | https://vkbottle.readthedocs.io/ru/latest/tutorial/error-handling/ | `VKAPIError`, коды ошибок, `ErrorHandler`, `register_error_handler` |
| VK-DOC-08 | https://vkbottle.readthedocs.io/ru/latest/tutorial/faq/ | asyncio, блокирующие вызовы, токены, `API.request`, ошибки валидации |
| VK-DOC-09 | https://vkbottle.readthedocs.io/ru/latest/high-level/bot/ | атрибуты `Bot`, `run_polling`, `run_forever`, `process_event` |
| VK-DOC-10 | https://vkbottle.readthedocs.io/ru/latest/high-level/bot/labeler/ | `BotLabeler`, `load`, разбиение обработчиков по файлам |
| VK-DOC-11 | https://vkbottle.readthedocs.io/ru/latest/high-level/handling/rules/ | список шорткатов, включая `payload`, `payload_contains`, `state`, `func` |
| VK-DOC-12 | https://vkbottle.readthedocs.io/ru/latest/high-level/handling/state-dispenser/ | `get` / `set` / `delete`, `StateRule`, `BaseStateGroup` |
| VK-DOC-13 | https://vkbottle.readthedocs.io/ru/latest/tools/keyboard/ | `Keyboard`, `KeyboardButtonColor`, `Text`, `get_json`, `EMPTY_KEYBOARD` |
| VK-DOC-14 | https://vkbottle.readthedocs.io/ru/latest/low-level/polling/ | `Polling`, `get_server`, `get_event`, `listen`, `wait`, `rps_delay` |

## 3. Метаданные пакетов

| Источник | URL | Что проверено |
|---|---|---|
| PYPI-VK | https://pypi.org/pypi/vkbottle/4.11.0/json | версия 4.11.0, публикация 26.08.2026, `Requires-Python: >=3.10,<4.0` |
| PYPI-DOTENV | https://pypi.org/pypi/python-dotenv/1.2.4/json | версия 1.2.4, публикация 01.10.2026, `Requires-Python: >=3.10` |

Страницы пакетов для человека:

- https://pypi.org/project/vkbottle/4.11.0/
- https://pypi.org/project/python-dotenv/1.2.4/

## 4. Исходный код VKBottle v4.11.0

Использован для проверки поведения, которое документация описывает неполно или устаревше.

| № | URL | Что проверено |
|---|---|---|
| VK-SRC-01 | https://github.com/vkbottle/vkbottle/blob/v4.11.0/vkbottle/framework/bot/bot.py | параметр `skip_old_events` (по умолчанию `True`), создание `BotPolling`, `process_event` |
| VK-SRC-02 | https://github.com/vkbottle/vkbottle/blob/v4.11.0/vkbottle/framework/base.py | `run()`, `run_polling()`, `run_forever()` помечен `@deprecated` |
| VK-SRC-03 | https://github.com/vkbottle/vkbottle/blob/v4.11.0/vkbottle/polling/bot_polling.py | `wait = min(wait or 25, 90)`, путь `.vkbottle/bot-polling/{group_id}.json`, восстановление `ts` |
| VK-SRC-04 | https://github.com/vkbottle/vkbottle/blob/v4.11.0/vkbottle/polling/base.py | обработка `failed` (1–4), повторные попытки при сетевых ошибках и `VKAPIError[10]` |
| VK-SRC-05 | https://github.com/vkbottle/vkbottle/blob/v4.11.0/vkbottle/dispatch/rules/base.py | `PayloadRule` сравнивает payload целиком, `PayloadContainsRule` — частично |
| VK-SRC-06 | https://github.com/vkbottle/vkbottle/blob/v4.11.0/vkbottle/api/api.py | `API.__repr__` выводит генератор токена, а не сам токен |
| VK-SRC-07 | https://github.com/vkbottle/vkbottle/blob/v4.11.0/vkbottle/api/token_generator/abc.py | `__repr__` генератора не содержит значения токена |
| VK-SRC-08 | https://github.com/vkbottle/vkbottle/blob/v4.11.0/pyproject.toml | `requires-python = ">=3.10,<4.0"`, classifiers включают 3.14 |

## 5. Документация ВКонтакте

**Ограничение доступа `[ФАКТ]`:** 10.11.2026 живые страницы `dev.vk.com` не отдавали полезный
текст — открывалась SPA-оболочка либо сообщение о недоступности части функций. Поэтому
использованы архивные копии Wayback Machine. Это не то же самое, что актуальная документация:
детали могли измениться после даты снимка. Перед запуском настройки нужно сверить с интерфейсом
сообщества.

| № | Архивный URL | Дата снимка | Что проверено |
|---|---|---|---|
| VK-API-01 | https://web.archive.org/web/20241216144451/https://dev.vk.com/ru/api/bots/getting-started | 16.12.2024 | создание бота сообщества, токен, включение LongPoll |
| VK-API-02 | https://web.archive.org/web/20250114040459/https://dev.vk.com/ru/api/bots-long-poll/getting-started | 14.01.2025 | механика LongPoll, `getLongPollServer`, `ts`, `wait` |
| VK-API-03 | https://web.archive.org/web/20250119200407/https://dev.vk.com/ru/api/callback/getting-started | 19.01.2025 | требования Callback API — используются только для сравнения |
| VK-API-04 | https://web.archive.org/web/20241209165637/https://dev.vk.com/ru/api/bots/development/keyboard | 09.12.2024 | ограничения клавиатуры: текст кнопки ≤ 40 символов, payload ≤ 255 символов |
| VK-API-05 | https://web.archive.org/web/20250114040459/https://dev.vk.com/ru/api/community-events/json-schema | 14.01.2025 | типы событий: `message_new`, `message_reply`, `message_event` |

## 6. Прайсы сопоставимых салонов

Цены ниже — **не прайс «Ясных очей»**. Это открытые данные других организаций, использованные
как ориентир среднего ценового сегмента.

| № | URL | Что проверено | Ограничения |
|---|---|---|---|
| PRICE-01 | https://optikapetrov.ru/services | диагностика 2 500 / 3 000 ₽; подбор МКЛ 3 000 ₽; сварка 2 000 ₽; винты 150 / 400 ₽; носоупоры 200 / 300 ₽; сборка 1 300 / 1 600 ₽; переустановка линз 700 ₽; переточка 1 200 ₽ | Москва, Митино и Путилково; цены могут меняться; часть услуг зависит от материалов |
| PRICE-02 | https://optimistoptica.ru/tovary-i-uslugi/uslugi/kompyuternaya-diagnostika/ | обследование 2 500 ₽, полный осмотр 3 500 ₽ | сеть работает в нескольких регионах; регион конкретного салона нужно уточнять |
| PRICE-03 | https://optimistoptica.ru/tovary-i-uslugi/uslugi/podbor-kontaktnykh-linz/ | подбор линз 2 000 ₽ взрослым, 2 500 ₽ детям | цена зависит от сложности линз и возраста |
| PRICE-04 | https://optimistoptica.ru/tovary-i-uslugi/uslugi/ultrazvukovaya-chistka-ochkov/ | чистка 200 ₽ для очков из других компаний; для своих — бесплатно; только металлические оправы | ограничение по материалу оправы; акция «бесплатно» может измениться |
| PRICE-05 | https://remont-ochkov.com/ | сварка от 1 500 ₽ за шов; носоупоры от 500 ₽; винты от 300 ₽; чистка от 1 000 ₽; выправка от 500 ₽; леска от 500 ₽ | мастерская ремонта, а не салон оптики; цены «ориентировочные», не публичная оферта |

## 7. Ограничения доступа и достоверности

1. **`[ФАКТ]` Живая документация VK недоступна.** Использованы снимки декабря 2024 — января 2025.
   Настройки сообщества и состав событий могли измениться.
2. **`[ФАКТ]` Документация VKBottle не привязана к версии.** Страницы `latest` могут опережать
   или отставать от установленного пакета. Поэтому ключевые утверждения сверены с кодом `v4.11.0`.
3. **`[ФАКТ]` Цены конкурентов динамичны.** Указана дата проверки; перед публикацией нужна
   повторная сверка и утверждение владельцем.
4. **`[ФАКТ]` Данные «Ясных очей» отсутствуют.** Не проверены: лицензия, медицинский кабинет,
   оборудование, квалификация специалистов, фактический перечень услуг, адреса, режим работы,
   ссылка на сообщество, процесс работы менеджера.
5. **`[ФАКТ]` Совместимость с Python 3.15 не проверялась.** В проекте есть `.venv` с Python 3.15.2,
   но `vkbottle` и `python-dotenv` в нём не установлены; для реализации планируется 3.12/3.13.

## 8. Что не считается проверенным

- Медицинские возможности и лицензии «Ясных очей».
- Наличие конкретного оборудования и специалистов.
- Действующие цены «Ясных очей».
- Возможность оказывать услуги из карточек в каждом салоне.
- Автоматическая передача диалога менеджеру.
- Поведение VK LongPoll на актуальной версии API в 2026 году.
- Работоспособность бота на Python 3.15.

## 9. Правила цитирования

- Примеры кода VKBottle в [`vkbottle-notes.md`](vkbottle-notes.md) приведены с точным URL,
  назначением, версией и ограничениями.
- Собственные примеры и псевдокод помечены как проектные и не выдаются за цитаты.
- Секреты, токены и содержимое `.env` в документацию не добавляются.
- Если источник недоступен, это указано явно; ссылки не реконструируются по памяти.
