from requests import Session
import requests
from geovisio_cli.model import Geovisio
from geovisio_cli.exception import raise_for_status
from geovisio_cli import utils
import os
from dataclasses import dataclass, field
from typing import List, Optional
import toml
from rich import print


def login(s: Session, geovisio: Geovisio) -> bool:
    """
    Login to geovisio and store auth cookie in session
    """
    if geovisio.token is not None:
        return _login_with_token(s, geovisio)

    return _login_with_stored_credentials(s, geovisio)


def _login_with_token(s: Session, geovisio: Geovisio) -> bool:
    s.headers.update({"Authorization": f"Bearer {geovisio.token}"})
    return True


def _login_with_stored_credentials(s: Session, geovisio: Geovisio):
    creds = _read_existing_credentials(geovisio)

    instance_cred = creds.get_instance_credentials(geovisio.url)
    if not instance_cred:
        _generate_and_update_credentials(creds, geovisio)
        return False

    account_name = _check_if_associated(geovisio, instance_cred)
    if not account_name:
        claim_url = f"{geovisio.url}/api/auth/tokens/{instance_cred.token_id}/claim"
        print(
            f"🔐 We're waiting for you to link your user account with generated API token. To finalize authentication, please either go to the URL below, or scan the QR code below."
        )
        print(f"[green]{claim_url}[/green]")
        _display_qr_code(claim_url)
        return False

    print(f"👤 Using stored credentials, logged in as [green]{account_name}[/green]")
    s.headers.update({"Authorization": f"Bearer {instance_cred.jwt_token}"})
    return True


@dataclass
class InstanceCredential:
    url: str
    jwt_token: str
    token_id: str

    def get_claim_url(self) -> str:
        return f"{self.url}/api/auth/tokens/{self.token_id}/claim"


@dataclass
class Credentials:
    instances: List[InstanceCredential] = field(default_factory=lambda: [])

    def from_toml(self, data):
        self.instances = [
            InstanceCredential(
                url=i["url"], jwt_token=i["jwt_token"], token_id=i["token_id"]
            )
            for i in data.get("instances", [])
        ]

    def toml(self):
        return {
            "instances": [
                {"url": i.url, "jwt_token": i.jwt_token, "token_id": i.token_id}
                for i in self.instances
            ]
        }

    def get_instance_credentials(self, instance_url: str):
        return next((c for c in self.instances if c.url == instance_url), None)


def create_auth_credentials(geovisio: Geovisio) -> InstanceCredential:
    """
    Login to geovisio and store auth cookie in session
    """
    utils.test_geovisio_url(geovisio.url)
    creds = _read_existing_credentials(geovisio)

    instance_cred = creds.get_instance_credentials(geovisio.url)
    if instance_cred:
        account_name = _check_if_associated(geovisio, instance_cred)
        if account_name:
            print(f"👤 Already logged to instance as [green]{account_name}[/green]")
            return instance_cred
        claim_url = instance_cred.get_claim_url()
        print(
            f"🔐 We're waiting for you to link your user account with generated API token. To finalize authentication, please either go to the URL below, or scan the QR code below."
        )
        print(f"[green]{claim_url}[/green]")
        _display_qr_code(claim_url)
        return instance_cred

    return _generate_and_update_credentials(creds, geovisio)


def _generate_and_update_credentials(
    creds: Credentials, geovisio: Geovisio
) -> InstanceCredential:
    i = _generate_new_instance_credentials(geovisio)

    creds.instances.append(i)

    _write_credentials(creds)
    return i


def get_config_file_path() -> str:
    # store config file either if [XDG](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) defined directory or in a user specifig .config directory
    config_file_dir = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
        os.path.expanduser("~"), ".config"
    )

    return os.path.join(config_file_dir, "geovisio", "config.toml")


def _read_existing_credentials(geovisio: Geovisio) -> Credentials:
    creds = Credentials()
    if not os.path.exists(get_config_file_path()):
        return creds

    with open(get_config_file_path(), "r") as f:
        tomlFileContent = f.read()
        creds.from_toml(toml.loads(tomlFileContent))
        f.close()
    return creds


def _generate_new_instance_credentials(geovisio: Geovisio) -> InstanceCredential:
    token_response = requests.post(f"{geovisio.url}/api/auth/tokens/generate")
    raise_for_status(token_response, "Impossible to generate a GeoVisio token")

    token = token_response.json()
    jwt_token = token["jwt_token"]
    id = token["id"]

    claim_url = next(l["href"] for l in token["links"] if l["rel"] == "claim")
    print(
        f"🔐 Your computer is not yet authorized against GeoVisio API {geovisio.url}. To authenticate, please either go to the URL below, or scan the QR code below."
    )
    print(f"[green]{claim_url}[/green]")
    _display_qr_code(claim_url)
    return InstanceCredential(url=geovisio.url, jwt_token=jwt_token, token_id=id)


def _write_credentials(creds: Credentials):
    config_file_path = get_config_file_path()
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
    with open(config_file_path, "w") as f:
        f.write(toml.dumps(creds.toml()))
        f.close()


def _check_if_associated(
    geovisio: Geovisio, creds: InstanceCredential
) -> Optional[str]:
    token_response = requests.get(
        f"{geovisio.url}/api/users/me",
        headers={"Authorization": f"Bearer {creds.jwt_token}"},
    )
    if token_response.status_code == 403 or token_response.status_code == 401:
        return None
    raise_for_status(token_response, "Impossible to get token status")

    return token_response.json()["name"]


def _display_qr_code(url):
    import qrcode  # type: ignore
    import io

    qr = qrcode.QRCode()
    qr.add_data(url)
    f = io.StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    print(f.read())
