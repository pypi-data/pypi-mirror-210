import datetime
import os
from collections import namedtuple

import imageio
import pytest
from matplotlib import pyplot as plt
from numpy.testing import assert_array_equal
from PIL import Image
from PyQt5.QtCore import Qt

from uwsift.view import export_image


def _get_mock_model():
    """Mock LayerModel class for testing."""

    class MockPrez:
        def __init__(self):
            self.colormap = "Rainbow (IR Default)"
            self.climits = (0, 1)

    class MockDataset:
        def __init__(self):
            self.info = {}
            self.info["unit_conversion"] = ("unit", lambda t: t, lambda t: t)
            self.info["timeline"] = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
            self.info["display_name"] = "name"

    class MockModel:
        def __init__(self):
            self.moc_prez = MockPrez()
            self.moc_dataset = MockDataset()

        def get_dataset_presentation_by_uuid(self, u):
            return self.moc_prez

        def get_dataset_by_uuid(self, u):
            return self.moc_dataset

    return MockModel()


def _get_mock_sd(fr, fn):
    """Mock ScreenshotDialog class for testing."""

    class MockScreenshotDialog:
        def __init__(self, frame_range, filename):
            self.info = {
                "frame_range": frame_range,
                "include_footer": True,
                "filename": filename,
                "colorbar": True,
                "font_size": 10,
                "loop": True,
            }

        def get_info(self):
            return self.info

    return MockScreenshotDialog(fr, fn)


def _get_mock_sgm(frame_order):
    """Mock SceneGraphManager class for testing."""

    class MockAnimationController:
        def __init__(self):
            self._frame_order = frame_order

        def get_current_frame_index(self):
            return max(self._frame_order, 1) if self._frame_order else 0

        def get_frame_uuids(self):
            return self._frame_order if self._frame_order else []

    class MockSGM:
        def __init__(self):
            self.animation_controller = MockAnimationController()

        def get_screenshot_array(self, fr):
            if fr is None:
                return None
            return [[fr[1], fr[1] - fr[0]]]

    return MockSGM()


def _get_mock_writer():
    """Mock Writer class for testing."""

    class MockWriter:
        def __init__(self):
            self.data = []

        def append_data(self, data):
            self.data.append(data)

        def close(self):
            pass

    return MockWriter()


@pytest.mark.parametrize(
    "size,mode,exp",
    [
        ((100, 100), "vertical", [0.1, 1.2]),
        ((100, 100), "horizontal", [1.2, 0.1]),
    ],
)
def test_create_colorbar(size, mode, exp, monkeypatch, window):
    """Test colorbar is created correctly given dimensions and the colorbar append direction."""
    monkeypatch.setattr(window.export_image, "model", _get_mock_model())
    monkeypatch.setattr(window.export_image.sgm.main_canvas, "dpi", 100)

    res = window.export_image._create_colorbar(mode, None, size)

    assert_array_equal(res.get_size_inches(), exp)
    assert res.dpi == 100


@pytest.mark.parametrize(
    "mode,cbar_size,exp",
    [
        (None, (0, 0), (100, 100)),
        ("vertical", (10, 120), (108, 100)),
        ("horizontal", (110, 10), (100, 109)),
    ],
)
def test_append_colorbar(mode, cbar_size, exp, monkeypatch, window):
    """Test colorbar is appended to the appropriate location given the colorbar append direction."""
    monkeypatch.setattr(window.export_image, "model", _get_mock_model())
    monkeypatch.setattr(window.export_image.sgm.main_canvas, "dpi", 100)
    monkeypatch.setattr(window.export_image, "_create_colorbar", lambda x, y, z: plt.figure(figsize=cbar_size))

    im = Image.new("RGBA", (100, 100))
    res = window.export_image._append_colorbar(mode, im, None)

    assert res.size == exp


@pytest.mark.parametrize("size,fs,exp", [((100, 100), 10, (100, 110))])
def test_add_screenshot_footer(size, fs, exp, window):
    """Test screenshot footer is appended correctly."""
    im = Image.new("RGBA", size)
    res = window.export_image._add_screenshot_footer(im, "text", font_size=fs)
    assert res.size == exp


@pytest.mark.parametrize(
    "range,exp",
    [
        (None, None),
        ((None, 2), (0, 1)),
        ((1, None), (0, 0)),
        ((1, 5), (0, 4)),
    ],
)
def test_convert_frame_range(range, exp, window):
    """Test frame range is converted correctly."""
    res = window.export_image._convert_frame_range(range)
    assert res == exp


@pytest.mark.parametrize(
    "info,isgif,exp",
    [
        ({"fps": None, "filename": None, "loop": 0}, True, {"duration": [0.1, 0.1], "loop": 0}),
        ({"fps": None, "filename": None, "loop": 0}, False, {"fps": 10}),
        ({"fps": 1, "filename": None}, True, {"fps": 1, "loop": 0}),
        ({"fps": 1, "filename": None}, False, {"fps": 1}),
    ],
)
def test_get_animation_parameters(info, isgif, exp, monkeypatch, window):
    """Test animation parameters are calculated correctly."""
    monkeypatch.setattr(window.export_image, "model", _get_mock_model())
    monkeypatch.setattr(export_image, "is_gif_filename", lambda x: isgif)

    im = Image.new("RGBA", (100, 100))

    res = window.export_image._get_animation_parameters(info, [(0, im), (0, im)])
    assert res == exp


@pytest.mark.parametrize("fn,exp", [("test.gif", True), ("test.png", False)])
def test_is_gif_filename(fn, exp):
    """Test that gif file names are recognized."""
    res = export_image.is_gif_filename(fn)
    assert res == exp


@pytest.mark.parametrize("fn,exp", [("test.gif", True), ("test.m4v", True), ("test.mp4", True), ("test.png", False)])
def test_is_video_filename(fn, exp):
    """Test that video file names are recognized."""
    res = export_image.is_video_filename(fn)
    assert res == exp


@pytest.mark.parametrize(
    "uuids,base,exp",
    [
        ([0, 0], "test.gif", ([0, 0], ["test.gif"])),
        ([0, 0], "test.png", ([0, 0], ["test_001.png", "test_002.png"])),
        (None, "test.gif", ([None], ["test.gif"])),
    ],
)
def test_create_filenames(uuids, base, exp, monkeypatch, window):
    """Test file names are created correctly."""
    monkeypatch.setattr(window.export_image, "model", _get_mock_model())
    res = window.export_image._create_filenames(uuids, base)
    assert res == exp


@pytest.mark.parametrize(
    "fr,fn,overwrite,exp",
    [
        ([1, 2], "test.gif", True, 1),
        ([1, 2], "test.m4v", True, 1),
        (None, "test.m4v", True, 0),
        ([1, 2], "test.gif", False, 0),
    ],
)
def test_save_screenshot(fr, fn, overwrite, exp, monkeypatch, window):
    """Test screenshot is saved correctly given the frame range and filename."""
    writer = _get_mock_writer()
    IFormat = namedtuple("IFormat", "name")

    monkeypatch.setattr(window.export_image, "_screenshot_dialog", _get_mock_sd(fr, fn))
    monkeypatch.setattr(window.export_image, "_convert_frame_range", lambda x: fr)
    monkeypatch.setattr(window.export_image, "sgm", _get_mock_sgm(fr))
    monkeypatch.setattr(window.export_image, "_create_filenames", lambda x, y: ([1], [fn]))
    monkeypatch.setattr(window.export_image, "model", _get_mock_model())
    monkeypatch.setattr(window.export_image, "_overwrite_dialog", lambda: overwrite)
    monkeypatch.setattr(window.export_image, "_append_colorbar", lambda x, y, z: y)
    monkeypatch.setattr(window.export_image, "_add_screenshot_footer", lambda x, y, font_size=10: x)
    monkeypatch.setattr(window.export_image, "_get_animation_parameters", lambda x, y: {"loop": True})
    monkeypatch.setattr(export_image, "get_imageio_format", lambda x: IFormat(name="test"))
    monkeypatch.setattr(os.path, "isfile", lambda x: True)
    monkeypatch.setattr(Image, "fromarray", lambda x: x)
    monkeypatch.setattr(imageio, "get_writer", lambda x, y: writer)

    window.export_image._save_screenshot()

    assert len(writer.data) == exp


def test_cmd_open_export_image_dialog(qtbot, window):
    """Test that the keyboard shortcut Ctrl/Cmd + I opens the export image menu."""
    qtbot.addWidget(window)
    qtbot.keyClick(window, Qt.Key_I, Qt.ControlModifier)

    def check_dialog():
        assert window.export_image._screenshot_dialog is not None

    qtbot.waitUntil(check_dialog)


def test_export_image_dialog_info_default(qtbot, window):
    """Assert changing no options results in the default screenshot settings."""
    window.export_image.take_screenshot()
    qtbot.waitUntil(lambda: window.export_image._screenshot_dialog is not None)

    res = window.export_image._screenshot_dialog.get_info()

    # only look at the filename
    res["filename"] = os.path.split(res["filename"])[-1]

    exp = {
        "frame_range": None,
        "include_footer": True,
        "loop": True,
        "filename": export_image.ExportImageDialog.default_filename,
        "fps": None,
        "font_size": 11,
        "colorbar": None,
    }

    assert res == exp


def test_export_image_dialog_info(qtbot, window):
    """Test changing the options in the export image GUI."""
    window.export_image.take_screenshot()
    qtbot.waitUntil(lambda: window.export_image._screenshot_dialog is not None)

    qtbot.keyClick(window.export_image._screenshot_dialog.ui.saveAsLineEdit, Qt.Key_A, Qt.ControlModifier)
    qtbot.keyClick(window.export_image._screenshot_dialog.ui.saveAsLineEdit, Qt.Key_Backspace)
    qtbot.keyClicks(window.export_image._screenshot_dialog.ui.saveAsLineEdit, "test.png")
    qtbot.keyClick(window.export_image._screenshot_dialog.ui.footerFontSizeSpinBox, Qt.Key_A, Qt.ControlModifier)
    qtbot.keyClick(window.export_image._screenshot_dialog.ui.footerFontSizeSpinBox, Qt.Key_Backspace)
    qtbot.keyClicks(window.export_image._screenshot_dialog.ui.footerFontSizeSpinBox, "20")
    qtbot.mouseClick(window.export_image._screenshot_dialog.ui.frameRangeRadio, Qt.LeftButton)
    qtbot.mouseClick(window.export_image._screenshot_dialog.ui.colorbarVerticalRadio, Qt.LeftButton)
    qtbot.mouseClick(window.export_image._screenshot_dialog.ui.includeFooterCheckbox, Qt.LeftButton)

    res = window.export_image._screenshot_dialog.get_info()
    res["filename"] = os.path.split(res["filename"])[-1]

    exp = {
        "frame_range": [1, 1],
        "include_footer": False,
        "loop": True,
        "filename": "test.png",
        "fps": None,
        "font_size": 20,
        "colorbar": "vertical",
    }

    assert res == exp
