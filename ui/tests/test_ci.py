import os
from pathlib import Path
from streamlit.testing.v1 import AppTest


APP_PATH = os.getenv("APP_PATH", default="main.py")


def get_file_paths() -> list[str]:
    """Get a list of file paths for the main page + each page in the pages folder."""
    page_folder = Path(APP_PATH).parent / "pages"
    if not page_folder.exists():
        return [APP_PATH]
    page_files = page_folder.glob("*.py")
    file_paths = [str(file.absolute().resolve()) for file in page_files]
    return [APP_PATH] + file_paths


def pytest_generate_tests(metafunc):
    """
    This is a special function that is called automatically by pytest to generate tests.
    https://docs.pytest.org/en/7.1.x/how-to/parametrize.html#pytest-generate-tests
    """
    if "file_path" in metafunc.fixturenames:
        metafunc.parametrize(
            "file_path", get_file_paths(), ids=lambda x: x.split("/")[-1]
        )


def test_smoke_page(file_path):
    """
    This will run a basic test on each page in the pages folder, checking to see that
    there are no exceptions raised while the app runs.
    """
    at = AppTest.from_file(file_path, default_timeout=100).run()
    assert not at.exception