# KPI Specification

The machine-readable contracts are stored in `configs/kpi_contracts.yaml`. This document explains their business meaning.

## 1. Near-Threshold Value Ratio

**Question:** How concentrated is relevant cash activity inside the configured proximity band below the illustrative threshold?

**Formula:** qualifying near-threshold cash value divided by all relevant cash value in the same slice.

**Primary drivers:** region, branch, channel, business type, account age.  
**Unit:** percentage.  
**Grain:** region-day.

## 2. Linked-Pattern Exposure

**Question:** What unique transaction value belongs to connected clusters that meet the transparent review rules?

**Formula:** sum of unique qualifying transaction IDs belonging to reviewed clusters. A transaction must never be counted twice.

**Primary drivers:** region, cluster, shared identifier, channel, account age.  
**Unit:** INR.  
**Grain:** region-day.

## 3. High-Risk Cluster Count

**Question:** How many connected clusters exceed the configured review-score threshold?

**Formula:** count of distinct qualifying cluster IDs.  
**Unit:** count.  
**Grain:** region-day.

The score is a review-prioritisation score, not a probability of wrongdoing.

## 4. Alert Investigation Yield

**Question:** Of completed investigations, how many were confirmed or escalated?

**Formula:** confirmed/escalated closed cases divided by all closed investigated cases.

**Unit:** percentage.  
**Grain:** region-week.  
**Label-delay note:** current open cases are excluded.

## 5. Case SLA Risk

**Question:** How many open cases are due to breach their SLA within the configured horizon?

**Formula:** count of open or in-review cases with `sla_due_at` between the as-of time and the configured horizon.

**Unit:** count.  
**Grain:** region-hour.

## Materiality policy

A KPI movement is prioritised only when its configured statistical/business condition is met and the evidence-quality gate passes. A hard business rule may override the statistical gate, but the override must be visible in the evidence.

