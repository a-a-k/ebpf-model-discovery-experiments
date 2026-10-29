"""Exact two functions from f6cb591, retained for byte-equivalence checks."""
import hashlib
import json

def journal_event_sha256(seq, kind, wall_ns, monotonic_ns, encoded_data) -> str:
    """Digest the exact retained SQLite event fields, including the original JSON bytes."""
    value = [seq, kind, wall_ns, monotonic_ns, encoded_data]
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()

def _journal_transports(journal) -> dict[str, dict]:
    with journal.lock:
        rows = list(journal.db.execute(
            "SELECT seq,kind,wall_ns,monotonic_ns,data FROM events "
            "WHERE kind IN ('step_started','step_finished','step_transport_unknown') ORDER BY seq"))
    by_transport = {}
    for seq, kind, wall_ns, monotonic_ns, encoded in rows:
        data = json.loads(encoded)
        identity = data.get("transport_id")
        if not identity:
            continue
        row = by_transport.setdefault(identity, {"started": [], "terminal": []})
        target = "started" if kind == "step_started" else "terminal"
        row[target].append({
            "seq": seq, "kind": kind, "wall_ns": wall_ns,
            "monotonic_ns": monotonic_ns, "data": data, "data_json": encoded,
            "event_row_sha256": journal_event_sha256(
                seq, kind, wall_ns, monotonic_ns, encoded),
        })
    result = {}
    for identity, row in by_transport.items():
        if len(row["started"]) != 1 or len(row["terminal"]) != 1:
            continue
        start, terminal = row["started"][0], row["terminal"][0]
        request_id = start["data"].get("request_id")
        if (terminal["kind"] != "step_finished" or terminal["data"].get("request_id") != request_id):
            continue
        if request_id in result:
            result[request_id] = None
        else:
            result[request_id] = {"transport_id": identity, "started": start, "terminal": terminal}
    return result
