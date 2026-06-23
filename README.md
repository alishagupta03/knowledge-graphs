# CQI Knowledge Graph — Schema Draft

> Draft schema for the 101GenAI Care Quality Intelligence (CQI) platform.  
> Covers two HEDIS use cases: **CIS-10** (Childhood Immunization Status) and **CCS** (Cervical Cancer Screening).

This repo contains a Python script that sets up the Neo4j graph schema — constraints, indexes, and sample patient data — so you can explore the graph structure visually in Neo4j Browser.

---

## What's in the graph

The schema is organized into five layers:

| Layer | Nodes |
|-------|-------|
| Core | `Patient`, `MeasureContext`, `DataSnapshot` |
| Clinical events | `ImmunizationEvent`, `ScreeningEvent`, `ObservationEvent` |
| Quality logic | `QualityComponent`, `ComplianceResult`, `EligibilityWindow` |
| Agent infrastructure | `SemanticRule`, `AgentTrace`, `HumanReviewItem` |
| Audit | `AuditEvent`, `OutreachEvent` |

The key design idea: `ClinicalEvent` is an abstract parent type. `ImmunizationEvent` (used by CIS-10) and `ScreeningEvent` (used by CCS) are subtypes. Adding a new HEDIS measure only requires new `MeasureContext`, `QualityComponent`, and `SemanticRule` nodes — no schema changes.

---

## Setup

### 1. Get a free Neo4j database

Go to [neo4j.com/cloud/aura-free](https://neo4j.com/cloud/aura-free/) and create a free AuraDB instance. Save your connection URI and password.

### 2. Install the Python driver

```bash
pip install neo4j
```

### 3. Set your credentials

Either export them as environment variables:

```bash
export NEO4J_URI="neo4j+s://xxxxxxxx.databases.neo4j.io"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="your-password"
```

Or just paste them directly into `schema.py` (fine for local use, don't commit the password).

### 4. Run the script

```bash
python schema.py
```

### 5. Open Neo4j Browser

Go to your AuraDB instance → Open Browser, then run:

```cypher
MATCH (n) RETURN n LIMIT 100
```

You should see the full graph with patients, clinical events, compliance results, and audit nodes.

---

## Sample queries

These are all in the `DEMO_QUERIES` variable in `schema.py`. Copy-paste into Neo4j Browser:

```cypher
-- Emma's full graph neighborhood
MATCH (p:Patient {patientId: "PAT-8392"})-[r]->(n)
RETURN p, r, n

-- All non-compliant patients and what they're missing
MATCH (p:Patient)-[:HAS_RESULT]->(r:ComplianceResult)
WHERE r.overallStatus = "NON_COMPLIANT"
RETURN p.name, r.missingComponents

-- Full audit chain (for NCQA audit defense)
MATCH (p:Patient {patientId: "PAT-8392"})-[:HAS_RESULT]->(r:ComplianceResult)
      -[:USED_SNAPSHOT]->(ds:DataSnapshot)
MATCH (r)-[:FOR_MEASURE]->(m:MeasureContext)
MATCH (ae:AuditEvent)-[:AUDIT_FOR]->(p)
RETURN p.name, r.overallStatus, r.missingComponents, ds.sha256, m.measureId, ae.description
```

---

## Sample data included

| Patient | Measure | Status | Notes |
|---------|---------|--------|-------|
| Emma Rodriguez (PAT-8392) | CIS-10 | NON_COMPLIANT | Missing MMR, HepA, Influenza. One low-confidence influenza event flagged for nurse review. |
| Liam Chen (PAT-9102) | CIS-10 | (no result yet) | Enrolled, no events loaded |
| Sofia Patel (PAT-5501) | CCS | COMPLIANT | Normal Pap smear on file |

---

## Open questions (for team review)

1. Should `ClinicalEvent` subtypes use Neo4j multi-labels (`:ClinicalEvent:ImmunizationEvent`) or a single label with a `type` property?
2. Should `MeasureContext` serve as the KG root node, or do we need a separate `KGRoot` above `Patient`?
3. Should `goldenPathStatus` live on `AgentTrace` or on a separate `GoldenPath` node?
4. Should the LLM-generated code for `daysToDeadline` be stored on `AgentTrace` for reproducibility?
5. Are there FHIR resource types beyond Immunization, Observation, and Procedure needed for CCS (e.g., DiagnosticReport)?
