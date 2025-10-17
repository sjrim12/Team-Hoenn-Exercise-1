import pytest
#tested with our own code problem5_code file
from problem5_code import InventorySystem


def test_init_starts_empty_and_value_zero():
    inv = InventorySystem()
    assert inv.get_inventory_value() == pytest.approx(0.0, abs=1e-9)


def test_add_products_and_inventory_value_example():
    inv = InventorySystem()
    inv.add_product("A001", "Wise Glasses", 5, 1200.00)
    inv.add_product("A002", "Muscle Band", 20, 25.50)
    # 5*1200 + 20*25.50 = 6510.00
    assert inv.get_inventory_value() == pytest.approx(6510.00, abs=1e-9)


def test_search_products_case_insensitive_and_shape():
    inv = InventorySystem()
    inv.add_product("A001", "Wise Glasses", 5, 1200.00)
    inv.add_product("A002", "Muscle Band", 20, 25.50)
    inv.add_product("B010", "Amulet Coin", 3, 99.99)

    # 'mu' appears in both 'Muscle Band' and 'Amulet Coin'
    results = inv.search_products("mu")
    expected = [
        {"id": "A002", "name": "Muscle Band", "quantity": 20, "price": 25.50},
        {"id": "B010", "name": "Amulet Coin", "quantity": 3, "price": 99.99},
    ]

    # Order-independent comparison
    results_sorted = sorted(results, key=lambda x: x["id"])
    expected_sorted = sorted(expected, key=lambda x: x["id"])

    assert isinstance(results, list)
    assert results_sorted == expected_sorted

    # Case-insensitive search still works; 'MUS' should only match 'Muscle Band'
    results_ci = inv.search_products("MUS")
    assert results_ci == [
        {"id": "A002", "name": "Muscle Band", "quantity": 20, "price": 25.50}
    ]


def test_update_existing_product_overwrites_properties_and_enforces_unique_ids():
    inv = InventorySystem()
    inv.add_product("X1", "Widget", 2, 10.0)
    inv.add_product("X1", "Widget Pro", 5, 12.5)  # update same ID

    # Only one product with id "X1" should exist, with updated fields
    results = inv.search_products("widget")
    assert results == [{"id": "X1", "name": "Widget Pro", "quantity": 5, "price": 12.5}]
    assert inv.get_inventory_value() == pytest.approx(62.5, abs=1e-9)


def test_remove_product_returns_true_then_false():
    inv = InventorySystem()
    inv.add_product("P100", "Pencil", 10, 1.25)
    assert inv.get_inventory_value() == pytest.approx(12.5, abs=1e-9)

    assert inv.remove_product("P100") is True
    assert inv.get_inventory_value() == pytest.approx(0.0, abs=1e-9)

    # Removing again should return False
    assert inv.remove_product("P100") is False


@pytest.mark.parametrize(
    "qty,price",
    [
        (-1, 1.0),   # negative quantity
        (1, -0.01),  # negative price
        (-5, -2.0),  # both negative
    ],
)
def test_add_product_negative_values_raise(qty, price):
    inv = InventorySystem()
    with pytest.raises(Exception):
        inv.add_product("NEG1", "BadItem", qty, price)


def test_zero_quantity_allowed_and_counts_in_value():
    inv = InventorySystem()
    inv.add_product("Z1", "ZeroThing", 0, 999.99)
    assert inv.get_inventory_value() == pytest.approx(0.0, abs=1e-9)
    # Update to non-zero quantity
    inv.add_product("Z1", "ZeroThing", 2, 999.99)
    assert inv.get_inventory_value() == pytest.approx(1999.98, abs=1e-6)


def test_bool_is_rejected_for_quantity_and_price():
    inv = InventorySystem()
    with pytest.raises(Exception):
        inv.add_product("B1", "BoolQty", True, 10.0)  # bool for quantity
    with pytest.raises(Exception):
        inv.add_product("B2", "BoolPrice", 1, True)   # bool for price


@pytest.mark.parametrize("bad_text", ["", "   ", None, 123])
def test_nonempty_strings_required_for_ids_and_names(bad_text):
    inv = InventorySystem()
    # product_id validation
    with pytest.raises(Exception):
        inv.add_product(bad_text, "ValidName", 1, 1.0)
    # name validation
    with pytest.raises(Exception):
        inv.add_product("ID1", bad_text, 1, 1.0)
