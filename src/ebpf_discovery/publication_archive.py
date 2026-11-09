"""Archive/replay the fixed published report, not raw captures or model builds.

Scientific projection remains the byte-pinned c4 reader. Only its three I/O
functions use archived source, historical API receipts and original ZIP bytes.
Large downloads and execution are restricted to repository Actions workers.
"""
from __future__ import annotations

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import zipfile

import requests


REPO = "a-a-k/ebpf-model-discovery-experiments"
SOURCE = "c4f066d7c067d5661c3d942aacadb25d3103820d"
READER = ".github/workflows/read-v6-full108-results.yml"
READER_SHA = "38eb812a4d87fa269294bb023f45df3bbc49438014ce4a0dc631943b41df8bed"
MANIFEST = "docs/v6-full108-completed-result-manifest.json"
LEDGER = "docs/v6-full108-completed-cost-ledger.json"
REFERENCE_SHA = "1153f70032bc36bbc1936e666c8338e0935c24d2c8553b64836e711c9005bf36"
MANIFEST_SHA = "23b73280cc0f6386bffe35a29b85fb903fddbdf905a20f61a6643944cdc691a6"
LEDGER_SHA = "198cd5825bea33567353afb5166d552c9a2df963b8f4a86628122de82a4cbf3e"
RESERVE = 2 * 1024**3
ARCHIVE_MARKER = f"Fixed-publication-dataset: {SOURCE}; manifest-sha256: {MANIFEST_SHA}; payloads: 103; bytes: 12344016466."


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024**2), b""):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf8")


def reader_tree(body):
    require(digest(body) == READER_SHA, "unqualified reader source")
    source = body.decode().split("          python - <<'PY'\n", 1)[1].split("\n          PY\n", 1)[0]
    return ast.parse("\n".join(line[10:] if line.startswith(" " * 10) else line
                               for line in source.splitlines()))


def bound_reader(body):
    tree = reader_tree(body)
    names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name in {"api", "blob", "download"}}
    require(names == {"api", "blob", "download"}, "reader I/O boundary changed")
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.FunctionDef) and node.name in names)]
    return compile(ast.fix_missing_locations(tree), "archived-c4-publication-reader", "exec")


def payloads(manifest):
    roots = {}
    for cell in manifest["cells"]:
        a = cell["artifact"]
        require(a["id"] not in roots or roots[a["id"]] == a, "conflicting artifact")
        roots[a["id"]] = a
    require(len(roots) == 102, "canonical publication selection changed")
    for retry in manifest["technical_publication_retries"]:
        a = retry["historical_metadata"]
        require(a["id"] not in roots, "historical prefix duplicated")
        roots[a["id"]] = a
    require(len(roots) == 103 and sum(a["bytes"] for a in roots.values()) == 12344016466,
            "bounded publication archive selection changed")
    return roots


class GitHub:
    def __init__(self, replay=False):
        self.replay = replay
        self.calls = []

    def request(self, method, endpoint, **kwargs):
        if self.replay:
            require("/actions/" not in "/" + endpoint, "live Actions API forbidden during archive replay")
        url = endpoint if endpoint.startswith("https://") else f"https://api.github.com/repos/{REPO}/{endpoint}"
        require(url.startswith((f"https://api.github.com/repos/{REPO}/",
                                f"https://uploads.github.com/repos/{REPO}/")), "unexpected API destination")
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if os.environ.get("GH_TOKEN"):
            headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
        headers.update(kwargs.pop("headers", {}))
        self.calls.append({"method": method, "endpoint": endpoint, "started_ns": time.time_ns()})
        # Retry read-only requests. Mutating uploads reconcile remote state separately.
        for attempt in range(4 if method == "GET" else 1):
            try:
                response = requests.request(method, url, headers=headers, timeout=(30, 180), **kwargs)
                response.raise_for_status()
                return response
            except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as error:
                code = getattr(getattr(error, "response", None), "status_code", 0)
                if method != "GET" or attempt == 3 or (code and code < 500 and code != 429):
                    raise
                time.sleep(2 ** attempt)

    def json(self, endpoint, **kwargs):
        return self.request("GET", endpoint, **kwargs).json()

    def pages(self, endpoint, key=None):
        result = []
        for page in range(1, 100):
            data = self.json(endpoint + ("&" if "?" in endpoint else "?") + f"per_page=100&page={page}")
            rows = data[key] if key else data
            result.extend(rows)
            if len(rows) < 100:
                if key:
                    require(len(result) == data["total_count"], "incomplete paginated API receipt")
                return result
        raise ValueError("unbounded API pagination")

    def download(self, endpoint, path, size, sha):
        require(shutil.disk_usage(Path(path).parent).free >= size + RESERVE, "download disk reserve")
        response = self.request("GET", endpoint, headers={"Accept": "application/octet-stream"},
                                allow_redirects=False, stream=True)
        if response.is_redirect:
            target = response.headers["Location"]
            from urllib.parse import urlsplit
            parsed = urlsplit(target)
            require(parsed.scheme == "https" and parsed.hostname and any(parsed.hostname.endswith(s)
                    for s in (".blob.core.windows.net", ".githubusercontent.com", ".actions.githubusercontent.com")),
                    "unexpected download delivery host")
            response.close()
            response = requests.get(target, stream=True, timeout=(30, 180))
            response.raise_for_status()
        total = 0
        h = hashlib.sha256()
        pending = Path(str(path) + ".partial")
        try:
            with response, pending.open("wb") as output:
                for body in response.iter_content(1024**2):
                    total += len(body)
                    require(total <= size, "download exceeds exact archive byte count")
                    h.update(body)
                    output.write(body)
            require(total == size and h.hexdigest() == sha, "download byte count/SHA differs")
            require(not Path(path).exists(), "download destination already exists")
            pending.rename(path)
        finally:
            pending.unlink(missing_ok=True)


class Release:
    def __init__(self, github, release_id):
        self.github, self.id = github, int(release_id)
        self.assets = {a["name"]: a for a in github.pages(f"releases/{self.id}/assets")}

    def publish(self, path):
        path = Path(path)
        size, sha = path.stat().st_size, file_digest(path)
        require(size < 2 * 1024**3 and re.fullmatch(r"[A-Za-z0-9._-]+", path.name), "release asset bounds")
        for attempt in range(4):
            existing = self.assets.get(path.name)
            if existing:
                verified = self.github.json(f"releases/assets/{existing['id']}")
                require((verified["name"], verified["size"], verified["digest"], verified["state"]) ==
                        (path.name, size, "sha256:" + sha, "uploaded"), "conflicting/incomplete existing release asset")
                self.assets[path.name] = verified
                return verified
            try:
                with path.open("rb") as body:
                    asset = self.github.request("POST", f"https://uploads.github.com/repos/{REPO}/releases/{self.id}/assets?name={path.name}",
                                                headers={"Content-Type": "application/octet-stream"}, data=body).json()
                self.assets[path.name] = asset
                verified = self.github.json(f"releases/assets/{asset['id']}")
                require((verified["name"], verified["size"], verified["digest"], verified["state"]) ==
                        (path.name, size, "sha256:" + sha, "uploaded"), "uploaded release asset differs")
                self.assets[path.name] = verified
                return verified
            except (requests.RequestException, ValueError):
                self.assets = {a["name"]: a for a in self.github.pages(f"releases/{self.id}/assets")}
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        raise ValueError("upload was not remotely verified")


def validate_asset(actual, expected):
    require(actual is not None and all(actual.get(k) == expected[k]
            for k in ("id", "name", "size", "digest", "state")), "archive asset ID/bytes/SHA/state differs")


def validate_release_owner(github, info, release, roots):
    match = re.fullmatch(r"publication-archive-([1-9][0-9]*)", info["tag_name"])
    require(match and ARCHIVE_MARKER in (info.get("body") or "") and
            re.fullmatch(r"[0-9a-f]{40}", info["target_commitish"]), "release is not the intended publication archive")
    creator = github.json(f"actions/runs/{match[1]}")
    require(creator["head_sha"] == info["target_commitish"] and creator["id"] == int(match[1]) and
            creator["path"] == ".github/workflows/publication-archive.yml" and
            creator["event"] == "workflow_dispatch", "release creation workflow/source differs")
    allowed = {f"artifact-{a['id']}.zip": a for a in roots.values()}
    require(set(release.assets) <= set(allowed) | {"publication-inputs.zip", "archive-index.json"},
            "unexpected assets in resumed publication archive")
    for name, actual in release.assets.items():
        require(actual["state"] == "uploaded" and actual["size"] > 0 and
                re.fullmatch(r"sha256:[0-9a-f]{64}", actual.get("digest") or ""), "incomplete existing asset")
        if name in allowed:
            a = allowed[name]
            require(actual["size"] == a["bytes"] and actual["digest"] == "sha256:" + a["sha256"],
                    "existing payload differs from fixed dataset")


def validate_bundle_owner(bundle, info):
    require(bundle.index["archive_owner"] == {"release_id": info["id"], "release_tag": info["tag_name"],
            "creation_source": info["target_commitish"]}, "bundle belongs to a different archive release")


def validate_archive_index(index, bundle, release, info):
    require((index["repository"], index["source"], index["release_id"], index["release_tag"],
             index["payload_count"], index["payload_bytes"]) ==
            (REPO, SOURCE, release.id, info["tag_name"], 103, 12344016466), "foreign/incomplete archive index")
    validate_bundle_owner(bundle, info)
    validate_asset(release.assets.get("publication-inputs.zip"), index["bundle_asset"])
    expected = {f"artifact-{a['id']}.zip": a for a in bundle.index["payloads"]}
    indexed = {a["name"]: a for a in index["payload_assets"]}
    require(len(index["payload_assets"]) == 103 and set(indexed) == set(expected), "archive index incomplete payload set")
    for name, artifact in expected.items():
        actual = release.assets.get(name)
        validate_asset(actual, indexed[name])
        require(actual["state"] == "uploaded" and actual["size"] == artifact["bytes"] and
                actual["digest"] == "sha256:" + artifact["sha256"], "fixed payload identity differs")
    require(index["projection"]["scientific_fields_equal_reference"] is True and
            index["projection"]["reference_sha256"] == REFERENCE_SHA and
            index["historical_prefix_is_extra_independent_case"] is False, "archive lacks exact report verification")


def publish_release(github, info):
    published = (github.request("PATCH", f"releases/{info['id']}", json={"draft": False}).json()
                 if info["draft"] else github.json(f"releases/{info['id']}"))
    require(not published["draft"] and all(published[k] == info[k]
            for k in ("id", "tag_name", "target_commitish")), "release publication identity differs")


def snapshot(github, ledger):
    runs = sorted({row["workflow"]["id"] for row in ledger["workflows"]})
    runs = sorted(set(runs) | {42518287343, 42518575853, 42520110541, 42520421400})

    def one(run):
        header = github.json(f"actions/runs/{run}")
        jobs = github.pages(f"actions/runs/{run}/jobs?filter=all", "jobs")
        artifacts = github.pages(f"actions/runs/{run}/artifacts", "artifacts")
        return {"run": header, "jobs": jobs, "artifacts": artifacts}

    with ThreadPoolExecutor(max_workers=4) as pool:
        receipts = list(pool.map(one, runs))
    endpoints = {}
    for receipt in receipts:
        for kind, rows in (("jobs", receipt["jobs"]), ("artifacts", receipt["artifacts"])):
            for row in rows:
                route = f"actions/{kind}/{row['id']}"
                require(route not in endpoints or endpoints[route] == row, "conflicting API receipt")
                endpoints[route] = row
    return {"captured_ns": time.time_ns(), "scope": "Official run headers and complete paginated jobs(filter=all)/artifact indexes; endpoint views are exact list entries, not separate GET receipts.",
            "runs": receipts, "endpoint_views": endpoints}


def git_blob(path):
    return subprocess.check_output(["git", "show", SOURCE + ":" + path])


def create_bundle(github, path, release_info):
    workflow = git_blob(READER)
    tree = reader_tree(workflow)
    paths = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant)
             and isinstance(node.value, str) and node.value.startswith("docs/") and node.value.endswith(".json")}
    for profile in json.loads(git_blob("docs/v6-full108-literal-five-continuation-profiles-20261108.json"))["profiles"]:
        paths.update((profile["parent"]["path"], profile["binding"]["path"]))
    files = {"source/" + p: git_blob(p) for p in paths | {READER}}
    require(digest(files["source/" + MANIFEST]) == MANIFEST_SHA and
            digest(files["source/" + LEDGER]) == LEDGER_SHA, "historical manifest/ledger changed")
    reference = Path("results/literal-results.json").read_bytes()
    require(digest(reference) == REFERENCE_SHA, "historical report changed")
    files["reference/literal-results.json"] = reference
    files["erratum/semantic-correction.json"] = Path("results/semantic-correction.json").read_bytes()
    receipts = snapshot(github, json.loads(files["source/" + LEDGER]))
    files["api/snapshot.json"] = json.dumps(receipts).encode()
    index = {"scope": "Fixed publication replay; raw/model regeneration inputs are not archived by this tier.",
             "source": SOURCE, "reader_sha256": READER_SHA,
             "archive_owner": {"release_id": release_info["id"], "release_tag": release_info["tag_name"],
                               "creation_source": release_info["target_commitish"]},
             "payloads": list(payloads(json.loads(files["source/" + MANIFEST])).values()),
             "files": {name: {"bytes": len(body), "sha256": digest(body)} for name, body in files.items()}}
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as output:
        for name, body in files.items():
            output.writestr(name, body)
        output.writestr("bundle-index.json", json.dumps(index))


class Bundle:
    def __init__(self, path):
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)) and sum(i.file_size for i in archive.infolist()) < 128 * 1024**2,
                    "duplicate/oversized archive input bundle")
            self.index = json.loads(archive.read("bundle-index.json"))
            require(set(names) == set(self.index["files"]) | {"bundle-index.json"}, "bundle member set differs")
            self.files = {}
            for name, identity in self.index["files"].items():
                body = archive.read(name)
                require(len(body) == identity["bytes"] and digest(body) == identity["sha256"], "bundle source receipt differs")
                self.files[name] = body
        require(self.index["source"] == SOURCE and self.index["reader_sha256"] == READER_SHA, "bundle qualified source differs")
        require(digest(self.blob(MANIFEST)) == MANIFEST_SHA and digest(self.blob(LEDGER)) == LEDGER_SHA and
                digest(self.files["reference/literal-results.json"]) == REFERENCE_SHA, "historical input identity differs")
        require(self.index["payloads"] == list(payloads(json.loads(self.blob(MANIFEST))).values()), "bundle payload selection differs")
        self.receipts = json.loads(self.files["api/snapshot.json"])

    def blob(self, path):
        return self.files["source/" + path]

    def api(self, path):
        require(path in self.receipts["endpoint_views"], "missing archived API receipt: " + path)
        return self.receipts["endpoint_views"][path]


class Backend:
    def __init__(self, bundle, github, release, create):
        self.bundle, self.github, self.release, self.create = bundle, github, release, create
        self.roots = {a["id"]: a for a in bundle.index["payloads"]}
        self.downloaded = []

    def download(self, artifact, path):
        require(self.roots.get(artifact["id"]) == artifact, "download outside exact 103-publication allowlist")
        name = f"artifact-{artifact['id']}.zip"
        asset = self.release.assets.get(name)
        if asset:
            require((asset["size"], asset["digest"], asset["state"]) ==
                    (artifact["bytes"], "sha256:" + artifact["sha256"], "uploaded"), "release payload identity differs")
            endpoint = f"releases/assets/{asset['id']}"
        else:
            require(self.create, "missing archived payload")
            endpoint = f"actions/artifacts/{artifact['id']}/zip"
        self.github.download(endpoint, path, artifact["bytes"], artifact["sha256"])
        if self.create:
            # Original reader owns/deletes path. Upload the same bytes using a hard link.
            link = Path(path).with_name(name)
            os.link(path, link)
            try:
                asset = self.release.publish(link)
            finally:
                link.unlink()
        self.downloaded.append({"artifact_id": artifact["id"], "asset_id": asset["id"],
                                "bytes": artifact["bytes"], "sha256": artifact["sha256"]})
        print(json.dumps({"verified_payload": artifact["id"], "count": len(self.downloaded)}), flush=True)


@contextmanager
def in_directory(path):
    previous = Path.cwd()
    Path(path).mkdir(parents=True, exist_ok=False)
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def project(bundle, backend, directory, host_receipt):
    with in_directory(directory):
        Path("work").mkdir()
        shutil.copyfile(host_receipt, "work/reader-host-resources.json")
        exec(bound_reader(bundle.blob(READER)), {
            "blob": bundle.blob, "api": bundle.api, "download": backend.download,
        })
        output = Path("work/full108-results/literal-results.json")
        result = json.loads(output.read_bytes())
        reference = json.loads(bundle.files["reference/literal-results.json"])
        fields = ("key", "allocation_regime", "original_metadata_artifact", "original_evaluation",
                  "original_publication", "original_forecast", "source_member_hashes", "omitted", "literal_evaluation")
        def scientific_cells(report):
            def identity(cell):
                value = {key: cell[key] for key in fields}
                lineage = cell["verified_replay_lineage"]
                if lineage:
                    value["lineage"] = {k: v for k, v in lineage.items()
                                        if k not in ("model_artifact_API", "actual_model_job_API")}
                    a, j = lineage["model_artifact_API"], lineage["actual_model_job_API"]
                    value["lineage"]["artifact"] = {k: a[k] for k in ("id", "name", "size_in_bytes", "digest")}
                    value["lineage"]["artifact"]["workflow_run"] = {k: a["workflow_run"][k] for k in ("id", "head_sha")}
                    value["lineage"]["job"] = {k: j[k] for k in
                        ("id", "run_id", "head_sha", "run_attempt", "name", "status", "conclusion", "started_at", "completed_at")}
                else:
                    value["lineage"] = None
                return value
            return sorted((identity(cell) for cell in report["cells"]),
                          key=lambda cell: tuple(cell["key"]))
        require(result["status"] == "complete" and result["coverage"] == reference["coverage"] and
                scientific_cells(result) == scientific_cells(reference), "archived scientific report differs")
        # Original engine is unchanged; qualify the historical metadata explicitly.
        result["manifest"]["committed_source"] = SOURCE
        result["archive_replay"] = {
            "scientific_fields_equal_reference": True, "reference_sha256": REFERENCE_SHA,
            "input_source": SOURCE, "engine_sha256": READER_SHA,
            "live_Actions_API_checked_by_reader": False,
            "API_fields_are_historical_snapshot_not_current_expiry_status": True,
            "snapshot_captured_ns": bundle.receipts["captured_ns"],
            "full_raw_capture_or_model_regeneration": False,
        }
        dump(output, result)
        return {"report_sha256": file_digest(output), "coverage": result["coverage"],
                **result["archive_replay"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("create", "replay"))
    parser.add_argument("--release-id", type=int)
    parser.add_argument("--index-asset-id", type=int)
    parser.add_argument("--index-bytes", type=int)
    parser.add_argument("--index-sha256")
    args = parser.parse_args()
    require(os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_REPOSITORY") == REPO,
            "publication archive processing is repository Actions only")
    require(args.mode != "replay" or (args.index_asset_id and args.index_bytes and args.index_sha256),
            "replay requires exact published index asset identity")
    started = time.time_ns()
    root = Path("work/publication-archive").resolve()
    root.mkdir(parents=True, exist_ok=True)
    host = Path("work/reader-host-resources.json").resolve()
    github = GitHub(replay=args.mode == "replay")
    proof = {"mode": args.mode, "execution_source": os.environ["GITHUB_SHA"],
             "run_id": os.environ["GITHUB_RUN_ID"], "started_ns": started,
             "human_work_seconds": None, "complete_comparable_cost_comparison": False,
             "full_raw_capture_or_model_regeneration": False, "status": "started"}
    try:
        if args.mode == "create":
            if args.release_id:
                release_info = github.json(f"releases/{args.release_id}")
            else:
                release_info = github.request("POST", "releases", json={
                    "tag_name": "publication-archive-" + os.environ["GITHUB_RUN_ID"],
                    "target_commitish": os.environ["GITHUB_SHA"], "draft": True,
                    "name": "Published study report and original metadata",
                    "body": ARCHIVE_MARKER + "\n\nFixed 108-case publication replay: 102 canonical metadata ZIPs and one historical failed-publication prefix, pinned source and historical API receipts. Does not archive all raw captures/model-build inputs. The compose_post semantic erratum applies; this archive does not validate a corrected forecast or a durable-write claim. No Actions expiry applies to release assets; continued repository/release availability remains required.",
                }).json()
            release = Release(github, release_info["id"])
            roots = payloads(json.loads(git_blob(MANIFEST)))
            validate_release_owner(github, release_info, release, roots)
            require(release_info["draft"] or "archive-index.json" in release.assets,
                    "published release cannot be extended without its verified final index")
            proof["release"] = release_info
            dump(root / "proof.json", proof)
            bundle_path = root / "publication-inputs.zip"
            old = release.assets.get(bundle_path.name)
            if old:
                github.download(f"releases/assets/{old['id']}", bundle_path, old["size"], old["digest"].removeprefix("sha256:"))
            else:
                create_bundle(github, bundle_path, release_info)
            bundle_asset = release.publish(bundle_path)
            bundle = Bundle(bundle_path)
            validate_bundle_owner(bundle, release_info)
            old_index = release.assets.get("archive-index.json")
            if old_index:
                index_path = root / "archive-index.json"
                github.download(f"releases/assets/{old_index['id']}", index_path, old_index["size"],
                                old_index["digest"].removeprefix("sha256:"))
                index = json.loads(index_path.read_bytes())
                validate_archive_index(index, bundle, release, release_info)
                publish_release(github, release_info)
                proof.update(status="complete", resumed_existing_immutable_index=True,
                             fresh_scientific_projection_performed=False, projection=index["projection"],
                             archive_index={"asset_id": old_index["id"], "bytes": old_index["size"],
                                            "sha256": file_digest(index_path), "url": old_index["browser_download_url"]},
                             original_Actions_API_requests=[c for c in github.calls if "/actions/" in "/" + c["endpoint"]])
                return
        else:
            index_path = root / "archive-index.json"
            github.download(f"releases/assets/{args.index_asset_id}", index_path, args.index_bytes, args.index_sha256)
            index = json.loads(index_path.read_bytes())
            require(index["repository"] == REPO and index["source"] == SOURCE, "foreign archive index")
            release = Release(github, index["release_id"])
            release_info = github.json(f"releases/{release.id}")
            require(not release_info["draft"], "replay requires published archive")
            require(release.assets.get("archive-index.json", {}).get("id") == args.index_asset_id,
                    "index is not a member of the selected archive release")
            bundle_asset = index["bundle_asset"]
            bundle_path = root / "publication-inputs.zip"
            github.download(f"releases/assets/{bundle_asset['id']}", bundle_path, bundle_asset["size"], bundle_asset["digest"].removeprefix("sha256:"))
            validate_archive_index(index, Bundle(bundle_path), release, release_info)
        bundle = Bundle(bundle_path)
        backend = Backend(bundle, github, release, args.mode == "create")
        proof["projection"] = project(bundle, backend, root / "reader", host)
        if args.mode == "create":
            historical = json.loads(bundle.blob(MANIFEST))["technical_publication_retries"][0]["historical_metadata"]
            path = root / "historical-prefix.zip"
            backend.download(historical, path)
            with zipfile.ZipFile(path) as archive:
                require(archive.testzip() is None, "historical publication ZIP CRC differs")
            path.unlink()
            require(len(backend.downloaded) == 103, "not all exact publication ZIPs archived")
            index = {"repository": REPO, "source": SOURCE, "release_id": release.id,
                     "release_tag": release_info["tag_name"], "scope": bundle.index["scope"],
                     "created_ns": time.time_ns(), "execution_source": os.environ["GITHUB_SHA"],
                     "bundle_asset": bundle_asset, "payload_assets": [release.assets[f"artifact-{a['id']}.zip"] for a in bundle.index["payloads"]],
                     "payload_count": 103, "payload_bytes": 12344016466,
                     "projection": proof["projection"], "historical_prefix_is_extra_independent_case": False}
            index_path = root / "archive-index.json"
            dump(index_path, index)
            index_asset = release.publish(index_path)
            proof["archive_index"] = {"asset_id": index_asset["id"], "bytes": index_asset["size"],
                                      "sha256": file_digest(index_path), "url": index_asset["browser_download_url"]}
            validate_archive_index(index, bundle, release, release_info)
            publish_release(github, release_info)
        proof.update(status="complete", verified_downloads=backend.downloaded,
                     original_Actions_API_requests=[c for c in github.calls if "/actions/" in "/" + c["endpoint"]])
        require(args.mode != "replay" or not proof["original_Actions_API_requests"], "replay used live Actions API")
    except BaseException as error:
        proof.update(status="failed", error=repr(error))
        raise
    finally:
        proof.update(ended_ns=time.time_ns(), API_requests=github.calls,
                     free_disk_bytes_after=shutil.disk_usage(root).free)
        dump(root / "proof.json", proof)
        print(json.dumps({k: v for k, v in proof.items() if k in ("mode", "status", "archive_index", "error")}), flush=True)


if __name__ == "__main__":
    main()
