from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from vanty._client import Client
from vanty.cli import app
from vanty.config import config

runner = CliRunner()


def test_verify_success(mocked_api):
    client = Client()
    result = client.verify("test_license_id")
    assert result.is_valid
    assert result.token_id == "test_token_id"
    assert result.token_secret == "test_token_secret"


@patch("zipfile.ZipFile.extractall")
def test_download_success(mock_extract, mocked_api):
    client = Client()
    client.download()

    assert mock_extract.called
    assert (
        "Project files downloaded successfully"
        in runner.invoke(app, ["download"]).output
    )
