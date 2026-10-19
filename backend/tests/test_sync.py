import tempfile
from pathlib import Path

from app.agri.sync.pipeline import run_daily_sync
from app.agri.sync.phone_bundle import build_incremental_bundle, verify_bundle


def test_daily_sync_publishes_version():
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp)
        report = run_daily_sync(data_dir=data_dir, adapters=[lambda: []])
        assert report.published_version
        assert (data_dir / "published_facts.json").exists()


def test_phone_bundle_signature():
    records = [{"record_id": "a", "region_id": "ap", "crop_id": "rice", "body": "x"}]
    bundle = build_incremental_bundle(records, region_id="ap", crop_ids=["rice"], secret="test-secret")
    assert verify_bundle(bundle, "test-secret")
