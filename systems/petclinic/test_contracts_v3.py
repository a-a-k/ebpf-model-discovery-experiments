import pytest

from systems.petclinic.contracts_v3 import (
    CONTRACTS,
    ENTRY_SERVICES,
    payload_verdict,
    status_ok,
    strict_json,
)


def fixture():
    return {
        "owners": [{"id": 1, "pets": []}],
        "details": {"id": 6, "pets": [{"id": 7, "visits": [{"id": 1}]}]},
        "vets": [{"id": 1, "specialties": []}],
    }


def test_interface_and_exact_status_predicates():
    assert ENTRY_SERVICES == {"ebpf": ["api-gateway"], "native": ["api-gateway"]}
    assert set(CONTRACTS) == {"list_owners", "owner_details_with_visits", "create_visit", "list_vets"}
    assert status_ok("list_owners", 0, 200)
    assert not status_ok("list_owners", 0, 201)
    assert status_ok("create_visit", 0, 201)
    assert not status_ok("create_visit", 0, 200)
    with pytest.raises(IndexError):
        status_ok("list_vets", 1, 200)


def test_strict_json_rejects_duplicate_keys_and_non_finite_numbers():
    with pytest.raises(ValueError, match="duplicate_json_key"):
        strict_json('{"id":1,"id":2}')
    with pytest.raises(ValueError, match="non_finite_json_constant"):
        strict_json('{"id":NaN}')


def test_read_payload_uses_exact_pinned_fixture_semantics():
    context = {"fixture": fixture()}
    assert payload_verdict("list_owners", '[{"id":1,"pets":[],"extra":true}]', context)["value"] is True
    verdict = payload_verdict(
        "owner_details_with_visits",
        '{"id":6,"pets":[{"id":7,"visits":[]}]}',
        context,
    )
    assert verdict["value"] is False
    assert verdict["reason"].startswith("payload_contract_mismatch:")


def test_invalid_complete_body_is_false_but_missing_fixture_is_unknown():
    assert payload_verdict("list_vets", "{", {"fixture": fixture()})["value"] is False
    assert payload_verdict("list_vets", "[]", {}) == {
        "value": None,
        "reason": "fixture_unavailable",
    }


def test_create_acknowledgment_never_claims_persistence():
    verdict = payload_verdict(
        "create_visit",
        '{"id":42,"petId":1,"date":"2026-09-01","description":"ebpf-study-deadbeef"}',
        {"fixture": fixture()},
    )
    assert verdict == {"value": None, "reason": "persistence_requires_independent_sql_oracle"}
