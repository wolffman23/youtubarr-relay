import subprocess
import sys
import zipfile
from pathlib import Path


def test_plugin_zip_has_single_wrapper_root_and_no_secret_files(tmp_path: Path) -> None:
    destination = tmp_path / "youtubarr-relay-plugin.zip"
    result = subprocess.run(
        [sys.executable, "scripts/build_plugin_zip.py", "--output", str(destination)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "built" in result.stdout
    with zipfile.ZipFile(destination) as archive:
        names = archive.namelist()
    assert "youtubarr_relay/plugin.py" in names
    assert "youtubarr_relay/plugin.json" in names
    assert all("__pycache__" not in name and "cookies" not in name.lower() for name in names)
