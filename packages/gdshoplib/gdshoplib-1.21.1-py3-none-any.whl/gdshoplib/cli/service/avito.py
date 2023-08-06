import typer

from gdshoplib.services.avito.avito import Avito

app = typer.Typer()


@app.command()
def access_code():
    print(Avito().get_access_token())
