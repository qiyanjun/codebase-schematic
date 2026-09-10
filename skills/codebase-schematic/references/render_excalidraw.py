#!/usr/bin/env python3
"""Render an Excalidraw JSON file to a PNG screenshot.

Loads the diagram in a headless Chromium page (via Playwright), calls
Excalidraw's own exportToSvg() to produce the real rendering, then
screenshots the resulting SVG element. This is a rendering step, not a
layout engine of our own — Excalidraw does the layout; we just capture it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_TOP_LEVEL_KEYS = ("type", "elements")


def validate_excalidraw(data: dict) -> list[str]:
    """Return human-readable problems with an Excalidraw document.

    An empty list means the document is well-formed enough to attempt a render.
    """
    errors: list[str] = []
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            errors.append(f"missing top-level '{key}' key")

    elements = data.get("elements")
    if elements is not None:
        if not isinstance(elements, list):
            errors.append("'elements' must be a list")
        elif len(elements) == 0:
            errors.append("'elements' is empty — nothing to render")

    return errors


def compute_bounding_box(elements: list[dict]) -> tuple[float, float, float, float]:
    """Compute (min_x, min_y, max_x, max_y) across all non-deleted elements.

    Width/height can be negative in Excalidraw (the user dragged up-left
    instead of down-right), so every corner is compared against every other
    corner rather than assuming (x, y) is the top-left corner.
    """
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")

    for element in elements:
        if element.get("isDeleted"):
            continue

        x = element.get("x", 0)
        y = element.get("y", 0)

        if element.get("type") in ("arrow", "line") and "points" in element:
            corners = [(x + px, y + py) for px, py in element["points"]]
        else:
            w = element.get("width", 0)
            h = element.get("height", 0)
            corners = [(x, y), (x + w, y + h)]

        for corner_x, corner_y in corners:
            min_x, max_x = min(min_x, corner_x), max(max_x, corner_x)
            min_y, max_y = min(min_y, corner_y), max(max_y, corner_y)

    if min_x == float("inf"):
        return (0, 0, 800, 600)

    return (min_x, min_y, max_x, max_y)


def render(
    excalidraw_path: Path,
    output_path: Path | None = None,
    scale: int = 2,
    max_width: int = 1920,
) -> Path:
    """Render an .excalidraw file to PNG. Returns the output PNG path."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed.", file=sys.stderr)
        print(
            "Run: cd skills/codebase-schematic/references && uv sync && uv run playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    raw = excalidraw_path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {excalidraw_path}: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate_excalidraw(data)
    if errors:
        print("ERROR: invalid Excalidraw document:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    elements = [e for e in data["elements"] if not e.get("isDeleted")]
    min_x, min_y, max_x, max_y = compute_bounding_box(elements)
    padding = 80
    viewport_width = min(int(max_x - min_x + padding * 2), max_width)
    viewport_height = max(int(max_y - min_y + padding * 2), 600)

    if output_path is None:
        output_path = excalidraw_path.with_suffix(".png")

    template_path = Path(__file__).parent / "render_template.html"
    if not template_path.exists():
        print(f"ERROR: template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as e:
            if "Executable doesn't exist" in str(e):
                print("ERROR: Chromium not installed for Playwright.", file=sys.stderr)
                print(
                    "Run: cd skills/codebase-schematic/references && uv run playwright install chromium",
                    file=sys.stderr,
                )
                sys.exit(1)
            raise

        page = browser.new_page(
            viewport={"width": viewport_width, "height": viewport_height},
            device_scale_factor=scale,
        )
        page.goto(template_path.as_uri())
        page.wait_for_function("window.__moduleReady === true", timeout=30000)

        result = page.evaluate(f"window.renderDiagram({json.dumps(data)})")
        if not result or not result.get("success"):
            error = result.get("error", "unknown render error") if result else "renderDiagram returned null"
            print(f"ERROR: render failed: {error}", file=sys.stderr)
            browser.close()
            sys.exit(1)

        page.wait_for_function("window.__renderComplete === true", timeout=15000)

        svg = page.query_selector("#root svg")
        if svg is None:
            print("ERROR: no SVG element found after render.", file=sys.stderr)
            browser.close()
            sys.exit(1)

        svg.screenshot(path=str(output_path))
        browser.close()

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an .excalidraw file to PNG")
    parser.add_argument("input", type=Path, help="path to the .excalidraw JSON file")
    parser.add_argument("--output", "-o", type=Path, default=None)
    parser.add_argument("--scale", "-s", type=int, default=2)
    parser.add_argument("--width", "-w", type=int, default=1920)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    png_path = render(args.input, args.output, args.scale, args.width)
    print(str(png_path))


if __name__ == "__main__":
    main()
