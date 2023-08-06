import typer

from gdshoplib.apps.crm.stats import Statistic

app = typer.Typer()


@app.command()
def price(price_type="average", filter_type="complited_shop"):
    if price_type == "average":
        print(Statistic().avg_price(filter_type=filter_type))

    elif price_type == "percentile":
        print(Statistic().percentile(filter_type=filter_type))
