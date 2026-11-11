"""Тексты экранов бота и форматирование цен."""

from __future__ import annotations

from .catalog import Catalog, Service

DISCLAIMER = "Цены ориентировочные, не являются публичной офертой."

GREETING = (
    "Здравствуйте! Это бот салонов оптики «Ясные очи».\n\n"
    "Здесь можно посмотреть услуги и ориентировочные цены, а также связаться с менеджером.\n\n"
    "Выберите раздел:"
)

MENU = "Главное меню. Выберите раздел:"

QUIET_EXIT = "Бот снова на связи.\n\nГлавное меню. Выберите раздел:"

SERVICE_LIST = (
    "Услуги салонов «Ясные очи»\n\n"
    "Выберите услугу, чтобы посмотреть описание, состав и цену. "
    "Цены ориентировочные — уточняйте у менеджера."
)

UNKNOWN = (
    "Не понял сообщение.\n\n"
    "Пользуйтесь кнопками ниже:\n"
    "• «Услуги» — список услуг и карточек;\n"
    "• «Прайс-лист» — все цены;\n"
    "• «Связаться с менеджером» — переписка с человеком."
)

STALE_BUTTON = "Эта кнопка устарела: такого раздела больше нет.\n\nОткрываю актуальное меню."

SERVICE_NOT_FOUND = (
    "Услуга не найдена: возможно, она больше не публикуется.\n\n"
    "Открываю список актуальных услуг."
)

ACTION_ERROR = (
    "Не получилось выполнить действие. Попробуйте ещё раз или вернитесь в главное меню."
)


def format_price(service: Service) -> str:
    """Единое форматирование цены для карточки и прайс-листа."""

    amount = f"{service.price:,}".replace(",", " ")
    if service.price_type == "from":
        return f"от {amount} ₽"
    return f"{amount} ₽"


def price_with_unit(service: Service) -> str:
    return f"{format_price(service)} {service.price_unit}"


def service_card(service: Service) -> str:
    includes = "\n".join(f"• {item};" for item in service.includes)
    caveats = "\n".join(f"• {item};" for item in service.caveats)
    return (
        f"{service.name}\n\n"
        f"{price_with_unit(service)}\n\n"
        f"{service.full}\n\n"
        f"Что входит:\n{includes}\n\n"
        f"Важно:\n{caveats}\n\n"
        f"{DISCLAIMER}"
    )


def price_list(catalog: Catalog) -> str:
    lines = "\n".join(
        f"• {service.name} — {price_with_unit(service)}" for service in catalog.ordered()
    )
    return (
        "Прайс-лист\n\n"
        f"{catalog.price_note}\n\n"
        f"{lines}\n\n"
        "Полные описания — в разделе «Услуги». "
        "Стоимость материалов и изделий уточняйте у менеджера."
    )


def manager_screen(manager_contact_url: str) -> str:
    return (
        "Связь с менеджером\n\n"
        "Напишите менеджеру в диалоге сообщества:\n"
        f"{manager_contact_url}\n\n"
        "Менеджер отвечает с 10:00 до 19:00 МСК в рабочие дни. Если вы написали вне "
        "этого времени, сообщение сохранится, и менеджер ответит в рабочее время.\n\n"
        "Отвечает человек, а не бот. Если менеджер сейчас недоступен, сообщение останется "
        "в диалоге, и ответ придёт позже.\n\n"
        "После того как напишете, нажмите «Я написал менеджеру». Бот перестанет отвечать "
        "на обычные сообщения, чтобы не мешать разговору."
    )


def quiet_ack(ttl_hours: int) -> str:
    return (
        "Хорошо. Я не буду отвечать на обычные сообщения, пока вы общаетесь с менеджером.\n\n"
        "Вернуться в меню можно кнопкой «В главное меню». "
        f"Через {ttl_hours} часов бот снова начнёт отвечать автоматически."
    )
