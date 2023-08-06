from geovisio_cli.exception import CliException
import requests

REQUESTS_TIMEOUT = 30


def test_geovisio_url(geovisio: str):
    full_url = f"{geovisio}/api/collections"
    try:
        r = requests.get(full_url, timeout=REQUESTS_TIMEOUT)
    except (
        requests.Timeout,
        requests.ConnectionError,
        requests.ConnectTimeout,
        requests.TooManyRedirects,
    ) as e:
        raise CliException(
            f"""The API is not reachable. Please check error and used URL below, and retry later if the URL is correct.

[bold]Used URL:[/bold] {full_url}
[bold]Error:[/bold]
{e}"""
        )
    except Exception as e:
        raise CliException(
            f"""Error while connecting to the API. Please check error and used URL below

[bold]Used URL:[/bold] {full_url}
[bold]Error:[/bold]
{e}"""
        )

    if r.status_code == 404:
        raise CliException(
            f"""The API URL is not valid.

Note that your URL should be the API root (something like https://geovisio.fr, https://panoramax.ign.fr or any other geovisio instance).
Please make sure you gave the correct URL and retry.

[bold]Used URL:[/bold] {full_url}
[bold]Error:[/bold]
{r.text}"""
        )
    if r.status_code > 404:
        raise CliException(
            f"""The API is unavailable for now. Please check given error and retry later.
[bold]Used URL:[/bold] {full_url}
[bold]Error[/bold] (code [cyan]{r.status_code}[/cyan]):
{r.text}"""
        )
