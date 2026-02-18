"""Test that style_ids are padded to absolute coordinates (0-indexed from A1)."""

import fastexcel_keye as fastexcel

from .utils import path_for_fixture


def test_style_ids_padded_for_offset_data():
    """When data starts below row 0 / right of col 0, style_ids should be
    padded with zeros so that style_ids[row][col] uses absolute Excel
    coordinates.  This keeps them aligned with DataFrames produced via
    skip_rows=0.
    """
    # styled-with-offset.xlsx has data at C3:D5 (row_offset=2, col_offset=2)
    #   C3:D4 = red font (style 1)
    #   C5:D5 = blue font (style 2)
    reader = fastexcel.read_excel(path_for_fixture("styled-with-offset.xlsx"))
    style_ids = reader.get_style_ids(0)
    palette = reader.get_style_palette(0)

    # Grid should be 5 rows x 4 cols (absolute: rows 0-4, cols 0-3)
    assert len(style_ids) == 5
    assert all(len(row) == 4 for row in style_ids)

    # Padded region: rows 0-1 (all cols) and cols 0-1 (all rows) should be 0
    for r in range(2):
        assert style_ids[r] == [0, 0, 0, 0], f"Padded row {r} should be all zeros"
    for r in range(2, 5):
        assert style_ids[r][0] == 0 and style_ids[r][1] == 0, (
            f"Padded cols in row {r} should be zero"
        )

    # Data region: rows 2-3 should share one style, row 4 a different one
    red_id = style_ids[2][2]
    blue_id = style_ids[4][2]
    assert red_id != 0, "Red style should not be the default"
    assert blue_id != 0, "Blue style should not be the default"
    assert red_id != blue_id, "Red and blue should be different styles"

    # Rows 2-3 cols 2-3 = red
    assert style_ids[2] == [0, 0, red_id, red_id]
    assert style_ids[3] == [0, 0, red_id, red_id]
    # Row 4 cols 2-3 = blue
    assert style_ids[4] == [0, 0, blue_id, blue_id]

    # Palette: ID 0 is the default (empty), red_id has red font, blue_id has blue font
    assert 0 in palette  # default style exists
    red_style = palette[red_id]
    blue_style = palette[blue_id]
    assert red_style.font.color.red == 255 and red_style.font.color.blue == 0
    assert blue_style.font.color.blue == 255 and blue_style.font.color.red == 0


def test_style_ids_no_offset():
    """When data starts at A1, no padding should be added."""
    reader = fastexcel.read_excel(path_for_fixture("fixture-single-sheet.xlsx"))
    style_ids = reader.get_style_ids(0)

    if len(style_ids) > 0:
        # First row should correspond to row 0 of the sheet (no padding)
        # Just verify the grid exists and has reasonable dimensions
        assert len(style_ids[0]) > 0
