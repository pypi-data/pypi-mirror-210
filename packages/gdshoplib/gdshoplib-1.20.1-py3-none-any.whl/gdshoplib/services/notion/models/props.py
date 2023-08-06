from typing import List, Optional

from dateutil.parser import parse
from pydantic import BaseModel


class PropModel(BaseModel):
    id: Optional[str]
    key: Optional[str]
    name: Optional[str]

    page: dict
    fields: Optional[List[dict]]

    def get_data(self):
        field = None
        page_field = None

        if not self.fields:
            raise KeyError

        for field_context in self.fields:
            _page_field = self.page["properties"].get(field_context["name"])
            if _page_field and _page_field["id"] == field_context["id"]:
                field = field_context
                page_field = _page_field

        if not page_field:
            return

        data = self.get_type_data(page_field)
        handler = field.get("handler")

        if handler and data:
            return handler(data)
        return data

    def get_type_data(self, page_field):
        return self.properties_type_parse_map.get(page_field["type"])(page_field)

    @property
    def properties_type_parse_map(self):
        return {
            "rich_text": lambda data: " ".join(
                [t.get("plain_text", "") for t in data["rich_text"]]
            )
            or "",
            "text": lambda data: data["plain_text"] or "",
            "number": lambda data: data["number"] or 0,
            "title": lambda data: data["title"][0]["text"]["content"],
            "select": lambda data: data.get("select").get("name")
            if data.get("select")
            else None,
            "multi_select": lambda data: data,
            "status": lambda data: data["status"]["name"],
            "date": lambda data: data["date"],
            "formula": lambda data: data["formula"]["number"],
            "relation": lambda data: data["relation"],
            "rollup": lambda data: data,
            "people": lambda data: data,
            "files": lambda data: data["files"],
            "checkbox": lambda data: data["checkbox"],
            "url": lambda data: data["url"],
            "email": lambda data: data,
            "phone_number": lambda data: data,
            "created_time": lambda data: parse(data["created_time"]),
            "created_by": lambda data: str(data["created_by"]),
            "last_edited_time": lambda data: parse(data["last_edited_time"]),
            "last_edited_by": lambda data: str(data["last_edited_by"]),
            "image": lambda data: data["image"]["file"]["url"],
            "video": lambda data: data["video"]["file"]["url"],
        }
