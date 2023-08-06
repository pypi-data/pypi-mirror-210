import typer

from gdshoplib.services.vk.market import VKMarket
from gdshoplib.services.vk.page import VKPage
from gdshoplib.services.vk.vk import VK

app = typer.Typer()


@app.command()
def access_code(code=None):
    if not code:
        VK().get_oauth_code()
        code = typer.prompt("Код")

    print(VK().get_access_token(code))


@app.command()
def online(active: bool = True):
    if active:
        VKPage().set_enable()
    else:
        VKPage().set_disable()


@app.command()
def health():
    assert VKMarket().list(), "Запрос в VK не выполняется"
    print("OK")
