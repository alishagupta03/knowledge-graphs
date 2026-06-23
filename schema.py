"""
CQI Knowledge Graph — Schema Setup
101GenAI | Care Quality Intelligence Platform

Creates constraints, indexes, and sample data for two HEDIS use cases:
  - CIS-10 (Childhood Immunization Status)
  - CCS   (Cervical Cancer Screening)

Requirements:
    pip install neo4j

Usage:
    1. Create a free Neo4j AuraDB at https://neo4j.com/cloud/aura-free/
    2. Copy your connection URI, username, and password into the .env file
    3. Run: python schema.py
"""

import os
from neo4j import GraphDatabase

# ── Connection ────────────────────────────────────────────────────────────────
# Set these as environment variables, or paste directly for quick testing
URI      = os.getenv("NEO4J_URI",      "neo4j+s://YOUR_AURA_URI.databases.neo4j.io")
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password-here")


# ── Constraints & Indexes ─────────────────────────────────────────────────────
CONSTRAINTS = [
    # Each node type gets a unique constraint on its primary key
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Patient)          REQUIRE n.patientId    IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:MeasureContext)   REQUIRE n.measureId    IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:DataSnapshot)     REQUIRE n.snapshotId   IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:ClinicalEvent)    REQUIRE n.eventId      IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:QualityComponent) REQUIRE n.componentId  IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:ComplianceResult) REQUIRE n.resultId     IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:SemanticRule)     REQUIRE n.ruleId       IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AgentTrace)       REQUIRE n.traceId      IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:HumanReviewItem)  REQUIRE n.reviewId     IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AuditEvent)       REQUIRE n.eventId      IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:OutreachEvent)    REQUIRE n.outreachId   IS UNIQUE",
]


# ── Sample Data ───────────────────────────────────────────────────────────────
# Two patients, two measures, a handful of clinical events, and results.
# This is enough to make the graph visually interesting in Neo4j Browser.

SAMPLE_DATA = """
// ── Patients ──────────────────────────────────────────────────────────────────
MERGE (p1:Patient {
    patientId: "PAT-8392",
    name: "Emma Rodriguez",
    dob: date("2023-01-15"),
    gender: "F",
    measurementYear: 2025
})
MERGE (p2:Patient {
    patientId: "PAT-9102",
    name: "Liam Chen",
    dob: date("2023-03-22"),
    gender: "M",
    measurementYear: 2025
})
MERGE (p3:Patient {
    patientId: "PAT-5501",
    name: "Sofia Patel",
    dob: date("1990-07-04"),
    gender: "F",
    measurementYear: 2025
})

// ── Measure Contexts ──────────────────────────────────────────────────────────
MERGE (cis:MeasureContext {
    measureId: "CIS-10",
    measureName: "Childhood Immunization Status Combo 10",
    version: "HEDIS-2025",
    measureType: "IMMUNIZATION"
})
MERGE (ccs:MeasureContext {
    measureId: "CCS",
    measureName: "Cervical Cancer Screening",
    version: "HEDIS-2025",
    measureType: "SCREENING"
})

// ── Enroll patients in measures ───────────────────────────────────────────────
MERGE (p1)-[:ENROLLED_IN]->(cis)
MERGE (p2)-[:ENROLLED_IN]->(cis)
MERGE (p3)-[:ENROLLED_IN]->(ccs)

// ── Data Snapshots ────────────────────────────────────────────────────────────
MERGE (ds1:DataSnapshot {
    snapshotId: "DS-001",
    sourceFile: "CIS10_demo_patients.json",
    sha256: "a3f9b2c1d4e5f6a7b8c9d0e1f2a3b4c5",
    fhirServer: "http://fhir.demo.local/fhir",
    ingestedAt: datetime("2025-06-01T08:00:00Z")
})
MERGE (ds2:DataSnapshot {
    snapshotId: "DS-002",
    sourceFile: "CCS_demo_patients.json",
    sha256: "b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9",
    fhirServer: "http://fhir.demo.local/fhir",
    ingestedAt: datetime("2025-06-01T08:05:00Z")
})

// ── CIS-10: Quality Components (vaccine requirements) ─────────────────────────
MERGE (dtap:QualityComponent  { componentId: "CIS10_DTaP",      name: "DTaP",      requiredCount: 4, measureId: "CIS-10" })
MERGE (ipv:QualityComponent   { componentId: "CIS10_IPV",       name: "IPV",       requiredCount: 3, measureId: "CIS-10" })
MERGE (mmr:QualityComponent   { componentId: "CIS10_MMR",       name: "MMR",       requiredCount: 1, measureId: "CIS-10" })
MERGE (hib:QualityComponent   { componentId: "CIS10_HiB",       name: "HiB",       requiredCount: 3, measureId: "CIS-10" })
MERGE (hepb:QualityComponent  { componentId: "CIS10_HepB",      name: "HepB",      requiredCount: 3, measureId: "CIS-10" })
MERGE (vzv:QualityComponent   { componentId: "CIS10_VZV",       name: "VZV",       requiredCount: 1, measureId: "CIS-10" })
MERGE (pcv:QualityComponent   { componentId: "CIS10_PCV",       name: "PCV",       requiredCount: 4, measureId: "CIS-10" })
MERGE (hepa:QualityComponent  { componentId: "CIS10_HepA",      name: "HepA",      requiredCount: 2, measureId: "CIS-10" })
MERGE (rota:QualityComponent  { componentId: "CIS10_Rotavirus", name: "Rotavirus", requiredCount: 3, measureId: "CIS-10" })
MERGE (flu:QualityComponent   { componentId: "CIS10_Influenza", name: "Influenza", requiredCount: 2, measureId: "CIS-10" })

MERGE (cis)-[:HAS_COMPONENT]->(dtap)
MERGE (cis)-[:HAS_COMPONENT]->(ipv)
MERGE (cis)-[:HAS_COMPONENT]->(mmr)
MERGE (cis)-[:HAS_COMPONENT]->(hib)
MERGE (cis)-[:HAS_COMPONENT]->(hepb)
MERGE (cis)-[:HAS_COMPONENT]->(vzv)
MERGE (cis)-[:HAS_COMPONENT]->(pcv)
MERGE (cis)-[:HAS_COMPONENT]->(hepa)
MERGE (cis)-[:HAS_COMPONENT]->(rota)
MERGE (cis)-[:HAS_COMPONENT]->(flu)

// ── CCS: Quality Components ───────────────────────────────────────────────────
MERGE (pap:QualityComponent { componentId: "CCS_Pap",   name: "Pap smear (3yr)", requiredCount: 1, measureId: "CCS" })
MERGE (hpv:QualityComponent { componentId: "CCS_HPV",   name: "HPV cotest (5yr)", requiredCount: 1, measureId: "CCS" })
MERGE (ccs)-[:HAS_COMPONENT]->(pap)
MERGE (ccs)-[:HAS_COMPONENT]->(hpv)

// ── Semantic Rules ────────────────────────────────────────────────────────────
MERGE (r1:SemanticRule {
    ruleId: "RULE-DTaP-001",
    measureId: "CIS-10",
    predicate: "4 DTaP doses (CVX 20 or 106) between day 42 and day 730",
    ruleType: "DOSE_COUNT",
    version: "HEDIS-2025"
})
MERGE (r2:SemanticRule {
    ruleId: "RULE-MMR-001",
    measureId: "CIS-10",
    predicate: "1 MMR dose (CVX 03) between day 365 and day 730",
    ruleType: "DOSE_COUNT",
    version: "HEDIS-2025"
})
MERGE (r3:SemanticRule {
    ruleId: "RULE-CCS-PAP-001",
    measureId: "CCS",
    predicate: "1 Pap smear (LOINC 10524-7) in last 3 years for age 21-64",
    ruleType: "AGE_WINDOW",
    version: "HEDIS-2025"
})

MERGE (dtap)-[:GOVERNED_BY]->(r1)
MERGE (mmr)-[:GOVERNED_BY]->(r2)
MERGE (pap)-[:GOVERNED_BY]->(r3)

// ── Immunization Events for Emma (PAT-8392) ───────────────────────────────────
// Emma has DTaP x3 (needs 4), IPV x3, HepB x3, HiB x3, PCV x3 — missing MMR, HepA, Influenza
MERGE (e1:ClinicalEvent:ImmunizationEvent {
    eventId: "EVT-001", cvxCode: "20", vaccineDescription: "DTaP",
    administeredDate: date("2023-03-20"), source: "EHR", confidence: 1.0, humanVerified: false
})
MERGE (e2:ClinicalEvent:ImmunizationEvent {
    eventId: "EVT-002", cvxCode: "20", vaccineDescription: "DTaP",
    administeredDate: date("2023-05-15"), source: "EHR", confidence: 1.0, humanVerified: false
})
MERGE (e3:ClinicalEvent:ImmunizationEvent {
    eventId: "EVT-003", cvxCode: "20", vaccineDescription: "DTaP",
    administeredDate: date("2023-07-10"), source: "EHR", confidence: 1.0, humanVerified: false
})
MERGE (e4:ClinicalEvent:ImmunizationEvent {
    eventId: "EVT-004", cvxCode: "49", vaccineDescription: "HiB",
    administeredDate: date("2023-03-20"), source: "EHR", confidence: 1.0, humanVerified: false
})
MERGE (e5:ClinicalEvent:ImmunizationEvent {
    eventId: "EVT-005", cvxCode: "08", vaccineDescription: "HepB",
    administeredDate: date("2023-01-16"), source: "EHR", confidence: 1.0, humanVerified: false
})
// Low-confidence event from clinical note — needs nurse review
MERGE (e6:ClinicalEvent:ImmunizationEvent {
    eventId: "EVT-006", cvxCode: "88", vaccineDescription: "Influenza",
    administeredDate: date("2023-10-01"), source: "NOTE", confidence: 0.72, humanVerified: false
})

MERGE (p1)-[:HAS_EVENT]->(e1)
MERGE (p1)-[:HAS_EVENT]->(e2)
MERGE (p1)-[:HAS_EVENT]->(e3)
MERGE (p1)-[:HAS_EVENT]->(e4)
MERGE (p1)-[:HAS_EVENT]->(e5)
MERGE (p1)-[:HAS_EVENT]->(e6)

MERGE (e1)-[:USED_SNAPSHOT]->(ds1)
MERGE (e2)-[:USED_SNAPSHOT]->(ds1)
MERGE (e3)-[:USED_SNAPSHOT]->(ds1)
MERGE (e4)-[:USED_SNAPSHOT]->(ds1)
MERGE (e5)-[:USED_SNAPSHOT]->(ds1)
MERGE (e6)-[:USED_SNAPSHOT]->(ds1)

MERGE (e1)-[:SATISFIES]->(dtap)
MERGE (e2)-[:SATISFIES]->(dtap)
MERGE (e3)-[:SATISFIES]->(dtap)
MERGE (e4)-[:SATISFIES]->(hib)
MERGE (e5)-[:SATISFIES]->(hepb)

// ── Compliance Result for Emma ────────────────────────────────────────────────
MERGE (res1:ComplianceResult {
    resultId: "CALC-8392-001",
    overallStatus: "NON_COMPLIANT",
    missingComponents: ["MMR", "HepA", "Influenza"],
    calculatedAt: datetime("2025-06-01T09:00:00Z"),
    measureVersion: "HEDIS-2025",
    calculationPath: "DETERMINISTIC"
})
MERGE (p1)-[:HAS_RESULT]->(res1)
MERGE (res1)-[:FOR_MEASURE]->(cis)
MERGE (res1)-[:USED_SNAPSHOT]->(ds1)

// ── Human Review Item for low-confidence influenza event ──────────────────────
MERGE (hr1:HumanReviewItem {
    reviewId: "REVIEW-001",
    fieldName: "administeredDate",
    aiExtractedValue: "2023-10-01",
    confidence: 0.72,
    status: "PENDING"
})
MERGE (e6)-[:FLAGGED_FOR_REVIEW]->(hr1)

// ── Agent Trace for Emma's calculation ───────────────────────────────────────
MERGE (at1:AgentTrace {
    traceId: "TRACE-001",
    agentType: "COMPUTE",
    input: '{"patientId": "PAT-8392", "measure": "CIS-10"}',
    output: '{"compliant": false, "missing": ["MMR", "HepA", "Influenza"]}',
    confidence: 1.0,
    goldenPathStatus: "NONE",
    executedAt: datetime("2025-06-01T09:00:00Z")
})
MERGE (res1)-[:GENERATED_TRACE]->(at1)

// ── Audit Event ───────────────────────────────────────────────────────────────
MERGE (ae1:AuditEvent {
    eventId: "AUDIT-001",
    eventType: "CALCULATION",
    actor: "SYSTEM",
    description: "CIS-10 compliance calculated for PAT-8392 — NON_COMPLIANT (missing MMR, HepA, Influenza)",
    timestamp: datetime("2025-06-01T09:00:00Z")
})
MERGE (ae1)-[:AUDIT_FOR]->(p1)

// ── Screening Event for Sofia (CCS) ───────────────────────────────────────────
MERGE (s1:ClinicalEvent:ScreeningEvent {
    eventId: "EVT-101",
    loincCode: "10524-7",
    screeningType: "PAP_SMEAR",
    date: date("2024-03-10"),
    result: "NORMAL",
    source: "EHR",
    confidence: 1.0
})
MERGE (p3)-[:HAS_EVENT]->(s1)
MERGE (s1)-[:USED_SNAPSHOT]->(ds2)
MERGE (s1)-[:SATISFIES]->(pap)

MERGE (res2:ComplianceResult {
    resultId: "CALC-5501-001",
    overallStatus: "COMPLIANT",
    missingComponents: [],
    calculatedAt: datetime("2025-06-01T09:05:00Z"),
    measureVersion: "HEDIS-2025",
    calculationPath: "DETERMINISTIC"
})
MERGE (p3)-[:HAS_RESULT]->(res2)
MERGE (res2)-[:FOR_MEASURE]->(ccs)
MERGE (res2)-[:USED_SNAPSHOT]->(ds2)

// ── Outreach Event for Emma ───────────────────────────────────────────────────
MERGE (oe1:OutreachEvent {
    outreachId: "OUTREACH-001",
    channel: "SMS",
    status: "DELIVERED",
    sentAt: datetime("2025-06-02T09:02:00Z"),
    response: null
})
MERGE (oe1)-[:OUTREACH_FOR]->(p1)
"""


# ── Useful Demo Queries ────────────────────────────────────────────────────────
# Copy-paste these into Neo4j Browser to explore the graph

DEMO_QUERIES = """
-- See Emma's full graph neighborhood
MATCH (p:Patient {patientId: "PAT-8392"})-[r]->(n)
RETURN p, r, n

-- All non-compliant patients and what they're missing
MATCH (p:Patient)-[:HAS_RESULT]->(r:ComplianceResult)
WHERE r.overallStatus = "NON_COMPLIANT"
RETURN p.name, r.missingComponents

-- Full audit chain for a calculation
MATCH (p:Patient {patientId: "PAT-8392"})-[:HAS_RESULT]->(r:ComplianceResult)
      -[:USED_SNAPSHOT]->(ds:DataSnapshot)
MATCH (r)-[:FOR_MEASURE]->(m:MeasureContext)
MATCH (ae:AuditEvent)-[:AUDIT_FOR]->(p)
RETURN p.name, r.overallStatus, r.missingComponents, ds.sha256, m.measureId, ae.description

-- All events that need human review
MATCH (e:ClinicalEvent)-[:FLAGGED_FOR_REVIEW]->(hr:HumanReviewItem)
MATCH (p:Patient)-[:HAS_EVENT]->(e)
RETURN p.name, e.vaccineDescription, e.confidence, hr.status

-- Which events satisfy which components (CIS-10)
MATCH (p:Patient)-[:HAS_EVENT]->(e:ImmunizationEvent)-[:SATISFIES]->(c:QualityComponent)
RETURN p.name, e.vaccineDescription, e.administeredDate, c.name
ORDER BY p.name, e.administeredDate

-- Measure components and the rules that govern them
MATCH (m:MeasureContext)-[:HAS_COMPONENT]->(c:QualityComponent)-[:GOVERNED_BY]->(r:SemanticRule)
RETURN m.measureId, c.name, r.predicate
"""


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Connecting to Neo4j...")
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    with driver.session() as session:
        print("Creating constraints...")
        for constraint in CONSTRAINTS:
            session.run(constraint)

        print("Loading sample data...")
        session.run(SAMPLE_DATA)

        print("Done! Graph is ready.")
        print()
        print("Open Neo4j Browser and run this to see everything:")
        print("  MATCH (n) RETURN n LIMIT 100")
        print()
        print("Demo queries are in the DEMO_QUERIES variable in this file.")

    driver.close()


if __name__ == "__main__":
    main()
