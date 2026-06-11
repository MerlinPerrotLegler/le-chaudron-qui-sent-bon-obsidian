# AI Knowledge System Instructions

## Purpose

This vault is the single source of truth for a long-term project.

The objective is to transform documents, PDFs, emails, notes, regulations, studies, administrative files and personal reflections into a structured and interconnected knowledge base.

The AI must act as a knowledge architect, not as a simple summarization tool.

---

# Core Principles

1. Knowledge must be atomic.
2. Each note should contain a single concept whenever possible.
3. Avoid duplication.
4. Prefer links over copied content.
5. Preserve source information.
6. Every important fact should be traceable to a source.
7. Long documents should be decomposed into smaller notes.
8. Notes should remain understandable years later.

---

# Vault Structure

## Inbox

Temporary notes awaiting processing.

Location:

00 Inbox/

---

## Dashboards

Project navigation and high-level summaries.

Location:

01 Dashboard/

---

## Projects

Active initiatives with a clear objective and deadline.

Location:

02 Projects/

Examples:

* Agricultural Project
* Building Permit
* Forestry Management
* Spice Production

---

## Domains

Permanent responsibilities and areas of expertise.

Location:

03 Domains/

Examples:

* Agriculture
* Forestry
* Administration
* Finance
* Construction
* Marketing

---

## Resources

Reference material and knowledge.

Location:

04 Resources/

Examples:

* Regulations
* Suppliers
* Technical Documentation
* Research Papers

---

## References

External documents and imported information.

Location:

05 References/

Examples:

* PDFs
* Administrative Forms
* Government Documents
* Studies

---

## Journal

Chronological information.

Location:

06 Journal/

---

## Archive

Inactive material.

Location:

99 Archive/

---

# Required Metadata

Every note should contain frontmatter.

Example:

---

type: concept
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags:

* agriculture
* permit
  source:
* source_document.pdf

---

---

# Note Types

## Concept

A reusable piece of knowledge.

Examples:

* SPANC
* Agroforestry
* Spice Drying

---

## Decision

A choice made during the project.

Must include:

* Context
* Alternatives
* Reasoning
* Consequences

---

## Task

Actionable work.

Must include:

* Description
* Priority
* Status
* Dependencies

---

## Contact

Person or organization.

Must include:

* Role
* Contact Information
* Related Projects

---

## Procedure

Step-by-step process.

Examples:

* Building Permit Submission
* SPANC Validation

---

## Regulation

Legal or administrative requirement.

Must include:

* Authority
* Scope
* Constraints
* Source

---

## Source

Original imported document.

Must never be modified.

---

# Processing Rules For PDFs

When importing a PDF:

1. Create a source note.
2. Extract key concepts.
3. Extract decisions.
4. Extract regulations.
5. Extract contacts.
6. Extract tasks.
7. Create backlinks.
8. Preserve source references.

Do not store information only inside PDF files.

Knowledge must be extracted into notes.

---

# Linking Rules

Always create links when relationships exist.

Examples:

[[SPANC]]
[[Building Permit]]
[[Forestry Management]]
[[Agricultural Project]]

Prefer many useful links over isolated notes.

---

# Task Extraction

When a document implies an action:

Create a task.

Example:

* [ ] Contact SPANC for soil study
* [ ] Submit permit application
* [ ] Obtain forestry assessment

---

# Missing Information Detection

Always identify:

* Missing documents
* Missing approvals
* Missing dates
* Missing stakeholders
* Missing regulatory information

Create dedicated notes when needed.

---

# Dashboard Generation

The AI should maintain dashboards containing:

* Open tasks
* Pending decisions
* Upcoming deadlines
* Missing information
* Important contacts
* Active projects

---

# Expected Behaviour

The AI should:

* Organize knowledge
* Create notes
* Refactor notes
* Link information
* Detect inconsistencies
* Surface missing information
* Maintain project memory

The AI should never:

* Duplicate information unnecessarily
* Create orphan notes
* Remove source references
* Mix unrelated concepts into a single note
