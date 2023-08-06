import time
from typing import Optional

import typer

from gdshoplib.apps.crm.orders import Order

app = typer.Typer()


@app.command()
def on_request_update():
    # Взять все заказы, в нужном статусе
    # Обновить позиции на заказ
    for order in Order.query(params=Order.list_filter()):
        order.on_request.update()


@app.command()
def update(loop_iteration: Optional[int] = typer.Option(None)):
    # Обновить расчеты заказов
    while True:
        Order.update()
        if loop_iteration:
            time.sleep(loop_iteration)
        else:
            break


@app.command()
def notify():
    # Разослать уведомление для менеджеров из CRM
    ...
