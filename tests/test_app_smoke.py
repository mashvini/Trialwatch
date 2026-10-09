"""The app must start and run the pipeline in mock mode without crashing, whatever is built so far."""
from __future__ import annotations

from helpers import ROOT
from streamlit.testing.v1 import AppTest

APP = str(ROOT / "app.py")


def test_app_starts():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception


def test_run_analysis_in_mock_mode():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.radio[0].set_value("mock").run()
    at.button(key="run").click().run()
    assert not at.exception
