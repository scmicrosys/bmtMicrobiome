from typer.testing import CliRunner

from .console import app

runner = CliRunner()


def test_app_true():
    result = runner.invoke(app, ["test-app", "True"])
    assert result.exit_code == 0
    assert "True" in result.stdout


def test_app_false():
    result = runner.invoke(app, ["test-app"])
    assert result.exit_code == 0
    assert "False" in result.stdout
