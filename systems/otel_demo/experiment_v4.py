"""Iteration-4 OpenTelemetry Demo adapter.

This module deliberately leaves :mod:`systems.otel_demo.adapter` unchanged.  It
adds the uncapped, durably journaled workload contract used by protocol v4 and
keeps source-audited obligations separate from Bering's recovered graph.
"""
from __future__ import annotations

import base64
import copy
import json
import time
import uuid
from typing import Any

import requests
import yaml

from .adapter import Adapter as LegacyAdapter
from .adapter import PRODUCT_ID, _ORDER_ID


CONTROLLED_SERVICE_ALIASES = [
    "product-catalog",
    "product_catalog",
    "oteldemo.ProductCatalogService",
]

ENTRY_SERVICE_ALIASES = ["frontend", "frontend-service"]
CATALOG_DATABASE_ALIASES = ["astronomy-db", "astronomy_db", "postgresql"]
SELECTED_DATABASE = {"db_system": "postgresql", "db_role": "catalog",
                     "container": "astronomy-db", "fault_scope": "whole_database_container"}


def _call(
    call_id: str,
    caller: list[str],
    callee: list[str],
    **hints: Any,
) -> dict[str, Any]:
    return {"call_id": call_id, "caller": caller, "callee": callee, **hints}


def _db_call(
    call_id: str,
    caller: list[str],
    db_system: str,
    db_role: str,
    **hints: Any,
) -> dict[str, Any]:
    return {
        "call_id": call_id,
        "caller": caller,
        "db_system": db_system,
        "db_role": db_role,
        **hints,
    }


_FRONTEND = ENTRY_SERVICE_ALIASES
_CATALOG = CONTROLLED_SERVICE_ALIASES
_CART = ["cart", "cart-service", "oteldemo.CartService"]
_CHECKOUT = ["checkout", "checkout-service", "oteldemo.CheckoutService"]
_CURRENCY = ["currency", "currency-service", "oteldemo.CurrencyService"]
_SHIPPING = ["shipping", "shipping-service"]
_PAYMENT = ["payment", "payment-service", "oteldemo.PaymentService"]

_BROWSE_CALLS = [
    _call(
        "browse.frontend.catalog.get_product",
        _FRONTEND,
        _CATALOG,
        protocol="grpc",
        operation_hint="ProductCatalogService/GetProduct",
    ),
    _db_call(
        "browse.catalog.postgresql.get_product",
        _CATALOG,
        "postgresql",
        "catalog",
        operation_hint="SELECT catalog.products by product id",
    ),
]

_ADD_CALLS = [
    *_BROWSE_CALLS,
    _call(
        "add.frontend.cart.add_item",
        _FRONTEND,
        _CART,
        protocol="grpc",
        operation_hint="CartService/AddItem",
    ),
    _db_call(
        "add.cart.redis.add_item",
        _CART,
        "redis",
        "cart",
        operation_hint="AddItem",
    ),
    _call(
        "add.frontend.cart.get_cart",
        _FRONTEND,
        _CART,
        protocol="grpc",
        operation_hint="CartService/GetCart",
    ),
    _db_call(
        "add.cart.redis.get_cart",
        _CART,
        "redis",
        "cart",
        operation_hint="GetCart",
    ),
]

_CHECKOUT_CALLS = [
    *_ADD_CALLS,
    _call(
        "checkout.frontend.checkout.place_order",
        _FRONTEND,
        _CHECKOUT,
        protocol="grpc",
        operation_hint="CheckoutService/PlaceOrder",
    ),
    _call(
        "checkout.checkout.cart.get_cart",
        _CHECKOUT,
        _CART,
        protocol="grpc",
        operation_hint="CartService/GetCart",
    ),
    _db_call(
        "checkout.cart.redis.get_cart",
        _CART,
        "redis",
        "cart",
        operation_hint="GetCart during PlaceOrder",
    ),
    _call(
        "checkout.checkout.catalog.get_product",
        _CHECKOUT,
        _CATALOG,
        protocol="grpc",
        operation_hint="ProductCatalogService/GetProduct",
    ),
    _db_call(
        "checkout.catalog.postgresql.price_product",
        _CATALOG,
        "postgresql",
        "catalog",
        operation_hint="SELECT catalog.products by product id",
    ),
    _call(
        "checkout.checkout.currency.convert_item",
        _CHECKOUT,
        _CURRENCY,
        protocol="grpc",
        operation_hint="CurrencyService/Convert",
        purpose="item price",
    ),
    _call(
        "checkout.checkout.shipping.quote",
        _CHECKOUT,
        _SHIPPING,
        protocol="http",
        operation_hint="POST /get-quote",
    ),
    _call(
        "checkout.checkout.currency.convert_shipping",
        _CHECKOUT,
        _CURRENCY,
        protocol="grpc",
        operation_hint="CurrencyService/Convert",
        purpose="shipping price",
    ),
    _call(
        "checkout.checkout.payment.charge",
        _CHECKOUT,
        _PAYMENT,
        protocol="grpc",
        operation_hint="PaymentService/Charge",
    ),
    _call(
        "checkout.checkout.shipping.ship",
        _CHECKOUT,
        _SHIPPING,
        protocol="http",
        operation_hint="POST /ship-order",
    ),
    _call(
        "checkout.frontend.catalog.enrich_response",
        _FRONTEND,
        _CATALOG,
        protocol="grpc",
        operation_hint="ProductCatalogService/GetProduct",
    ),
    _db_call(
        "checkout.catalog.postgresql.enrich_response",
        _CATALOG,
        "postgresql",
        "catalog",
        operation_hint="SELECT catalog.products by product id",
    ),
]


CONTRACTS: dict[str, dict[str, Any]] = {
    "browse_product": {
        "steps": [{"method": "GET", "path": f"/api/products/{PRODUCT_ID}",
                   "preflight_targets": [_CATALOG[0]]}],
        "entry_services": ENTRY_SERVICE_ALIASES,
        "required_calls": _BROWSE_CALLS,
    },
    "add_to_cart": {
        "steps": [
            {"method": "GET", "path": f"/api/products/{PRODUCT_ID}", "preflight_targets": [_CATALOG[0]]},
            {"method": "POST", "path": "/api/cart", "preflight_targets": [_CART[0]]},
        ],
        "entry_services": ENTRY_SERVICE_ALIASES,
        "required_calls": _ADD_CALLS,
    },
    "checkout": {
        "steps": [
            {"method": "GET", "path": f"/api/products/{PRODUCT_ID}", "preflight_targets": [_CATALOG[0]]},
            {"method": "POST", "path": "/api/cart", "preflight_targets": [_CART[0]]},
            {"method": "POST", "path": "/api/checkout?currencyCode=USD",
             "preflight_targets": [_CHECKOUT[0], _CART[0], _CATALOG[0], _CURRENCY[0], _SHIPPING[0], _PAYMENT[0]]},
        ],
        "entry_services": ENTRY_SERVICE_ALIASES,
        "required_calls": _CHECKOUT_CALLS,
    },
}


_PLAN_NAMESPACE = uuid.UUID("dc7947ae-23bf-43ee-8f2d-192d8ad2b32f")


def _v4_request(method: str, url: str, **kwargs: Any) -> requests.Response:
    from ebpf_discovery.transport_v4 import request

    return request(method, url, **kwargs)


class Adapter(LegacyAdapter):
    """Uncapped protocol-v4 workload over the established deployment."""

    def metadata(self) -> dict[str, Any]:
        metadata = super().metadata()
        # PostgreSQL container port in the pinned rendered deployment.
        metadata["database"].update(port=5432, system="postgresql")
        metadata["v4_contract"] = {
            "controlled_service_aliases": list(CONTROLLED_SERVICE_ALIASES),
            "contracts_module": "systems.otel_demo.experiment_v4.CONTRACTS",
            "catalog_database_mapping": self.selected_database_mapping(),
            "prediction_semantics": "required calls resolve against, but never modify, the recovered graph",
            "router_native_defaults_after_adapter_limits_removed": {
                "route_timeout_seconds": None,
                "route_timeout_configuration": "0s disables the Envoy route deadline",
                "connect_timeout_seconds": 5,
                "provenance": "explicitly disabled route deadline and native Envoy connect default",
            },
        }
        return metadata

    def selected_database_mapping(self) -> dict[str, Any]:
        """Return separately attributed deployment inventory for catalog SQL."""
        database = copy.deepcopy(super().metadata()["database"])
        return {
            "caller_aliases": list(CONTROLLED_SERVICE_ALIASES),
            "database_aliases": list(CATALOG_DATABASE_ALIASES),
            "db_system": "postgresql",
            "db_role": "catalog",
            "deployment": database,
            "provenance": "static adapter inventory; does not create a Bering node or edge",
        }

    def plan_operation(self, name: str, index: int, namespace: str) -> dict[str, Any]:
        if name not in CONTRACTS:
            raise ValueError(f"unsupported operation {name!r}")
        key = f"otel-demo-v4\0{namespace}\0{name}\0{index}"
        attempt_uuid = uuid.uuid5(_PLAN_NAMESPACE, key)
        return {
            "attempt_id": f"{namespace}-{name}-{index}-{attempt_uuid.hex[:12]}",
            "operation": name,
            "http_steps": [
                {
                    "request_id": uuid.uuid5(
                        _PLAN_NAMESPACE, f"{key}\0step\0{ordinal}"
                    ).hex,
                    "method": step["method"],
                    "path": step["path"],
                }
                for ordinal, step in enumerate(CONTRACTS[name]["steps"])
            ],
        }

    def operation(
        self,
        name: str,
        index: int,
        namespace: str,
        deadline: float | None = None,
    ) -> dict[str, Any]:
        """Execute one operation without an experiment timeout or clock gate."""
        if deadline is not None:
            raise ValueError("protocol v4 does not accept an experiment HTTP deadline")
        plan = self.plan_operation(name, index, namespace)
        fixture_token = uuid.uuid5(_PLAN_NAMESPACE, plan["attempt_id"]).hex
        user_id = f"u-{fixture_token}"
        record: dict[str, Any] = {
            "operation": name,
            "attempt_id": plan["attempt_id"],
            "started_ns": time.time_ns(),
            "ended_ns": None,
            "success": None,
            "http_steps": [],
            "request_plan": copy.deepcopy(plan["http_steps"]),
            "not_attempted_steps": [],
            "error": None,
            "observation": {
                "policy": "uncapped-v4",
                "deadline_seconds": None,
                "timestamp_eligibility_gate": False,
                "termination": None,
            },
        }

        bodies: list[dict[str, Any] | None] = [None] * len(plan["http_steps"])
        if name in {"add_to_cart", "checkout"}:
            bodies[1] = {
                "userId": user_id,
                "item": {"productId": PRODUCT_ID, "quantity": 1},
            }
        if name == "checkout":
            bodies[2] = {
                "userId": user_id,
                "email": f"{fixture_token}@example.invalid",
                "address": {
                    "streetAddress": "1 Observatory Way",
                    "city": "Testville",
                    "state": "CA",
                    "country": "US",
                    "zipCode": "94000",
                },
                "userCurrency": "USD",
                "creditCard": {
                    "creditCardNumber": "4432801561520454",
                    "creditCardCvv": 672,
                    "creditCardExpirationYear": 2039,
                    "creditCardExpirationMonth": 1,
                },
            }

        termination = "complete"
        try:
            for ordinal, planned in enumerate(plan["http_steps"]):
                step = self._http_step_v4(
                    record,
                    planned["method"],
                    planned["path"],
                    bodies[ordinal],
                    planned["request_id"],
                    ordinal,
                )
                if step["status"] != 200:
                    record["success"] = False
                    termination = "completed_response_mismatch"
                    self._mark_suffix_not_attempted(record, plan, ordinal + 1)
                    break
            else:
                record["success"] = True
        except requests.RequestException as exc:
            record["error"] = str(exc)
            record["success"] = None
            termination = "transport_incomplete"
            self._mark_suffix_not_attempted(record, plan, len(record["http_steps"]))
        finally:
            record["ended_ns"] = time.time_ns()
            record["observation"]["termination"] = termination

        record["user_id"] = user_id if name != "browse_product" else None
        if name == "checkout" and record["http_steps"]:
            final = record["http_steps"][-1]
            if final.get("ordinal") == 2 and isinstance(final.get("json"), dict):
                payload = final["json"]
                record["order_id"] = payload.get("orderId") or payload.get("order_id")
            record["async_expected"] = self._expected_async_postcondition()
        verified = self.verify([record])[0]
        if record.get("success") is True and verified.get("success") is False:
            verified["observation"]["termination"] = "completed_payload_mismatch"
        return verified

    @staticmethod
    def _mark_suffix_not_attempted(
        record: dict[str, Any], plan: dict[str, Any], start: int
    ) -> None:
        record["not_attempted_steps"] = [
            {**copy.deepcopy(step), "ordinal": ordinal, "state": "not_attempted"}
            for ordinal, step in enumerate(plan["http_steps"])
            if ordinal >= start
        ]

    def _http_step_v4(
        self,
        record: dict[str, Any],
        method: str,
        path: str,
        body: dict[str, Any] | None,
        request_id: str,
        ordinal: int,
    ) -> dict[str, Any]:
        started_ns = time.time_ns()
        request_bytes = (
            b"" if body is None else json.dumps(body, separators=(",", ":")).encode()
        )
        step: dict[str, Any] = {
            "ordinal": ordinal,
            "request_id": request_id,
            "method": method,
            "path": path,
            "url": self.entry_url + path,
            "state": "started",
            "started_ns": started_ns,
            "request_body_b64": base64.b64encode(request_bytes).decode("ascii"),
        }
        try:
            response = _v4_request(
                method,
                self.entry_url + path,
                json=body,
                timeout=None,
                journal=self.ctx.journal,
                headers={"X-Experiment-Request-Id": request_id},
            )
            step.update(
                state="complete",
                status=response.status_code,
                response_body_b64=base64.b64encode(response.content).decode("ascii"),
                ended_ns=int(getattr(response, "_study_body_completed_ns", time.time_ns())),
                transport_error=False,
                error=None,
            )
            try:
                step["json"] = response.json()
            except ValueError:
                step["json"] = None
        except requests.RequestException as exc:
            step.update(
                state="transport_incomplete",
                status=None,
                response_body_b64="",
                ended_ns=time.time_ns(),
                transport_error=True,
                error=str(exc),
                json=None,
            )
            record["http_steps"].append(step)
            raise
        record["http_steps"].append(step)
        return step

    def verify(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        verified: list[dict[str, Any]] = []
        for original in records:
            record = copy.deepcopy(original)
            expected_steps = CONTRACTS.get(record.get("operation"), {}).get("steps", [])
            actual = record.get("http_steps") or []
            if record.get("success") is None or len(actual) != len(expected_steps):
                record["payload_postcondition"] = None
                record["success"] = None if record.get("success") is None else False
                verified.append(record)
                continue
            if any(step.get("state") != "complete" or step.get("status") != 200 for step in actual):
                record["payload_postcondition"] = False
                record["success"] = False
                verified.append(record)
                continue
            step_postconditions: list[dict[str, Any]] = []
            for ordinal, step in enumerate(actual):
                payload = step.get("json")
                if ordinal == 0:
                    value = isinstance(payload, dict) and payload.get("id") == PRODUCT_ID
                    reason = "selected_product_id_matches" if value else "selected_product_id_mismatch"
                elif ordinal == 1:
                    value = self._cart_contains_selected_item(payload)
                    reason = "cart_contains_selected_item" if value else "cart_missing_selected_item"
                else:
                    order_id = (
                        payload.get("orderId") or payload.get("order_id")
                        if isinstance(payload, dict)
                        else None
                    )
                    order_ok = isinstance(order_id, str) and bool(order_id)
                    item_ok = self._checkout_contains_selected_item(payload)
                    value = order_ok and item_ok
                    reason = (
                        "checkout_order_and_item_match"
                        if value
                        else "checkout_order_or_item_mismatch"
                    )
                    record["order_id"] = order_id
                step_postconditions.append(
                    {
                        "ordinal": ordinal,
                        "request_id": step.get("request_id"),
                        "value": bool(value),
                        "reason": reason,
                    }
                )
            postcondition = all(item["value"] for item in step_postconditions)
            record["step_payload_postconditions"] = step_postconditions
            record["payload_postcondition"] = postcondition
            record["success"] = postcondition
            verified.append(record)
        return verified

    @staticmethod
    def _cart_contains_selected_item(payload: Any) -> bool:
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            return False
        return any(
            isinstance(item, dict)
            and item.get("productId") == PRODUCT_ID
            and item.get("quantity") == 1
            for item in payload["items"]
        )

    @staticmethod
    def _checkout_contains_selected_item(payload: Any) -> bool:
        """Match the pinned frontend's IProductCheckoutItem response shape."""
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            return False
        return any(
            isinstance(entry, dict)
            and isinstance(entry.get("item"), dict)
            and entry["item"].get("productId") == PRODUCT_ID
            and entry["item"].get("quantity") == 1
            for entry in payload["items"]
        )

    def set_consumer(self, up: bool) -> None:
        """Transition accounting immediately; v4 has no persistence-window hold."""
        if not up:
            self._compose("a", "stop -t 20 accounting", timeout=60)
            self._consumer_paused = True
            return
        self._compose("a", "start accounting", timeout=60)
        self._consumer_paused = False

    def observe_async(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Take exactly one independent SQL snapshot, including while paused."""
        return self._async_snapshot(records, phase="paused_snapshot")

    def verify_async(
        self, records: list[dict[str, Any]], deadline: float | None = None
    ) -> list[dict[str, Any]]:
        """Observe exact-ID persistence once, with no elapsed-time classification."""
        if deadline is not None:
            raise ValueError("protocol v4 async verification has no completion deadline")
        return self._async_snapshot(records, phase="post_resume_verification")

    def _async_snapshot(
        self, records: list[dict[str, Any]], phase: str
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for original in records:
            record = copy.deepcopy(original)
            order_id = record.get("order_id")
            observations: list[dict[str, Any]] = []
            success: bool | None = None
            state = "identity_unavailable"
            if isinstance(order_id, str) and _ORDER_ID.fullmatch(order_id):
                observation = self._read_order(order_id)
                observations.append(observation)
                if observation.get("complete") is True:
                    success = True
                    state = "persisted_exact"
                elif observation.get("terminal_wrong_persisted_payload") is True:
                    success = False
                    state = "persisted_mismatch"
                elif observation.get("query_ok") is True:
                    state = "pending"
                else:
                    state = "query_unavailable"
            else:
                record["async_error"] = "missing or unsafe order_id"
            record["async_verification"] = {
                "observation_policy": "uncapped-v4-single-snapshot",
                "phase": phase,
                "success": success,
                "state": state,
                "observations": observations,
                "evidence": "independent PostgreSQL read keyed only by returned order_id",
                "expected_postcondition": record.get("async_expected")
                or self._expected_async_postcondition(),
                "deadline_seconds": None,
            }
            results.append(record)
        return results

    @staticmethod
    def _expected_async_postcondition() -> dict[str, Any]:
        return {
            "items": [{"product_id": PRODUCT_ID, "quantity": 1}],
            "shipping_address": {
                "street_address": "1 Observatory Way",
                "city": "Testville",
                "state": "CA",
                "country": "US",
                "zip_code": "94000",
            },
        }

    def _envoy_config(self) -> str:
        """Remove v3's experiment-injected request/connect deadlines."""
        config = yaml.safe_load(super()._envoy_config())
        listener = config["static_resources"]["listeners"][0]
        manager = listener["filter_chains"][0]["filters"][0]["typed_config"]
        routes = manager["route_config"]["virtual_hosts"][0]["routes"]
        for route in routes:
            route.setdefault("route", {})["timeout"] = "0s"
        for cluster in config["static_resources"]["clusters"]:
            if cluster.get("name") == "product_catalog_replicas":
                cluster.pop("connect_timeout", None)
        return yaml.safe_dump(config, sort_keys=False)
