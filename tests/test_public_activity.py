import importlib.util
from pathlib import Path
import unittest
import tempfile

spec=importlib.util.spec_from_file_location("public_activity",Path(__file__).resolve().parents[1]/"scripts/public_activity.py")
activity=importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)

def fake(path):
    if path=="":return {"full_name":activity.REPO,"private":False,"visibility":"public"}
    if path.startswith("/pulls?"):return [{"merged_at":"2026-01-01"},{"merged_at":None}]
    if path.startswith("/issues?"):return [{"number":1},{"number":2,"pull_request":{}}]
    if path.startswith("/releases?"):return [{"draft":False,"prerelease":False,"published_at":"2026-01-01","tag_name":"v0.1.0"}]
    raise AssertionError(path)

class PublicActivityTests(unittest.TestCase):
    def test_counts(self):
        x=activity.collect(fake)
        self.assertEqual(x["merged_pull_requests"],1)
        self.assertEqual(x["open_issues"],1)
        self.assertEqual(x["published_releases"],1)
        self.assertEqual(x["latest_release"],"v0.1.0")
    def test_private_rejected(self):
        with self.assertRaises(ValueError):
            activity.collect(lambda p:{"full_name":activity.REPO,"private":True,"visibility":"private"})
    def test_invalid_tag(self):
        x=activity.collect(fake)
        x["latest_release"]="<bad>"
        with self.assertRaises(ValueError):
            activity.render(x)
    def test_publish_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            x=activity.collect(fake)
            activity.publish(x,root)
            a=(root/"assets/public-activity.svg").read_bytes()
            self.assertEqual(a,(root/"docs/assets/public-activity.svg").read_bytes())
            activity.publish(x,root)
            self.assertEqual(a,(root/"assets/public-activity.svg").read_bytes())
