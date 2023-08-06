import io
import zipfile

import httpx
import rich

from .config import config
from .schema import DownloadProjectHttpResponse, LicenseVerifiedHttpResponse


class Client:
    def _download_zip(self, url: str) -> io.BytesIO:
        """
        Downloads the zip file from the url.

        :param url:
        :return:
        """
        response = httpx.get(url)
        zipped_file = io.BytesIO(response.content)
        return zipped_file

    def verify(self, license_id: str) -> LicenseVerifiedHttpResponse:
        """
        Authenticates the token.

        :param token:
        :return:
        """
        server_url = config.get("server_url")
        rich.print(f"Verifying license against [blue]{server_url}[/blue]")
        try:
            res = httpx.post(
                f"{server_url}/projects/authenticate-license/",
                json={"license_id": license_id},
            )
            data = res.json()
            return LicenseVerifiedHttpResponse(**data)
        except Exception as e:
            rich.print(f"[red]Error: {e}[/red]")
            return LicenseVerifiedHttpResponse.error()

    def download(self):
        """
        Gets the project.
        :return:
        """
        headers = {"X-API-Token": f"{config.get('token_secret')}"}
        local_folder = config.get("local_folder")
        server_url = config.get("server_url")

        rich.print(f"Downloading project from [blue]{server_url}[/blue]")
        response = httpx.get(f"{server_url}/projects/", headers=headers)
        data = DownloadProjectHttpResponse(**response.json())

        if data.is_valid is False or data.profile_status == "inactive":
            rich.print(
                "[red]Project Download Failed, the link may have expired!\n Please try again.[/red]"
            )
            return

        if data.profile_status == "inactive":
            rich.print("[red]Project is no longer active or has expired.[/red]")
            return

        # fetch the zip file
        response = httpx.get(data.url)
        if not response.status_code == 200:
            rich.print(
                "[red]File Download Failed, the link may have expired!\n Please try again.[/red]"
            )
            return

        # save the zip file
        zipped_file = self._download_zip(data.url)
        with zipfile.ZipFile(zipped_file) as zf:
            zf.extractall(path=local_folder)

        rich.print("[green]Project files downloaded successfully[/green]")
