"""
CQI Knowledge Graph — CIS-10 Schema
101GenAI | Care Quality Intelligence Platform

Sets up a Neo4j graph for the HEDIS CIS-10 (Childhood Immunization Status)
quality measure, including constraints and sample patient data.

Requirements:
    pip install neo4j

Usage:
    1. Create a free Neo4j AuraDB at https://neo4j.com/cloud/aura-free/
    2. Fill in your URI, username, and password below
    3. Run: python schema.py
"""

import os
from neo4j import GraphDatabase

# ── Connection ────────────────────────────────────────────────────────────────
URI      = os.getenv("NEO4J_URI",      "neo4j+s://YOUR_URI.databases.neo4j.io")
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password-here")


# ── Constraints ───────────────────────────────────────────────────────────────
CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Patient)          REQUIRE n.patientId   IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:ImmunizationEvent) REQUIRE n.eventId    IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:QualityComponent) REQUIRE n.componentId IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:ComplianceResult) REQUIRE n.resultId    IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:DataSnapshot)     REQUIRE n.snapshotId  IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AuditEvent)       REQUIRE n.eventId     IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:HumanReviewItem)  REQUIRE n.reviewId    IS UNIQUE",
]


# ── Sample Data ───────────────────────────────────────────────────────────────
SAMPLE_DATA = """

// ── Patients ──────────────────────────────────────────────────────────────────
MERGE (p1:Patient {
    patientId:        "PAT-8392",
    name:             "Emma Rodriguez",
    dob:              date("2023-01-15"),
    gender:           "F",
    measurementYear:  2025
})
MERGE (p2:Patient {
    patientId:        "PAT-9102",
    name:             "Liam Chen",
    dob:              date("2023-03-22"),
    gender:           "M",
    measurementYear:  2025
})

// ── Data Snapshot (source FHIR bundle) ───────────────────────────────────────
MERGE (ds:DataSnapshot {
    snapshotId:  "DS-001",
    sourceFile:  "CIS10_demo_patients.json",
    sha256:      "a3f9b2c1d4e5f6a7b8c9d0e1f2a3b4c5",
    fhirServer:  "http://fhir.demo.local/fhir",
    ingestedAt:  datetime("2025-06-01T08:00:00Z")
})

// ── CIS-10 Vaccine Components (what each child needs) ─────────────────────────
MERGE (dtap:QualityComponent { componentId: "CIS10_DTaP",      name: "DTaP",      requiredCount: 4 })
MERGE (ipv:QualityComponent  { componentId: "CIS10_IPV",       name: "IPV",       requiredCount: 3 })
MERGE (mmr:QualityComponent  { componentId: "CIS10_MMR",       name: "MMR",       requiredCount: 1 })
MERGE (hib:QualityComponent  { componentId: "CIS10_HiB",       name: "HiB",       requiredCount: 3 })
MERGE (hepb:QualityComponent { componentId: "CIS10_HepB",      name: "HepB",      requiredCount: 3 })
MERGE (vzv:QualityComponent  { componentId: "CIS10_VZV",       name: "VZV",       requiredCount: 1 })
MERGE (pcv:QualityComponent  { componentId: "CIS10_PCV",       name: "PCV",       requiredCount: 4 })
MERGE (hepa:QualityComponent { componentId: "CIS10_HepA",      name: "HepA",      requiredCount: 2 })
MERGE (rota:QualityComponent { componentId: "CIS10_Rotavirus", name: "Rotavirus", requiredCount: 3 })
MERGE (flu:QualityComponent  { componentId: "CIS10_Influenza", name: "Influenza", requiredCount: 2 })

// ── Emma's immunization events ────────────────────────────────────────────────
// Emma has DTaP x3 (needs 4), HiB x1, HepB x1 — missing MMR, HepA, Influenza
MERGE (e1:ImmunizationEvent { eventId: "EVT-001", cvxCode: "20", vaccine: "DTaP",     date: date("2023-03-20"), source: "EHR",      confidence: 1.0 })
MERGE (e2:ImmunizationEvent { eventId: "EVT-002", cvxCode: "20", vaccine: "DTaP",     date: date("2023-05-15"), source: "EHR",      confidence: 1.0 })
MERGE (e3:ImmunizationEvent { eventId: "EVT-003", cvxCode: "20", vaccine: "DTaP",     date: date("2023-07-10"), source: "EHR",      confidence: 1.0 })
MERGE (e4:ImmunizationEvent { eventId: "EVT-004", cvxCode: "49", vaccine: "HiB",      date: date("2023-03-20"), source: "EHR",      confidence: 1.0 })
MERGE (e5:ImmunizationEvent { eventId: "EVT-005", cvxCode: "08", vaccine: "HepB",     date: date("2023-01-16"), source: "EHR",      confidence: 1.0 })
// Low-confidence event from a clinical note — flagged for nurse review
MERGE (e6:ImmunizationEvent { eventId: "EVT-006", cvxCode: "88", vaccine: "Influenza",date: date("2023-10-01"), source: "NOTE",     confidence: 0.72 })

MERGE (p1)-[:HAS_EVENT]->(e1)
MERGE (p1)-[:HAS_EVENT]->(e2)
MERGE (p1)-[:HAS_EVENT]->(e3)
MERGE (p1)-[:HAS_EVENT]->(e4)
MERGE (p1)-[:HAS_EVENT]->(e5)
MERGE (p1)-[:HAS_EVENT]->(e6)

// Link every event back to its source bundle
MERGE (e1)-[:FROM_SNAPSHOT]->(ds)
MERGE (e2)-[:FROM_SNAPSHOT]->(ds)
MERGE (e3)-[:FROM_SNAPSHOT]->(ds)
MERGE (e4)-[:FROM_SNAPSHOT]->(ds)
MERGE (e5)-[:FROM_SNAPSHOT]->(ds)
MERGE (e6)-[:FROM_SNAPSHOT]->(ds)

// Which component does each event satisfy?
MERGE (e1)-[:SATISFIES]->(dtap)
MERGE (e2)-[:SATISFIES]->(dtap)
MERGE (e3)-[:SATISFIES]->(dtap)
MERGE (e4)-[:SATISFIES]->(hib)
MERGE (e5)-[:SATISFIES]->(hepb)

// ── Emma's compliance result ───────────────────────────────────────────────────
MERGE (res1:ComplianceResult {
    resultId:          "CALC-8392-001",
    status:            "NON_COMPLIANT",
    missingComponents: ["MMR", "HepA", "Influenza"],
    calculatedAt:      datetime("2025-06-01T09:00:00Z"),
    measureVersion:    "HEDIS-2025"
})
MERGE (p1)-[:HAS_RESULT]->(res1)
MERGE (res1)-[:USED_SNAPSHOT]->(ds)

// ── Human review item for Emma's low-confidence influenza event ───────────────
MERGE (hr1:HumanReviewItem {
    reviewId:         "REVIEW-001",
    field:            "administeredDate",
    aiExtractedValue: "2023-10-01",
    confidence:       0.72,
    status:           "PENDING"
})
MERGE (e6)-[:FLAGGED_FOR_REVIEW]->(hr1)

// ── Audit event for Emma's calculation ────────────────────────────────────────
MERGE (ae1:AuditEvent {
    eventId:     "AUDIT-001",
    type:        "CALCULATION",
    actor:       "SYSTEM",
    description: "CIS-10 calculated for PAT-8392 — NON_COMPLIANT (missing MMR, HepA, Influenza)",
    timestamp:   datetime("2025-06-01T09:00:00Z")
})
MERGE (ae1)-[:AUDIT_FOR]->(p1)

// ── Liam's immunization events ────────────────────────────────────────────────
// Liam is more complete — compliant on everything except HepA
MERGE (e7:ImmunizationEvent  { eventId: "EVT-007", cvxCode: "20",  vaccine: "DTaP",    date: date("2023-05-25"), source: "EHR", confidence: 1.0 })
MERGE (e8:ImmunizationEvent  { eventId: "EVT-008", cvxCode: "20",  vaccine: "DTaP",    date: date("2023-07-20"), source: "EHR", confidence: 1.0 })
MERGE (e9:ImmunizationEvent  { eventId: "EVT-009", cvxCode: "20",  vaccine: "DTaP",    date: date("2023-09-18"), source: "EHR", confidence: 1.0 })
MERGE (e10:ImmunizationEvent { eventId: "EVT-010", cvxCode: "20",  vaccine: "DTaP",    date: date("2024-03-22"), source: "EHR", confidence: 1.0 })
MERGE (e11:ImmunizationEvent { eventId: "EVT-011", cvxCode: "03",  vaccine: "MMR",     date: date("2024-04-01"), source: "EHR", confidence: 1.0 })
MERGE (e12:ImmunizationEvent { eventId: "EVT-012", cvxCode: "21",  vaccine: "VZV",     date: date("2024-04-01"), source: "EHR", confidence: 1.0 })
MERGE (e13:ImmunizationEvent { eventId: "EVT-013", cvxCode: "88",  vaccine: "Influenza",date: date("2024-10-05"), source: "EHR", confidence: 1.0 })

MERGE (p2)-[:HAS_EVENT]->(e7)
MERGE (p2)-[:HAS_EVENT]->(e8)
MERGE (p2)-[:HAS_EVENT]->(e9)
MERGE (p2)-[:HAS_EVENT]->(e10)
MERGE (p2)-[:HAS_EVENT]->(e11)
MERGE (p2)-[:HAS_EVENT]->(e12)
MERGE (p2)-[:HAS_EVENT]->(e13)

MERGE (e7)-[:FROM_SNAPSHOT]->(ds)
MERGE (e8)-[:FROM_SNAPSHOT]->(ds)
MERGE (e9)-[:FROM_SNAPSHOT]->(ds)
MERGE (e10)-[:FROM_SNAPSHOT]->(ds)
MERGE (e11)-[:FROM_SNAPSHOT]->(ds)
MERGE (e12)-[:FROM_SNAPSHOT]->(ds)
MERGE (e13)-[:FROM_SNAPSHOT]->(ds)

MERGE (e7)-[:SATISFIES]->(dtap)
MERGE (e8)-[:SATISFIES]->(dtap)
MERGE (e9)-[:SATISFIES]->(dtap)
MERGE (e10)-[:SATISFIES]->(dtap)
MERGE (e11)-[:SATISFIES]->(mmr)
MERGE (e12)-[:SATISFIES]->(vzv)
MERGE (e13)-[:SATISFIES]->(flu)

MERGE (res2:ComplianceResult {
    resultId:          "CALC-9102-001",
    status:            "NON_COMPLIANT",
    missingComponents: ["IPV", "HiB", "HepB", "PCV", "HepA", "Rotavirus"],
    calculatedAt:      datetime("2025-06-01T09:00:00Z"),
    measureVersion:    "HEDIS-2025"
})
MERGE (p2)-[:HAS_RESULT]->(res2)
MERGE (res2)-[:USED_SNAPSHOT]->(ds)

MERGE (ae2:AuditEvent {
    eventId:     "AUDIT-002",
    type:        "CALCULATION",
    actor:       "SYSTEM",
    description: "CIS-10 calculated for PAT-9102 — NON_COMPLIANT",
    timestamp:   datetime("2025-06-01T09:00:00Z")
})
MERGE (ae2)-[:AUDIT_FOR]->(p2)
"""


# ── Demo Queries ──────────────────────────────────────────────────────────────
# Copy-paste any of these into Neo4j Browser to explore the graph

DEMO_QUERIES = """
-- See everything
MATCH (n) RETURN n LIMIT 100

-- Emma's full neighborhood
MATCH (p:Patient {patientId: "PAT-8392"})-[r]->(n)
RETURN p, r, n

-- Which vaccines has each patient received, and what do they satisfy?
MATCH (p:Patient)-[:HAS_EVENT]->(e:ImmunizationEvent)-[:SATISFIES]->(c:QualityComponent)
RETURN p.name, e.vaccine, e.date, c.name
ORDER BY p.name, e.date

-- Non-compliant patients and what's missing
MATCH (p:Patient)-[:HAS_RESULT]->(r:ComplianceResult)
WHERE r.status = "NON_COMPLIANT"
RETURN p.name, r.missingComponents

-- Events flagged for nurse review
MATCH (p:Patient)-[:HAS_EVENT]->(e:ImmunizationEvent)-[:FLAGGED_FOR_REVIEW]->(hr:HumanReviewItem)
RETURN p.name, e.vaccine, e.confidence, hr.status

-- Full audit chain for Emma (for NCQA audit defense)
MATCH (p:Patient {patientId: "PAT-8392"})-[:HAS_RESULT]->(r:ComplianceResult)-[:USED_SNAPSHOT]->(ds:DataSnapshot)
MATCH (ae:AuditEvent)-[:AUDIT_FOR]->(p)
RETURN p.name, r.status, r.missingComponents, ds.sha256, ae.description
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

        print("\nDone! Open Neo4j Browser and run:")
        print("  MATCH (n) RETURN n LIMIT 100")
        print("\nDemo queries are in the DEMO_QUERIES variable in this file.")

    driver.close()


if __name__ == "__main__":
    main()
