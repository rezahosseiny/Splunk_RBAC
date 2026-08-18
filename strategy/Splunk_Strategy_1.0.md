# Splunk Strategy

**Tri-State Generation and Transmission Association**
**Revision 1.0**
**Author: Reza Hosseiny, Vice President, Technical Services**

> This document does not include BES Cyber System Information and is intended for Tri-State internal use only.

---

## Contents

- [Introduction](#introduction)
- [Executive Summary](#executive-summary)
- [Purpose, Scope & Audience](#purpose-scope-audience)
  - [Purpose](#purpose)
  - [Scope](#scope)
  - [Audience](#audience)
- [Vision](#vision)
- [Strategic Intent & Design Choices](#strategic-intent-design-choices)
  - [Objectives](#objectives)
  - [Key Strategic Design Choices](#key-strategic-design-choices)
- [Principles](#principles)
- [Governance & Operating Model](#governance-operating-model)
  - [Governance](#governance)
  - [Governance structure and decision rights](#governance-structure-and-decision-rights)
  - [Governance controls](#governance-controls)
  - [Operating Model](#operating-model)
  - [Core roles](#core-roles)
  - [Standard workflows](#standard-workflows)
  - [Success measures](#success-measures)
- [High-Level Architecture Strategy](#high-level-architecture-strategy)
  - [Target Topology: Stretched Active–Active Multi-Site Cluster](#target-topology-stretched-activeactive-multi-site-cluster)
    - [Site Roles](#site-roles)
  - [Component Role Strategy (Separation of Functions)](#component-role-strategy-separation-of-functions)
  - [Server Role Isolation Rules (Role Mixing Restrictions)](#server-role-isolation-rules-role-mixing-restrictions)
    - [Indexers](#indexers)
    - [Search Heads](#search-heads)
    - [Management Plane (Utility Server)](#management-plane-utility-server)
    - [Ingestion Plane](#ingestion-plane)
    - [Tenant / Dedicated Search Heads](#tenant-dedicated-search-heads)
  - [Network Zoning & Zero Trust Architecture](#network-zoning-zero-trust-architecture)
  - [Scalability & Multi-Tenancy Strategy](#scalability-multi-tenancy-strategy)
- [Availability, Resiliency & DR Strategy](#availability-resiliency-dr-strategy)
  - [Clustering & Replication Logic (N–1 Baseline)](#clustering-replication-logic-n1-baseline)
  - [Failure and Partition Scenarios](#failure-and-partition-scenarios)
- [Data Strategy & Onboarding](#data-strategy-onboarding)
  - [Data Classification & Governance](#data-classification-governance)
  - [Data Classes (Sensitivity)](#data-classes-sensitivity)
- [Indexing, Retention & Lifecycle Management](#indexing-retention-lifecycle-management)
  - [Schema](#schema)
  - [Governance Prefix (Mandatory, 3-letter codes)](#governance-prefix-mandatory-3-letter-codes)
    - [Data Class (class) – STRICTLY DEFINED](#data-class-class-strictly-defined)
    - [Compliance (compliance) – DEFINABLE by Data Governance Council](#compliance-compliance-definable-by-data-governance-council)
    - [Domain (domain) – DEFINABLE by Data Governance Council](#domain-domain-definable-by-data-governance-council)
    - [Content (content) – DEFINABLE by Data Governance Council](#content-content-definable-by-data-governance-council)
    - [Optional Detail (Flexible)](#optional-detail-flexible)
    - [Retention Suffix (Mandatory)](#retention-suffix-mandatory)
    - [Real-world naming examples](#real-world-naming-examples)
  - [Segregation Rules](#segregation-rules)
  - [Retention & Lifecycle Strategy](#retention-lifecycle-strategy)
  - [Lifecycle definitions:](#lifecycle-definitions)
  - [Data Catalog](#data-catalog)
  - [Metadata Standards (source, sourcetype, host)](#metadata-standards-source-sourcetype-host)
    - [sourcetype standard](#sourcetype-standard)
    - [source standard](#source-standard)
    - [host standard](#host-standard)
    - [Standard ownership and maintenance](#standard-ownership-and-maintenance)
  - [Data Quality & Timestamping](#data-quality-timestamping)
  - [Field Naming & CIM Alignment](#field-naming-cim-alignment)
    - [Data Dictionary Mandate](#data-dictionary-mandate)
    - [Governance & Approval](#governance-approval)
    - [Naming Standards](#naming-standards)
  - [The Sandbox Protocol (Temporary Innovation)](#the-sandbox-protocol-temporary-innovation)
    - [Scope & Purpose](#scope-purpose)
    - [Relaxed Standards](#relaxed-standards)
    - [Restrictions](#restrictions)
- [Role Based Access Control (RBAC)](#role-based-access-control-rbac)
  - [Conceptual Model](#conceptual-model)
  - [Role Types and Naming Convention](#role-types-and-naming-convention)
    - [Conventions](#conventions)
    - [Business Roles (rl_)](#business-roles-rl_)
    - [Privilege Bundles (pr_)](#privilege-bundles-pr_)
  - [Integration with Data Classification and Index Naming](#integration-with-data-classification-and-index-naming)
  - [Multi-Tenancy and Tenant Search Heads](#multi-tenancy-and-tenant-search-heads)
  - [Sandbox and Temporary Access](#sandbox-and-temporary-access)
  - [Enforcement of the 1:1 User–Role Relationship](#enforcement-of-the-11-userrole-relationship)
    - [Enforcement In the IdP (AD/LDAP/SAML)](#enforcement-in-the-idp-adldapsaml)
    - [Enforcement In Splunk](#enforcement-in-splunk)
    - [Monitoring and Reporting](#monitoring-and-reporting)
- [Security, Privacy & Compliance](#security-privacy-compliance)
  - [Data Protection & Segregation](#data-protection-segregation)
  - [Access Control & Identity](#access-control-identity)
  - [Network Security & Encryption](#network-security-encryption)
  - [Regulatory Compliance & Auditability](#regulatory-compliance-auditability)
  - [Privacy & Data Minimization](#privacy-data-minimization)
- [Performance, Capacity, Sizing & Cost Awareness](#performance-capacity-sizing-cost-awareness)
- [App, Content & Use Case Development](#app-content-use-case-development)
  - [Objectives](#objectives-1)
  - [Use Case Intake & Prioritization](#use-case-intake-prioritization)
  - [Content Standards (Searches, Alerts, Dashboards, Knowledge Objects)](#content-standards-searches-alerts-dashboards-knowledge-objects)
    - [Searches & Alerts](#searches-alerts)
    - [Dashboards & Reports](#dashboards-reports)
  - [Other Splunk Entities Catalog and Naming Standards](#other-splunk-entities-catalog-and-naming-standards)
    - [In-scope entities](#in-scope-entities)
    - [Naming convention](#naming-convention)
    - [Prefixes](#prefixes)
    - [Suffixes](#suffixes)
    - [Management rule](#management-rule)
  - [Knowledge Objects (KOs)](#knowledge-objects-kos)
  - [Knowledge Object Sharing & Multi-Tenancy](#knowledge-object-sharing-multi-tenancy)
    - [Scope & Sharing](#scope-sharing)
    - [Tenant / Dedicated Search Heads](#tenant-dedicated-search-heads-1)
  - [Apps & Technology Add-ons (TAs)](#apps-technology-add-ons-tas)
    - [Splunkbase Apps](#splunkbase-apps)
    - [Internal Apps](#internal-apps)
  - [Custom Commands, Custom Code, and Apps](#custom-commands-custom-code-and-apps)
    - [Guiding Principles](#guiding-principles)
  - [Environment & Configuration-as-Code Guardrails](#environment-configuration-as-code-guardrails)
    - [Where custom code is allowed](#where-custom-code-is-allowed)
    - [Source control and documentation](#source-control-and-documentation)
    - [Languages, runtimes, and platforms](#languages-runtimes-and-platforms)
    - [Data access, whitelists, configuration, and libraries](#data-access-whitelists-configuration-and-libraries)
    - [Promotion path](#promotion-path)
    - [Development & Approval](#development-approval)
    - [Performance expectations and guardrails](#performance-expectations-and-guardrails)
    - [Secrets and Configuration handling rules](#secrets-and-configuration-handling-rules)
    - [Support and ownership](#support-and-ownership)
    - [Splunkbase apps vs. internal apps vs. one-off scripts](#splunkbase-apps-vs-internal-apps-vs-one-off-scripts)
- [Operations, Monitoring & Maintenance (Platform Operations)](#operations-monitoring-maintenance-platform-operations)
  - [Operational responsibilities](#operational-responsibilities)
  - [Monitoring and alerting expectations](#monitoring-and-alerting-expectations)
  - [Maintenance and lifecycle management](#maintenance-and-lifecycle-management)
  - [Incident, problem, and recovery management](#incident-problem-and-recovery-management)
  - [Access, exceptions, and periodic review support](#access-exceptions-and-periodic-review-support)
  - [Operational documentation and runbooks](#operational-documentation-and-runbooks)
  - [Continuous improvement](#continuous-improvement)
- [Interfaces and Data Movements](#interfaces-and-data-movements)
  - [Core principles for interfaces and data movement](#core-principles-for-interfaces-and-data-movement)
  - [Inbound access approvals and periodic review](#inbound-access-approvals-and-periodic-review)
  - [Cross-zone pattern](#cross-zone-pattern)
    - [Recommended DMZ broker patterns](#recommended-dmz-broker-patterns)
  - [Outbound interfaces](#outbound-interfaces)
  - [Innovation-enabled interfaces](#innovation-enabled-interfaces)
- [AI Training and Inference](#ai-training-and-inference)
  - [Separation of planes](#separation-of-planes)
  - [Training rules](#training-rules)
  - [Inference rules](#inference-rules)
- [Change & Release Management](#change-release-management)
  - [Scope](#scope-1)
  - [Change classification](#change-classification)
  - [Environments and promotion path](#environments-and-promotion-path)
  - [Testing and validation requirements](#testing-and-validation-requirements)
  - [Release planning and scheduling](#release-planning-and-scheduling)
  - [Approvals and decision rights](#approvals-and-decision-rights)
  - [Rollback and recovery expectations](#rollback-and-recovery-expectations)
  - [Configuration management and traceability](#configuration-management-and-traceability)
  - [Third-party apps and custom development controls](#third-party-apps-and-custom-development-controls)
  - [AI-related change controls](#ai-related-change-controls)
  - [Post-release review and continuous improvement](#post-release-review-and-continuous-improvement)
- [Training, Enablement & Adoption](#training-enablement-adoption)
  - [Role-based training paths](#role-based-training-paths)
  - [Additional enablement considerations](#additional-enablement-considerations)
- [Roadmap & Phased Implementation Plan](#roadmap-phased-implementation-plan)
  - [Phase 0: Capability readiness and mobilization](#phase-0-capability-readiness-and-mobilization)
  - [Phase 1: Infrastructure and topology design](#phase-1-infrastructure-and-topology-design)
  - [Phase 2: Hardware procurement and environment strategy](#phase-2-hardware-procurement-and-environment-strategy)
  - [Phase 3: Test implementation build and validation](#phase-3-test-implementation-build-and-validation)
  - [Phase 4: Data architecture and onboarding framework](#phase-4-data-architecture-and-onboarding-framework)
  - [Phase 5: Core production build and hardening](#phase-5-core-production-build-and-hardening)
  - [Phase 6: Initial data onboarding and priority use cases](#phase-6-initial-data-onboarding-and-priority-use-cases)
  - [Phase 7: Production rollout and scaling](#phase-7-production-rollout-and-scaling)
  - [Phase 8: Optimization and continuous improvement](#phase-8-optimization-and-continuous-improvement)
  - [Phase 9: AI and machine learning enablement](#phase-9-ai-and-machine-learning-enablement)
  - [Strategic note on sequencing](#strategic-note-on-sequencing)
- [Risk Management & Assumptions](#risk-management-assumptions)
  - [Risks](#risks)
  - [Assumptions](#assumptions)
- [KPIs, Value Realization & FinOps Metrics](#kpis-value-realization-finops-metrics)
  - [Minimum KPI categories to define](#minimum-kpi-categories-to-define)
  - [Minimum Ops metrics to define](#minimum-ops-metrics-to-define)
  - [Strategic guidance](#strategic-guidance)

---

# Introduction

Tri-State Generation and Transmission Association is increasingly dependent on high-quality operational and security telemetry from both OT and IT environments to maintain system reliability, meet regulatory obligations, and support data-driven decision making. Splunk has been chosen as the strategic platform for collecting, normalizing, analyzing, and visualizing this telemetry across the enterprise.

This Splunk Strategy document defines how Tri-State will design, operate, and govern the Splunk platform so that it becomes a reliable, secure, and sustainable capability rather than just another tool. It establishes the guiding principles, architectural patterns, and governance mechanisms that will shape all future Splunk-related decisions, from infrastructure topology and role separation to data onboarding, index lifecycle, and Role Based Access Control (RBAC).

The document is intentionally prescriptive at the principle level, while leaving room for engineering teams to innovate within those boundaries.

This document does not include BES Cyber System Information and is intended for internal Tri-State use only.

# Executive Summary

Tri-State is adopting Splunk as a strategic platform for operational visibility and cybersecurity across both OT and IT environments. This document defines how Splunk will be designed, governed, and operated so it becomes a reliable, secure, and sustainable enterprise service rather than a one-off tool.

At a high level, the strategy establishes: a resilient, multi-site architecture, clear separation of duties across data, search, management, and ingestion layers, a governed data model and index naming standard that encode classification and retention, and a Role-Based Access Control (RBAC) model built directly on that structure. It also introduces a controlled sandbox approach so teams can innovate safely without bypassing governance.

Together, these elements ensure that Splunk supports Tri-State’s reliability, compliance, and security obligations while still providing enough flexibility for future use cases and growth.

# Purpose, Scope & Audience

## Purpose

The purpose of this document is to establish a clear, unified strategy for the design, deployment, and governance of the Splunk platform at Tri-State. It:

- Defines the architectural patterns and design choices that will guide Splunk implementations.

- Establishes data governance standards, including classification, index naming, and retention lifecycle.

- Describes the access control model and supporting RBAC structures that protect sensitive OT and security data.

- Provides a common reference for future standards, runbooks, and implementation projects.

This document is the strategic foundation for Splunk at Tri-State. It is not an implementation guide or configuration manual.

## Scope

This strategy applies to:

- All production Splunk environments operated by or on behalf of Tri-State.

- Both OT (e.g., SCADA, EMS, ICS, field telemetry) and IT (e.g., infrastructure, applications, identity, business systems) data sources onboarded into Splunk.

- All Splunk components participating in the production platform, including indexers, search heads, cluster managers, license managers, monitoring consoles, deployment servers, heavy/universal forwarders, and related integrations.

- Supporting governance mechanisms, such as data cataloging, index lifecycle management, RBAC, sandbox usage, and Zero Trust-aligned network zoning.

Out of scope for this document:

- Detailed server build procedures, OS hardening baselines, and patch management processes.

- Detailed Splunk configuration (e.g., specific props.conf/transforms.conf stanzas, search queries, dashboards).

- Non-production or lab environments beyond the high-level principles defined in the Sandbox Protocol and environment strategy.

## Audience

The primary audience for this document includes:

- **Senior leadership** responsible for reliability, cybersecurity, and regulatory compliance.

- **Platform owners and architects** responsible for Splunk infrastructure design and lifecycle.

- **OT and IT engineering teams** responsible for onboarding and maintaining data sources.

- **Security, compliance, and audit teams** relying on Splunk data and RBAC controls for monitoring and evidence.

- **Operations/NOC and SOC personnel** who use Splunk as a core tool for situational awareness and incident response.

Secondary audiences include project managers, application owners, and other stakeholders who need to understand how Splunk fits into Tri-State’s broader operational and compliance ecosystem

# Vision

Tri-State’s Splunk platform will operate as a reliable, secure, and sustainable enterprise service that turns OT and IT telemetry, logs and system events into trusted operational visibility and cybersecurity outcomes. The vision is a single, governed log capability that supports system reliability, regulatory obligations, and data-driven decision making, while still leaving room for teams to innovate safely within defined boundaries.

# Strategic Intent & Design Choices

## Objectives

- Establish Splunk as an enterprise capability with consistent design, operations, and governance that can scale across OT and IT.

- Meet reliability, security, and compliance needs by enforcing separation of duties, governed data onboarding, and audit-ready access control.

- Enable innovation without bypassing governance by providing a controlled sandbox approach and clear promotion paths from experimentation to production.

- Ensure cross-domain visibility while respecting sensitivity walls and regulated-data isolation using the data classification model, index naming, and RBAC.

## Key Strategic Design Choices

- Resilient, multi-site architecture using a stretched active–active multi-site cluster to meet high availability and disaster recovery needs.

- Clear separation of duties across data, search, management, and ingestion planes to avoid resource contention and simplify operations.

- Controlled ingestion boundary using the Ingestion Plane (Edge Server) as the termination point for raw feeds, with only forwarder traffic permitted directly to indexers.

- Zero Trust-aligned network zoning with deny-by-default traffic enforcement, governed port openings, controlled administrative access, and enforced security measures where supported.

- Governed data model and index naming that encodes classification and retention, enabling consistent enforcement of compliance and sensitivity boundaries.

- RBAC that is built directly on the governed data structure (classes, compliance drivers, domains) to ensure least-privilege access and auditability.

# Principles

- Reliability, resilience, and compliance are design requirements, not optional features.

- Design for operational simplicity, repeatability, and supportability.

- Apply Zero Trust by default and deny-by-default flows, explicit allowlists, and strong identity-based access.

- Use least privilege and separation of duties across platform planes and administrative functions.

- Governed onboarding is mandatory. Ownership, classification, metadata standards, and documented intent are required for production ingestion.

- Preserve evidence of integrity, raw events remain immutable, enrichment and derived outputs are additive.

- Enable safe innovation, experimentation is permitted, but time-bounded, auditable, and never a bypass around production controls.

- Standardize and automate wherever possible to reduce drift, improve consistency, and increase reliability.

- Practice financial responsibility by designing for cost transparency and predictability, using guardrails like tiering, quotas, and retention, and continuously optimizing spend without compromising reliability or security.

# Governance & Operating Model

## Governance

Governance ensures the Splunk platform remains secure, compliant, reliable, resilient, and operationally sustainable while enabling innovation through controlled patterns and documented exceptions.

## Governance structure and decision rights

**Platform Owner**

- Accountable for the Splunk service, strategic roadmap, service health, and alignment to enterprise architecture and security expectations.

**Splunk Platform Team**

- Owns architecture standards, baseline configurations, operational procedures, platform engineering, upgrades, and day-to-day reliability and performance.

**Splunk Data Governance and Data Stewards**

- Own data onboarding policy, classification mapping, metadata standards, and the approved registry of sources and sourcetypes.

- Approve field mapping and validation requirements prior to production onboarding.

**Security and Compliance**

- Approves zoning and network-flow exceptions, regulated-data handling requirements, RBAC design, and periodic access reviews.

- Ensures audit logging, evidence integrity, and regulatory obligations are met.

**Business/Data Owners**

- Accountable for data quality, continued business need, and approving new sources, use cases, and access requests.

## Governance controls

**Approval gates**

Production ingestion requires defined ownership, classification, sourcetype and source definitions, and approved onboarding documentation.

**Periodic review**

Inbound interfaces, cross-zone flows, and privileged access are reviewed on a scheduled cadence to validate business need and compliance.

**Exception management**

- Exceptions are allowed only when documented, risk-assessed, time-bounded, and approved.

- Exceptions must include a rollback plan and periodic re-approval.

**Audit and traceability**

Administrative actions and access to sensitive or regulated data are logged and retained according to retention standards.

## Operating Model

The operating model treats Splunk as an enterprise service with defined roles, standard workflows, and measurable operational outcomes.

## Core roles

**Platform Operations**

Runs the platform 24x7 or as required, manages availability and performance, operates upgrades, and executes incident/problem management.

**Platform Engineering**

Implements architecture patterns, automation, standard onboarding pipelines, and platform enhancements.

**Data Owners and Technical Owners**

Own the originating systems and are accountable for data correctness, change notifications, and coordinating onboarding and lifecycle changes.

**Data Stewards**

Validate metadata standards, classification, field mapping, and onboarding readiness; enforce governance rules.

**Security and Compliance**

Reviews and approves access, cross-zone flows, exceptions, and audit requirements; supports assessments and audits.

## Standard workflows

**Data onboarding (production)**

- Intake request, classification and ownership assignment, metadata definition (source, sourcetype, host strategy), field mapping, testing/validation, approval, production enablement, and post-onboarding review.

**Sandbox and innovation**

- Time-bounded onboarding allowed under strict rules (short retention, explicit expiration, controlled access, and prohibited regulated/highly sensitive data unless explicitly approved).

**Access management**

- RBAC requests tied to business roles, data classes, and domains; privileged access is time-bound where possible and reviewed periodically.

**Change management**

- Standard change control for platform upgrades, parsing changes, index strategy changes, and knowledge object changes; emergency change procedures defined for operational incidents.

**Incident and resilience operations**

- Defined on-call and escalation paths, runbooks, and recovery procedures; regular resilience testing and validation of monitoring/alerting.

**Service management**

- Define and track service KPIs and SLOs (availability, ingestion latency, search performance, onboarding lead time, incident MTTR), and conduct regular service reviews with stakeholders.

## Success measures

- Reduced time to onboard new data sources safely.

- Consistent RBAC and segregation of regulated data.

- Improved operational visibility and faster incident response outcomes.

- Predictable platform performance and reduced operational risk from drift and unmanaged integrations.

# High-Level Architecture Strategy

## Target Topology: Stretched Active–Active Multi-Site Cluster

To meet High Availability (HA) and Disaster Recovery (DR) requirements, Splunk will be deployed as a **stretched, active–active multi-site indexer cluster** spanning at least two data centers:

### Site Roles

**Site P (Primary – 5 nodes)**

- Hosts the **management plane**, **ingestion control**, and the **primary search UI endpoint**.

- Indexers in Site P are fully active participants in indexing and searching.

**Site B (Secondary – 3 nodes)**

- Hosts a **search UI endpoint** and indexers that fully participate in data replication **and** searching.

- Acts as the designated **secondary user access site** and becomes the primary user access site if Site P is unavailable.

- Provisions shall be defined for quick recovery of the management plane (servers 4 and 5) at the secondary site during an emergency

Key characteristics:

The **indexer and search fabric is active–active**:

- All indexers in both sites ingest and store data.

- All search heads can query all indexers across both sites.

- From a **user access and operations** perspective, Site P is treated as the **preferred entry point**, with Site B positioned as the secondary/DR user access site.

- As the platform scales, additional indexers and search heads are added to both sites while preserving this stretched, active–active topology.

## Component Role Strategy (Separation of Functions)

The architecture follows strict **separation of functions** to avoid resource contention and simplify operations. Each server group is dedicated to a specific plane:

| Server Group     | Role         | Site                            | Strategy & Purpose                                                                                                                                                                                                                                                                                                                                                                     |
|------------------|--------------|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Data Plane       | Indexers     | P & B (2 in P, 2 in B baseline) | Pure data storage and retrieval. No search head, management, or ingestion roles are allowed on indexers. All indexers are active participants in the stretched cluster.                                                                                                                                                                                                                |
| Search Plane     | Search Heads | P & B (1 in P, 1 in B baseline) | Provide user interface and search execution. All search heads can query all indexers. Site P is the preferred UI endpoint; Site B is available for regional/DR access. Target state is a Search Head Cluster spanning both sites as demand grows.                                                                                                                                      |
| Management Plane | Utility      | P only                          | Hosts Indexer Cluster Master, License Master Monitoring Console and Search Head Cluster Deployer. Serves as the “brain” of the cluster. Warm-standby capacity exists in Site B (templates/backups and a documented failover runbook). The Deployment Server role is explicitly excluded from this host.                                                                                |
| Ingestion Plane  | Edge Server  | P only                          | Hosts Deployment Server and Heavy Forwarder / ingestion gateway functions. Acts as the controlled termination point for raw Syslog, NetFlow, API/HTTP feeds and similar protocols before data is forwarded on to the indexer cluster. Only Splunk Forwarder traffic is permitted to reach indexers directly. The Edge Server must not host Cluster Master or Monitoring Console roles. |

All future scaling (capacity, volume, or new use cases) should follow these planes, rather than mixing roles on existing nodes.

## Server Role Isolation Rules (Role Mixing Restrictions)

To maintain performance, reliability, and security, certain Splunk roles **must not be mixed** on the same server in production. The following rules apply.

### Indexers

Indexers are **data-only** nodes.

Indexers must not host:

- Search Head roles (no UI, no user-facing searches), including Search Head Cluster Deployer

- Cluster Master, License Master, or Monitoring Console.

- Deployment Server.

- Heavy Forwarder or other ingestion gateway functions.

- Non-Splunk application workloads (databases, application servers, web servers, etc.).

Intent: keep indexers dedicated to indexing and search servicing, ensuring predictable performance and limiting operational blast radius.

### Search Heads

Search Heads are **search and UX-only** nodes.

Search Heads must not:

- Act as indexers or participate in the indexer cluster.

- Host Cluster Master, License Master, Monitoring Console, or Deployment Server roles nor Search Head Cluster Deployer

- Perform high-volume Heavy Forwarder duties (protocol gateways, parsing for large feeds).

- Share resources with non-Splunk workloads that compete heavily for CPU, memory, or disk.

Limited exceptions for small, non-production environments do not change this **production standard**.

### Management Plane (Utility Server)

The Utility server is the **control-plane** node.

The Management Plane may host:

- Cluster Master

- License Master

- Monitoring Console

- Search Head Cluster Deployer

The Management Plane must **NOT**:

- Run indexer roles or store production indexes.

- Act as a general user-facing Search Head (beyond the Monitoring Console UI).

- Host Heavy Forwarder roles for production ingestion volume.

- Combine Cluster Master and Deployment Server roles on the same server.

- Combine Monitoring Console and Deployment Server roles on the same server.

Intent: ensure that cluster control (both Indexer and Search Head), licensing, and monitoring remain responsive and isolated from data and search workloads, and that management functions are separated from large-scale configuration distribution.

### Ingestion Plane

The Edge server is the **ingestion and configuration gateway**.

It is dedicated to:

- Deployment Server responsibilities (forwarder and app configuration).

- Heavy Forwarder / protocol gateway functions (for example, Syslog aggregation, NetFlow, API/HTTP event collection, DB inputs).

#### Ingestion Plane restrictions:

**The Ingestion Plane must NOT:**

- Host indexer roles or be part of the indexer cluster.

- Serve as a general user Search Head for interactive searches.

- Host Cluster Master, License Master, or Monitoring Console roles nor Search Head Cluster Deployer

**Deployment Server must remain on this dedicated Ingestion Plane server and must not be combined on the same host with Cluster Master or Monitoring Console.**

#### Traffic rules:

**Allowed direct-to-indexer traffic:**

- Only **Splunk Forwarder traffic** (Universal Forwarders or intermediate Heavy Forwarders) may send data directly to the indexer tier (typically via a load balancer).

**Disallowed direct-to-indexer traffic:**

- **Raw Syslog**, **NetFlow**, **SNMP traps**, **API/HTTP event feeds**, database inputs, and other non-forwarder integrations must **not** be pointed directly at indexers.

- These integrations must terminate on the **Ingestion Plane (Edge Server)**, which then forwards processed data on to the indexers.

This design provides:

- A controlled **ingestion DMZ** and security boundary.

- **Rate limiting, filtering, and normalization** of high-volume or noisy sources.

- A single place to manage complex **parsing, sourcetyping, and routing** before data enters the indexer cluster.

- Cribl or other type of ingestion control?

### Tenant / Dedicated Search Heads

- Where dedicated/tenant Search Heads are deployed for specific business units or tenants, they must not Host indexer roles or Cluster Master functions.

- Act as Deployment Servers or Heavy Forwarders for the broader platform.

- Bypass central RBAC or platform configuration standards.

They remain **under the control of the central Splunk Platform team**, even when tenant admins have delegated permissions within their own apps and data scope.

## Network Zoning & Zero Trust Architecture

Splunk infrastructure adheres to a **Zero Trust** network model:

**Isolation Mandate**

All Splunk components reside in dedicated **management subnets/VLANs** that are separate from user endpoints and general server networks.

**Access Control**

Traffic is enforced at Layer 3 (firewalls/ACLs). The default posture is **deny by default**, with only specific, documented ports and flows permitted (for example, HTTPS for UI, management API, and forwarder ingestion).

**Port Governance**

Opening new ports or flows is allowed only after formal review and approval by Security and the Splunk Platform team.

**Administrative Access**

Direct SSH/RDP from user subnets to Splunk infrastructure is prohibited. All administrative access must traverse a **Jump Host or Privileged Access Management (PAM)** solution.

**Encryption**

All user access and inter-Splunk communication use **TLS-secured endpoints** where supported (UI, management interfaces, and forwarder traffic where feasible).

## Scalability & Multi-Tenancy Strategy

**Approved Multi-Tenancy Pattern: Dedicated Tenant Search Heads**

Where justified (for example, HR, Finance, highly regulated business units), the platform may host **additional dedicated Search Head instances or Search Head Clusters** for specific tenants.

**Shared Data Plane**

All tenant search heads use the **shared indexer cluster**, maintaining a unified data lake while preventing data silos and unnecessary infrastructure duplication.

**Isolation & Control**

- Tenants are isolated primarily via **Role-Based Access Control (RBAC)** and dedicated index naming (for example, `finance_*`, `hr_*`).

- Default tenant roles are locked to their approved index sets and capabilities.

- Platform administration for all search heads and indexers remains with the **central Splunk Platform team**.

- Dedicated tenant support/admin teams are permitted, but their elevated access is explicitly approved, time-bounded where appropriate, and governed under the central RBAC model.

**Exception-Based Use**

Dedicated tenant search heads are treated as an **exception pattern** for well-justified business or regulatory needs, not as the default approach for every team.

# Availability, Resiliency & DR Strategy

## Clustering & Replication Logic (N–1 Baseline)

To ensure data durability and search resiliency, the platform uses a **stretched, active–active multi-site indexer cluster** with a defined baseline configuration:

- **Total Indexers (N):** 4 in the initial design (2 per site).

- **Replication Factor (RF):** 3.

- **Search Factor (SF):** 3.

Strategic intent:

- Each event is stored on **three separate indexers** distributed across the sites.

- All search heads have visibility into all indexers and participate in searching across the full data set.

- The environment can tolerate the loss of an indexer and remain search-capable without data loss; in the event of a full site outage, data remains recoverable with a temporary reduction in redundancy until capacity is restored.

- As the platform grows, the total indexer count and RF/SF settings are periodically reviewed and adjusted to maintain an **N–1 or better** resiliency posture.

Where appropriate, **site-aware replication** (site replication factor and site search factor) is configured to ensure that copies of critical data exist in both sites.

## Failure and Partition Scenarios

**Failure of Site P (preferred user access site)**

- The cluster continues to function using Site B indexers and search head.

- Users are redirected to the Site B UI by DNS, load balancer, or documented endpoint changes.

- Once Site P is restored, the cluster is rebalanced and failback is performed according to an approved runbook.

**Failure of Site B**

- Primary operations remain at Site P with no user-facing disruption.

- Replication factor may be temporarily reduced while Site B is rebuilt or brought back online.

- No data loss is expected; redundancy is reduced until restoration.

**Network Partition / Split-Brain Risk**

- The **Cluster Manager in Site P** is the system of record for the cluster.

- Network and routing design, combined with documented operational procedures, defines which site remains authoritative in the event of a partition.

- Only the designated authoritative side continues to accept writes during a partition, preventing split-brain behavior and ensuring data consistency.

# Data Strategy & Onboarding

## Data Classification & Governance

To ensure security, compliance, and alignment with organizational standards, all data ingested into Splunk must be mapped to the Enterprise Data Governance Council’s Data Sensitivity Classes and tagged with relevant Compliance Drivers.

## Data Classes (Sensitivity)

**Class 1 – Public**

External or open data (for example, weather, markets). Low sensitivity.

**Class 2 – Enterprise**

Internal business data (for example, ERP, project planning). Standard confidentiality.

**Class 3 – Operational**

Operational business data (for example, outage tickets, work orders, IT events). Restricted to operations/NOC and related functions.

**Class 4 – Control**

OT/ICS control and telemetry (for example, SCADA, setpoints). High sensitivity. Restricted to OT/engineering and designated stakeholders.

**Class 5 – Restricted**

Critical security, legal, and highly sensitive design/topology data. Maximum security. Access is on a strict “need to know” basis.

Each onboarded data source must have:

- A **Data Class** (1–5)

- One or more **Compliance Drivers** (for example, PCI, NERC CIP, HIPAA, GDPR, or “non” for non-regulated)

# Indexing, Retention & Lifecycle Management

Indexes use a strict multi-segment naming scheme. The name is divided into a governance-oriented **prefix**, an optional detail segment, and a retention-oriented **suffix**.

## Schema

`[class]_[compliance]_[domain]_[content]_[optional_detail]_[retention]`

## Governance Prefix (Mandatory, 3-letter codes)

Each field in the prefix is a three-letter, lowercase abbreviation.

### Data Class (class) – STRICTLY DEFINED

These map directly to the Data Classification Framework:

- pub – Class 1 (Public)

- ent – Class 2 (Enterprise)

- ops – Class 3 (Operational)

- ctl – Class 4 (Control / OT)

- res – Class 5 (Restricted / Security)

### Compliance (compliance) – DEFINABLE by Data Governance Council

Compliance drivers, defined in the Data Catalog before ingestion. Examples:

- pci – Payment Card Industry

- cip – NERC CIP

- hpa – HIPAA

- gdr – GDPR

- non – Non-regulated / general

### Domain (domain) – DEFINABLE by Data Governance Council

High-level functional area, defined in the Data Catalog. Examples:

- sec – Security

- ics – Industrial Control Systems (OT)

- inf – Infrastructure (IT)

- app – Application / business logic

### Content (content) – DEFINABLE by Data Governance Council

Descriptive name of the data source type. Examples:

- win – Windows event logs

- fwl – Firewall traffic

- scd – SCADA telemetry

- dns – DNS queries

- web – Web access logs

- lin – Linux Logs

- ndl – network device logs (sw, rtr)

- wfl – windows firewall logs

- lfl – linux firewall logs

### Optional Detail (Flexible)

- Used when multiple indexes exist for the same governance category (for example, separating by region, environment, or app name).

- Uses lower_snake_case alphanumeric (for example, na, billing_app, east_plant).

### Retention Suffix (Mandatory)

Retention categories are encoded in the suffix:

- `_s` – Short term

- `_m` – Medium term

- `_l` – Long term

Proposed defaults:

- `_s` – Short Term: 30 days total (7 days hot / 23 days cold). Used for troubleshooting, verbose debug logs, and high-volume metrics.

- `_m` – Medium Term: 1 year total (30 days hot / 335 days cold). Used for operational lookback, general IT logs, and non-regulated business data.

- `_l` – Long Term: 3 years total (90 days hot / 3 years cold . Used for regulated data (PCI/NERC), security audit trails, and long-hold requirements.

### Real-world naming examples

- ctl_cip_ics_scd_s  
  Control-class, NERC-CIP, ICS, SCADA telemetry, short-term retention.

- res_pci_sec_aud_l  
  Restricted-class, PCI, security, audit-related data, long-term retention.

- ent_non_app_web_billing_app_m  
  Enterprise-class, non-regulated, application/web logs for the “billing_app” service, medium-term retention.

## Segregation Rules

**Sensitivity walls**

Data of fundamentally different Classes (for example, ent vs res) must never be mixed in the same index.

**Compliance isolation**

Regulated data (for example, pci, cip) must live in dedicated indexes to support specific retention, audit, and purge requirements.

**Logical domain boundaries**

Create one index per logical data domain where distinct access controls or retention policies are required.

## Retention & Lifecycle Strategy

Retention policies are standardized into three categories. Every index must be assigned one of these via its name suffix.

| Category    | Suffix | Use Case                                               | Suggested Hot/Warm (Fast) | Suggested Cold (Capacity) | Suggested Frozen (Archive) | Suggested Total Retention |
|-------------|--------|--------------------------------------------------------|---------------------------|---------------------------|----------------------------|---------------------------|
| Short Term  | `_s`    | Troubleshooting, verbose debug, high-volume metrics    | 7 days                    | 23 days                   | Delete                     | 30 days                   |
| Medium Term | `_m`    | Operational lookback, general IT/non-reg business data | 30 days                   | 335 days                  | Delete                     | 1 year                    |
| Long Term   | `_l`    | Regulated data, audit trails, legal hold requirements  | 90 days                   | 3 years                   | 3 years (archive)          | 7 years                   |

## Lifecycle definitions:

**Hot/Warm**

High-performance NVMe/SSD. Immediate search results and frequent analyst use.

**Cold**

High-capacity HDD, SAN, or object storage (for example, SmartStore). Slower search performance but still online.

**Frozen**

Archived to offline or colder storage (for example, object archive, tape) or deleted. Not searchable without restoration.

## Data Catalog

A central **Data Catalog** must be maintained defining, for every onboarded input:

- Source system & IP / hostname

- Sourcetype

- Target index name (must follow the naming schema)

- Data Class & Compliance driver(s)

- Business owner and technical owner

No data is onboarded into production Splunk environments without an explicit entry in this catalog.

## Metadata Standards (source, sourcetype, host)

This section defines required metadata standards to ensure consistent onboarding, reliable correlation, efficient search, and audit-ready traceability across I&T environments. These standards apply to all production ingestion and must be defined, reviewed, and maintained as part of the data onboarding lifecycle.

### sourcetype standard

Sourcetype is the primary indicator of what the event represents and how it should be parsed. All sourcetypes must follow the **tag:tag:tag** format with the following requirements:

- **Format:** tag:tag:tag...

- **Maximum tags:** 5

- **Tag order:** left-to-right from **most abstract** to **most specific**

- **Case:** all **lower case**

- **Stability:** must be stable over time and meaningful

- **No ephemeral values:** do not include values that change frequently or are unique per instance (for example, transaction IDs, session IDs, GUIDs, timestamps, random strings, dynamically assigned port numbers)

- **Governance:** sourcetypes must be **defined and maintained** in the organization’s approved catalog/registry; new sourcetypes or changes to existing sourcetypes require governance review as part of onboarding

**Recommended approved patterns and examples**

**Vendor product logs: vendor:product:logtype**

- Examples: paloalto:pan:traffic, paloalto:pan:threat

**Operating system logs: os:logtype:logname**

- Examples: linux:system:audit, windows:security:eventlog

**Custom applications (if used): org:appname:logtype**

- Example: acme:billing:trans

### source standard

Source identifies the logical origin of the data feed and should help operators understand where the data came from without being tied to transient details. All sources must also follow the **tag:tag:tag** format and align to the same conventions:

- **Format:** tag:tag:tag...

- **Maximum tags:** 5

- **Tag order:** left-to-right from **most abstract** to **most specific**

- **Case:** all **lower case**

- **Stability:** must be stable, meaningful, and consistent across time

- **Avoid ephemeral values:** do not include unique filenames that rotate with timestamps, unique IDs, per-run GUIDs, or per-connection attributes

- **Preferred source identifiers:** logical feed names, connector IDs, integration names, stable file paths, or stable pipeline identifiers

- **Governance:** sources must be defined and maintained in the catalog/registry; production sources must have an owner and be subject to periodic review

**Examples**

- Logical feed naming: ot:substation:syslog, it:datacenter:network:syslog

- Connector identifier pattern: api:servicenow:incident, api:azuread:signin

- Stable file path style (abstracted): file:linux:auth, file:windows:log

### host standard

Host identifies the originating asset and is critical for correlation, incident response, and compliance evidence.

- **Accepted format:** host should match the **FQDN** or **CMDB asset name** where FQDN is not available (for example, srv-01.domain.local) rather than raw IP addresses.

- **OT alignment:** for OT, host naming must be agreed with OT stakeholders and mapped to a stable OT asset identifier that ties back to the OT CMDB (for example, ot-asset-12345), with supporting fields maintained as needed for readability (such as asset_name, asset function types, site, or zone).

- **Stability:** host values must remain stable and must not be overloaded with transient context (for example, do not embed session IDs or collector-specific details).

### Standard ownership and maintenance

- Designated custodians are responsible for maintaining an approved registry of source and sourcetype definitions, including the standard naming, description, owner, data class, and intended use.

- Any change to a production source or sourcetype must be treated as a controlled change because it can impact parsing, knowledge objects, detections, dashboards, and downstream analytics.

## Data Quality & Timestamping

**Timezone Strategy**

- Events are assumed to be in **UTC**, unless the data source explicitly includes a timezone offset in the event text.

- Where sources log in local time (often OT/ICS), ingestion configurations must normalize timestamps to UTC to support cross-domain correlation.

**The Quarantine Protocol**

Data that fails onboarding standards must **not** be indexed into production indexes.

- Such data is routed to a dedicated **quarantine index**, for example:  
  ops_non_inf_bad_s (Operational, non-regulated, infrastructure, “bad” data, short-term retention).

**The technical owner is responsible for:**

- Correcting the configuration.

- Ensuring that once fixed, data is routed to the correct production index and removed from quarantine.

## Field Naming & CIM Alignment

### Data Dictionary Mandate

Before a data source is approved for **production ingestion**, a **Field Mapping Document** must be created, listing:

- All extracted fields and their meaning

- Data types

- CIM mappings (where applicable)

- Any field aliases

### Governance & Approval

- Designated **Data Stewards / Architects** are responsible for reviewing and approving the Field Mapping Document.

- Gatekeeper rule: **No data source is configured in production** until a Steward has approved the mapping.

### Naming Standards

- **Custom fields** use lower_snake_case (lowercase with underscores).

- Avoid ambiguous names (for example, value, type, id) unless they are clearly aliased to meaningful names.

## The Sandbox Protocol (Temporary Innovation)

To foster innovation and rapid prototyping without compromising production stability, a **Temporary Onboarding (“sandbox”) process** is permitted under strict conditions.

### Scope & Purpose

- Intended for **proof-of-concept (PoC)**, development, or ad-hoc troubleshooting.

- Data ingested under this protocol is **best-effort** and has **no SLA**.

### Relaxed Standards

- Metadata: Custom or experimental sourcetype and source values are permitted without prior registration in the Data Catalog.

- Governance: The Field Mapping and CIM approval processes are **waived** for the duration of the temporary use.

### Restrictions

**Index naming**

Must use the reserved prefix `tmp_` followed by a project name and a short-term suffix, for example: tmp_project_alpha_s

**Retention**

- Sandbox indexes must always use the **Short Term (`_s`)** suffix.

- Data is automatically purged after 30 days or less.

**Expiration**

- All sandbox configurations (inputs, props, transforms) must have an explicit **Expiration Date**.

- If the use case is not transitioned to production (with full catalog, classification, and field mapping) by that date, the sandbox configuration is removed.

**Data sensitivity**

Regulated or highly sensitive production data must not be ingested into `tmp_` indexes. Sandbox is for **non-production or low-risk** data only.

# Role Based Access Control (RBAC)

## Conceptual Model

RBAC in Splunk is tightly aligned with Tri-State’s **Data Classification Model** and **index naming standard**. Access is granted based on what a user does (Business Role) and which data classes and domains they are permitted to see (Privilege Bundles), not on individual, ad hoc permissions.

Relationships are defined as:

- Each user has a 1:1 relationship with a Business Role.

- Each Business Role has a 1:N relationship with Privilege Bundles.

- Each Privilege Bundle has a 1:N relationship with indexes, capabilities, and workspaces.

This model ensures that all access decisions stay consistent with:

- The **data classification model** (Classes 1–5).

- The **index naming standard**

RBAC is therefore the enforcement layer that connects identity, business function, and governed data.

## Role Types and Naming Convention

All roles and privilege bundles must be defined and managed centrally by the Splunk Platform team in collaboration with Security and Identity Management.

### Conventions

- Use lower_snake_case for all role names.

- Use fixed, documented naming patterns for consistency and automation.

- All user-facing access is controlled through Business Roles (`rl_*`) and Privilege Bundles (`pr_*`).

### Business Roles (rl_*)

Business Roles represent job functions such as SOC Tier 1, PCI Auditor, OT Engineer, IT Engineer, Platform Admin, and similar:

- Business Roles are the **only roles assigned directly to users** under normal circumstances.

- Recommended prefix: `rl_` (for example, rl_it_usr, rl_it_adm, rl_ot_eng, rl_soc_t1).

- Every user has a 1:1 relationship with a single Business Role.

### Privilege Bundles (pr_*)

Privilege Bundles are reusable building blocks that group related permissions and are attached to Business Roles, not directly to users. All privilege bundles must:

- Use the prefix `pr_*`.

- Be documented, approved, and tracked for changes.

- Be defined at a level that can be reused across multiple Business Roles.

A single Business Role can have a 1:N relationship with Privilege Bundles. At minimum, the following categories are defined:

**Data bundles (`pr_data_*`)**

Define which indexes can be searched based on the index naming schema and data classification.

Examples (conceptual):

- pr_data_res_sec for Restricted security indexes that begin with `res_*_sec_*_*`.

- pr_data_res_pci for Restricted PCI security indexes that begin with `res_pci_sec_*_*`.

- pr_data_ctl_ics for Control/OT ICS telemetry indexes that begin with `ctl_*_ics_*_*`.

**Search bundles (`pr_search_*`)**

Define which search commands, time ranges, and resource limits (for example, concurrency, real-time search) are allowed.

Examples:

pr_search_basic, pr_search_advanced, pr_search_realtime.

**Feature bundles (`pr_feat_*`)**

Define what users can do beyond running searches, such as:

- Creating alerts.

- Building dashboards.

- Managing knowledge objects.

- Administering the platform.

Examples:

pr_feat_alert_viewer, pr_feat_alert_creator, pr_feat_dashboard_creator, pr_feat_ko_manager, pr_feat_admin_platform.

**Workspace bundles (`pr_workspace_*`)**

Define default apps, dashboards, and user experience for a role (for example, SOC, OT, PCI).

Examples: pr_workspace_soc, pr_workspace_ot, pr_workspace_pci.

Each Privilege Bundle has a 1:N relationship with the concrete permissions it represents (indexes, search capabilities, features, apps, or workspaces). Role-to-bundle mappings are defined once and governed centrally.

## Integration with Data Classification and Index Naming

RBAC must consistently enforce the **index naming** and **classification** standards:

- Index names follow: `[class]_[compliance]_[domain]_[content]_[optional_detail]_[retention]`

- Privilege bundles are defined in terms of the class, compliance, and domain segments to ensure that access aligns with sensitivity and regulatory boundaries.

Examples:

- Restricted security data (`res_*_sec_*_*`) is exposed only through data bundles designed for Restricted security use cases (for example, pr_data_res_sec).

- Control/OT data (`ctl_*_ics_*_*`) is exposed only to OT-focused roles through pr_data_ctl_ics or similar bundles.

- PCI or other regulated data (`*_pci_*`) is isolated in dedicated bundles and assigned only to appropriate audit or compliance roles.

This scheme ensures that sensitivity walls and compliance isolation defined in the data onboarding and index lifecycle policies are consistently enforced at the access-control layer.

## Multi-Tenancy and Tenant Search Heads

When tenant-specific or dedicated Search Heads are deployed (for example, for a particular business unit or regulatory domain):

- Tenant Search Heads do not bypass central RBAC or platform configuration standards.

- Business Roles (`rl_*`) and Privilege Bundles (`pr_*`) remain defined centrally and are applied consistently to shared and tenant Search Heads.

- Data access is still governed by index-based data bundles, even if the user interface is tenant-specific.

This maintains a single, coherent RBAC model across the entire Splunk estate.

## Sandbox and Temporary Access

Sandbox indexes (`tmp_*`) and temporary onboarding are used for innovation and early-stage testing, but are still controlled by RBAC:

- Standard Business Roles may include limited data bundles for `tmp_*` indexes where appropriate.

- Regulated or highly sensitive production data must not be ingested into `tmp_*` indexes; bundles must not grant broad sandbox access that would violate this principle.

- Any temporary access exceptions (for example, short-term investigative access) must be explicitly **documented**, **approved**, and **time**-bound.

This ensures sandbox experimentation does not weaken production access controls.

## Enforcement of the 1:1 User–Role Relationship

The 1:1 relationship between users and Business Roles is enforced through the Identity Provider (IdP) and verified in Splunk.

### Enforcement In the IdP (AD/LDAP/SAML)

- One group exists per Business Role.

- Each group has a 1:N relationship with the users that need that role.

- Examples: GRP_splunk_rl_soc_tier1, GRP_splunk_rl_pci_auditor.

- Policy: a given user must be a member of at most one Splunk Business Role group at any time, maintaining a 1:1 relationship between user and Business Role.

### Enforcement In Splunk

- Each IdP group is mapped to a single `rl_*` Business Role (1:1 relationship between IdP group and Business Role).

- Users inherit Privilege Bundles only through their assigned Business Role.

- `pr_data_*`, `pr_search_*`, `pr_feat_*`, and `pr_workspace_*` roles are not assigned directly to users under normal conditions.

### Monitoring and Reporting

Regular reviews identify:

- Any user with more than one `rl_*` role (violates the 1:1 design).

- Any user with `pr_data_*`, `pr_search_*`, `pr_feat_*`, or `pr_workspace_*` assigned directly (policy violation).

Detected exceptions are treated as temporary, must be documented and approved, and must include a clear expiration.

This RBAC strategy creates a clear, auditable chain of relationships from user identity, through Business Roles and Privilege Bundles, to specific, governed indexes and capabilities defined in the data onboarding and architecture standards.

# Security, Privacy & Compliance

The Splunk platform must support Tri-State’s security and compliance obligations while protecting sensitive OT and IT data from unauthorized access, misuse, or leakage. Security and privacy are treated as **design constraints**, not features to be added later. This section defines how Splunk will:

- Enforce data segregation and least-privilege access.

- Align with applicable regulatory and internal policy requirements (for example, NERC CIP, corporate security standards).

- Provide auditable evidence of control operation for internal and external assessments.

Splunk is both a **consumer** of security controls (hardened infrastructure, Zero Trust network posture, RBAC) and a **provider** of security capabilities (monitoring, alerting, and forensic data).

## Data Protection & Segregation

Data protection within Splunk is grounded in:

- The **5-Class Data Model** (Public, Enterprise, Operations, Control, Restricted) and associated Compliance Drivers.

- The **index naming schema** (`[class_compliance_domain_content_detail_retention]`) and retention tiers (`_s`, `_m`, `_l`) that encode sensitivity, compliance drivers, and lifecycle into every index.

- Mandatory **segregation rules** that prevent mixing data of different sensitivity or compliance regimes in the same index.

Security and compliance expectations:

**Class-based separation:**

- Data of different sensitivity classes (for example, ent vs res) must not share an index.

- Control/OT data (for example, `ctl_cip_ics_*_*`) is kept separate from general IT/business data.

**Compliance isolation:**

- Regulated data lives in dedicated indexes, enabling specific retention, purge, and audit controls.

**Data catalog & ownership:**

- Every data source onboarded into production must be defined in the Data Catalog with class, compliance drivers, and business/technical owners before ingestion is enabled.

**Edge filtering and minimization:**

- Non-actionable noise (debug logs, low-value verbose fields) that is not dictated by compliance should be removed at the ingestion layer where feasible, reducing risk exposure and license cost while preserving necessary forensic value. The ingested data must be reviewed periodically for such decisions.

These policies ensure that security and compliance posture are baked into how data is onboarded, named, and retained.

## Access Control & Identity

Access to data and administrative capabilities in Splunk is governed by the **Role-Based Access Control (RBAC)** model defined in the RBAC section:

- Each user has a 1:1 relationship with a Business Role, and each Business Role has a 1:N relationship with Privilege Bundles that define data, search, feature, and workspace permissions.

- Privilege Bundles are aligned to index patterns (class, compliance, domain) so that users see only the data their function requires.

- Administrative privileges (platform admin, app admin, knowledge-object admin) are separated from standard user roles to enforce separation of duties.

Security requirements for identity and access:

- **Centralized identity:** All user authentication integrates with the enterprise Identity Provider (IdP) and follows corporate standards for MFA and password policies.

- **Least privilege:** Default roles grant minimal search and feature permissions; additional Privilege Bundles are added only when justified and approved.

- **Periodic reviews:** Access rights (Business Roles, Privilege Bundles, and IdP group membership) are reviewed on a regular, defined cadence to detect and remediate excess access or violations of the 1:1 user–role relationship.

## Network Security & Encryption

Splunk infrastructure participates in Tri-State’s **Zero Trust network model**, as defined in the Network Zoning & Zero Trust Architecture section:

- **Isolation:** All Splunk components reside in dedicated management subnets/VLANs, separate from user endpoints and general server networks.

- **Access control:** Traffic is denied by default and allowed only for documented ports and flows (for example, HTTPS for UI, management API, and forwarder ingestion) approved by Security and the Splunk Platform team.

- **Privileged access:** Administrative access (SSH/RDP) is permitted only via approved jump hosts or Privileged Access Management solutions; direct access from user subnets is prohibited.

Encryption controls:

- **In transit:** All user access and inter-Splunk communication (UI, management, forwarder traffic where supported) use TLS-secured endpoints.

- **At rest:** Storage for Splunk components (indexes, configuration, and metadata) must follow Tri-State standards for disk and database encryption, particularly for data classified as Control or Restricted.

- **Certificate management:** TLS certificates for Splunk endpoints are issued, renewed, and revoked in line with corporate PKI policies and monitored for expiry.

## Regulatory Compliance & Auditability

Splunk must support and not hinder compliance with applicable regulatory frameworks and internal policies (for example, NERC CIP for OT/EMS, PCI DSS for payment data, and internal security standards). At a strategy level, this means:

**Audit-ready logging:**

- Administrative actions within Splunk (role changes, index changes, configuration changes) must be logged and retained in dedicated audit indexes following long-term retention policies.

- Access to sensitive or regulated data is traceable back to users and Business Roles through Splunk and IdP logs.

**Retention alignment:**

- Retention policies encoded via suffixes (`_s`, `_m`, `_l`) must be chosen to satisfy or exceed regulatory minimums for relevant data classes and compliance drivers.

**Change control:**

- Security-relevant configuration changes in Splunk (for example, indexes.conf, authentication.conf, authorize.conf) are managed via Configuration-as-Code, documented, and subject to formal change control and review.

**Evidence generation:**

- The platform provides defined reports, dashboards, and search patterns that can be used by Compliance and Audit teams to demonstrate control operation (for example, access reviews, log coverage, retention enforcement).

## Privacy & Data Minimization

Even when data is primarily operational or security-related, logs and telemetry can contain personal or otherwise sensitive information. Splunk must therefore adhere to privacy-by-design principles:

- **Data minimization:** Only data necessary for security, reliability, and operational use cases is ingested; high-risk personal data (for example, free-form text fields, full payloads) is avoided or stripped where feasible.

- **Masking and pseudonymization:** Where business requirements demand storing identifiers or user-related fields, masking or pseudonymization patterns are applied at the ingestion or parsing layer in line with corporate privacy standards.

- **Use-case justification:** New data sources that include potential PII or other sensitive attributes require an explicit risk assessment and approval by Security/Privacy before onboarding into production.

- **Access controls on sensitive fields:** Where PII or similar data is present, RBAC and search controls must restrict access to only those roles that need it, with additional monitoring for misuse.

Together, these policies ensure that Splunk operates as a **secure, privacy-aware, and compliant platform**, where protection of sensitive OT and IT data is enforced through classification, architecture, RBAC, network controls, and auditable processes.

# Performance, Capacity, Sizing & Cost Awareness

This section establishes how Splunk performance and capacity will be managed to maintain reliability and resilience, while ensuring the platform remains financially sustainable. The intent is to treat Splunk as an enterprise service with predictable performance, disciplined growth, and cost-aware onboarding.

**Performance objectives**

- Maintain stable ingestion, indexing, and search performance under normal and peak conditions.

- Protect critical operational and security use cases from resource contention.

- Ensure that platform changes (data onboarding, parsing, apps, dashboards, alerts, integrations) do not degrade service health.

**Capacity and sizing approach**

- Use a standardized sizing model that considers ingestion rate, retention tiers, search concurrency, indexing complexity, and growth projections.

- Validate sizing assumptions during the test implementation environment before scaling production.

- Reassess sizing and capacity regularly as new data sources and use cases are onboarded.

**Capacity management practices**

- Establish platform baselines for ingestion throughput, indexing latency, search performance, storage growth, and system utilization.

- Implement proactive monitoring for leading indicators such as queue growth, indexing delay, replication/search health, disk IOPS pressure, and search head saturation.

- Use thresholds and operational runbooks to manage peaks, prioritize workloads, and protect platform stability.

**Cost awareness and sustainable growth**

- Treat data onboarding as a cost decision as well as a technical decision.

- Prioritize high-value telemetry and apply data minimization at ingestion to reduce unnecessary volume.

- Align retention to data class, compliance need, and operational value, using retention tiers rather than “one size fits all.”

- Periodically review existing sources and content to identify low-value data, redundant feeds, and overly verbose events that can be filtered or retired.

**Search and content performance discipline**

- Require performance-aware design for scheduled searches, dashboards, and correlation content.

- Encourage reuse of shared data models, standard macros, and curated datasets rather than duplicating expensive search patterns.

- Validate search performance and resource impact in the test environment before promoting high-impact content to production.

**Governance linkage**

- Performance and cost impacts should be assessed during onboarding approvals and change reviews.

- Managers should periodically review platform utilization and cost drivers and adjust onboarding priorities, retention tiers, and optimization initiatives accordingly.

# App, Content & Use Case Development

This section defines how use cases are proposed, designed, implemented, and maintained on the Splunk platform. It covers searches, alerts, dashboards, knowledge objects, and applications (including custom commands and code). The goal is to ensure that all content is **governed, consistent, performant, and supportable**, while still allowing teams to innovate.

## Objectives

- Provide a **consistent framework** for developing Splunk content that aligns with data classification, index naming, and RBAC standards.

- Ensure that new use cases go through a **structured intake, design, and approval process**.

- Promote **reuse and standardization** of searches, dashboards, and apps across OT and IT teams.

- Manage the **risk and cost** of content (search load, license consumption, maintenance overhead).

## Use Case Intake & Prioritization

All new Splunk use cases (for example, dashboards, alerts, reports, analytics apps) should follow a common intake process:

**Use Case Definition**

- Problem statement and objective.

- Target users (NOC, SOC, OT engineers, business owners).

- Data sources required (mapped to Data Catalog entries).

**Classification & Governance Alignment**

- Confirm that needed data is already in the **Data Catalog** with defined class, compliance drivers, and target indexes.

- If new data is required, follow the **Data Strategy & Onboarding** process before proceeding.

**Prioritization**

- Use agreed prioritization criteria (for example, security/compliance impact, reliability benefit, effort, dependencies).

- Capture approved use cases in a central backlog managed by the Splunk Platform team and key stakeholders (OT/IT/SOC).

## Content Standards (Searches, Alerts, Dashboards, Knowledge Objects)

All Splunk content must conform to a basic set of standards:

### Searches & Alerts

- Use **CIM-aligned fields** where applicable, leveraging the Field Mapping and Data Dictionary standards.

- Optimize for performance (use index/time constraints, avoid unbounded wildcards, use summary or accelerated data where appropriate).

- Explicitly define severity, owner, and run frequency for alerts.

- Structured naming

- snake_case without restrictions on upper or lower case

- And the requirement that standards are approved and documented up front.

### Dashboards & Reports

- Use consistent layouts and page structures (for example, “Overview,” “Investigate,” “Detail” tabs).

Follow a documented, pre-approved naming standard for all dashboards and reports.

- Naming standards must be **defined, approved, and documented** by the Splunk Design Authority (or equivalent governance group) **before** dashboards or reports are created in production.

- Use a **structured snake_case** pattern to make objects easy to identify and search. Recommended format:

  - \<Object_type\>`_`\<Domain\>`_`\<Detailed_name\>

  - OBJECT_TYPE:

    - RP= Report

    - DS = Dashboard

  - DOMAIN: high-level domain such as IT, OT, SEC, PCI, NOC, etc.

  - DETAILED_NAME: short, descriptive name in snake_case.

- Examples:

  - RP_IT_NETWORK_ABNORMALITIES

  - DS_OT_CRITICAL_MEASURES

- Clearly label data sources, time ranges, and filters in the UI so users understand context and scope.

- Avoid excessive real-time panels, prefer scheduled reports, summary indexes, or accelerated data models when feasible to reduce load and improve performance.

## Other Splunk Entities Catalog and Naming Standards

In addition to data sources, the Data Catalog must include key Splunk entities that represent operational logic and platform outputs. These entities must be consistently named, owned, and managed to support reliability, auditability, reuse, and controlled change.

### In-scope entities

- Alerts and alert actions

- Summary reports and summary indexes

- Scheduled searches and correlation searches

- Dashboards, reports, and saved searches

- Lookups and KV store collections (where used)

- Macros, event types, tags, and calculated fields (where used)

- Notable event definitions, suppression rules, and tuning exceptions (where applicable)

### Naming convention

All entities must follow a consistent naming convention aligned to snake_case convention.

### Prefixes

To support discoverability and lifecycle management, use standardized prefixes by entity type, followed by a meaningful tag-based name [RECOMMENDED]:

- `al_` for alerts

- `sr_` for summary reports / summary indexing jobs

- `cs_` for correlation searches

- `ss_` for scheduled searches

- `da_` for dashboards

- `rp_` for reports

- `lk_` for lookups

- `mc_` for macros

- Example formats:

- al_security_authentication_bruteforce

- sr_ops_availability_daily

- cs_ot_anomaly_protocol

- ds_it_patching_status

### Suffixes

Furthermore, use suffixes to define categorical identification. For example:

For a summary report that runs daily, use `_daily` as a suffix:

- `sr_[`…`]_daily`

For a scheduled search that runs every 4 hours, use `_4h` as a suffix:

- `ss_[`…`]_4h`

These suffixes and formats need to be defined, approved and maintained.

### Management rule

All cataloged Splunk entities must have an assigned owner, an intended use, and a defined lifecycle state (for example: draft, approved, production, deprecated). Changes to production entities must follow change and release management practices, and entities must be periodically reviewed to confirm continued business need, RBAC alignment, and operational relevance

## Knowledge Objects (KOs)

- Naming conventions must follow snake_case and be descriptive (no search1, temp_test, etc.).

- Ownership and sharing scope must be explicitly set (private, app, or global) and aligned with RBAC and data sensitivity.

- Reusable macros and lookups should be centralized in **utility apps** rather than duplicated across many apps.

## Knowledge Object Sharing & Multi-Tenancy

### Scope & Sharing

- Default scope for new content is **app-level**, not global.

- Global sharing is allowed only when the content is broadly reusable and does not expose restricted data or logic.

### Tenant / Dedicated Search Heads

- Tenant Search Heads follow the same content standards, but content is scoped to tenant apps by default.

- Shared, cross-tenant content must be provided from centrally managed apps and governed by the Splunk Platform team.

## Apps & Technology Add-ons (TAs)

Splunk capabilities are packaged and deployed as apps and TAs:

### Splunkbase Apps

Must be reviewed for:

- Security (permissions, network access, code inspection where feasible).

- Compatibility with the current Splunk version and topology.

- Overlap with existing capabilities.

Only approved versions are installed in production; upgrades follow change management.

### Internal Apps

Used for:

- Organization-specific dashboards and workflows.

- Normalization logic and knowledge objects.

- Custom commands, modular inputs, and integrations.

Must be version-controlled (Git) and deployed only upon approval.

## Custom Commands, Custom Code, and Apps

Custom code is a powerful enabler in Splunk, but it introduces risk if it is not governed. This subsection defines how custom search commands, modular inputs, apps, integrations, and supporting code are allowed, developed, deployed, and operated on the Splunk platform.

### Guiding Principles

#### Native first

Before introducing custom code, teams must evaluate whether native SPL, base Splunk features, or supported Splunk/Splunkbase apps can satisfy the requirement. Custom code is a last resort, not the default.

#### Governed and security-reviewed

Custom code is allowed, but only when subject to defined governance, security review, performance review, and lifecycle management.

#### Confined to applications

All custom logic (commands, scripts, modular inputs, lookups, UI components) must live inside Splunk apps, not in ad hoc filesystem locations or stand-alone scripts.

#### Config-as-Code by default

All custom code and configuration deployed to production must be under version control, with changes promoted via change management process. No “snowflake” manual edits on production search heads.

#### Security and performance conscious

Custom code must respect RBAC, data classification rules, and resource constraints. It must not bypass access controls or materially degrade platform performance.

## Environment & Configuration-as-Code Guardrails

### Where custom code is allowed

- Custom search commands, modular inputs, and related configurations are allowed **only on Splunk Search Heads** and must be packaged and deployed as part of Splunk apps.

- All custom code must be confined within app directories (for example, \$SPLUNK_HOME/etc/apps/\<app_name\>).

### Source control and documentation

All custom code and app configuration that runs in production must:

- Be committed to an approved **Git repository** (or equivalent).

- Be **properly documented and commented**, including:

  - Purpose and supported use cases.

  - Inputs/outputs and assumptions.

  - Ownership and escalation contacts.

Include **operational documentation** (how to deploy, test, monitor, and roll back).

### Languages, runtimes, and platforms

- **Python is preferred** for Splunk-side custom development due to native support and operational familiarity.

- Other programming languages are allowed upon explicit approval and Security, provided:

  - Runtime management is clearly defined (versioning, patching, dependencies).

  - Logging, monitoring, and resource usage can be controlled.

- **Kubernetes and containers** are allowed for supporting components (for example, external services, ML jobs, enrichment APIs), provided they are:

  - Treated as managed services with clear ownership.

  - Aligned with network zoning and Zero Trust policies.

### Data access, whitelists, configuration, and libraries

Custom commands and code:

- Run with the **effective permissions of the invoking user** and therefore remain subject to Splunk RBAC and data classification rules.

- May operate over any datasets and indexes that the invoking user is authorized to access; they are not artificially constrained to a subset of indexes.

> Storing **whitelists, configuration files, and reference data** within apps is allowed, provided:

- They are under version control.

- Sensitive values (secrets, credentials) use approved secure mechanisms, not plain text.

> **Downloading libraries** (for example, Python packages) is allowed, subject to:

- Preferential use of internal repositories where available.

- Version pinning to known-safe versions.

- Dependency review and security scanning as part of CI/CD.

### Promotion path

All custom search commands, modular inputs, TAs with code, and internal apps must follow a controlled promotion flow:

**Development / Sandbox**

1.  Code is developed and iterated in dev or sandbox environments using non-production or test data (for example, `tmp_` indexes where appropriate).

**Test / QA**

2.  Deployed through change control management to a test environment that reflects production topology as closely as practical.

3.  Functional, security, and performance testing is performed.

**Stage / Pre-Prod (recommended)**

4.  Deployed to a staging environment for final validation and user acceptance testing.

**Production**

5.  Promotion only after passing defined quality gates:

    1.  Code review complete.

    2.  Security review and dependency scanning complete.

    3.  Performance impact validated as acceptable.

6.  Deployed via automated pipelines from Git; **no manual installation** on production search heads.

7.  Rollback procedures (for example, revert to previous app version, disable problematic command) must be documented and tested.

### Development & Approval

#### When custom code is allowed

Custom search commands, Python code, modular inputs, and similar extensions are allowed only when:

- The required function **does not inherently exist** in Splunk SPL or standard features; and

- A custom implementation is required as existing apps do not offer a comparable, secure feature set. Management has approved custom development to prioritize long-term maintainability and specific operational requirements over off-the-shelf solutions

#### Review and approval process

All custom code must undergo:

**Peer review**

- At least one reviewer other than the author must review code and configuration.

**Security review**

- Dependency scanning for third-party libraries.

- Checks for credential handling, input validation, and proper logging.

**Documentation review**

- Confirm that purpose, usage, ownership, and rollback are documented.

- Confirm that any new data flows are consistent with data classification and network zoning.

Custom code is deployed **only on Search Heads** (and any explicitly approved external runtimes) and must not be installed on indexers or utility servers except where specifically justified and approved.

### Performance expectations and guardrails

Custom code must:

- Incorporate **resource limits** (timeouts, concurrency limits, reasonable result set sizes).

- Undergo **performance testing** in test/stage environments before production deployment.

- **Fail gracefully** with clear error messages, no unbounded loops, and safe error handling that does not take down the platform.

### Secrets and Configuration handling rules

These rules apply uniformly to all custom commands, modular inputs, integrations, and apps, regardless of language or runtime.

**No hardcoded secrets**

- Passwords, API keys, access tokens, SNMP community strings, private keys, certificates, and similar secrets must **never** be hardcoded in code, configuration files committed to Git, or dashboards.

- Secrets must be stored and retrieved using **approved secret management mechanisms** (for example, enterprise secrets manager, Splunk secure storage, or equivalent), not in plain text.

**No hardcoded environment-specific endpoints**

- Direct IP addresses, hostnames, and URLs for production systems must not be hardcoded in code.

- Environment-specific details (endpoints, ports, tenants, realms) must be externalized into configuration managed via apps and Config-as-Code, not embedded in source code.

**Secure configuration and whitelists**

- Configuration files and whitelists may be stored in apps and version-controlled, but must not contain secrets.

- Where sensitive references are required (for example, identifiers that map to secrets), use indirection (keys, IDs) that are resolved via the approved secret/configuration mechanism at runtime.

**No logging of sensitive values**

- Custom code must not log passwords, tokens, SNMP strings, certificates, or full connection strings, even in debug logs.

- Where troubleshooting requires context, log non-sensitive metadata (for example, connection name, endpoint alias) instead of raw credentials or payloads.

### Support and ownership

Each custom app/command must have:

- A clearly defined **owner** (team and primary contact).

- A defined **support model** (who responds to incidents, who approves changes).

- Lifecycle expectations (criteria for deprecation, replacement, or migration).

### Splunkbase apps vs. internal apps vs. one-off scripts

**Splunkbase apps**

- Preferred when they are mature, supported, and secure.

- Must be reviewed before production use.

**Internal apps**

- Follow all the rules in this subsection (Git, CI/CD, review, documentation, monitoring).

- Are the standard vehicle for custom commands, modular inputs, TAs, and reusable KOs.

**One-off scripts**

- Unmanaged scripts on Splunk hosts are **not allowed** in production.

- Any script that becomes operationally important must be converted into a governed internal app.

This section ensures that all apps, content, and custom code on the Splunk platform are **intentional, governed, and sustainable**, while still giving Tri-State teams the flexibility to build the analytics and workflows they need.

# Operations, Monitoring & Maintenance (Platform Operations)

Platform Operations is responsible for running Splunk as a secure, compliant, reliable, resilient enterprise service. This includes day-to-day operations, monitoring, routine maintenance, lifecycle management, and operational governance to ensure the platform consistently meets business and regulatory needs.

## Operational responsibilities

- Operate and maintain all Splunk platform components (ingestion tier, indexers, search heads, management components, forwarder services, and supporting integrations).

- Maintain platform stability, performance, and availability through proactive monitoring and disciplined change control.

- Enforce platform standards for security zoning, RBAC, data segregation, metadata standards, and evidence integrity.

- Provide operational support for onboarding pipelines, including validation of ingestion health and troubleshooting parsing or pipeline issues.

## Monitoring and alerting expectations

Platform Operations will implement and maintain monitoring that provides early warning and operational context, including:

**Ingestion and pipeline health**

- Forwarder and collector health, connectivity, queue depth, dropped events, and ingestion latency.

- Data volume anomalies (unexpected spikes or drops) by source, sourcetype, and index.

**Indexing and storage health**

- Indexing throughput, indexing delay, disk utilization, IOPS pressure, hot/warm bucket behavior, and retention enforcement.

- Cluster health indicators, including replication and search integrity.

**Search and user experience**

- Search head resource utilization, search concurrency and saturation, scheduler health, and slow search detection.

- Impact monitoring for scheduled searches, summary jobs, alerts, and high-cost dashboards.

**Security and audit signals**

- Authentication events, privileged access patterns, administrative actions, configuration changes, and audit log completeness.

- Detection of unauthorized interfaces, unexpected outbound connections, or cross-zone flow anomalies.

## Maintenance and lifecycle management

- Execute routine maintenance activities such as certificate renewals, housekeeping, capacity tuning, app lifecycle maintenance, and supported upgrades.

- Maintain a vendor support alignment plan for Splunk versions and critical dependencies.

- Implement standard backup and recovery procedures for critical configuration and platform state.

- Ensure the test implementation environment is used to validate upgrades and high-impact changes before production release.

## Incident, problem, and recovery management

- Maintain on-call and escalation procedures for platform incidents, including defined severity levels and communications protocols, where applicable.

- Use runbooks for common failure scenarios (ingestion stoppage, indexing delays, search degradation, cluster health issues, certificate failures).

- Conduct post-incident reviews for significant events and feed findings into operational improvements, monitoring enhancements, and change practices.

- Validate resiliency through periodic recovery exercises and failover testing aligned to business continuity expectations.

## Access, exceptions, and periodic review support

- Support periodic reviews of inbound interfaces, cross-zone flows, and privileged access.

- Ensure temporary exceptions are documented, time-bounded, and removed or re-approved according to governance expectations.

- Maintain an operational record of platform changes and releases to support audit readiness.

## Operational documentation and runbooks

- Maintain current runbooks, standard operating procedures, and escalation guides.

- Document standard patterns for onboarding, troubleshooting, and maintenance to reduce dependency on individual knowledge and improve resilience.

## Continuous improvement

- Track operational trends (stability, performance, capacity, incident drivers) and recommend optimization initiatives.

- Identify sources of waste (noisy data, redundant feeds, inefficient searches) and partner with stakeholders to reduce cost and improve performance.

- Regularly review platform posture to ensure it remains aligned with evolving security, compliance, and operational requirements.

# Interfaces and Data Movements

This section defines the approved ways data may enter, move within, and exit Splunk. The goal is to enable fast onboarding and innovation while staying secure, compliant (including NERC CIP), reliable, resilient, and operationally supportable. Splunk’s design is prescriptive at the boundaries and zoning level, while allowing teams to innovate safely inside those guardrails.

## Core principles for interfaces and data movement

- **Zone-aware movement:** Interfaces and data movement must respect network zoning and Zero Trust expectations; supporting components must be aligned with network zoning and Zero Trust policies.

- **Regulatory isolation (including CIP):** Data classification and compliance drivers (including NERC CIP) are encoded into indexes and enforced through segregation rules so regulated data can have specific retention, purge, and audit controls.

- **RBAC is mandatory at every interface:** Access to Splunk data and capabilities is governed by role-based design tied to identity groups, business roles, and privilege bundles, with an auditable chain from identity to governed indexes and capabilities.

- **Data minimization and protection:** Non-actionable noise and low-value verbose fields should be removed at the ingestion layer where feasible, reducing risk exposure and cost while preserving necessary forensic value.

- **Anonymization and obfuscation where necessary:** When datasets must cross zones or be used for broader visibility, sensitive attributes must be masked, tokenized, or obfuscated as required by classification and compliance needs (including minimizing re-identification risk).

## Inbound access approvals and periodic review

- **Production onboarding requires a Data Catalog entry:** No data is onboarded into production Splunk environments without an explicit catalog entry defining source, sourcetype, target index, data class, compliance drivers, and owners.

- **Field-level governance before production:** Before a data source is approved for production ingestion, a Field Mapping Document must be created and approved by a designated Data Steward or Architect (gatekeeper rule).

- **Inbound interface approvals:** Any inbound path (forwarders, syslog, HEC, APIs, cross-zone feeds, partner integrations) must be explicitly approved by platform governance and the appropriate security, compliance, and data owner stakeholders, consistent with classification and compliance isolation.

- **Periodic review:** All inbound interfaces and granted access are subject to periodic review to validate continued business need, appropriate RBAC alignment, and ongoing compliance. RBAC monitoring already expects regular reviews to identify exceptions and enforce expirations for temporary deviations.

## Cross-zone pattern

When a higher security zone requires visibility into data originating in a lower security zone, use a controlled DMZ pattern to avoid direct trust relationships and to support compliance, auditability, and resilience.

### Recommended DMZ broker patterns

- **OT Splunk to DMZ broker (push):** OT producers forward only approved datasets to a DMZ broker instance.

- **IT Splunk from DMZ broker (pull):** IT consumers pull only from the DMZ broker instance using approved service identities and allowlisted interfaces.

**DMZ enforcement expectations**

- Enforce segregation and compliance isolation through index strategy and governance rules.

- Apply minimization plus anonymization or obfuscation before exposure across zones.

- Ensure RBAC remains consistent and auditable from identity to governed datasets.

## Outbound interfaces

- **Default stance:** Splunk is a system of evidence; data egress is allowed only for approved business/operational outcomes (SOC/NOC workflows, compliance reporting, enrichment services, AI/analytics pipelines) and must not bypass RBAC or classification boundaries.

- **No “side channels”:** Exports, APIs, and integrations must use defined/monitored endpoints, with service identities and allowlists, and must meet audit logging requirements for regulated/sensitive data.

## Innovation-enabled interfaces

Innovation is encouraged when implemented as a managed, reviewable pattern that does not bypass zoning, RBAC, or compliance controls.

- **Custom Splunk-side development:** Custom commands and code run with the effective permissions of the invoking user and remain subject to Splunk RBAC and data classification rules. Any new data flows must be consistent with data classification and network zoning.

- **Containers and supporting services:** Kubernetes and containers are allowed for supporting components (external services, ML jobs, enrichment APIs) when treated as managed services with clear ownership and alignment to network zoning and Zero Trust policies.

- **Sandbox for rapid prototyping:** A temporary onboarding process is permitted for proof-of-concept and troubleshooting using `tmp_` indexes, short retention, explicit expiration dates, and a strict prohibition on regulated or highly sensitive production data.

# AI Training and Inference

This section defines how AI can be trained and used with Splunk and operational/security data while enabling innovation and maintaining security, compliance, reliability, resilience, and operational integrity. It separates the **training plane** from the **inference plane**, enforces RBAC throughout, and ensures AI never compromises safety or the immutability of evidence.

## Separation of planes

- **Training plane:** Dataset creation, preparation, training, and validation. Training plane controls focus on data location, sample set handling, lineage, and approval.

- **Inference plane:** Execution of approved models against permitted data to produce **derived outputs** (scores, tags, summaries, anomaly indicators). Inference may be hosted on Splunk search heads, on-prem inference services, or cloud inference services, as long as compliance, security, RBAC, and audit expectations are met.

## Training rules

**Training Rule 1: Data location and classification are enforced**

OT, operational, and highly sensitive data stay on-prem in OAP; CAP works with enterprise and external data plus only approved aggregates from OAP.

**Training Rule 2: Safe sharing uses aggregation and approved obfuscation**

When broader visibility is needed, produce aggregated KPI-level outputs or apply approved obfuscation techniques, and share only those safe outputs.

**Training Rule 3: Cloud training safeguard prohibits unsafe training or prompting**

No external or cloud-hosted AI or large language model may be trained on or prompted with raw OT telemetry, sensitive security logs, or regulated personal data, allowed classes and contractual safeguards are governed.

**Training Rule 4: RBAC applies throughout training, including sample set creation**

Implement RBAC across all tiers of data and for all AI and ML workloads including during training.

**Training Rule 5: Sample sets are controlled, minimal, and traceable**

Training sample sets must be purpose-bound to an approved use case, minimized to necessary fields, anonymized or obfuscated when required, and tracked for lineage (source to transforms to dataset to model artifact). This aligns with the strategy requirement that AI usage, data flows, and key decisions are auditable and traceable.

**Training Rule 6: Cross-platform and cross-zone flows are auditable and reviewable**

All OAP and CAP data flows must pass through defined, monitored interfaces, with metadata logged and retained for review (who, what, when, why, and under which rule).

## Inference rules

**Inference Rule 1: Inference runs under RBAC and least privilege**

RBAC applies to all AI workloads, including inference. Inference must not expand access beyond what the requesting identity or approved service identity is authorized to access.

**Inference Rule 2: Inference plane placement is allowed with compliance controls**

Inference components may exist on Splunk search heads, cloud, or on-prem solutions, provided data location rules and safe-sharing rules are honored (for example, CAP consumes approved aggregates; OAP handles OT and operational data).

**Inference Rule 3: Prompts, context, and network flows must be explicitly defined and reviewed**

For any LLM or external inference service, network flows, authentication, prompt construction rules, allowed context fields, logging, and retention must be documented, reviewed, and periodically re-reviewed under the auditability requirement.

**Inference Rule 4: Generative AI use is permitted only under explicit guardrails**

On-prem generative AI, including Splunk-inherent LLM capabilities, may be used when air-gapped or when explicitly approved with documented flows, prompts, RBAC enforcement, and audit logs. Other LLMs may be considered only under the same documented-and-reviewed requirements and must obey the cloud training safeguard for prohibited data classes.

**Inference Rule 5: No autonomy**

No AI solution may compromise safety, reliability, or regulatory obligations, and there are no autonomous controls. AI recommends and humans decide for critical or high-impact operational decisions. Any exception requires explicit approval from the one of the senior leaders of Technical Services.

**Inference Rule 6: Preserve immutability of evidence**

AI outputs must be additive and derived (for example, enriched fields, risk scores, anomaly indicators, summaries) and must not alter, rewrite, or “correct” original events. Splunk remains a system of evidence and audit; AI must not undermine the immutability and traceability expectations.

# Change & Release Management

Change and Release Management ensures the Splunk platform remains secure, compliant, reliable, resilient, and operationally supportable while enabling teams to deliver enhancements and onboard new data safely. The approach balances agility with control by using risk-based change tiers, strong testing and validation, and clear approval and rollback expectations.

This section does not cover underlying architecture changes including operating system changes and only focuses on Splunk as a platform.

## Scope

- Change and Release Management applies to the items below, and the classification for each type of change must be defined.Splunk core platform upgrades and patches (search heads, indexers, cluster manager, deployer, deployment server, heavy forwarders, edge/ingestion tier)

- Configuration changes (inputs, outputs, props/transforms, index strategy, retention, RBAC, authentication, certificates, network flows)

- Knowledge objects (dashboards, alerts, correlation searches, reports, lookups, macros, data models)

- Integrations (HEC endpoints, APIs, syslog feeds, third-party apps, containerized enrichment services)

- Cross-zone and cross-platform data movement (including DMZ broker patterns)

- AI-related integrations and inference services connected to Splunk (prompting, context retrieval, model endpoints)

## Change classification

Changes are categorized to ensure the level of control matches the risk.

**Standard changes**

- Pre-approved, low-risk, repeatable activities executed using documented runbooks (for example, onboarding a source using an approved pattern, routine certificate renewal, adding a user to an approved RBAC group).

- Require validation steps and logging, but do not require a formal CAB meeting.

**Normal changes**

- Planned changes that require review and approval (for example, new sourcetype definitions, new index creation, new parsing logic, enabling a new integration endpoint).

- Require a documented implementation plan, testing evidence, and a rollback plan.

**Emergency changes**

- Time-critical changes required to restore service or address active security risk.

- Must still be logged and must be reviewed after implementation to confirm completeness, remove temporary exceptions, and capture lessons learned.

## Environments and promotion path

- **Development and test environments** are used to build and validate changes safely before impacting production.

- **Sandbox onboarding** is permitted for proof-of-concept and troubleshooting with explicit expiration and short retention; it is not a bypass around production governance.

- **Promotion to production** occurs only after documented validation and approval, with the minimum required privileges and clear ownership.

## Testing and validation requirements

All production-impacting changes must be validated based on the change type:

**Functional validation**

- Verify ingestion continuity, parsing accuracy, timestamps, host/source/sourcetype conventions, and expected fields.

**Security and access validation**

- Verify RBAC enforcement, least privilege, and that no new access paths were unintentionally introduced.

- Confirm that cross-zone flows remain correct and constrained to approved interfaces.

**Reliability and performance validation**

- Validate expected indexing rates, latency, search performance, and resource utilization.

- Confirm clustering health, replication/search factors, and site resiliency behavior where applicable.

**Compliance validation**

- Confirm regulated data remains in the correct indexes with correct retention and audit logging enabled.

- Confirm anonymization/obfuscation controls remain in effect where required.

**Operational readiness**

- Update runbooks, monitoring, dashboards, and alert thresholds if the change alters behavior or dependencies.

## Release planning and scheduling

**Release cadence**

- Core platform releases follow a defined cadence aligned to vendor support, security patch cycles, and operational windows.

- High-risk changes are grouped into planned maintenance windows.

**Change windows**

- Changes affecting ingestion pipelines, indexing, clustering, or cross-zone flows are executed only during approved maintenance windows unless emergency conditions apply.

**Communications**

- Release notes are distributed to impacted stakeholders, including expected impacts, risk level, testing results, and rollback approach.

## Approvals and decision rights

Approvals depend on the change type and impacted scope:

- **Platform Team approval** for platform configuration and operational changes

- **Data Steward and Data Owner approval** for onboarding, sourcetype/source definitions, index strategy changes, and parsing changes

- **Security and Compliance approval** for RBAC changes, new network flows, cross-zone patterns, regulated data handling, anonymization/obfuscation changes, and exception requests

- **Architecture review** for major design changes, new platform components, and new integration patterns (including containers and external services)

## Rollback and recovery expectations

- Every Normal change must include a rollback plan and recovery steps.

- Where rollback is not feasible (for example, some migrations), the plan must include compensating controls, staged cutovers, and a clear restoration approach.

- Rollback steps must be practiced for high-impact releases and must be documented in runbooks.

## Configuration management and traceability

- Platform configuration must be version-controlled where feasible (deployment apps, patterns, documented baseline configurations).

- Changes must be traceable to a request, owner, approver, and implementation record.

- Temporary exceptions (including emergency access or temporary ingestion rules) must have an expiration date and must be removed or re-approved during periodic review.

## Third-party apps and custom development controls

- Third-party Splunk apps, add-ons, and custom commands must be security-reviewed and maintained through a lifecycle process (patching, deprecation, compatibility testing).

- Custom code must not bypass RBAC or data classification boundaries and must be treated as production software with testing, logging, and peer review.

## AI-related change controls

- Any integration that sends data to an inference or LLM endpoint must define network flows, authentication, prompt/context rules, logging, and retention.

- AI integrations must follow the separation of training and inference planes and must not introduce autonomous actions.

- AI outputs must be additive and must not modify or overwrite original events to preserve evidence of integrity.

## Post-release review and continuous improvement

- Significant releases require a post-implementation review to confirm outcomes, capture issues, and update standards.

- Incident learnings are fed back into runbooks, monitoring, and change patterns to reduce recurrence and improve platform resilience.

# Training, Enablement & Adoption

Training and enablement will be delivered through role-based learning paths. The intent is to ensure users can adopt Splunk safely and effectively, while maintaining security, compliance, reliability, resilience, and operational consistency.

## Role-based training paths

**Consumers (Operators, Analysts, Business Users)**

- Splunk search basics (time bounding, fields, filters, pivoting)

- Using standard dashboards, reports, and alerts

- Interpreting derived signals and scores appropriately (no assumptions of autonomy)

- Handling and sharing results in a compliant manner

**Content Builders (Power Users, Detection Engineers, Dashboard Developers)**

- Advanced SPL, search performance practices, scheduling basics

- Building production-ready dashboards, reports, and alerts using standard naming and documentation

- Working within RBAC constraints and designing content that respects segregation

- Validating content before promotion to production

**Data Onboarding Engineers**

- Onboarding workflow and required documentation (ownership, classification, metadata standards)

- Defining and applying source, sourcetype, and host standards

- Field mapping, parsing, timestamp handling, and normalization

- Data minimization plus anonymization/obfuscation where required, including regulated data handling

- Cross-zone onboarding patterns such as OT to DMZ to IT

**Platform Administrators**

- Core administration and platform operations (roles, indexing, search head operations)

- Deployment practices and configuration management

- Authentication, RBAC administration, certificates, and secure administration

- Monitoring, capacity management, upgrades, backup, and recovery procedures

**OT Stakeholders**

- OT telemetry onboarding patterns and OT asset identification standards

- Operational safety expectations and disciplined change control

- Cross-zone visibility and data sharing patterns aligned to zoning and compliance requirements

## Additional enablement considerations

Additional elements such as enablement assets, adoption support models, service KPIs, training completion tracking, and broader adoption metrics may be defined later. It is recommended that managers review these strategically over time and implement them in a way that aligns to organizational maturity, capacity, and priority use cases.

# Roadmap & Phased Implementation Plan

This roadmap provides a strategic, phased approach to establish Splunk as a secure, compliant, reliable, resilient enterprise service across I&T. Phases may overlap based on resourcing, dependencies, and priority use cases. Each phase should include clear entry and exit criteria so progress is measurable and governance remains enforceable.

## Phase 0: Capability readiness and mobilization

- Establish platform ownership, governance decision rights, and an operating model that includes OT, IT, cybersecurity, and compliance stakeholders.

- Confirm skill coverage and role-based training needs for platform administration, data onboarding, detection/content development, and operational support.

- Align stakeholders on initial scope, success measures, and priority outcomes (reliability, security monitoring, regulatory reporting, OT visibility).

- Define the initial intake process for new data sources and use cases, including approvals and periodic review expectations.

## Phase 1: Infrastructure and topology design

- Finalize the target Splunk topology (indexing, search, ingestion tier, management components) and the resiliency posture aligned to availability and recovery objectives.

- Complete sizing and capacity assumptions (ingest rates, retention tiers, performance targets, storage IOPS), with a plan for growth.

- Define network segmentation, firewall rules, and Zero Trust-aligned flows across security zones, including where DMZ patterns are required.

- Confirm security foundations (authentication approach, certificate strategy, admin access paths, audit logging requirements).

## Phase 2: Hardware procurement and environment strategy

- Procure hardware and supporting infrastructure based on approved sizing and resiliency design.

Define an environment strategy that supports controlled promotion and risk reduction:

- A dedicated test implementation environment built after hardware is received, separate from production.

- A production environment that is built only after testing implementation acceptance is complete.

Establish the policy for test data usage (prefer synthetic, replayed, or anonymized datasets; limit regulated or highly sensitive data unless explicitly approved).

## Phase 3: Test implementation build and validation

- Build a non-production Splunk environment that mirrors production patterns as closely as practical (ingestion boundary approach, indexing/search separation, RBAC foundations, monitoring).

- Validate baseline platform operations: health monitoring, backup and recovery approach, performance baselines, upgrade approach, and operational runbooks.

- Validate security and compliance controls: RBAC behavior, audit logging, zoning flows, data segregation expectations, and exception handling process.

- Use the test implementation to prove the “golden paths” for onboarding and content promotion before production rollout.

**In this phase, limited-scope trial and error is acceptable in the test environment, and temporary control exceptions may be permitted as long as the environment remains strictly non-production and all deviations are documented and time-bounded.**

## Phase 4: Data architecture and onboarding framework

- Create the enterprise data onboarding framework, including data classification mapping, index strategy, retention tiers, and metadata standards (source, sourcetype, host).

- Inventory and prioritize data sources from OT, IT, SOC, and compliance perspectives, including volume estimates and retention requirements.

- Establish parsing, normalization, enrichment, tagging standards, and field mapping governance so production onboarding is predictable and supportable.

- Define cross-zone data movement patterns where needed, including brokered approaches such as OT to DMZ to IT, with minimization and obfuscation where required.

## Phase 5: Core production build and hardening

- Build the production Splunk platform aligned to the approved topology, resiliency posture, and security requirements.

- Implement baseline RBAC structures, index segregation, and audit controls.

- Establish operational readiness: monitoring, alerting, capacity tracking, incident response procedures, and platform support model.

- Confirm release discipline and configuration management approach so production does not drift.

## Phase 6: Initial data onboarding and priority use cases

- Onboard an initial set of high-value data sources using governed patterns and validated onboarding practices.

- Deliver initial dashboards, alerts, and reports tied to agreed outcomes (operations reliability, OT visibility, cybersecurity monitoring, compliance evidence).

- Establish a repeatable promotion path from test to production for data onboarding changes, apps, and knowledge objects.

## Phase 7: Production rollout and scaling

- Expand onboarding to additional sources and business domains using standardized intake, approval, and periodic review processes.

- Mature operational controls: tuning and optimization, lifecycle management, cost awareness, and ongoing resiliency validation.

- Reduce exceptions by migrating ad hoc integrations toward approved patterns (ingestion tier, DMZ brokering, governed APIs, containerized services as managed components).

## Phase 8: Optimization and continuous improvement

- Optimize performance, retention alignment, and operational efficiency based on observed usage and growth.

- Operationalize regular service reviews (health, capacity, reliability incidents, security posture, onboarding throughput).

- Continuously improve content quality (detections, dashboards, correlation) and retire low-value data or content to control cost and complexity.

## Phase 9: AI and machine learning enablement

- Introduce AI capabilities only after foundational governance, RBAC, zoning, and data quality controls are stable.

- Operationalize separation of training and inference planes, with clear rules for data handling, access, and auditability.

- Enable inference in approved locations (search head, on-prem inference services, or cloud inference services) subject to classification, security zone constraints, and explicit review of network flows, prompts, and logging.

- Keep AI outputs additive and derived, preserve immutability of original events, and prohibit autonomous actions in all cases.

## Strategic note on sequencing

Managers may adjust sequencing based on business priorities, but the roadmap assumes a disciplined progression: establish governance and foundations first, validate in a test implementation environment, then scale production onboarding and use cases, and only then expand into advanced analytics and AI enablement.

# Risk Management & Assumptions

This section identifies key risks and planning assumptions for implementing and operating Splunk as an enterprise service across I&T. The intent is to reduce delivery risk, protect regulated environments, and ensure the platform remains secure, compliant, reliable, resilient, and operationally supportable.

## Risks

**Security zone boundary and cross-zone data movement risk**

- Risk that uncontrolled flows between higher and lower security zones could create unacceptable exposure or compliance violations.

- Mitigation: enforce deny-by-default network posture, brokered patterns (such as DMZ), explicit allowlists, RBAC enforcement, and periodic review of inbound interfaces and cross-zone flows.

**Regulatory and compliance risk (including CIP)**

- Risk that regulated data is not properly segregated, retained, audited, or handled according to policy and regulatory expectations.

- Mitigation: encode compliance drivers in index strategy, enforce RBAC aligned to classification, maintain audit logging, and require documented onboarding and field mapping approvals.

**Data quality and metadata inconsistency risk**

- Risk that inconsistent source, sourcetype, and host practices reduce correlation, impact dashboards/detections, and increase support burden.

- Mitigation: enforce metadata standards, maintain a custodian-managed registry of source and sourcetype definitions, and require validation prior to production onboarding.

**Scope growth and platform cost risk**

- Risk that onboarding volume grows faster than capacity planning, increasing licensing, storage, and operational cost, and reducing performance.

- Mitigation: use phased onboarding, prioritize high-value use cases, apply data minimization at ingestion, and continuously review retention tiers and data value.

**Operational reliability and resiliency risk**

- Risk that platform outages, ingestion delays, or cluster misconfiguration reduce visibility during incidents and impact operations.

- Mitigation: design for HA/DR, implement monitoring and alerting, maintain runbooks, test recovery procedures, and enforce disciplined change and release management.

**RBAC drift and privileged access risk**

- Risk that access expands over time, exceptions become permanent, or privileged roles are overused.

- Mitigation: role-based access tied to classification, periodic access reviews, time-bounded exceptions, and audit logging with review.

**Integration and customization risk**

- Risk that custom apps, modular inputs, scripts, containers, or external services introduce vulnerabilities, bypass controls, or increase support complexity.

- Mitigation: approve integration patterns, require security review, document network flows and identities, enforce RBAC, and manage lifecycle/patching.

**Cross-functional dependency risk**

- Risk that delivery is delayed due to dependencies on network/firewall changes, PKI/certificates, identity integration, OT stakeholder alignment, or procurement lead times.

- Mitigation: formalize dependencies early, create a shared delivery plan with owners, and validate feasibility in the test implementation phase.

**AI and generative AI risk**

- Risk that LLM usage introduces data leakage, unapproved prompting, insufficient auditability, or unsafe operational outcomes.

- Mitigation: separation of training and inference planes, explicit rules for prompts/context and network flows, approval and periodic review, full logging, additive-only outputs, and no autonomous actions.

## Assumptions

**Governance and ownership**

- A platform owner and platform team are assigned with clear decision rights for standards, operations, onboarding gates, and exceptions.

- Data owners and custodians exist and can approve onboarding intent, metadata definitions, and periodic reviews.

**Security and compliance participation**

- Security and compliance stakeholders are available to approve zoning flows, RBAC design, regulated data handling, and exception requests.

- Regulatory requirements (including CIP where applicable) are defined sufficiently to map to indexing, retention, and audit controls.

**Infrastructure readiness**

- Required hardware, storage, and network capacity will be available according to sizing and resiliency design.

- Certificate management (PKI), identity integration, and time synchronization are available and can be implemented consistently.

**Environment strategy**

- A strictly non-production test implementation environment will be built after hardware procurement to validate topology, controls, onboarding patterns, and operational readiness prior to production rollout.

- Test data will be synthetic, replayed, or anonymized by default; use of regulated or highly sensitive production data in test requires explicit approval.

**Data onboarding discipline**

- Production ingestion will follow the governed intake and approval workflow and will adhere to metadata standards and required documentation.

- Source systems will provide stable identifiers (CMDB/FQDN or OT asset identifiers) to support host naming and correlation.

**Operational support**

- Runbooks, monitoring, and a support model (including escalation) will be established before broad production scaling.

- Change and release management practices will be applied consistently to avoid drift and protect platform stability.

**Innovation within guardrails**

Teams may propose innovative integrations (including containers and service-based access) as long as network flows, access controls, compliance needs, and logging are defined, reviewed, and approved.

# KPIs, Value Realization & FinOps Metrics

Splunk should be managed as an enterprise service with the focus on operational areas (IT vs. OT) with measurable outcomes. Managers should define and maintain a small set of KPIs and value metrics that reflect organizational priorities (security, compliance, reliability, resilience, and operational effectiveness) and adjust them over time as maturity increases. Metrics should be reviewed on a regular cadence and used to drive prioritization, onboarding decisions, and continuous improvement.

## Minimum KPI categories to define

Managers should establish targets and reporting for metrics in these areas:

> **Service health and reliability**

Availability, incident frequency, mean time to detect and recover platform issues, ingestion latency, and search performance.

> **Security and compliance**

RBAC alignment and exception counts, privileged access usage, completion of periodic access/interface reviews, audit log completeness, and regulated-data handling adherence.

> **Operational outcomes and value realization**

Measurable improvements in operational reliability, faster incident response and troubleshooting, reduced downtime impacts, improved detection coverage, and increased automation of reporting or evidence collection.

> **Adoption and enablement**

Active usage by role, onboarding throughput, number of governed sources in production, and reuse of standard dashboards, detections, and onboarding patterns.

## Minimum Ops metrics to define

Managers should define cost and efficiency measures that ensure Splunk remains sustainable:

**Cost drivers**

Ingest volume trends, retention consumption, storage growth, compute utilization, and licensing alignment to actual usage.

**Efficiency and waste reduction**

Percentage of ingest reduced through filtering/minimization, duplicate/noisy data reduction, “low-value data” retirement, and optimization of retention tiers.

**Unit economics**

Cost per onboarded data source, cost per use case supported, and cost per operational outcome (where practical).

## Strategic guidance

Managers should keep the initial metric set small, focus on actionable measures, and evolve the KPI and FinOps framework as the platform matures. Metrics should directly influence roadmap sequencing, onboarding priorities, and decisions to optimize, expand, or retire data and content.
