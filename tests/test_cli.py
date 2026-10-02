"""The claimcheck command wraps the existing scripts without changing them."""
import subprocess, sys
from pathlib import Path
from claimcheck.cli import COMMANDS, main

ROOT = Path(__file__).resolve().parent.parent

def test_every_command_points_at_a_real_script():
    for name, (script, _) in COMMANDS.items():
        assert (ROOT / "scripts" / script).exists(), name

def test_help_lists_commands(capsys):
    assert main(["--help"]) == 0
    out = capsys.readouterr().out
    assert all(name in out for name in COMMANDS)

def test_unknown_command_fails(capsys):
    assert main(["nope"]) == 2

def test_exit_codes_pass_through(tmp_path):
    # train_pt_judge refuses a second run with exit code 1; the wrapper must return 1 too
    (tmp_path / "pytorch_judge.md").write_text("x")
    code = subprocess.run([sys.executable, "-m", "claimcheck.cli", "pt-judge", "--results", str(tmp_path)],
                          capture_output=True, text=True, cwd=ROOT).returncode
    assert code == 1
