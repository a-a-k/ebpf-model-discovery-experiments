from __future__ import annotations

import json
from pathlib import Path
import runpy

import pytest

from ebpf_discovery.deepflow_codec_v5 import codec_file
from ebpf_discovery.observations import otlp
from ebpf_discovery.runtime_identity_v5 import capture, inventory, resolve, resolve_all


def _owner(service="frontend", container="a" * 64):
    return {"container_id": container, "container_name": service + "-1",
            "image": "sha256:image", "config_image": "example@sha256:image",
            "container_started_at": "2026-10-29T00:00:00Z", "container_running": True,
            "compose": {"project": "application", "service": service,
                        "container_number": "1", "config_hash": "cfg", "oneoff": "False"},
            "ownership_proofs": ["exact_container_init_cgroup_set"]}


def _sample(stage, *, edge, pid=41, boot="boot-a", host_ns="pid:[100]",
            process_ns="pid:[200]", start_ticks=900, owner=None):
    point = 100 if edge == "before" else 200
    process = {"host_pid": pid, "state": "S", "comm": "server", "start_ticks": start_ticks,
               "pid_namespace": process_ns, "cgroups": [{"path": "/docker/a"}],
               "exe": "/app/server", "owner": _owner() if owner is None else owner}
    return {"schema": "runtime-identity-guest-sample-v5", "node": "a", "stage": stage,
            "boot_id": boot, "host_pid_namespace": host_ns, "clock_ticks_per_second": 100,
            "clocks": {"started": {"realtime_unix_ns": point, "monotonic_ns": point,
                                     "boottime_ns": point},
                       "ended": {"realtime_unix_ns": point, "monotonic_ns": point,
                                 "boottime_ns": point}},
            "containers": [], "docker_proof": {"list_returncode": 0, "inspect_returncode": 0},
            "processes": [process], "process_scan_errors": []}


def _inventory(before=None, after=None):
    return {"schema": "runtime-identity-inventory-v5", "captures": [],
            "samples": [before or _sample("before-block-1", edge="before"),
                        after or _sample("after-block-1", edge="after")]}


def _realtime_relation(*, node="a", boot="boot-a", pid_namespace="pid:[100]"):
    evidence = {"kind": "documented_clock_relation", "locator":
                f"runtime-identity-v5/clock-relation-{node}.json", "sha256": "f" * 64,
                "bytes": 123}
    return ({"domain": "guest_realtime_unix_ns",
             "relation": "documented_same_guest_realtime_relation", "evidence": evidence},
            {"node": node, "boot_id": boot, "pid_namespace": pid_namespace,
             "domain": "guest_realtime_unix_ns",
             "relation": "documented_same_guest_realtime_relation", "evidence": evidence,
             "verified_hash_bound_source_config_guest_relation": True,
             "host_receipt_time_used": False,
             "arbitrary_tolerance_or_age_filter_used": False,
             "clock_step_limitation_retained": True})


def _record(**updates):
    runtime = {"node": "a", "host_pid": 41, "pid_scope": "guest_host",
               "block_id": "block-1", "event_start_ns": 120, "event_end_ns": 180,
               "clock": {"domain": "guest_monotonic_ns",
                         "relation": "linux_bpf_ktime_get_ns",
                         "evidence": {"kind": "pinned_source", "locator": "source:1",
                                      "sha256": "c" * 64}},
               "event_role": "synchronous_server_entry", "method": "GET", "route": "/entry",
               "boot_id": "boot-a", "pid_namespace": "pid:[100]",
               "locator": {"raw_file": "events.jsonl", "offset": 17}}
    runtime.update(updates)
    return {"name": "observed event", "_runtime_identity": runtime}


def test_resolve_requires_exact_lifecycle_and_actual_compose_owner():
    result = resolve(_record(), _inventory())
    assert result["status"] == "resolved"
    assert result["service_identity"] == {
        "compose_project": "application", "compose_service": "frontend",
        "compose_container_number": "1", "container_id": "a" * 64,
        "container_name": "frontend-1"}
    assert result["process_identity"]["start_ticks"] == 900
    assert result["record_locator"] == {"raw_file": "events.jsonl", "offset": 17}
    assert result["graph_edges_injected"] is False

    nested = {"attributes": {"_runtime_identity": _record()["_runtime_identity"]}}
    assert resolve(nested, _inventory())["status"] == "resolved"
    flattened = {"attributes": {"_runtime_identity." + key: value
                                 for key, value in _record()["_runtime_identity"].items()}}
    assert resolve(flattened, _inventory())["status"] == "resolved"


@pytest.mark.parametrize(
    ("after", "reason"),
    [
        (_sample("after-block-1", edge="after", boot="boot-b"),
         "source_guest_boot_or_pid_namespace_mismatch"),
        (_sample("after-block-1", edge="after", host_ns="pid:[101]"),
         "source_guest_boot_or_pid_namespace_mismatch"),
        (_sample("after-block-1", edge="after", process_ns="pid:[201]"),
         "process_lifecycle_identity_changed"),
        (_sample("after-block-1", edge="after", start_ticks=901),
         "process_lifecycle_identity_changed"),
        (_sample("after-block-1", edge="after", owner=_owner(container="b" * 64)),
         "container_owner_changed"),
        (_sample("after-block-1", edge="after", owner=None), None),
    ],
)
def test_resolve_rejects_changed_identity(after, reason):
    if reason is None:  # default owner sentinel is intentional in the fixture helper
        after["processes"][0]["owner"] = None
        reason = "actual_container_owner_unobserved"
    result = resolve(_record(), _inventory(after=after))
    assert result["status"] == "unknown"
    assert reason in result["unknown_reasons"]


def test_delayed_or_unbracketed_records_and_receipt_time_do_not_bind():
    delayed = _record(event_start_ns=220, event_end_ns=230,
                      receipt_wall_ns=150, receipt_monotonic_ns=150)
    result = resolve(delayed, _inventory())
    assert result["unknown_reasons"] == ["source_event_not_bracketed"]

    no_source_clock = _record(clock=None, event_start_ns=None, event_end_ns=None,
                              receipt_wall_ns=150)
    result = resolve(no_source_clock, _inventory())
    assert result["unknown_reasons"] == ["source_clock_relation_unsupported"]


def test_source_record_must_carry_the_same_guest_boot_and_host_pid_namespace():
    assert resolve(_record(boot_id="other"), _inventory())["unknown_reasons"] == [
        "source_guest_boot_or_pid_namespace_mismatch"]


@pytest.mark.parametrize("value", ["01", "0", "-1", "+1", "1.0", 1.0, True])
def test_host_pid_rejects_noncanonical_or_coerced_values(value):
    assert resolve(_record(host_pid=value), _inventory())["unknown_reasons"] == [
        "guest_node_or_host_pid_invalid"]


def test_canonical_decimal_event_bounds_are_supported_and_recorded():
    result = resolve(_record(host_pid="41", event_start_ns="120", event_end_ns="180"),
                     _inventory())
    assert result["status"] == "resolved"
    assert result["representation_normalization"]["host_pid"] == {
        "original": "41", "canonical_integer": 41}
    assert result["representation_normalization"]["event_start_ns"]["canonical_integer"] == 120
    assert resolve(_record(pid_namespace="pid:[999]"), _inventory())["unknown_reasons"] == [
        "source_guest_boot_or_pid_namespace_mismatch"]


def test_whole_fresh_capture_lifetime_is_the_only_clockless_alternative():
    retained = _inventory()
    retained["capture_lifetimes"] = [{
        "source_capture_id": "deepflow-fresh-a", "node": "a",
        "before_stage": "before-block-1", "after_stage": "after-block-1",
        "fresh_capture": True, "closed_capture": True, "technical_complete": True,
        "opened_after_before_sample": True, "closed_before_after_sample": True,
        "runner_monotonic_sequence": {"before_sample_completed_ns": 10,
                                      "capture_opened_ns": 20, "capture_closed_ns": 30,
                                      "after_sample_started_ns": 40},
        "evidence": {"kind": "retained_capture_lifecycle", "locator": "capture.json",
                     "sha256": "d" * 64}}]
    record = _record(clock={"domain": "deepflow_derived_epoch_us", "relation": "derived",
                            "evidence": {"source": "pinned"}},
                     source_capture_id="deepflow-fresh-a")
    result = resolve(record, retained)
    assert result["status"] == "resolved"
    assert result["bracket"]["kind"] == "whole_fresh_capture_lifetime"
    assert result["bracket"]["before_ended_ns"] is None

    retained["capture_lifetimes"][0]["closed_before_after_sample"] = False
    assert resolve(record, retained)["unknown_reasons"] == ["source_clock_relation_unsupported"]


def test_exact_fresh_request_nonce_encloses_event_without_clock_conversion():
    retained = _inventory()
    locator = {"source_file": "events.jsonl", "retained_file": "raw/events.jsonl",
               "offset": 17, "length": 42, "sha256": "a" * 64}
    retained["event_enclosures"] = [{
        "request_nonce": "fresh-opaque-nonce", "node": "a", "record_locator": locator,
        "method": "GET", "route": "/entry",
        "before_stage": "before-block-1", "after_stage": "after-block-1",
        "source_event_contains_exact_nonce": True, "synchronous_server_entry": True,
        "terminal_request_exchange": True,
        "technical_complete": True,
        "runner_monotonic_sequence": {"before_sample_completed_ns": 10,
                                      "request_started_ns": 20, "request_completed_ns": 30,
                                      "after_sample_started_ns": 40},
        "evidence": {"kind": "retained_exact_nonce", "locator": "nonce-proof.json",
                     "sha256": "e" * 64}}]
    record = _record(clock={"domain": "derived_epoch", "relation": "unknown"},
                     request_nonce="fresh-opaque-nonce", locator=locator)
    result = resolve(record, retained)
    assert result["status"] == "resolved"
    assert result["bracket"]["kind"] == "exact_request_nonce"
    assert result["bracket"]["request_nonce"] == "fresh-opaque-nonce"

    retained["event_enclosures"][0]["terminal_request_exchange"] = False
    assert resolve(record, retained)["unknown_reasons"] == ["source_clock_relation_unsupported"]

    retained["event_enclosures"][0]["terminal_request_exchange"] = True
    descendant = _record(clock={"domain": "derived_epoch", "relation": "unknown"},
                         request_nonce="fresh-opaque-nonce", locator=locator,
                         event_role="async_descendant")
    assert resolve(descendant, retained)["unknown_reasons"] == ["source_clock_relation_unsupported"]


def test_clock_domain_requires_documented_compatible_source_relation():
    unsupported = _record(clock={"domain": "host_receipt_ns", "relation": "same_machine",
                                 "evidence": {"guess": True}})
    assert resolve(unsupported, _inventory())["unknown_reasons"] == [
        "source_clock_relation_unsupported"]
    clock, relation = _realtime_relation()
    realtime = _record(clock=clock)
    retained = _inventory(); retained["clock_relations"] = [relation]
    assert resolve(realtime, retained)["status"] == "resolved"
    assert resolve(realtime, _inventory())["unknown_reasons"] == [
        "source_clock_relation_evidence_unverified"]
    unproven = _record(clock={"domain": "guest_monotonic_ns", "relation": "assumed",
                              "evidence": {"guess": True}})
    assert resolve(unproven, _inventory())["unknown_reasons"] == [
        "source_clock_compatibility_unproven"]


def test_saved_deepflow_database_row_uses_shared_domain_but_keeps_identity_contradictions():
    """Values are a minimized exact-field fixture from saved pilot 40910393953."""
    start, end = 1793291175425018000, 1793291175425170000
    boot, host_ns, process_ns = ("11dd547e-1a21-4b17-888c-897ad58c5137",
                                  "pid:[4026531836]", "pid:[4026532325]")
    container = "220cfb2db41cdb524a5733691f264e6e9b10ce03ddf98927f2d1472c69dccdee"
    owner = _owner(service="database", container=container)
    owner.update(container_name="petclinic-a-database-1",
                 container_started_at="2026-10-29T16:23:44.874129527Z")
    owner["compose"].update(project="petclinic-a")
    before = _sample("before-calibration-01", edge="before", pid=6367, boot=boot,
                     host_ns=host_ns, process_ns=process_ns, start_ticks=18479, owner=owner)
    after = _sample("after-calibration-01", edge="after", pid=6367, boot=boot,
                    host_ns=host_ns, process_ns=process_ns, start_ticks=18479, owner=owner)
    before["clocks"]["ended"]["realtime_unix_ns"] = 1793291174315809454
    after["clocks"]["started"]["realtime_unix_ns"] = 1793291176727728171
    clock, relation = _realtime_relation(boot=boot, pid_namespace=host_ns)
    retained = _inventory(before, after); retained["clock_relations"] = [relation]
    row = _record(host_pid="6367", before_stage=None,
                  after_stage=None, block_id=None, event_start_ns=str(start),
                  event_end_ns=str(end), clock=clock, boot_id=boot, pid_namespace=host_ns,
                  locator={"source_file": "a/l7_flow_log",
                           "retained_file": "deepflow-raw/node-a/002-live-prefix/l7_flow_log",
                           "offset": "1758911", "length": "1168",
                           "sha256": "e1d15827e5ff030d17f215791ee5114c538681292840e91ff7ae5aeebdebb967"})
    result = resolve(row, retained)
    assert result["status"] == "resolved"
    assert result["service_identity"]["compose_service"] == "database"
    assert result["bracket"]["kind"] == "source_event_clock"
    assert result["canonical_record_locator"]["offset"] == 1758911

    after["processes"][0]["start_ticks"] = 18480
    assert resolve(row, retained)["unknown_reasons"] == ["process_lifecycle_identity_changed"]


def test_actual_compose_labels_are_required_not_expected_topology():
    owner = _owner()
    owner["compose"]["service"] = None
    before = _sample("before-block-1", edge="before", owner=owner)
    after = _sample("after-block-1", edge="after", owner=owner)
    result = resolve(_record(expected_service="frontend", ip="10.0.0.4"),
                     _inventory(before, after))
    assert result["unknown_reasons"] == ["actual_compose_service_identity_unobserved"]


@pytest.mark.parametrize("field", ["container_id", "container_name", "image", "container_started_at"])
def test_container_lifetime_identity_fields_must_be_nonempty(field):
    owner = _owner()
    owner[field] = None
    before = _sample("before-block-1", edge="before", owner=owner)
    after = _sample("after-block-1", edge="after", owner=owner)
    assert resolve(_record(), _inventory(before, after))["unknown_reasons"] == [
        "container_lifecycle_or_ownership_proof_missing"]


def test_shared_root_cgroup_is_not_container_ownership_evidence():
    helper = runpy.run_path(str(Path(__file__).parents[1] / "scripts" /
                                "runtime-identity-v5-guest.py"))
    owner = helper["_owner"]
    container = {"id": "a" * 64, "name": "service-1", "image": "sha256:image",
                 "config_image": "image", "state": {"Pid": 10, "Running": True,
                 "StartedAt": "now"}, "compose": {"project": "p", "service": "s"},
                 "init_cgroups": [{"path": "/"}]}
    assert owner(11, [{"path": "/"}], [container]) is None
    assert "container_init_host_pid" in owner(10, [{"path": "/"}], [container])[
        "ownership_proofs"]
    container["init_cgroups"] = [{"path": "/docker/" + "a" * 64}]
    assert "exact_container_init_cgroup_set" in owner(
        11, [{"path": "/docker/" + "a" * 64}], [container])["ownership_proofs"]


def test_real_deepflow_codec_otlp_round_trip_resolves_canonical_locator(tmp_path):
    raw = tmp_path / "l7_flow_log"
    row = {"signal_source": "EBPF", "tap_side": "ServerProcess",
           "ebpf_type": "TracePoint", "l7_protocol": "Http1", "msg_type": "Request",
           "start_time": 10, "end_time": 20, "ip_src": "192.0.2.1",
           "ip_dst": "192.0.2.2", "port_src": 41000, "port_dst": 8080,
           "process_id_1": 123, "process_kname_1": "frontend",
           "request_type": "GET", "request_resource": "/items/7",
           "request_domain": "example.test", "version": "1.1",
           "x_request_id_0": "fresh-codec-nonce"}
    raw.write_text(json.dumps(row, separators=(",", ":")) + "\n", encoding="utf-8")
    batches, accounting, _ = codec_file(
        raw, node="a", source_file="a/l7_flow_log", retained_file="raw/a/l7_flow_log",
        guest_context={"boot_id": "boot-a", "pid_namespace": "pid:[100]"})
    normalized = list(otlp(batches[0]["payload"], "ebpf", "a"))[0]
    retained = _inventory(
        _sample("before-block-1", edge="before", pid=123),
        _sample("after-block-1", edge="after", pid=123))
    accounting_locator = accounting[0]["_runtime_identity"]["locator"]
    retained["event_enclosures"] = [{
        "request_nonce": "fresh-codec-nonce", "node": "a",
        "record_locator": accounting_locator, "method": "GET", "route": "/items/7",
        "before_stage": "before-block-1", "after_stage": "after-block-1",
        "source_event_contains_exact_nonce": True, "synchronous_server_entry": True,
        "terminal_request_exchange": True, "technical_complete": True,
        "runner_monotonic_sequence": {"before_sample_completed_ns": 10,
                                      "request_started_ns": 20, "request_completed_ns": 30,
                                      "after_sample_started_ns": 40},
        "evidence": {"kind": "retained_exact_nonce", "locator": "nonce-proof.json",
                     "sha256": "e" * 64}}]
    result = resolve(normalized, retained)
    assert result["status"] == "resolved"
    assert type(result["record_locator"]["offset"]) is str
    assert type(accounting_locator["offset"]) is int
    assert result["canonical_record_locator"] == accounting_locator
    locator_proof = result["representation_normalization"]["locator"]
    assert locator_proof["original"] == result["record_locator"]
    assert locator_proof["canonical"] == accounting_locator
    assert locator_proof["enclosure_original"] == accounting_locator
    assert locator_proof["enclosure_canonical"] == accounting_locator


def test_real_deepflow_codec_clock_relation_survives_otlp_numeric_representation(tmp_path):
    raw = tmp_path / "l7_flow_log"
    row = {"signal_source": "EBPF", "tap_side": "ClientProcess",
           "ebpf_type": "TracePoint", "l7_protocol": "MySQL", "msg_type": "Session",
           "start_time": 10, "end_time": 20, "ip_src": "192.0.2.1",
           "ip_dst": "192.0.2.2", "port_src": 41000, "port_dst": 3306,
           "process_id_0": 41, "process_kname_0": "mysqld", "request_type": "COM_QUERY"}
    raw.write_text(json.dumps(row, separators=(",", ":")) + "\n", encoding="utf-8")
    clock, relation = _realtime_relation()
    batches, _, _ = codec_file(
        raw, node="a", guest_context={"boot_id": "boot-a", "pid_namespace": "pid:[100]"},
        runtime_clock=clock)
    normalized = list(otlp(batches[0]["payload"], "ebpf", "a"))[0]
    before, after = _sample("before-block-1", edge="before"), _sample(
        "after-block-1", edge="after")
    before["clocks"]["ended"]["realtime_unix_ns"] = 9_000
    after["clocks"]["started"]["realtime_unix_ns"] = 21_000
    retained = _inventory(before, after); retained["clock_relations"] = [relation]
    result = resolve(normalized, retained)
    assert result["status"] == "resolved"
    assert result["service_identity"]["compose_service"] == "frontend"
    assert normalized["attributes"]["_runtime_identity.clock"]["evidence"]["bytes"] == "123"
    # The serialized end floor (20_000) would fit, but its exact source-defined
    # microsecond bin extends through 20_999 and therefore is not bracketed.
    normalized["attributes"]["_runtime_identity.before_stage"] = "before-block-1"
    normalized["attributes"]["_runtime_identity.after_stage"] = "after-block-1"
    after["clocks"]["started"]["realtime_unix_ns"] = 20_500
    assert resolve(normalized, retained)["unknown_reasons"] == ["source_event_not_bracketed"]


def test_coverage_reports_unknowns_without_dropping_original_locators():
    report = resolve_all([_record(), _record(host_pid=99)], _inventory())
    assert report["records"] == 2
    assert report["resolved"] == 1
    assert report["unknown"] == 1
    assert report["unknown_reasons"] == {"pid_not_observed_in_both_brackets": 1}
    assert report["results"][1]["record_locator"]["offset"] == 17


class _Result:
    returncode = 0
    stderr = ""

    def __init__(self, stdout):
        self.stdout = stdout


class _Context:
    def __init__(self, root):
        self.out = root
        self.puts = []
        self.calls = []

    def node_put(self, node, source, destination):
        self.puts.append((node, Path(source), destination))

    def node_exec(self, node, command, **kwargs):
        self.calls.append((node, command, kwargs))
        assert command.startswith("sudo python3 /tmp/runtime-identity-v5-")
        sample = _sample("before-block-1", edge="before")
        sample["node"] = node
        return _Result(json.dumps(sample))


def test_capture_retains_raw_normalized_and_cost_separately(tmp_path):
    ctx = _Context(tmp_path)
    retained = capture(ctx, "before-block-1")
    assert {sample["node"] for sample in retained["samples"]} == {"a", "b"}
    assert retained["errors"] == []
    assert set(retained["files"]) == {
        "raw-before-block-1-a.json", "raw-before-block-1-a.stderr.log",
        "sample-before-block-1-a.json", "raw-before-block-1-b.json",
        "raw-before-block-1-b.stderr.log", "sample-before-block-1-b.json",
        "cost-before-block-1.json"}
    merged = inventory([retained])
    assert merged["schema"] == "runtime-identity-inventory-v5"
    assert len(merged["samples"]) == 2
    assert all(len(value["sha256"]) == 64 for value in retained["files"].values())
    assert len(ctx.puts) == 2
    assert len(ctx.calls) == 2
    assert retained["helper"]["commands"] == {
        node: command for node, command, _ in ctx.calls}
    cost = json.loads((tmp_path / "runtime-identity-v5" /
                       "cost-before-block-1.json").read_text())
    assert all(row["command"].startswith("sudo python3 ")
               for row in cost["by_node"].values())
    assert all("read-only" in row["privilege_scope"]
               for row in cost["by_node"].values())
    assert retained["runner_interval"]["started_monotonic_ns"] <= (
        retained["runner_interval"]["ended_monotonic_ns"])
