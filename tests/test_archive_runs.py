"""Synthetic GitHub responses for the read-only release archive path."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = b"PK\x03\x04synthetic-artifact-bytes"


@unittest.skipUnless(os.name == "posix", "shell archive fixture runs on Linux")
class ArchiveRunsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.bin = self.home / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(textwrap.dedent('''\
            #!/usr/bin/env python3
            import hashlib, io, json, os, sys, zipfile
            endpoint = sys.argv[2]
            scenario = os.environ.get("MOCK_SCENARIO", "metadata_only")
            artifact = b"PK\\x03\\x04synthetic-artifact-bytes"
            remote = os.path.join(os.environ['ARCHIVE_DIR'], 'mock-remote.json')
            assets = json.load(open(remote)) if os.path.exists(remote) else []
            if sys.argv[1:3] == ['release', 'upload']:
                if '--clobber' in sys.argv: raise AssertionError('overwrite forbidden')
                if scenario == 'incremental_upload_error': sys.exit(1)
                path = sys.argv[4]
                data = open(path, 'rb').read()
                assets.append({'id':len(assets)+1, 'name':os.path.basename(path),
                    'state':'uploaded', 'size':len(data),
                    'digest':'sha256:'+hashlib.sha256(data).hexdigest(),
                    'browser_download_url':'https://example.test/asset'})
                with open(remote, 'w') as output: json.dump(assets, output)
                sys.exit(0)
            if '/releases/tags/' in endpoint:
                print(json.dumps({'id':55, 'draft':scenario!='incremental_published',
                    'tag_name':'data-99', 'target_commitish':'a'*40}))
                sys.exit(0)
            if '/releases/55/assets?' in endpoint:
                assert '--paginate' in sys.argv and '--slurp' in sys.argv
                if assets:
                    if scenario == 'incremental_null_digest': assets[-1]['digest'] = None
                    if scenario == 'incremental_bad_digest': assets[-1]['digest'] = 'sha256:'+'0'*64
                    if scenario == 'incremental_bad_size': assets[-1]['size'] += 1
                    if scenario == 'incremental_not_uploaded': assets[-1]['state'] = 'new'
                # The matching asset lives beyond the first 100 entries.
                dummy=[{'name':f'other-{i}'} for i in range(100)]
                print(json.dumps([dummy, assets])); sys.exit(0)
            if endpoint.endswith("/logs"):
                if scenario == "ansi_logs" and "--allow-escape-sequences" not in sys.argv:
                    print("gh: the response contains terminal escape sequences; pass --allow-escape-sequences to output it anyway", file=sys.stderr)
                    sys.exit(1)
                if scenario == "auth_failure":
                    print("gh: Resource not accessible by integration (HTTP 403)", file=sys.stderr)
                    sys.exit(1)
                if scenario == "server_failure":
                    print("gh: HTTP 503 Unavailable", file=sys.stderr)
                    sys.exit(1)
                if scenario == "network_failure":
                    print("gh: connection reset by peer", file=sys.stderr)
                    sys.exit(1)
                if scenario == "gone_logs":
                    print("gh: Gone (HTTP 410)", file=sys.stderr)
                    sys.exit(1)
                if scenario in ("workflow_only", "workflow_corrupt") and "/jobs/" not in endpoint:
                    out = io.BytesIO()
                    with zipfile.ZipFile(out, "w") as archive:
                        archive.writestr("other-job.txt", "available only in workflow ZIP")
                    raw = out.getvalue()
                    if scenario == "workflow_corrupt":
                        raw = raw.replace(b"available only", b"xvailable only", 1)
                    sys.stdout.buffer.write(raw)
                    sys.exit(0)
                if scenario == "artifact" and "/jobs/" in endpoint:
                    sys.stdout.buffer.write(b"synthetic job log\\n")
                    sys.exit(0)
                if scenario == "ansi_logs" and "/jobs/" in endpoint:
                    sys.stdout.buffer.write(b"\\x1b[31msynthetic job log\\x1b[0m\\n")
                    sys.exit(0)
                print("gh: HTTP 404 The specified blob does not exist.", file=sys.stderr)
                sys.exit(1)
            if endpoint.endswith(("/artifacts/42/zip", "/artifacts/43/zip")):
                if endpoint.endswith('/artifacts/43/zip'):
                    import glob
                    remaining=glob.glob(os.path.join(os.environ['ARCHIVE_DIR'],'7-artifact-42-capture.zip*'))
                    assert all(x.endswith('.chunks.json') for x in remaining), 'previous working copy retained'
                if scenario == "artifact_missing":
                    print("gh: HTTP 404 Artifact not found", file=sys.stderr)
                    sys.exit(1)
                sys.stdout.buffer.write(artifact)
                sys.exit(0)
            if endpoint.endswith("/artifacts?per_page=100"):
                digest = hashlib.sha256(artifact).hexdigest()
                if scenario == "bad_digest": digest = "0" * 64
                if scenario == 'incremental_bad_source': digest = '0'*64
                artifacts = ([] if scenario in ("metadata_only", "live", "auth_failure", "server_failure",
                                              "network_failure", "gone_logs", "workflow_only",
                                              "workflow_corrupt", "ansi_logs")
                             else [{"id":42,"name":"capture","digest":"sha256:"+digest}])
                if scenario == 'incremental_two':
                    artifacts.append({'id':43,'name':'capture2','digest':'sha256:'+digest})
                value = {"total_count":len(artifacts), "artifacts":artifacts}
            elif endpoint.endswith("/jobs?filter=all&per_page=100"):
                value = [{"total_count":1,"jobs":[{"id":11,"name":"campaign",
                    "run_attempt":1,
                    "check_run_url":"https://api.github.com/repos/example/repo/check-runs/11"}]}]
            elif endpoint.endswith("/check-runs/11/annotations?per_page=100"):
                value = [[{"annotation_level":"failure","message":"runner lost communication"}]]
            elif endpoint.endswith("/check-runs/11"):
                value = {"output":{"annotations_count":1},"conclusion":"failure"}
            elif endpoint.endswith("/runs/7"):
                value = {"id":7,"status":"in_progress" if scenario == "live" else "completed"}
            else:
                print("unexpected endpoint: " + endpoint, file=sys.stderr)
                sys.exit(2)
            sys.stdout.write(json.dumps(value))
        '''), encoding="utf-8")
        gh.chmod(0o755)
        sleep = self.bin / "sleep"
        sleep.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        sleep.chmod(0o755)
        self.archive = self.home / "archive"

    def run_archive(self, scenario, *, max_asset_bytes=None, chunk_bytes=None, incremental=False):
        env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}",
                   GITHUB_REPOSITORY="example/repo", RUN_IDS="7",
                   ARCHIVE_DIR=str(self.archive), MOCK_SCENARIO=scenario)
        if incremental:
            env.update(ARCHIVE_RELEASE_TAG='data-99', GITHUB_SHA='a'*40, GITHUB_RUN_ID='99')
        if max_asset_bytes is not None:
            env['ARCHIVE_MAX_ASSET_BYTES'] = str(max_asset_bytes)
            env['ARCHIVE_CHUNK_BYTES'] = str(chunk_bytes)
        return subprocess.run(["bash", str(ROOT / "scripts/archive-runs.sh")],
                              cwd=ROOT, env=env, text=True, capture_output=True)

    def test_metadata_only_failed_run_retains_annotations_and_explicit_absence(self):
        completed = self.run_archive("metadata_only")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(list(self.archive.glob("*.zip")), [])
        self.assertEqual((self.archive / "SHA256SUMS.txt").read_text(), "")
        self.assertEqual(json.loads((self.archive / "7-workflow-logs-status.json").read_text()),
                         {"endpoint":"repos/example/repo/actions/runs/7/logs",
                          "state":"unavailable","http_status":404})
        self.assertEqual(json.loads((self.archive / "7-job-11-logs-status.json").read_text())
                         ["http_status"], 404)
        with tarfile.open(self.archive / "provenance.tar.gz", "r:gz") as archive:
            names = archive.getnames()
        self.assertIn("./7-job-11-annotations.json", names)
        self.assertIn("./7-job-11-check-run.json", names)
        self.assertIn("./7-jobs-pages.json", names)

    def test_job_log_fallback_and_original_artifact_digest(self):
        completed = self.run_archive("artifact")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        original = self.archive / "7-artifact-42-capture.zip"
        self.assertEqual(original.read_bytes(), ARTIFACT)
        self.assertEqual((self.archive / "7-job-11.log").read_bytes(),
                         b"synthetic job log\n")
        self.assertIn(hashlib.sha256(ARTIFACT).hexdigest(),
                      (self.archive / "SHA256SUMS.txt").read_text())

    def test_whole_zip_does_not_claim_missing_job_log(self):
        completed = self.run_archive("workflow_only")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue((self.archive / "7-workflow-logs.zip").exists())
        self.assertEqual(json.loads((self.archive / "7-job-11-logs-status.json").read_text())
                         ["state"], "unavailable")

    def test_corrupt_workflow_log_zip_member_fails(self):
        completed = self.run_archive("workflow_corrupt")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Corrupt workflow log ZIP member", completed.stderr)
        self.assertFalse((self.archive / "provenance.tar.gz").exists())

    def test_gone_log_is_explicit_absence(self):
        completed = self.run_archive("gone_logs")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads((self.archive / "7-workflow-logs-status.json").read_text())
                         ["http_status"], 410)

    def test_ansi_log_requires_explicit_flag_and_preserves_original_bytes(self):
        completed = self.run_archive("ansi_logs")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual((self.archive / "7-job-11.log").read_bytes(),
                         b"\x1b[31msynthetic job log\x1b[0m\n")

    def test_oversized_asset_parts_reassemble_exact_original(self):
        completed = self.run_archive("artifact", max_asset_bytes=16, chunk_bytes=8)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        original = "7-artifact-42-capture.zip"
        self.assertFalse((self.archive / original).exists())
        manifest = json.loads((self.archive / (original + ".chunks.json")).read_text())
        self.assertEqual(manifest["original_size_bytes"], len(ARTIFACT))
        self.assertEqual(manifest["original_sha256"], hashlib.sha256(ARTIFACT).hexdigest())
        self.assertEqual(manifest["source_api_digest"], "sha256:" + hashlib.sha256(ARTIFACT).hexdigest())
        parts = manifest["parts"]
        self.assertEqual([part["filename"] for part in parts],
                         [f"{original}.part{index:04d}" for index in range(len(parts))])
        self.assertEqual([part["offset_bytes"] for part in parts], [0, 8, 16, 24])
        self.assertEqual(b"".join((self.archive / part["filename"]).read_bytes()
                                  for part in parts), ARTIFACT)
        for part in parts:
            data = (self.archive / part["filename"]).read_bytes()
            self.assertEqual(part["sha256"], hashlib.sha256(data).hexdigest())
            self.assertLess(len(data), 16)
        sums = (self.archive / "SHA256SUMS.txt").read_text()
        self.assertIn(parts[0]["filename"], sums)
        self.assertNotIn(original + "\n", sums)
        with tarfile.open(self.archive / "provenance.tar.gz", "r:gz") as bundle:
            self.assertIn("./" + original + ".chunks.json", bundle.getnames())
        subprocess.run(["bash", "-c", manifest["reassembly_command"]],
                       cwd=self.archive, check=True)
        subprocess.run(["bash", "-c", manifest["verification_command"]],
                       cwd=self.archive, check=True, capture_output=True)
        self.assertEqual((self.archive / original).read_bytes(), ARTIFACT)

    def test_incremental_deletes_only_after_remote_hash_and_preserves_checksums(self):
        completed = self.run_archive('incremental_two', incremental=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(list(self.archive.glob('*.zip')), [])
        rows = [json.loads(line) for line in (self.archive/'published-assets.jsonl').read_text().splitlines()]
        self.assertEqual(len(rows), 2)
        self.assertEqual({row['local_sha256'] for row in rows}, {hashlib.sha256(ARTIFACT).hexdigest()})
        sums=(self.archive/'SHA256SUMS.txt').read_text()
        self.assertIn('7-artifact-42-capture.zip', sums)
        self.assertIn('7-artifact-43-capture2.zip', sums)
        with tarfile.open(self.archive/'provenance.tar.gz') as bundle:
            self.assertIn('./published-assets.jsonl', bundle.getnames())

    def test_incremental_parts_remain_reassemblable_in_verified_remote_assets(self):
        completed = self.run_archive('incremental_two', incremental=True, max_asset_bytes=16, chunk_bytes=8)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(list(self.archive.glob('*.part[0-9][0-9][0-9][0-9]')), [])
        manifest=json.loads((self.archive/'7-artifact-42-capture.zip.chunks.json').read_text())
        rows=[json.loads(line) for line in (self.archive/'published-assets.jsonl').read_text().splitlines()]
        by_name={row['filename']:row for row in rows}
        for part in manifest['parts']:
            self.assertEqual(by_name[part['filename']]['local_sha256'], part['sha256'])
            self.assertIn(part['filename'], (self.archive/'SHA256SUMS.txt').read_text())

    def test_incremental_remote_failures_keep_unverified_working_copy(self):
        for scenario in ('incremental_upload_error','incremental_null_digest','incremental_bad_digest',
                         'incremental_bad_size','incremental_not_uploaded','incremental_bad_source'):
            with self.subTest(scenario=scenario):
                self.archive = self.home / scenario
                completed=self.run_archive(scenario, incremental=True)
                self.assertNotEqual(completed.returncode, 0)
                self.assertTrue((self.archive/'7-artifact-42-capture.zip').exists())
                self.assertFalse((self.archive/'provenance.tar.gz').exists())

    def test_incremental_rejects_a_published_release_before_reading_sources(self):
        completed=self.run_archive('incremental_published', incremental=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse((self.archive/'mock-remote.json').exists())
        self.assertFalse((self.archive/'7-run.json').exists())

    def test_live_run_and_missing_artifact_fail_closed(self):
        live = self.run_archive("live")
        self.assertNotEqual(live.returncode, 0)
        self.assertFalse((self.archive / "provenance.tar.gz").exists())
        bad = self.run_archive("bad_digest")
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("digest mismatch", bad.stderr)
        missing = self.run_archive("artifact_missing")
        self.assertNotEqual(missing.returncode, 0)
        self.assertFalse((self.archive / "provenance.tar.gz").exists())

    def test_auth_and_server_errors_are_not_misreported_as_missing_logs(self):
        for scenario in ("auth_failure", "server_failure", "network_failure"):
            with self.subTest(scenario=scenario):
                completed = self.run_archive(scenario)
                self.assertNotEqual(completed.returncode, 0)
                self.assertFalse((self.archive / "7-workflow-logs-status.json").exists())
                self.assertFalse((self.archive / "provenance.tar.gz").exists())


if __name__ == "__main__":
    unittest.main()
