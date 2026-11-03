from nexus_enforcement.audit_chain import HashChainedAuditSink

def test_audit_chain():
    sink = HashChainedAuditSink()
    h1 = sink.log_event("POLICY_EVAL", {"verdict": "ALLOW"})
    assert len(h1) == 64
