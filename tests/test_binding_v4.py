from ebpf_discovery.binding_v4 import endpoint_alias_evidence, matches_call_hint


class Store:
    def __init__(self, row, request_id="request-1"):
        self.row = row
        self.request_id = request_id

    def identity(self, source, trace, span):
        if (source, trace, span) == (self.row["source"], self.row["trace_id"], self.row["span_id"]):
            return [self.row]
        return []

    def candidates(self, source, request_id):
        return [self.row] if source == self.row["source"] and request_id == self.request_id else []


def root(**updates):
    value = {"source": "native", "trace_id": "1" * 32, "span_id": "2" * 16,
             "service": "frontend", "request_id": "request-1", "method": "GET",
             "path": "/api/products/OLJCESPC7Z", "binding_reason": "unique_declared_entry"}
    value.update(updates)
    return value


def observed(**updates):
    value = {"source": "native", "trace_id": "1" * 32, "span_id": "2" * 16,
             "service": "frontend", "node": "a", "raw_file": "traces.json:17",
             "attribute_conflicts": [], "attributes": {
                 "http.request.method": "GET",
                 "url.path": "/api/products/OLJCESPC7Z",
                 "http.route": "/api/products/[productId]/index",
             }}
    value.update(updates)
    return value


def test_exact_bound_root_retains_concrete_and_framework_endpoint_aliases():
    endpoints = [
        {"id": "concrete", "entry_service": "frontend", "method": "GET",
         "path": "/api/products/OLJCESPC7Z"},
        {"id": "next", "entry_service": "frontend", "method": "GET",
         "path": "/api/products/[productId]/index"},
        {"id": "other", "entry_service": "frontend", "method": "GET", "path": "/api/cart"},
    ]
    result = endpoint_alias_evidence(Store(observed()), [root()],
        {"method": "GET", "path": "/api/products/OLJCESPC7Z"}, "frontend", endpoints)
    assert result["endpoint_ids"] == ["concrete", "next"]
    assert result["evidence"][0]["endpoint_ids"] == ["concrete", "next"]
    assert result["evidence"][0]["provenance"] == {
        "source": "native", "request_id": "request-1", "trace_id": "1" * 32,
        "span_id": "2" * 16, "node": "a", "raw_file": "traces.json:17"}
    assert {item["attribute"] for item in result["evidence"][0]["observed_aliases"]} == {
        "url.path", "http.route"}


def test_endpoint_alias_requires_exact_selection_and_indexed_request_evidence():
    endpoint = [{"id": "next", "entry_service": "frontend", "method": "GET",
                 "path": "/api/products/[productId]/index"}]
    step = {"method": "GET", "path": "/api/products/OLJCESPC7Z"}
    assert not endpoint_alias_evidence(Store(observed()),
        [root(binding_reason="multiple_entries")], step, "frontend", endpoint)["endpoint_ids"]
    assert not endpoint_alias_evidence(Store(observed(), request_id="different"),
        [root()], step, "frontend", endpoint)["endpoint_ids"]
    assert not endpoint_alias_evidence(Store(observed(attribute_conflicts=[{"key": "http.route"}])),
        [root()], step, "frontend", endpoint)["endpoint_ids"]
    assert not endpoint_alias_evidence(Store(observed()),
        [root(service="other")], step, "frontend", endpoint)["endpoint_ids"]
    wrong_concrete = observed(attributes={
        "http.request.method": "GET", "url.path": "/api/products/WRONG",
        "http.route": "/api/products/[productId]/index"})
    assert not endpoint_alias_evidence(Store(wrong_concrete),
        [root()], step, "frontend", endpoint)["endpoint_ids"]


def test_relative_observed_route_matches_bering_leading_slash_endpoint_only():
    pet_root = root(
        service="customers-service", method="GET", path="/api/customer/owners")
    pet_row = observed(
        service="customers-service",
        attributes={
            "http.request.method": "GET",
            "url.path": "/api/customer/owners",
            "http.route": "customers",
        },
    )
    endpoints = [
        {"id": "framework-route", "entry_service": "customers-service",
         "method": "GET", "path": "/customers"},
        {"id": "wrong-route", "entry_service": "customers-service",
         "method": "GET", "path": "/owners"},
    ]
    result = endpoint_alias_evidence(
        Store(pet_row), [pet_root],
        {"method": "GET", "path": "/api/customer/owners"},
        "customers-service", endpoints,
    )
    assert result["endpoint_ids"] == ["framework-route"]
    assert {item["path"] for item in result["evidence"][0]["observed_aliases"]} == {
        "/api/customer/owners", "/customers"}


def test_rpc_hint_accepts_exact_rpc_and_grpc_over_http_post_tokens():
    assert matches_call_hint({"operation": "Convert"}, "CurrencyService/Convert") == (
        True, "rpc_method_token_exact")
    assert matches_call_hint({"operation": "oteldemo.CurrencyService/Convert"},
                             "oteldemo.CurrencyService/Convert")[0]
    assert matches_call_hint({"operation": "POST", "protocol": "http",
                              "route": "/oteldemo.CartService/AddItem"},
                             "CartService/AddItem",
                             permitted_services=("oteldemo.CartService",)) == (
        True, "rpc_over_http_post_route_exact")


def test_rpc_hint_requires_exact_qualified_namespace_or_explicit_contract_spelling():
    assert matches_call_hint({"operation": "other.pkg.CartService/AddItem"},
                             "oteldemo.CartService/AddItem") == (False, None)
    identity = {"operation": "POST", "route": "/other.pkg.CartService/AddItem"}
    assert matches_call_hint(identity, "CartService/AddItem") == (False, None)
    assert matches_call_hint(identity, "CartService/AddItem",
                             permitted_services=("oteldemo.CartService",)) == (False, None)
    assert matches_call_hint(identity, "CartService/AddItem",
                             permitted_services=("other.pkg.CartService",))[0]


def test_rpc_hint_rejects_wrong_method_service_get_and_substrings():
    hint = "oteldemo.CartService/AddItem"
    for identity in (
        {"operation": "POST", "route": "/oteldemo.CartService/GetCart"},
        {"operation": "POST", "route": "/oteldemo.OtherService/AddItem"},
        {"operation": "GET", "route": "/oteldemo.CartService/AddItem"},
        {"operation": "POST", "route": "/oteldemo.CartService/AddItemExtra"},
        {"operation": "AddItemExtra"},
    ):
        assert matches_call_hint(identity, hint) == (False, None)


def test_http_hint_keeps_exact_method_and_route_behavior():
    assert matches_call_hint({"operation": "POST", "route": "/get-quote"},
                             "POST /get-quote")[0]
    assert matches_call_hint({"operation": "GET", "route": "/get-quote"},
                             "POST /get-quote") == (False, None)
    assert matches_call_hint({"operation": "POST", "route": "/get-quote-extra"},
                             "POST /get-quote") == (False, None)
