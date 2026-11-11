#!/usr/bin/env python3
"""Read the small retained replay artifact; never execute study/model code."""
import csv
import hashlib
import io
import itertools
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

REPO = "a-a-k/ebpf-model-discovery-experiments"
RUN = 43063706864
ATTEMPT = 1
HEAD = "91c4a8334cea968c00da3f62c23b2f192cdc18e6"
NAME = f"publication-example-replay-{RUN}-attempt{ATTEMPT}"
MAX_ZIP = 128 * 1024**2
MAX_JSON = 32 * 1024**2
MAX_LOG = 240 * 1024
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
API = "https://api.github.com"
JSON_FILES = (
    "replay-receipt.json",
    "article-reaggregation-receipt.json",
    "evidence/edge-evidence/summary.json",
    "evidence/replay-comparison.json",
    "evidence/context/context-sidecar-receipt.json",
    "article-reaggregation/analysis.json",
)
CSV_FILES = (
    "evidence/edge-evidence/required-edges.csv",
    "evidence/context/context-summary.csv",
    "evidence/context/context-added-edges.csv",
)


class AuditError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def need(condition, reason):
    if not condition:
        raise AuditError(reason)


def api_request(path):
    need(path.startswith("/repos/" + REPO + "/"), "unexpected_api_path")
    return urllib.request.Request(
        API + path,
        headers={
            "Authorization": "Bearer " + TOKEN,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "publication-replay-artifact-reader",
        },
    )


def api_json(path):
    with OPENER.open(api_request(path), timeout=60) as response:
        body = response.read(2 * 1024**2 + 1)
    need(len(body) <= 2 * 1024**2, "api_response_too_large")
    return json.loads(body)


def clean(value):
    if isinstance(value, str):
        if TOKEN:
            value = value.replace(TOKEN, "[REDACTED_TOKEN]")
        value = re.sub(r"https?://[^\s<>\"']+", "[REDACTED_URL]", value)
        return re.sub(
            r"(?:github_pat_|gh[oprsu]_)[A-Za-z0-9_]+",
            "[REDACTED_TOKEN]",
            value,
        )
    if isinstance(value, list):
        return [clean(item) for item in value]
    if isinstance(value, dict):
        return {clean(str(key)): clean(item) for key, item in value.items()}
    return value


def compact(value, depth=6, width=24, string=900):
    if isinstance(value, str):
        return value if len(value) <= string else value[:string] + "[...omitted]"
    if not isinstance(value, (dict, list)):
        return value
    if depth <= 0:
        return {"_omitted_type": type(value).__name__, "_items": len(value)}
    if isinstance(value, list):
        result = [
            compact(item, depth - 1, width, string) for item in value[:width]
        ]
        if len(value) > width:
            result.append({"_omitted_items": len(value) - width})
        return result
    result = {
        str(key): compact(item, depth - 1, width, string)
        for key, item in list(value.items())[:width]
    }
    if len(value) > width:
        result["_omitted_keys"] = len(value) - width
    return result


def download_artifact(artifact):
    size = artifact.get("size_in_bytes")
    need(type(size) is int and 0 < size <= MAX_ZIP, "artifact_size_out_of_bounds")
    digest = artifact.get("digest") or ""
    need(
        re.fullmatch(r"sha256:[0-9a-fA-F]{64}", digest) is not None,
        "artifact_sha256_digest_missing",
    )
    path = f"/repos/{REPO}/actions/artifacts/{artifact['id']}/zip"
    try:
        response = OPENER.open(api_request(path), timeout=60)
    except urllib.error.HTTPError as error:
        if error.code not in (301, 302, 303, 307, 308):
            raise
        location = error.headers.get("Location", "")
        error.close()
        parsed = urllib.parse.urlsplit(location)
        need(
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None,
            "invalid_archive_redirect",
        )
        # No Authorization header, cookie jar, or authenticated opener is reused.
        request = urllib.request.Request(
            location, headers={"User-Agent": "publication-replay-artifact-reader"}
        )
        response = urllib.request.urlopen(request, timeout=60)
    data = io.BytesIO()
    hasher = hashlib.sha256()
    total = 0
    with response:
        length = response.headers.get("Content-Length")
        need(length is None or int(length) == size, "archive_size_header_mismatch")
        while total < size:
            chunk = response.read(min(1024 * 1024, size - total))
            if not chunk:
                break
            total += len(chunk)
            hasher.update(chunk)
            data.write(chunk)
    need(total == size, "archive_size_mismatch")
    actual = "sha256:" + hasher.hexdigest()
    need(actual == digest.lower(), "archive_digest_mismatch")
    data.seek(0)
    return data, actual


def member_report(archive, infos, requested):
    matches = [
        item for item in infos
        if not item.is_dir()
        and (item.filename == requested or item.filename.endswith("/" + requested))
    ]
    if not matches:
        return {"status": "missing"}
    if len(matches) != 1:
        return {"status": "ambiguous", "matches": len(matches)}
    item = matches[0]
    limit = MAX_JSON if requested.endswith(".json") else 2 * 1024**2
    result = {"member": item.filename, "bytes": item.file_size}
    if item.file_size > limit:
        return dict(result, status="member_size_out_of_bounds")
    try:
        raw = archive.read(item)
        result["sha256"] = hashlib.sha256(raw).hexdigest()
        decoded = raw.decode("utf-8-sig")
        if requested.endswith(".csv"):
            reader = csv.DictReader(io.StringIO(decoded, newline=""))
            rows = list(itertools.islice(reader, 201))
            result.update(
                status="read",
                columns=reader.fieldnames,
                rows=rows[:200],
                rows_truncated=len(rows) > 200,
            )
        else:
            document = json.loads(decoded)
            if requested == "article-reaggregation/analysis.json":
                wanted = ("execution", "inputs", "selection", "primary")
                if isinstance(document, dict):
                    result["available_top_level_keys"] = list(document)
                    document = {
                        key: document[key] for key in wanted if key in document
                    }
            result.update(status="read", content=compact(document))
    except Exception as error:
        result.update(status="member_read_failed", error_type=type(error).__name__)
    return result


def main():
    need(bool(TOKEN), "github_token_missing")
    run = api_json(f"/repos/{REPO}/actions/runs/{RUN}")
    need(run.get("id") == RUN, "run_id_mismatch")
    need(run.get("head_sha") == HEAD, "run_head_mismatch")
    need(run.get("run_attempt") == ATTEMPT, "run_attempt_mismatch")
    need(
        (run.get("repository") or {}).get("full_name") == REPO,
        "run_repository_mismatch",
    )
    need(run.get("status") == "completed", "run_not_completed")
    listing = api_json(
        f"/repos/{REPO}/actions/runs/{RUN}/artifacts?per_page=100"
    )
    need(listing.get("total_count", 0) <= 100, "artifact_listing_needs_pagination")
    matches = [
        item for item in listing.get("artifacts", [])
        if item.get("name") == NAME
    ]
    need(len(matches) == 1, "retained_artifact_not_unique")
    artifact_id = matches[0].get("id")
    need(type(artifact_id) is int and artifact_id > 0, "invalid_artifact_id")
    artifact = api_json(f"/repos/{REPO}/actions/artifacts/{artifact_id}")
    need(artifact.get("id") == artifact_id, "artifact_id_mismatch")
    need(artifact.get("name") == NAME, "artifact_name_mismatch")
    need(artifact.get("expired") is False, "artifact_expired")
    producer = artifact.get("workflow_run") or {}
    need(producer.get("id") == RUN, "artifact_producer_run_mismatch")
    need(producer.get("head_sha") == HEAD, "artifact_producer_head_mismatch")
    data, digest = download_artifact(artifact)
    report = {
        "status": "artifact_verified",
        "run": {
            key: run.get(key)
            for key in (
                "id", "run_attempt", "head_sha", "status", "conclusion",
                "name", "created_at", "updated_at",
            )
        },
        "artifact": {
            key: artifact.get(key)
            for key in (
                "id", "name", "size_in_bytes", "digest", "expired",
                "created_at", "updated_at",
            )
        },
        "download_sha256": digest,
        "models_executed": False,
        "files_extracted": False,
    }
    with zipfile.ZipFile(data) as archive:
        infos = archive.infolist()
        need(len(infos) <= 2000, "too_many_archive_members")
        names = [item.filename for item in infos]
        need(len(names) == len(set(names)), "duplicate_archive_members")
        report["documents"] = {
            requested: member_report(archive, infos, requested)
            for requested in JSON_FILES + CSV_FILES
        }
        report["file_inventory"] = [
            [item.filename, item.file_size, item.compress_size, f"{item.CRC:08x}"]
            for item in infos
        ]
        report["file_inventory_columns"] = [
            "member", "bytes", "compressed_bytes", "crc32"
        ]
    report = clean(report)
    encoded = json.dumps(report, ensure_ascii=True, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > MAX_LOG:
        inventory = report["file_inventory"]
        report["file_inventory"] = inventory[:100]
        report["file_inventory_omitted_count"] = max(0, len(inventory) - 100)
        report["documents"] = {
            key: compact(value, depth=5, width=12, string=300)
            for key, value in report["documents"].items()
        }
        encoded = json.dumps(report, ensure_ascii=True, separators=(",", ":"))
    need(len(encoded.encode("utf-8")) <= MAX_LOG, "report_exceeds_log_budget")
    print("PUBLICATION_AUDIT_JSON=" + encoded)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        failure = {"status": "reader_failed", "error_type": type(error).__name__}
        if isinstance(error, AuditError):
            failure["reason"] = str(error)
        elif isinstance(error, urllib.error.HTTPError):
            failure["http_status"] = error.code
        # Deliberately omit exception text, traceback, headers, and redirect URLs.
        print("PUBLICATION_AUDIT_JSON=" + json.dumps(failure, separators=(",", ":")))
        sys.exit(1)
