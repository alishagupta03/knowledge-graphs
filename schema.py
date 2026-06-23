"""
CQI Knowledge Graph — CIS-10
Pure Python, no database needed.

Run:
    python schema.py
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Node definitions ──────────────────────────────────────────────────────────

@dataclass
class Patient:
    patient_id: str
    name: str
    dob: str
    gender: str
    measurement_year: int


@dataclass
class ImmunizationEvent:
    event_id: str
    cvx_code: str
    vaccine: str
    date: str
    source: str        # EHR | REGISTRY | NOTE
    confidence: float  # 0.0 to 1.0


@dataclass
class QualityComponent:
    component_id: str
    name: str
    required_count: int


@dataclass
class ComplianceResult:
    result_id: str
    status: str              # COMPLIANT | NON_COMPLIANT
    missing_components: list[str]
    calculated_at: str
    measure_version: str


@dataclass
class DataSnapshot:
    snapshot_id: str
    source_file: str
    sha256: str
    ingested_at: str


@dataclass
class HumanReviewItem:
    review_id: str
    field: str
    ai_extracted_value: str
    confidence: float
    status: str              # PENDING | CONFIRMED | CORRECTED


@dataclass
class AuditEvent:
    event_id: str
    type: str
    actor: str
    description: str
    timestamp: str


# ── Graph ─────────────────────────────────────────────────────────────────────

class KnowledgeGraph:
    def __init__(self):
        self.patients:             dict[str, Patient]            = {}
        self.immunization_events:  dict[str, ImmunizationEvent]  = {}
        self.quality_components:   dict[str, QualityComponent]   = {}
        self.compliance_results:   dict[str, ComplianceResult]   = {}
        self.data_snapshots:       dict[str, DataSnapshot]        = {}
        self.human_review_items:   dict[str, HumanReviewItem]    = {}
        self.audit_events:         dict[str, AuditEvent]          = {}

        # Edges stored as (from_id, to_id) tuples per relationship type
        self.has_event:           list[tuple] = []   # Patient → ImmunizationEvent
        self.satisfies:           list[tuple] = []   # ImmunizationEvent → QualityComponent
        self.from_snapshot:       list[tuple] = []   # ImmunizationEvent → DataSnapshot
        self.has_result:          list[tuple] = []   # Patient → ComplianceResult
        self.used_snapshot:       list[tuple] = []   # ComplianceResult → DataSnapshot
        self.flagged_for_review:  list[tuple] = []   # ImmunizationEvent → HumanReviewItem
        self.audit_for:           list[tuple] = []   # AuditEvent → Patient

    # ── Add nodes ─────────────────────────────────────────────────────────────

    def add_patient(self, p: Patient):
        self.patients[p.patient_id] = p

    def add_event(self, e: ImmunizationEvent):
        self.immunization_events[e.event_id] = e

    def add_component(self, c: QualityComponent):
        self.quality_components[c.component_id] = c

    def add_result(self, r: ComplianceResult):
        self.compliance_results[r.result_id] = r

    def add_snapshot(self, s: DataSnapshot):
        self.data_snapshots[s.snapshot_id] = s

    def add_review_item(self, h: HumanReviewItem):
        self.human_review_items[h.review_id] = h

    def add_audit_event(self, a: AuditEvent):
        self.audit_events[a.event_id] = a

    # ── Add edges ─────────────────────────────────────────────────────────────

    def link(self, relationship: str, from_id: str, to_id: str):
        getattr(self, relationship).append((from_id, to_id))

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_patient_events(self, patient_id: str) -> list[ImmunizationEvent]:
        """All immunization events for a patient."""
        event_ids = [to for (frm, to) in self.has_event if frm == patient_id]
        return [self.immunization_events[eid] for eid in event_ids]

    def get_event_components(self, event_id: str) -> list[QualityComponent]:
        """Which components an event satisfies."""
        comp_ids = [to for (frm, to) in self.satisfies if frm == event_id]
        return [self.quality_components[cid] for cid in comp_ids]

    def get_patient_result(self, patient_id: str) -> Optional[ComplianceResult]:
        """Compliance result for a patient."""
        result_ids = [to for (frm, to) in self.has_result if frm == patient_id]
        return self.compliance_results[result_ids[0]] if result_ids else None

    def get_flagged_events(self) -> list[tuple[Patient, ImmunizationEvent, HumanReviewItem]]:
        """All events flagged for human review."""
        flagged = []
        for (event_id, review_id) in self.flagged_for_review:
            event = self.immunization_events[event_id]
            review = self.human_review_items[review_id]
            patient = next(
                (self.patients[pid] for (pid, eid) in self.has_event if eid == event_id),
                None
            )
            flagged.append((patient, event, review))
        return flagged

    def get_audit_chain(self, patient_id: str) -> dict:
        """Full audit chain for a patient — result + source data + audit log."""
        result = self.get_patient_result(patient_id)
        snapshot_ids = [to for (frm, to) in self.used_snapshot if result and frm == result.result_id]
        snapshot = self.data_snapshots[snapshot_ids[0]] if snapshot_ids else None
        audit_ids = [frm for (frm, to) in self.audit_for if to == patient_id]
        audits = [self.audit_events[aid] for aid in audit_ids]
        return {
            "patient":    self.patients[patient_id],
            "result":     result,
            "snapshot":   snapshot,
            "audit_log":  audits,
        }

    # ── Print helpers ─────────────────────────────────────────────────────────

    def print_summary(self):
        print("\n" + "="*60)
        print("  CIS-10 KNOWLEDGE GRAPH SUMMARY")
        print("="*60)
        print(f"  Patients:             {len(self.patients)}")
        print(f"  Immunization events:  {len(self.immunization_events)}")
        print(f"  Quality components:   {len(self.quality_components)}")
        print(f"  Compliance results:   {len(self.compliance_results)}")
        print(f"  Data snapshots:       {len(self.data_snapshots)}")
        print(f"  Human review items:   {len(self.human_review_items)}")
        print(f"  Audit events:         {len(self.audit_events)}")
        print()
        print(f"  HAS_EVENT edges:          {len(self.has_event)}")
        print(f"  SATISFIES edges:          {len(self.satisfies)}")
        print(f"  FROM_SNAPSHOT edges:      {len(self.from_snapshot)}")
        print(f"  HAS_RESULT edges:         {len(self.has_result)}")
        print(f"  USED_SNAPSHOT edges:      {len(self.used_snapshot)}")
        print(f"  FLAGGED_FOR_REVIEW edges: {len(self.flagged_for_review)}")
        print(f"  AUDIT_FOR edges:          {len(self.audit_for)}")
        print("="*60 + "\n")


# ── Build the graph ───────────────────────────────────────────────────────────

def build_graph() -> KnowledgeGraph:
    g = KnowledgeGraph()

    # Data snapshot (source FHIR bundle)
    g.add_snapshot(DataSnapshot(
        snapshot_id  = "DS-001",
        source_file  = "CIS10_demo_patients.json",
        sha256       = "a3f9b2c1d4e5f6a7b8c9d0e1f2a3b4c5",
        ingested_at  = "2025-06-01T08:00:00Z",
    ))

    # CIS-10 vaccine components
    components = [
        ("CIS10_DTaP",      "DTaP",      4),
        ("CIS10_IPV",       "IPV",       3),
        ("CIS10_MMR",       "MMR",       1),
        ("CIS10_HiB",       "HiB",       3),
        ("CIS10_HepB",      "HepB",      3),
        ("CIS10_VZV",       "VZV",       1),
        ("CIS10_PCV",       "PCV",       4),
        ("CIS10_HepA",      "HepA",      2),
        ("CIS10_Rotavirus", "Rotavirus", 3),
        ("CIS10_Influenza", "Influenza", 2),
    ]
    for cid, name, count in components:
        g.add_component(QualityComponent(cid, name, count))

    # ── Patient 1: Emma Rodriguez ─────────────────────────────────────────────
    g.add_patient(Patient("PAT-8392", "Emma Rodriguez", "2023-01-15", "F", 2025))

    emma_events = [
        ("EVT-001", "20", "DTaP",      "2023-03-20", "EHR",  1.0),
        ("EVT-002", "20", "DTaP",      "2023-05-15", "EHR",  1.0),
        ("EVT-003", "20", "DTaP",      "2023-07-10", "EHR",  1.0),
        ("EVT-004", "49", "HiB",       "2023-03-20", "EHR",  1.0),
        ("EVT-005", "08", "HepB",      "2023-01-16", "EHR",  1.0),
        ("EVT-006", "88", "Influenza", "2023-10-01", "NOTE", 0.72),  # low confidence
    ]
    emma_satisfies = {
        "EVT-001": "CIS10_DTaP",
        "EVT-002": "CIS10_DTaP",
        "EVT-003": "CIS10_DTaP",
        "EVT-004": "CIS10_HiB",
        "EVT-005": "CIS10_HepB",
    }
    for (eid, cvx, vaccine, date, source, conf) in emma_events:
        g.add_event(ImmunizationEvent(eid, cvx, vaccine, date, source, conf))
        g.link("has_event",     "PAT-8392", eid)
        g.link("from_snapshot", eid, "DS-001")
        if eid in emma_satisfies:
            g.link("satisfies", eid, emma_satisfies[eid])

    # Low-confidence event → human review
    g.add_review_item(HumanReviewItem("REVIEW-001", "administeredDate", "2023-10-01", 0.72, "PENDING"))
    g.link("flagged_for_review", "EVT-006", "REVIEW-001")

    g.add_result(ComplianceResult("CALC-8392", "NON_COMPLIANT", ["MMR", "HepA", "Influenza"], "2025-06-01T09:00:00Z", "HEDIS-2025"))
    g.link("has_result",    "PAT-8392", "CALC-8392")
    g.link("used_snapshot", "CALC-8392", "DS-001")

    g.add_audit_event(AuditEvent("AUDIT-001", "CALCULATION", "SYSTEM", "CIS-10 calculated for Emma Rodriguez — NON_COMPLIANT (missing MMR, HepA, Influenza)", "2025-06-01T09:00:00Z"))
    g.link("audit_for", "AUDIT-001", "PAT-8392")

    # ── Patient 2: Liam Chen ──────────────────────────────────────────────────
    g.add_patient(Patient("PAT-9102", "Liam Chen", "2023-03-22", "M", 2025))

    liam_events = [
        ("EVT-007", "20", "DTaP",     "2023-05-25", "EHR", 1.0),
        ("EVT-008", "20", "DTaP",     "2023-07-20", "EHR", 1.0),
        ("EVT-009", "20", "DTaP",     "2023-09-18", "EHR", 1.0),
        ("EVT-010", "20", "DTaP",     "2024-03-22", "EHR", 1.0),
        ("EVT-011", "03", "MMR",      "2024-04-01", "EHR", 1.0),
        ("EVT-012", "21", "VZV",      "2024-04-01", "EHR", 1.0),
        ("EVT-013", "88", "Influenza","2024-10-05", "EHR", 1.0),
    ]
    liam_satisfies = {
        "EVT-007": "CIS10_DTaP",
        "EVT-008": "CIS10_DTaP",
        "EVT-009": "CIS10_DTaP",
        "EVT-010": "CIS10_DTaP",
        "EVT-011": "CIS10_MMR",
        "EVT-012": "CIS10_VZV",
        "EVT-013": "CIS10_Influenza",
    }
    for (eid, cvx, vaccine, date, source, conf) in liam_events:
        g.add_event(ImmunizationEvent(eid, cvx, vaccine, date, source, conf))
        g.link("has_event",     "PAT-9102", eid)
        g.link("from_snapshot", eid, "DS-001")
        if eid in liam_satisfies:
            g.link("satisfies", eid, liam_satisfies[eid])

    g.add_result(ComplianceResult("CALC-9102", "NON_COMPLIANT", ["IPV", "HiB", "HepB", "PCV", "HepA", "Rotavirus"], "2025-06-01T09:00:00Z", "HEDIS-2025"))
    g.link("has_result",    "PAT-9102", "CALC-9102")
    g.link("used_snapshot", "CALC-9102", "DS-001")

    g.add_audit_event(AuditEvent("AUDIT-002", "CALCULATION", "SYSTEM", "CIS-10 calculated for Liam Chen — NON_COMPLIANT", "2025-06-01T09:00:00Z"))
    g.link("audit_for", "AUDIT-002", "PAT-9102")

    return g


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    g = build_graph()
    g.print_summary()

    # Query 1: each patient's vaccines
    print("── Vaccines per patient ─────────────────────────────────────")
    for patient in g.patients.values():
        events = g.get_patient_events(patient.patient_id)
        print(f"\n  {patient.name} ({patient.patient_id})")
        for e in events:
            components = g.get_event_components(e.event_id)
            satisfies = components[0].name if components else "—"
            conf = f"  ⚠ low confidence ({e.confidence})" if e.confidence < 0.9 else ""
            print(f"    {e.date}  {e.vaccine:<12} source={e.source:<8} satisfies={satisfies}{conf}")

    # Query 2: compliance results
    print("\n── Compliance results ───────────────────────────────────────")
    for patient in g.patients.values():
        result = g.get_patient_result(patient.patient_id)
        if result:
            missing = ", ".join(result.missing_components) or "none"
            print(f"  {patient.name}: {result.status}  —  missing: {missing}")

    # Query 3: flagged for review
    print("\n── Events flagged for human review ─────────────────────────")
    flagged = g.get_flagged_events()
    if flagged:
        for (patient, event, review) in flagged:
            print(f"  {patient.name} — {event.vaccine} on {event.date} (confidence={event.confidence}) — status: {review.status}")
    else:
        print("  None")

    # Query 4: full audit chain for Emma
    print("\n── Audit chain for Emma Rodriguez ──────────────────────────")
    chain = g.get_audit_chain("PAT-8392")
    print(f"  Patient:   {chain['patient'].name}")
    print(f"  Status:    {chain['result'].status}")
    print(f"  Missing:   {', '.join(chain['result'].missing_components)}")
    print(f"  Source:    {chain['snapshot'].source_file}")
    print(f"  SHA-256:   {chain['snapshot'].sha256}")
    for a in chain['audit_log']:
        print(f"  Audit:     [{a.timestamp}] {a.description}")

    print()


if __name__ == "__main__":
    main()
