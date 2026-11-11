import io
import logging

from app.__main__ import RedactingFormatter, setup_logging

TOKEN = "vk1.aVerySecretCommunityToken"


def make_logger(stream: io.StringIO, token: str = TOKEN) -> logging.Logger:
    logger = logging.getLogger(f"tests.redaction.{id(stream)}")
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(RedactingFormatter("%(levelname)s %(message)s", token))
    logger.addHandler(handler)
    return logger


def test_redacts_token_in_message_and_args():
    stream = io.StringIO()
    logger = make_logger(stream)

    logger.info("token=%s", TOKEN)
    logger.info("literal %s in message", TOKEN)

    output = stream.getvalue()
    assert TOKEN not in output
    assert output.count("***") >= 2


def test_redacts_token_in_exception_traceback():
    stream = io.StringIO()
    logger = make_logger(stream)

    try:
        raise RuntimeError(f"request failed with token {TOKEN}")
    except RuntimeError:
        logger.exception("unexpected_error")

    output = stream.getvalue()
    assert TOKEN not in output
    assert "Traceback" in output
    assert "***" in output


def test_redacts_vk1_like_tokens_from_third_party_messages():
    stream = io.StringIO()
    logger = make_logger(stream, token="another-token")

    logger.info("leaked vk1.abcdef123456 in a library message")

    assert "vk1.abcdef123456" not in stream.getvalue()


def test_setup_logging_uses_redacting_formatter():
    root = logging.getLogger()
    vk_logger = logging.getLogger("vkbottle")
    old_handlers = root.handlers[:]
    old_level = root.level
    old_vk_handlers = vk_logger.handlers[:]
    old_vk_level = vk_logger.level
    old_vk_propagate = vk_logger.propagate
    try:
        vk_logger.handlers[:] = [logging.NullHandler()]

        setup_logging("INFO", TOKEN)

        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, RedactingFormatter)
        # Собственный цветной handler VKBottle удалён, дублей в логах нет.
        assert vk_logger.handlers == []
        assert vk_logger.propagate is True
    finally:
        root.handlers[:] = old_handlers
        root.setLevel(old_level)
        vk_logger.handlers[:] = old_vk_handlers
        vk_logger.setLevel(old_vk_level)
        vk_logger.propagate = old_vk_propagate
