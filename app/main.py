import json
from fastapi import FastAPI
from sqlalchemy import text
from app.db import engine
from app.queries import (
    GET_ORDER_IDS,
    GET_ORDER_ITEMS,
    GET_SHIPMENT_DETAILS,
    GET_ORDER_FULL
)

app = FastAPI(title="WooCommerce API")


@app.get("/orders")
def orders(
    date_from: str,
    date_to: str,
    shipping_filter: str = "Wszystkie zamówienia"
):
    with engine.connect() as conn:
        result = conn.execute(
            text(GET_ORDER_IDS),
            {
                "date_from": f"{date_from}",
                "date_to": f"{date_to}",
                "shipping_filter": shipping_filter
            }
        )
        return [dict(r._mapping) for r in result]


@app.get("/orders/{order_id}/items")
def order_items(order_id: int):
    with engine.connect() as conn:
        result = conn.execute(
            text(GET_ORDER_ITEMS),
            {"order_id": order_id}
        )
        return [dict(r._mapping) for r in result]


@app.get("/orders/{order_id}/shipment")
def shipment(order_id: int):
    with engine.connect() as conn:
        result = conn.execute(
            text(GET_SHIPMENT_DETAILS),
            {"order_id": order_id}
        )
        return dict(result.first()._mapping)


@app.get("/orders/{order_id}/full")
def order_full(order_id: int):
    with engine.connect() as conn:
        result = conn.execute(
            text(GET_ORDER_FULL),
            {"order_id": order_id}
        )
        row = dict(result.first()._mapping)

        # Parsowanie JSON stringów do Python objects
        if row.get("products"):
            row["products"] = json.loads(row["products"])
        if row.get("shipment_details"):
            row["shipment_details"] = json.loads(row["shipment_details"])

        return row
