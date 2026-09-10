from render_excalidraw import compute_bounding_box, validate_excalidraw


def test_compute_bounding_box_positive_size():
    elements = [{"x": 100, "y": 100, "width": 50, "height": 30, "type": "rectangle"}]
    assert compute_bounding_box(elements) == (100, 100, 150, 130)


def test_compute_bounding_box_negative_size():
    # A rectangle dragged up-and-left has negative width/height in Excalidraw.
    # The visible region is x:[100,200], y:[150,200] — the bbox must land there,
    # not on the opposite side of the anchor point.
    elements = [{"x": 200, "y": 200, "width": -100, "height": -50, "type": "rectangle"}]
    assert compute_bounding_box(elements) == (100, 150, 200, 200)


def test_compute_bounding_box_arrow_uses_points():
    elements = [{"x": 0, "y": 0, "type": "arrow", "points": [[0, 0], [50, 20]]}]
    assert compute_bounding_box(elements) == (0, 0, 50, 20)


def test_compute_bounding_box_empty_elements_returns_default():
    assert compute_bounding_box([]) == (0, 0, 800, 600)


def test_compute_bounding_box_skips_deleted_elements():
    elements = [{"x": 0, "y": 0, "width": 10, "height": 10, "isDeleted": True}]
    assert compute_bounding_box(elements) == (0, 0, 800, 600)


def test_validate_excalidraw_accepts_well_formed_document():
    data = {"type": "excalidraw", "elements": [{"type": "rectangle"}]}
    assert validate_excalidraw(data) == []


def test_validate_excalidraw_rejects_empty_elements():
    data = {"type": "excalidraw", "elements": []}
    errors = validate_excalidraw(data)
    assert len(errors) == 1
    assert "empty" in errors[0]


def test_validate_excalidraw_rejects_missing_elements_key():
    data = {"type": "excalidraw"}
    errors = validate_excalidraw(data)
    assert any("elements" in e for e in errors)
