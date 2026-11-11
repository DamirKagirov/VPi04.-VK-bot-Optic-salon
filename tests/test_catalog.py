import copy
import json
from pathlib import Path

import pytest

from app.catalog import CatalogError, load_catalog, parse_catalog
from app.texts import format_price, price_with_unit

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog" / "services.json"

EXPECTED = {
    "vision_exam_glasses": (2500, "fixed", "2 500 ₽"),
    "vision_exam_full": (3000, "fixed", "3 000 ₽"),
    "contact_lens_fitting": (2500, "fixed", "2 500 ₽"),
    "glasses_assembly": (1300, "from", "от 1 300 ₽"),
    "frame_laser_welding": (1500, "from", "от 1 500 ₽"),
    "nose_pads_replacement": (300, "from", "от 300 ₽"),
    "screw_replacement": (300, "from", "от 300 ₽"),
    "lens_refit": (700, "fixed", "700 ₽"),
    "frame_adjustment": (500, "from", "от 500 ₽"),
    "ultrasonic_cleaning": (300, "from", "от 300 ₽"),
}


@pytest.fixture()
def raw_data():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def test_catalog_has_ten_services():
    catalog = load_catalog(CATALOG_PATH)
    assert len(catalog.services) == 10
    assert len({service.id for service in catalog.services}) == 10
    assert len({service.sort_order for service in catalog.services}) == 10


def test_prices_match_project_decisions():
    catalog = load_catalog(CATALOG_PATH)
    for service in catalog.services:
        price, price_type, formatted = EXPECTED[service.id]
        assert service.price == price
        assert service.price_type == price_type
        assert format_price(service) == formatted
        assert price_with_unit(service).startswith(formatted)


def test_button_labels_fit_vk_limit():
    catalog = load_catalog(CATALOG_PATH)
    for service in catalog.services:
        assert 0 < len(service.button) <= 40, service.id
        assert len(service.name) <= 120
        assert len(service.full) <= 1200


def test_all_services_require_owner_confirmation():
    catalog = load_catalog(CATALOG_PATH)
    assert all(service.requires_owner_confirmation for service in catalog.services)
    assert {service.confirmation_type for service in catalog.services} == {"medical", "workshop"}


def test_get_and_ordered():
    catalog = load_catalog(CATALOG_PATH)
    assert catalog.get("vision_exam_glasses").price == 2500
    assert catalog.get("missing") is None
    orders = [service.sort_order for service in catalog.ordered()]
    assert orders == sorted(orders)


def test_rejects_duplicate_id(raw_data):
    data = copy.deepcopy(raw_data)
    data["services"][1]["id"] = data["services"][0]["id"]
    with pytest.raises(CatalogError, match="уникальны"):
        parse_catalog(data)


def test_rejects_long_button(raw_data):
    data = copy.deepcopy(raw_data)
    data["services"][0]["button"] = "я" * 41
    with pytest.raises(CatalogError, match="длиннее 40"):
        parse_catalog(data)


def test_rejects_zero_price(raw_data):
    data = copy.deepcopy(raw_data)
    data["services"][0]["price"] = 0
    with pytest.raises(CatalogError, match="price"):
        parse_catalog(data)


def test_rejects_wrong_schema_version(raw_data):
    data = copy.deepcopy(raw_data)
    data["schema_version"] = 2
    with pytest.raises(CatalogError, match="schema_version"):
        parse_catalog(data)


def test_missing_file():
    with pytest.raises(CatalogError, match="не найден"):
        load_catalog(ROOT / "catalog" / "missing.json")
