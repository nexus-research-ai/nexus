from nexus_intelligence.meta_client import MetaClient
from nexus_intelligence.sam_segmenter import SAMSciFigureSegmenter

def test_meta_client_mock():
    c = MetaClient()
    res = c.generate("test prompt", mock=True)
    assert "text" in res
    assert res["usage"]["cost_usd"] > 0

def test_sam_segmenter_unit():
    s = SAMSciFigureSegmenter()
    elems = s.segment_elements({"name": "test.png"})
    assert len(elems) >= 2
    for el in elems:
        assert 0.0 <= el["bounding_box"][0] <= 1.0
