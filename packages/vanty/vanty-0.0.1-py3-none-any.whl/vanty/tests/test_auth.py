from unittest.mock import patch

from typer.testing import CliRunner

from vanty.auth import app

runner = CliRunner()


def test_set_command_success(mocked_api):
    with patch("getpass.getpass", return_value="test_license_id"):
        result = runner.invoke(app, ["set", "test_license_id"])

    assert "Verifying token against" in result.output
    assert "Token verified successfully" in result.output
    assert "Token written to" in result.output
    assert result.exit_code == 0


def test_set_command_failure(mocked_api):
    with patch("getpass.getpass", return_value="invalid_license_id"):
        result = runner.invoke(app, ["set", "test_license_idon"])

    assert "Verifying token against" in result.output
    assert "Token is invalid" in result.output
    assert result.exit_code == 0
