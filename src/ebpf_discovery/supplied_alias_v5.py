"""Training-frozen supplied logical aliases; never physical identity inference."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time


SCHEMA = "supplied-logical-service-aliases-v5"
ORIGIN = "supplied_deployment_inventory_alias"
ADMISSION_SCHEMA = "supplied-logical-alias-admission-v5"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def admission_core(value: dict) -> dict:
    """Canonical admission fields; lifecycle summaries cannot change row identity."""
    keys = ("schema", "origin", "aliases", "conflicts", "occurrence_proofs",
            "scoped_digest_aliases", "verified_scoped_digest_roles",
            "unique_verified_segments", "receiver_segments_reverified",
            "same_table_all_sources_and_direct_baseline", "physical_identity_inferred")
    return {key: deepcopy(value.get(key)) for key in keys}


def admission_sha256(value: dict) -> str:
    return hashlib.sha256(json.dumps(
        admission_core(value), sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode()).hexdigest()


def write_admission(value: dict, table_path: Path, out: Path) -> dict:
    retained = deepcopy(value)
    retained["table"] = {"path": table_path.relative_to(out.parent.parent).as_posix(),
                         "sha256": _sha(table_path), "bytes": table_path.stat().st_size}
    out.write_text(json.dumps(retained, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return retained


def load_admission(path: Path, root: Path, table: dict) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != ADMISSION_SCHEMA or value.get("origin") != ORIGIN:
        raise ValueError("supplied logical alias admission schema/origin mismatch")
    proof = value.get("table") or {}
    table_path = Path(proof.get("path", ""))
    if not table_path.is_absolute():
        table_path = root / table_path
    if (not table_path.is_file() or table_path.stat().st_size != proof.get("bytes")
            or _sha(table_path) != proof.get("sha256")
            or json.loads(table_path.read_text(encoding="utf-8")) != table):
        raise ValueError("supplied logical alias admission table dependency changed")
    return value


def build(inventory: dict, *, inventory_proof: dict) -> dict:
    """Build exact guest/name aliases from retained Compose labels."""
    started = time.monotonic_ns()
    observed: dict[tuple[str, str], set[tuple[str, str]]] = {}
    occurrences: dict[tuple[str, str], int] = {}
    for sample in inventory.get("samples") or []:
        node = sample.get("node")
        if node not in ("a", "b"):
            continue
        for container in sample.get("containers") or []:
            name = container.get("name")
            compose = container.get("compose") or {}
            project, service = compose.get("project"), compose.get("service")
            if not all(isinstance(value, str) and value for value in (name, project, service)):
                continue
            key = (node, name)
            observed.setdefault(key, set()).add((project, service))
            occurrences[key] = occurrences.get(key, 0) + 1
    rows, conflicts = [], []
    for (node, name), roles in sorted(observed.items()):
        if len(roles) != 1:
            conflicts.append({"node": node, "container_name": name,
                              "logical_roles": [list(role) for role in sorted(roles)],
                              "reason": "scoped_name_maps_to_multiple_logical_roles"})
            continue
        project, service = next(iter(roles))
        rows.append({"node": node, "container_name": name,
                     "carriers": [name, "/docker/" + name],
                     "compose_project": project, "compose_service": service,
                     "inventory_occurrences": occurrences[node, name], "origin": ORIGIN})
    # A post-Bering semantic view has no guest field. Only carriers whose scoped
    # rows agree globally are admissible there; guest collisions stay unknown.
    global_roles: dict[str, set[str]] = {}
    for row in rows:
        for carrier in row["carriers"]:
            global_roles.setdefault(carrier, set()).add(row["compose_service"])
    global_aliases = {carrier: next(iter(roles)) for carrier, roles in sorted(global_roles.items())
                      if len(roles) == 1}
    global_conflicts = [{"carrier": carrier, "logical_services": sorted(roles),
                         "reason": "cross_guest_carrier_maps_to_multiple_logical_roles"}
                        for carrier, roles in sorted(global_roles.items()) if len(roles) != 1]
    return {"schema": SCHEMA, "stage": "training", "origin": ORIGIN,
            "claim_scope": "supplied logical service role only; no physical identity or causality",
            "inventory": dict(inventory_proof), "rows": rows, "conflicts": conflicts,
            "global_aliases": global_aliases, "global_conflicts": global_conflicts,
            "same_table_all_sources_and_direct_baseline": True,
            "manual_baseline_information": "identical exact carrier-to-Compose.service rows",
            "direct_baseline": {
                "mapping_source": "rows",
                "application": "exact supplied carrier-to-Compose.service lookup",
                "same_information": True,
                "manual_preparation_seconds": None,
            },
            "generation_elapsed_seconds": (time.monotonic_ns() - started) / 1e9,
            "manual_preparation_seconds": None}


def write_training(inventory: dict, inventory_path: Path, out: Path) -> dict:
    proof_path = inventory_path.relative_to(out.parent.parent).as_posix()
    proof = {"path": proof_path, "sha256": _sha(inventory_path),
             "bytes": inventory_path.stat().st_size}
    value = build(inventory, inventory_proof=proof)
    out.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"path": out.as_posix(), "sha256": _sha(out), "bytes": out.stat().st_size,
            "rows": len(value["rows"]), "conflicts": len(value["conflicts"]),
            "global_aliases": len(value["global_aliases"]),
            "generation_elapsed_seconds": value["generation_elapsed_seconds"]}


def load(path: Path, root: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != SCHEMA or value.get("stage") != "training":
        raise ValueError("supplied logical alias table schema/stage mismatch")
    proof = value.get("inventory") or {}
    inventory_path = Path(proof.get("path", ""))
    if not inventory_path.is_absolute():
        inventory_path = root / inventory_path
    if (not inventory_path.is_file() or inventory_path.stat().st_size != proof.get("bytes")
            or _sha(inventory_path) != proof.get("sha256")):
        raise ValueError("supplied logical alias inventory dependency changed")
    if value.get("same_table_all_sources_and_direct_baseline") is not True:
        raise ValueError("supplied logical aliases are not declared common to all comparators")
    baseline = value.get("direct_baseline") or {}
    if (baseline.get("mapping_source") != "rows"
            or baseline.get("same_information") is not True
            or baseline.get("manual_preparation_seconds", object()) is not None):
        raise ValueError("direct baseline does not receive the same supplied alias rows/cost field")
    return value


def admit_observed(store, table: dict, *, expected_source_prefix: str | None = None) -> dict:
    """Admit aliases only when every retained occurrence has a matching guest row."""
    if store is None or not hasattr(store, "db"):
        return {"schema": ADMISSION_SCHEMA, "origin": ORIGIN,
                "aliases": {}, "conflicts": [], "receiver_segments_reverified": False,
                "scoped_digest_aliases": {},
                "verified_scoped_digest_roles": {},
                "reason": "observation_store_unavailable",
                "same_table_all_sources_and_direct_baseline": True,
                "physical_identity_inferred": False}
    scoped = {(row["node"], carrier): row["compose_service"]
              for row in table.get("rows") or [] for carrier in row.get("carriers") or []}
    scoped_carriers = {carrier for _, carrier in scoped}
    by_carrier: dict[str, dict] = {}
    scoped_digest_candidates: dict[str, tuple[str, str]] = {}
    observed_by_source: dict[str, set[str]] = {}
    carrier_sources: dict[str, set[str]] = {}
    segment_cache: dict[tuple, dict] = {}
    occurrence_proofs = []
    for digest, encoded in store.db.execute("SELECT digest,data FROM spans ORDER BY digest"):
        row = json.loads(encoded)
        carrier = row.get("service")
        source = row.get("source")
        if isinstance(carrier, str) and carrier:
            observed_by_source.setdefault(source, set()).add(carrier)
            carrier_sources.setdefault(carrier, set()).add(source)
        if source != "ebpf":
            continue
        if not isinstance(carrier, str) or carrier not in scoped_carriers:
            continue
        occurrences = list(store.db.execute(
            "SELECT raw_file,from_byte,through_byte,normalized_ordinal,segment_sha256 "
            "FROM observation_provenance WHERE digest=? ORDER BY raw_file,from_byte", (digest,)))
        source_node = row.get("node")
        container_carrier = (row.get("resource") or {}).get("container.id")
        nodes, valid = set(), bool(occurrences) and source_node in ("a", "b")
        if container_carrier not in (None, "", carrier):
            valid = False
        for raw_file, start, end, ordinal, expected in occurrences:
            path = Path(raw_file)
            if not path.is_file() and hasattr(store, "path"):
                parts = path.parts
                if "observations" in parts:
                    relative = Path(*parts[parts.index("observations"):])
                    candidate = (Path(store.path).parent / relative).resolve()
                    if candidate.is_relative_to(Path(store.path).parent.resolve()):
                        path = candidate
            node = path.stem if path.stem in ("a", "b") else None
            if node is None:
                valid = False
                continue
            key = (str(path.resolve()), start, end, expected)
            if key not in segment_cache:
                with path.open("rb") as stream:
                    stream.seek(start)
                    body = stream.read(end - start)
                if len(body) != end - start or hashlib.sha256(body).hexdigest() != expected:
                    raise ValueError("supplied alias receiver provenance changed")
                try:
                    wrappers = [json.loads(line) for line in body.splitlines() if line.strip()]
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ValueError("supplied alias receiver segment is malformed") from exc
                wrapper_sources = set()
                for wrapper in wrappers:
                    wrapper_node, wrapper_source = wrapper.get("node"), wrapper.get("source")
                    if (wrapper_node != node or not isinstance(wrapper_source, str)
                            or wrapper_source != (expected_source_prefix + ":" + node
                                if expected_source_prefix else wrapper_source)
                            or not wrapper_source.endswith(":" + node)
                            or not isinstance(wrapper.get("payload"), dict)):
                        raise ValueError("supplied alias wrapper source/node mismatch")
                    raw_ref, metadata_ref = wrapper.get("raw_ref"), wrapper.get("raw_metadata_ref")
                    if not isinstance(raw_ref, str) or not isinstance(metadata_ref, str):
                        raise ValueError("supplied alias wrapper lacks raw receiver references")
                    raw_path, metadata_path = path.parent / raw_ref, path.parent / metadata_ref
                    if (not raw_path.is_file() or not metadata_path.is_file()
                            or hashlib.sha256(raw_path.read_bytes()).hexdigest()
                            != wrapper.get("raw_sha256")
                            or raw_path.stat().st_size != wrapper.get("raw_size_bytes")):
                        raise ValueError("supplied alias raw receiver body changed")
                    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                    required = ("source", "node", "received_ns", "raw_ref",
                                "raw_sha256", "raw_size_bytes")
                    if any(metadata.get(field) != wrapper.get(field) for field in required):
                        raise ValueError("supplied alias raw receiver metadata mismatch")
                    wrapper_sources.add(wrapper_source)
                from .store_v5 import _digest
                from .store_v3 import normalized_file
                normalized = list(normalized_file(
                    path, "ebpf", start, end,
                    same_trace_parents=getattr(store, "same_trace_parents", False)))
                segment_cache[key] = {
                    "node": node, "sources": sorted(wrapper_sources),
                    "ordinals": {index: _digest(record)
                                 for index, record in enumerate(normalized)}}
            verified = segment_cache[key]
            if verified["ordinals"].get(ordinal) != digest:
                raise ValueError("supplied alias normalized ordinal/digest mismatch")
            nodes.add(verified["node"])
            proof_path = str(path)
            if hasattr(store, "path"):
                try:
                    proof_path = path.resolve().relative_to(
                        Path(store.path).parent.resolve()).as_posix()
                except ValueError:
                    raise ValueError(
                        "supplied alias receiver proof is outside the campaign root")
            occurrence_proofs.append({
                "digest": digest, "path": proof_path, "from_byte": start,
                "through_byte": end, "normalized_ordinal": ordinal,
                "segment_sha256": expected, "wrapper_node": verified["node"],
                "wrapper_sources": verified["sources"]})
        if nodes != {source_node}:
            valid = False
        entry = by_carrier.setdefault(carrier, {"nodes": set(), "valid": True, "digests": []})
        entry["nodes"].update(nodes)
        entry["valid"] = entry["valid"] and valid
        entry["digests"].append(digest)
        roles = {scoped.get((node, carrier)) for node in nodes}
        if valid and nodes and None not in roles and len(roles) == 1:
            scoped_digest_candidates[digest] = (carrier, next(iter(roles)))
    candidates, conflicts = {}, []
    for carrier, evidence in sorted(by_carrier.items()):
        roles = {scoped.get((node, carrier)) for node in evidence["nodes"]}
        if evidence["valid"] and evidence["nodes"] and None not in roles and len(roles) == 1:
            candidates[carrier] = next(iter(roles))
        elif carrier in scoped_carriers:
            conflicts.append({"carrier": carrier, "nodes": sorted(evidence["nodes"]),
                              "logical_services": sorted(role for role in roles if role),
                              "reason": "receiver_scope_missing_ambiguous_or_conflicting"})
    # Resolve presentation collisions before any common selector consumes the
    # effective Store view. Refusing an otherwise plausible alias is safer than
    # merging service nodes whose non-name metadata is only known after Bering.
    by_target: dict[str, set[str]] = {}
    for carrier, logical in candidates.items():
        by_target.setdefault(logical, set()).add(carrier)
    admitted = {}
    for carrier, logical in sorted(candidates.items()):
        sources = carrier_sources.get(carrier, set())
        target_conflict_sources = sorted(
            source for source in sources
            if logical != carrier and logical in observed_by_source.get(source, set()))
        colliders = sorted(other for other in by_target[logical]
                           if carrier_sources.get(other, set()) & sources)
        if target_conflict_sources:
            conflicts.append({"carrier": carrier, "logical_service": logical,
                              "sources": target_conflict_sources,
                              "reason": "logical_target_already_observed_as_service"})
        elif len(colliders) != 1:
            conflicts.append({"carrier": carrier, "logical_service": logical,
                              "colliding_carriers": colliders,
                              "reason": "multiple_observed_carriers_share_logical_target"})
        else:
            admitted[carrier] = logical
    scoped_digest_aliases = {
        digest: logical for digest, (carrier, logical) in sorted(scoped_digest_candidates.items())
        if admitted.get(carrier) == logical}
    verified_scoped_digest_roles = {
        digest: {"carrier": carrier, "logical_service": logical}
        for digest, (carrier, logical) in sorted(scoped_digest_candidates.items())}
    return {"schema": ADMISSION_SCHEMA, "origin": ORIGIN,
            "aliases": admitted, "conflicts": conflicts,
            "scoped_digest_aliases": scoped_digest_aliases,
            "verified_scoped_digest_roles": verified_scoped_digest_roles,
            "occurrence_proofs": occurrence_proofs,
            "unique_verified_segments": len(segment_cache),
            "receiver_segments_reverified": True,
            "same_table_all_sources_and_direct_baseline": True,
            "physical_identity_inferred": False}


def semantic_view(model: dict, quality: dict, table: dict,
                  admitted_aliases: dict | None = None) -> tuple[dict, dict, dict]:
    """Return a copied logical-role presentation while preserving raw output."""
    aliases = dict(admitted_aliases if admitted_aliases is not None
                   else table.get("global_aliases") or {})
    grouped: dict[str, list[dict]] = {}
    for raw_service in model.get("services") or []:
        raw = raw_service.get("id")
        grouped.setdefault(aliases.get(raw, raw), []).append(raw_service)
    collisions, merged_variants = [], []
    for logical, variants in sorted(grouped.items()):
        if len(variants) <= 1:
            continue
        normalized = []
        for original in variants:
            value = deepcopy(original)
            raw = value.get("id")
            value["id"] = logical
            if value.get("name") == raw:
                value["name"] = logical
            normalized.append(value)
        signatures = {json.dumps(value, sort_keys=True, separators=(",", ":"))
                      for value in normalized}
        if len(signatures) != 1:
            raw_ids = {value.get("id") for value in variants}
            aliases = {raw: target for raw, target in aliases.items()
                       if not (target == logical and raw in raw_ids)}
            collisions.append({"logical_service": logical, "raw_variants": deepcopy(variants),
                               "reason": "non_name_service_metadata_differs"})
        else:
            merged_variants.append({"logical_service": logical,
                                    "raw_variants": deepcopy(variants)})
    transformed = deepcopy(model)
    by_id: dict[str, list[dict]] = {}
    applied = []
    for service in transformed.get("services") or []:
        raw = service.get("id")
        logical = aliases.get(raw, raw)
        service["id"] = logical
        if service.get("name") == raw:
            service["name"] = logical
        if logical != raw:
            applied.append({"raw_service": raw, "logical_service": logical, "origin": ORIGIN})
        by_id.setdefault(logical, []).append(service)
    services = []
    for logical, variants in sorted(by_id.items()):
        service = variants[0]
        services.append(service)
    transformed["services"] = services
    for edge in transformed.get("edges") or []:
        edge["from"] = aliases.get(edge.get("from"), edge.get("from"))
        edge["to"] = aliases.get(edge.get("to"), edge.get("to"))
    for endpoint in transformed.get("endpoints") or []:
        endpoint["entry_service"] = aliases.get(
            endpoint.get("entry_service"), endpoint.get("entry_service"))
    transformed_quality = deepcopy(quality)
    for evidence in transformed_quality.get("observation_evidence") or []:
        if evidence.get("entity_type") == "service":
            evidence["entity_id"] = aliases.get(evidence.get("entity_id"), evidence.get("entity_id"))
    if collisions:
        transformed_quality["supplied_logical_alias_uncertainty"] = deepcopy(collisions)
    proof = {"schema": "supplied-logical-alias-application-v5", "origin": ORIGIN,
             "applied": applied, "raw_model_unchanged": True, "graph_edges_injected": False,
             "roles_or_endpoints_created": False, "physical_identity_inferred": False,
             "metadata_collisions": collisions, "lossless_merged_variants": merged_variants,
             "effective_aliases": aliases,
             "same_table_all_sources_and_direct_baseline": True}
    return transformed, transformed_quality, proof
