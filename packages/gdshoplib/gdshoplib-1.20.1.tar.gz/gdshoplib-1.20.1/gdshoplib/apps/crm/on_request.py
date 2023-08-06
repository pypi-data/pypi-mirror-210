from typing import Optional

from pydantic import BaseModel, ValidationError

from gdshoplib.apps.products.price import Price
from gdshoplib.services.notion.models.props import PropModel


class OnRequestTable:
    def __init__(self, blocks, /, notion, parent):
        self.notion = notion
        self.parent = parent

        self._blocks = blocks
        self._rows = []

        self.__iter = None

    def _parse_rows(self):
        result = []
        for i, block in enumerate(self._blocks):
            row = []
            for r in block["table_row"]["cells"]:
                if not r:
                    row.append(None)
                    continue
                row.append(PropModel(page={}).get_type_data(r[0]))

            if row[4] == "Ошибка":
                continue

            row_result = dict(
                block_id=block["id"],
                name=row[0] or None,
                link=row[1] or None,
                price=row[2] or None,
                quantity=row[3] or None,
            )
            try:
                result.append(OnRequestTableRow(**row_result))
            except ValidationError as e:
                row_result["error"] = str(e)
                result.append(OnRequestTableInvalidRow(**row_result))
        return result

    @property
    def rows(self):
        if not self._rows:
            self._rows = self._parse_rows()
        return self._rows

    def price(self, base_price="neitral"):
        return (
            sum(
                [
                    Price(r)[base_price] * r.quantity
                    for r in filter(
                        lambda x: isinstance(x, OnRequestTableRow), self.rows
                    )
                ]
            )
            or 0
        )

    def __bool__(self):
        return bool(self.rows)

    def __iter__(self):
        self.__iter = iter(self.rows)
        return self

    def __next__(self):
        return next(self.__iter)

    def update(self):
        for r in self.rows:
            self.notion.update_block(
                r.block_id,
                params={
                    "table_row": {
                        "cells": [
                            [self.row_object_formater(r.name)],
                            [self.row_object_formater(r.link)],
                            [self.row_object_formater(r.price)],
                            [self.row_object_formater(r.quantity)],
                            [self.row_object_formater(r.error)],
                        ]
                    }
                },
            )

    def row_object_formater(self, data):
        return {
            "type": "text",
            "text": {"content": f"{data}" if data else "", "link": None},
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default",
            },
            "plain_text": f"{data}" if data else "",
            "href": None,
        }


class OnRequestTableRow(BaseModel):
    block_id: str
    name: str
    link: str
    price: float
    quantity: int
    error: Optional[str]

    @property
    def price_eur(self):
        return self.price


class OnRequestTableInvalidRow(BaseModel):
    block_id: str
    name: Optional[str]
    link: Optional[str]
    price: Optional[str]
    quantity: Optional[str]
    error: str
