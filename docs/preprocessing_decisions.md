# Preprocessing Methodological Decisions

This document records preprocessing decisions that affect experiment validity.

## UWF `dest_port_zeek`

| Mode | Treatment | Rationale |
|------|-----------|-----------|
| **Within-dataset (native)** | Retained as numeric feature `dest_port` | Port is part of the Zeek conn log feature space for single-dataset experiments on UWF. |
| **Cross-dataset (Common-5/7)** | Used only for **service inference**, then **dropped** | Destination port is not semantically aligned across all datasets (KDD/NSL lack ports). Keeping it would leak dataset-specific service structure. |

## UWF `Duplicate` label policy

Default policy: **`exclude`** — rows with `label_binary == 'Duplicate'` are removed during transform.

Alternative policies (configurable via `DuplicatePolicy`):

- `attack` — treat as attack (binary 1)
- `benign` — treat as benign (binary 0)

Duplicate rows are never silently mapped without an explicit policy.

## Cross-dataset feature limitations

| Feature | Status | Caveat |
|---------|--------|--------|
| `duration` | Included | CIC datasets stored in microseconds; converted to seconds. |
| `src_bytes` / `dst_bytes` | Included | Direction semantics differ (src/dst vs fwd/bwd vs orig/resp). |
| `protocol` | Included | CIC-IDS2017 has no native protocol column; inferred from destination port (weak). |
| `service` | Included | CIC datasets infer service from port; CIC2018 files in this repo have no port column → service often `other`. |
| `src_packets` / `dst_packets` | Common-7 only | **Not available** in KDD99/NSL-KDD — Common-7 raises `Common7IncompatibleError`. |

## Missing labels

Missing labels raise `LabelProcessingError` by default. They are **never** silently converted to BENIGN.
