# Конспект документации VKBottle

**Библиотека:** `vkbottle==4.11.0` · **Python:** `>=3.10,<4.0` · **Документация:**
https://vkbottle.readthedocs.io/ru/latest/ (открыта 10.11.2026).

Документация не привязана к конкретной версии пакета, поэтому поведение, важное для проекта,
дополнительно сверено с исходным кодом тега `v4.11.0`. Все расхождения отмечены в разделе 12.

> **Оформление примеров.** Примеры ниже взяты со страниц документации. В веб-выдаче код
> отображается без переносов строк, поэтому переносы и отступы восстановлены для читаемости.
> Лексемы, имена, аргументы и порядок строк не изменялись. Собственные примеры проекта
> находятся в [`architecture.md`](architecture.md) и [`dialogues.md`](dialogues.md) и помечены
> как проектные.

## 1. Версии, установка, совместимость

`[ФАКТ]` По данным PyPI:

- `vkbottle` 4.11.0 опубликован 26.08.2026, требует Python `>=3.10,<4.0`;
- `python-dotenv` 1.2.4 опубликован 01.10.2026, требует Python `>=3.10`;
- в `pyproject.toml` VKBottle заявлены classifiers для Python 3.10–3.14.

`[РЕШЕНИЕ]` Для проекта выбираем **Python 3.12 или 3.13**, а не 3.15: 3.15 формально попадает
в `>=3.10,<4.0`, но не заявлен в classifiers и не проверялся с зависимостями библиотеки.

`[РЕШЕНИЕ]` Зафиксированные версии (установлены в `.venv313` на Python 3.13.7):

```text
vkbottle==4.11.0
python-dotenv==1.2.4
```

Команда установки выполнена 10.11.2026 в `.venv313` на Python 3.13.7:

```bash
python -m pip install "vkbottle==4.11.0" "python-dotenv==1.2.4"
```

## 2. Создание бота и запуск

`[ФАКТ]` `Bot` предназначен для сообществ. Инициализация возможна токеном или готовым `API`.
Для сообщений доступны три декоратора: `.message` (личные и беседы), `.private_message`,
`.chat_message`. `message.answer` — шорткат отправки сообщения, не требующий `peer_id`
и `random_id`.

### Пример 2.1. Минимальный бот с ответом на текст

```python
from vkbottle.bot import Bot, Message

bot = Bot(token="token")

@bot.on.message(text="Привет")
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    await message.answer("Привет, {}".format(users_info[0].first_name))

bot.run_forever()
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/tutorial/first-bot/
- **Назначение:** показывает инициализацию `Bot`, регистрацию обработчика, обращение к API
  и ответ пользователю.
- **Версия:** страница `latest` на 10.11.2026; библиотека 4.11.0.
- **Ограничения:** пример использует `run_forever()`. В 4.11.0 этот метод помечен
  `@deprecated` и вызывает `run()`; для нового кода рекомендуется `bot.run()` или
  `await bot.run_polling()`. Пример не показывает обработку ошибок и завершение процесса.
  Токен в примере — заглушка; реальный токен в документацию не добавляется.

`[ФАКТ]` В конце страницы отдельно сказано: если код не работает, нужно проверить галочки
событий в настройках LongPoll (в примере — новые сообщения) и версию LongPoll.

### Пример 2.2. Запуск через API-объект

```python
# Инициализация токеном
bot = Bot(token="token")

# (или) Инициализация с апи
bot = Bot(api=api)
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/tutorial/first-bot/
- **Назначение:** два способа передать зависимости в `Bot`.
- **Ограничения:** при передаче `api` токен должен быть уже настроен в этом объекте.

## 3. Правила обработчиков

`[ФАКТ]` Встроенные правила работают только с объектами `Message` и `MessageEvent` из
`vkbottle.bot`. Для сырых событий нужно писать собственную реализацию. Правило — класс,
реализующий асинхронный `check`, который возвращает `False`, `True` или словарь аргументов.

### Пример 3.1. Правило, импортированное напрямую

```python
from vkbottle.dispatch.rules.base import CommandRule

@bot.on.message(CommandRule("say", ["!", "/"], 1))
async def say_handler(message: Message, args: tuple[str]):
    await message.answer(f"<<{args[0]}>>")
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/tutorial/rules/
- **Назначение:** команда с префиксом и одним аргументом.
- **Ограничения:** пример не показывает регистрацию правила в лейблере и не описывает
  конфликты с другими обработчиками.

### Пример 3.2. Шорткат правила

```python
@bot.on.message(command=("say", 1))
async def say_handler(message: Message, args: tuple[str]):
    await message.answer(f"<<{args[0]}>>")
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/tutorial/rules/
- **Назначение:** тот же обработчик через шорткат.
- **Ограничения:** шорткаты перечислены на отдельной странице; не все правила имеют шорткат.

`[ФАКТ]` Список шорткатов включает `text`, `payload`, `payload_contains`, `payload_map`,
`state`, `state_group`, `command`, `func`, `regexp` и другие:
https://vkbottle.readthedocs.io/ru/latest/high-level/handling/rules/

`[РЕШЕНИЕ]` В проекте используются:

- `payload_contains={"v": 1, "a": "..."}` — для навигации и карточек;
- `text=[...]` — для явных текстовых команд («меню», «начать»);
- обработчик без правил, зарегистрированный последним, — для неизвестного ввода.

`[ПРЕДПОЛОЖЕНИЕ]` Порядок проверки обработчиков соответствует порядку регистрации; это нужно
подтвердить тестом при реализации, чтобы fallback не перехватывал валидные кнопки.

## 4. Клавиатуры

`[ФАКТ]` `Keyboard` принимает `one_time` и `inline`. Методы: `add(action, color)`, `row()`,
`get_json()`. Первый ряд создаётся автоматически. Для удаления клавиатуры используется
`EMPTY_KEYBOARD`.

### Пример 4.1. Создание клавиатуры

```python
from vkbottle import Keyboard, KeyboardButtonColor, Text

keyboard = Keyboard(one_time=True, inline=False)
# О параметрах one_time и inline вы можете прочитать в документации к апи вконтакте
keyboard.add(Text("Кнопка 1"), color=KeyboardButtonColor.POSITIVE)
# Первая строка (ряд) добавляется автоматически
keyboard.row()  # Переходим на следующую строку
keyboard.add(Text("Кнопка 2"))
keyboard.add(Text("Кнопка 3", payload={"command": 3}))
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/tools/keyboard/
- **Назначение:** последовательное добавление кнопок и рядов, payload у текстовой кнопки.
- **Ограничения:** пример не отправляет клавиатуру; для отправки нужен `get_json()`.
  Значения `one_time` и `inline` регулируют поведение у клиента, а не логику бота.

### Пример 4.2. Билдер и отправка

```python
from vkbottle import Keyboard, KeyboardButtonColor, Text

# ...
keyboard = (
    Keyboard(one_time=True, inline=False)
    .add(Text("Кнопка 1"), color=KeyboardButtonColor.POSITIVE)
    .row()
    .add(Text("Кнопка 2"))
    .add(Text("Кнопка 3", payload={"command": 3}))
).get_json()

await message.answer(
    message="Смотри сколько кнопок!!",
    keyboard=keyboard
)
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/tools/keyboard/
- **Назначение:** цепочка вызовов и отправка готового JSON.
- **Ограничения:** `message` и `await` в примере предполагают, что код находится внутри
  асинхронного обработчика.

### Пример 4.3. Отправка заранее созданной клавиатуры

```python
keyboard = ...  # see examples above

@bot.on.message()
async def send_keyboard(message):
    await message.answer("Here is your keyboard!", keyboard=keyboard)
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/tutorial/keyboards-attachments/
- **Назначение:** переиспользование статической клавиатуры.
- **Ограничения:** в примере не показано, что именно лежит в `keyboard`; на странице
  `tools/keyboard` для отправки используется результат `get_json()`.

`[ФАКТ]` Ограничения ВКонтакте (архивная копия документации, снимок 09.12.2024): текст кнопки —
до 40 символов, payload — до 255 символов.

`[РЕШЕНИЕ]` Все подписи кнопок проекта короче 40 символов; payload — компактный JSON
(`{"v":1,"a":"svc","id":"..."}`), укладывающийся в 255 символов с запасом.

## 5. `payload` и навигация

`[ФАКТ]` На странице правил перечислены `payload`, `payload_contains`, `payload_map`,
но примера использования `payload` там нет. Поэтому поведение проверено по исходному коду:
`PayloadRule` сравнивает payload целиком, `PayloadContainsRule` — только указанные ключи.

`[ФАКТ]` В коде `v4.11.0` `PayloadContainsRule.check` возвращает `False`, если `event.payload`
равен `None`; иначе сравнивает словарь частично.

`[ФАКТ]` У сообщения есть метод `get_payload_json()`, который разбирает строку payload в объект.

`[РЕШЕНИЕ]` Схема payload:

```json
{"v": 1, "a": "menu"}
{"v": 1, "a": "list"}
{"v": 1, "a": "price"}
{"v": 1, "a": "mgr"}
{"v": 1, "a": "mgr_ack"}
{"v": 1, "a": "svc", "id": "vision_exam_glasses"}
```

- `v` — версия схемы, позволяет отличить старые кнопки;
- `a` — действие;
- `id` — идентификатор услуги только для `a="svc"`.

`[ПРЕДПОЛОЖЕНИЕ]` Текстовая кнопка с payload приходит как обычное `message_new` с заполненным
payload. Это соответствует схеме событий ВКонтакте, но должно быть проверено на тестовом
сообществе: для callback-кнопок используется отдельное событие `message_event`.

`[РЕШЕНИЕ]` Не используем callback-кнопки в MVP: текстовые кнопки видны в истории переписки,
проще отлаживаются и не требуют отдельного обработчика `message_event`.

## 6. Отправка сообщений и обновление клавиатуры

`[ФАКТ]` `message.answer` принимает те же аргументы, что `messages.send`, кроме `peer_id`
и `random_id`. Клавиатура передаётся параметром `keyboard`.

`[РЕШЕНИЕ]` Каждый экран — новое сообщение с новой клавиатурой. «Обновления» одной клавиатуры
на месте нет: старые сообщения сохраняют старые кнопки. Поэтому обработчики обязаны быть
идемпотентными и не зависеть от текущего экрана.

`[ФАКТ]` Клавиатуру можно убрать, отправив `EMPTY_KEYBOARD`
(https://vkbottle.readthedocs.io/ru/latest/tools/keyboard/).

## 7. Состояние диалога

`[ФАКТ]` `StateDispenser` имеет методы `get`, `set`, `delete`. Состояние ловится правилом
`StateRule` (шорткат `state`). `set` может принимать дополнительные именованные аргументы,
доступные затем в `message.state_peer.payload`.

### Пример 7.1. Состояния и переход

```python
from vkbottle import BaseStateGroup
from vkbottle.bot import Message, Bot

bot = Bot("t")

class SuperStates(BaseStateGroup):
    AWKWARD_STATE = "awkward"
    CONFIDENT_STATE = "confident"
    TERRIFYING_STATE = "terrifying"

@bot.on.message(state=SuperStates.AWKWARD_STATE)  # StateRule(SuperStates.AWKWARD_STATE)
async def awkward_handler(message: Message):
    await message.answer("oi awkward")

@bot.on.message(lev="/die")
async def die_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, SuperStates.AWKWARD_STATE)
    return "ok"

bot.run_forever()
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/high-level/handling/state-dispenser/
- **Назначение:** объявление группы состояний, установка состояния и обработчик под состояние.
- **Ограничения:** пример использует `run_forever()` (в 4.11.0 deprecated).

`[ФАКТ]` `BuiltinStateDispenser` хранит состояния в обычном словаре в памяти процесса
(`vkbottle/dispatch/dispenser/builtin.py`, v4.11.0). После перезапуска состояния теряются.

`[РЕШЕНИЕ]` Для навигации состояние не нужно. Единственное состояние — «тихий режим» после
перехода к менеджеру; оно хранится отдельно в `runtime/state.json`, потому что должно переживать
перезапуск. `BuiltinStateDispenser` не используем.

## 8. Обработка ошибок

`[ФАКТ]` `VKAPIError` — подтип `CodeException`; имеет поля `code` и `error_msg`. Поддерживается
`except VKAPIError` и `except VKAPIError[code]`. `ErrorHandler` умеет регистрировать обработчики
для типов ошибок и для конкретных кодов.

### Пример 8.1. Обработка ошибки API

```python
try:
    await api.messages.send(peer_id=1, message="привет!", random_id=0)
except VKAPIError[902] as e:
    print("не могу отправить сообщение из-за настроек приватности")
except VKAPIError as e:
    print("не могу отправить:", e.error_msg)
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/tutorial/error-handling/
- **Назначение:** комбинация обработки конкретного кода и общего случая.
- **Ограничения:** пример печатает ошибку в stdout; для бота нужен логгер и запрет вывода
  секретов. Код 902 приведён как пример, а не как ожидаемая ошибка проекта.

### Пример 8.2. Глобальные обработчики ошибок

```python
from vkbottle import Bot, VKAPIError

bot = Bot("token")

@bot.error_handler.register_error_handler(RuntimeError)
async def runtime_error_handler(e: RuntimeError):
    print("возникла ошибка runtime", e)

@bot.error_handler.register_error_handler(VKAPIError[902])
async def unable_to_write_handler(e: VKAPIError):
    print("человек не разрешил отправлять сообщения", e)
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/tutorial/error-handling/
- **Назначение:** регистрация обработчиков для типа и для кода ошибки.
- **Ограничения:** `print` не заменяет логирование; пример не показывает, что делать после
  ошибки и как не потерять событие.

`[ФАКТ]` LongPoll-цикл сам обрабатывает коды `failed` 1–4: обновляет `ts`, перезапрашивает
сервер, сбрасывает версию. При сетевых ошибках, таймауте и `VKAPIError[10]` делает повтор
с задержкой до 6 секунд (`polling/base.py`, v4.11.0).

`[РЕШЕНИЕ]` Регистрируем обработчики для `VKAPIError` (общий) и для кодов 6, 9, 10; пишем
в лог код и метод, но не токен и не текст сообщения. Ошибка отправки не должна завершать
процесс: следующее действие пользователя создаёт новый запрос.

## 9. Разделение кода и лейблеры

`[ФАКТ]` Обработчики можно разносить по файлам через отдельные `BotLabeler` и `labeler.load(...)`.

### Пример 9.1. Конфигурация с общими объектами

```python
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

api = API("token")
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/tutorial/code-separation/
- **Назначение:** вынести API, лейблер и диспенсер в отдельный модуль.
- **Ограничения:** пример не читает токен из окружения; в проекте токен берётся только из `.env`.

### Пример 9.2. Сборка бота

```python
from vkbottle import Bot
from config import api, state_dispenser, labeler
from handlers import chat_labeler, admin_labeler

labeler.load(chat_labeler)
labeler.load(admin_labeler)

bot = Bot(
    api=api,
    labeler=labeler,
    state_dispenser=state_dispenser,
)

bot.run_forever()
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/tutorial/code-separation/
- **Назначение:** загрузка лейблеров и передача зависимостей в `Bot`.
- **Ограничения:** `from vkbottle import Bot` — вариант импорта из примера; в остальной
  документации используется `from vkbottle.bot import Bot`. `run_forever()` deprecated.
  `state_dispenser` в проекте не нужен.

### Пример 9.3. Лейблер и обработчик в отдельном файле

```python
from vkbottle.bot import BotLabeler, Message

bl = BotLabeler()

@bl.message(text=["привет", "хай", "здравствуй"])
async def greeting(message: Message):
    await message.answer("Привет, друг")
```

- **Источник:** https://vkbottle.readthedocs.io/ru/latest/high-level/bot/labeler/
- **Назначение:** портабельный лейблер с одним обработчиком.
- **Ограничения:** пример не показывает загрузку лейблера в бота; она делается через
  `bot.labeler.load(bl)`.

## 10. Логирование

`[ФАКТ]` Библиотека использует собственный логгер `vkbottle.modules.logger` и пишет служебные
сообщения о запуске polling, получении событий и сетевых ошибках.

`[РЕШЕНИЕ]` Приложение настраивает стандартный `logging` и не полагается на настройки
библиотеки по умолчанию. Обязательные требования:

- не логировать `VK_BOT_TOKEN` и заголовки запросов;
- не логировать текст сообщений пользователей по умолчанию;
- логировать `peer_id` и действие (`a`, `id`) для отладки навигации;
- фильтровать строки, похожие на токен, в сообщениях исключений.

`[ПРЕДПОЛОЖЕНИЕ]` `repr` API не раскрывает токен: в `api.py` и `token_generator/abc.py` v4.11.0
`__repr__` выводит только класс генератора. Это проверено по коду, но требует контрольного
теста логов при реализации.

## 11. LongPoll на уровне библиотеки

`[ФАКТ]` `BotPolling`:

- `wait = min(wait or 25, 90)` — по умолчанию 25 секунд, максимум 90;
- `skip_old_events=True` по умолчанию;
- при `skip_old_events=False` сохраняет `ts` в `.vkbottle/bot-polling/{group_id}.json`;
- получает `group_id` через `groups.getById`, если он не задан;
- получает сервер через `groups.getLongPollServer`.

`[РЕШЕНИЕ]` Используем `skip_old_events=False`, чтобы после перезапуска не терять события.
Риск повторной обработки последнего события принимаем: навигация идемпотентна, повторная
карточка или меню не ломают сценарий.

`[ФАКТ]` Подробная механика и настройки сообщества — в [`longpoll.md`](longpoll.md).

## 12. Расхождения документации и исходного кода

| № | Документация | Код v4.11.0 | Как поступаем |
|---|---|---|---|
| 1 | Примеры используют `bot.run_forever()` | `run_forever()` помечен `@deprecated`, вызывает `run()` | В проекте `bot.run()` |
| 2 | `payload` указан в списке правил, примера нет | `PayloadRule` — точное совпадение, `PayloadContainsRule` — частичное | Используем `payload_contains`, поведение покрываем тестом |
| 3 | `Bot` импортируют то из `vkbottle`, то из `vkbottle.bot` | Оба варианта присутствуют в примерах | Используем `from vkbottle.bot import Bot` |
| 4 | Про состояние не сказано, где оно хранится | `BuiltinStateDispenser` — словарь в памяти | Не используем для данных, переживающих перезапуск |
| 5 | Про `skip_old_events` на страницах туториала не сказано | Параметр есть, по умолчанию `True` | Явно задаём `False` и документируем риск |
| 6 | Не описано поведение при `failed` LongPoll | Коды 1–4 обрабатываются автоматически | Полагаемся на библиотеку, логируем сбои |
| 7 | Не описан формат ts-файла | `.vkbottle/bot-polling/{group_id}.json` | Добавляем `.vkbottle/` в `.gitignore` |

## 13. Что проверить на этапе реализации

- [ ] Текстовая кнопка с payload приходит как `message_new`, а не `message_event`.
- [ ] `payload_contains` не срабатывает на payload без нужных ключей.
- [ ] Fallback-обработчик не перехватывает валидные кнопки.
- [ ] Поведение `text`-правила с кириллицей и регистром.
- [ ] Ограничения клавиатуры в актуальном клиенте ВКонтакте.
- [ ] Отсутствие токена в логах при исключении HTTP-запроса.
- [ ] Повтор события после аварийного завершения при `skip_old_events=False`.
- [ ] Работа на Python 3.12/3.13 с зафиксированными версиями.
