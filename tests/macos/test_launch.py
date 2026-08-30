import os
import shlex
import stat
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAUNCH_SCRIPT = PROJECT_ROOT / "macos" / "POTA QSO Logging.app" / "Contents" / "MacOS" / "launch"


def _make_executable(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _stub_bin_dir(tmp_path: Path, osascript_record: Path) -> Path:
    bin_dir = tmp_path / "stub-bin"
    _make_executable(
        bin_dir / "osascript",
        '#!/bin/sh\necho "$@" >> ' + shlex.quote(str(osascript_record)) + "\nexit 0\n",
    )
    return bin_dir


def _run_launch(
    *, project_dir: Path, home: Path, bin_dir: Path
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["POTA_LAUNCHER_PROJECT_DIR"] = str(project_dir)
    env["HOME"] = str(home)
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
    return subprocess.run([str(LAUNCH_SCRIPT)], capture_output=True, text=True, env=env)


def test_shows_alert_and_exits_nonzero_when_venv_missing(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    home = tmp_path / "home"
    home.mkdir()
    osascript_record = tmp_path / "osascript-calls.txt"
    bin_dir = _stub_bin_dir(tmp_path, osascript_record)

    result = _run_launch(project_dir=project_dir, home=home, bin_dir=bin_dir)

    assert result.returncode != 0
    assert osascript_record.exists()
    assert not (home / "POTA Logs").exists()


def test_creates_logs_dir_and_runs_python_with_expected_argv_and_cwd(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    home = tmp_path / "home"
    home.mkdir()
    osascript_record = tmp_path / "osascript-calls.txt"
    bin_dir = _stub_bin_dir(tmp_path, osascript_record)
    record_file = tmp_path / "python-record.txt"
    _make_executable(
        project_dir / ".venv" / "bin" / "python",
        "#!/bin/sh\n"
        f"pwd > {shlex.quote(str(record_file))}\n"
        f'echo "$@" >> {shlex.quote(str(record_file))}\n'
        "exit 0\n",
    )

    result = _run_launch(project_dir=project_dir, home=home, bin_dir=bin_dir)

    logs_dir = home / "POTA Logs"
    recorded = record_file.read_text().splitlines()
    assert result.returncode == 0
    assert logs_dir.is_dir()
    assert recorded[0] == str(logs_dir)
    assert recorded[1] == "-m radio_pota_logging.api.composition_root"
    assert not osascript_record.exists()


def test_does_not_touch_existing_logs_directory_contents(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    home = tmp_path / "home"
    home.mkdir()
    logs_dir = home / "POTA Logs"
    logs_dir.mkdir()
    marker = logs_dir / "marker.txt"
    marker.write_text("keep me")
    osascript_record = tmp_path / "osascript-calls.txt"
    bin_dir = _stub_bin_dir(tmp_path, osascript_record)
    _make_executable(project_dir / ".venv" / "bin" / "python", "#!/bin/sh\nexit 0\n")

    result = _run_launch(project_dir=project_dir, home=home, bin_dir=bin_dir)

    assert result.returncode == 0
    assert marker.read_text() == "keep me"


def test_shows_alert_with_exit_code_and_log_path_on_crash(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    home = tmp_path / "home"
    home.mkdir()
    osascript_record = tmp_path / "osascript-calls.txt"
    bin_dir = _stub_bin_dir(tmp_path, osascript_record)
    _make_executable(
        project_dir / ".venv" / "bin" / "python",
        "#!/bin/sh\necho 'boom: simulated crash' 1>&2\nexit 1\n",
    )

    result = _run_launch(project_dir=project_dir, home=home, bin_dir=bin_dir)

    log_file = home / "POTA Logs" / "launcher.log"
    assert result.returncode == 1
    assert log_file.exists()
    assert "boom: simulated crash" in log_file.read_text()
    assert osascript_record.exists()
    alert_text = osascript_record.read_text()
    assert "(exit code 1)" in alert_text
    assert str(log_file) in alert_text
