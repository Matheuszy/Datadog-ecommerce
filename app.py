import os
import logging
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from dotenv import load_dotenv

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_series import MetricSeries
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem

print("API Key carregada:", bool(os.getenv("DD_API_KEY")))
print("DD_SITE:", os.getenv("DD_SITE"))



env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

print("Arquivo .env:", env_path)
print("Existe:", env_path.exists())
print("API Key carregada:", bool(os.getenv("DD_API_KEY")))
print("DD_SITE:", os.getenv("DD_SITE"))

app = FastAPI(title="E-commerce API")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


class Order(BaseModel):
    order_id: str
    customer_id: str
    amount: float
    payment_method: str


def send_error_metric():

    body = MetricPayload(
        series=[
            MetricSeries(
                metric="ecommerce.orders.errors",
                type=MetricIntakeType.COUNT,
                points=[
                    MetricPoint(
                        timestamp=int(datetime.now().timestamp()),
                        value=1.0,
                    )
                ],
                tags=[
                    "service:orders-api",
                    "env:production",
                    "version:1.0.0",
                    "region:sa-east-1"
                ],
            )
        ]
    )

    configuration = Configuration()

    with ApiClient(configuration) as api_client:
        api_instance = MetricsApi(api_client)

        response = api_instance.submit_metrics(body=body)

        print("Resposta Datadog:")
        print(response)

def send_error_log(order, error_type, error_message):
    message = (
        f"Erro ao processar pedido "
        f"order_id={order.order_id} "
        f"customer_id={order.customer_id} "
        f"amount={order.amount} "
        f"payment_method={order.payment_method} "
        f"status=failed "
        f"error_type={error_type} "
        f"error_message={error_message} "
        f"service=orders-api "
        f"env=production"
    )

    body = HTTPLog(
        [
            HTTPLogItem(
                message=message,
                service="orders-api",
                ddsource="python",
                status="error",
            )
        ]
    )

    configuration = Configuration()

    with ApiClient(configuration) as api_client:
        api_instance = LogsApi(api_client)

        response = api_instance.submit_log(body=body)

        print("Resposta Logs Datadog:")
        print(response)
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/orders")
def process_order(order: Order):

    has_error = order.order_id.startswith("ORD-ERROR")

    if has_error:

        if order.payment_method == "boleto":
            error_type = "payment_validation_error"
            error_message = "Falha na validacao do boleto"
        else:
            error_type = "order_processing_error"
            error_message = "Falha generica no processamento"

        logging.error(
            f"Erro ao processar pedido "
            f"order_id={order.order_id} "
            f"customer_id={order.customer_id} "
            f"amount={order.amount} "
            f"payment_method={order.payment_method} "
            f"status=failed "
            f"error_type={error_type} "
            f"error_message={error_message} "
            f"service=orders-api "
            f"env=production"
        )

        send_error_metric()

        send_error_log(
            order,
            error_type,
            error_message
        )

        return {
            "order_id": order.order_id,
            "status": "error"
        }

    logging.info(
        f"Pedido processado "
        f"order_id={order.order_id} "
        f"customer_id={order.customer_id}"
    )

    return {
        "order_id": order.order_id,
        "status": "success"
    }

    has_error = order.order_id.startswith("ORD-ERROR")

    if order.payment_method == "boleto":
        error_type = "payment_validation_error"
        error_message = "Falha na validacao do boleto"
    else:
        error_type = "order_processing_error"
        error_message = "Falha generica no processamento"

    if has_error:
        logging.error(
            f"Erro ao processar pedido "
            f"order_id={order.order_id} "
            f"customer_id={order.customer_id} "
            f"amount={order.amount} "
            f"payment_method={order.payment_method} "
            f"status=failed "
            f"service=orders-api "
            f"env=production"
        )

        send_error_metric()
        send_error_log(order)

        return {
            "order_id": order.order_id,
            "status": "error"
        }

    logging.info(
        f"Pedido processado "
        f"order_id={order.order_id} "
        f"customer_id={order.customer_id}"
    )

    return {
        "order_id": order.order_id,
        "status": "success"
    }