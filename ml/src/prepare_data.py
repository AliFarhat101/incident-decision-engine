import pandas as pd
import random
from pathlib import Path

RAW_PATH = Path("data/raw/HDFS_2k.log_structured.csv")
OUT_PATH = Path("data/processed/incidents_v1.csv")

random.seed(42)

TEMPLATE_RULES = [
    ("timeout", "timeout"),
    ("timed out", "timeout"),
    ("retry", "timeout"),
    ("slow", "timeout"),
    ("exception", "db_error"),
    ("error", "db_error"),
    ("fail", "db_error"),
    ("cannot", "db_error"),
    ("missing", "config"),
    ("invalid", "config"),
    ("not found", "config"),
    ("namenode", "config"),
    ("permission", "auth"),
    ("access denied", "auth"),
    ("unauthorized", "auth"),
    ("forbidden", "auth"),
]

ALLOWED = {"db_error", "timeout", "config", "auth", "unknown"}


def label_from_text(text: str) -> str:
    t = (text or "").lower()
    for key, label in TEMPLATE_RULES:
        if key in t:
            return label
    return "unknown"


def synth_timeout(i: int) -> dict:
    samples = [
        "WARN RPC: Call to NameNode timed out after 30000 ms, retrying",
        "ERROR DataStreamer: Pipeline recovery failed due to timeout",
        "WARN DFSClient: Read timed out while fetching block, retry attempt 2",
        "WARN IPC: RPC connection timed out to namenode, reconnecting",
        "ERROR LeaseRenewer: Lease renewal timed out, will retry",
    ]
    return {"source": "hdfs", "log": random.choice(samples), "incident_type": "timeout"}


def synth_auth(i: int) -> dict:
    samples = [
        "ERROR Authorization: Permission denied for user=hdfs on path=/user/data",
        "WARN Security: Unauthorized access attempt, token expired",
        "ERROR ACL: Access denied while opening file /user/hive/warehouse",
        "WARN Kerberos: Authentication failed, invalid ticket",
        "ERROR Permission: Forbidden operation for user=guest",
    ]
    return {"source": "security", "log": random.choice(samples), "incident_type": "auth"}


def synth_db_error(i: int) -> dict:
    samples = [
        "ERROR DataNode: IOException while writing block, disk error",
        "ERROR BlockReceiver: Failed to receive block due to connection reset",
        "WARN DataNode: Failed to transfer block, connection refused",
        "ERROR FSVolume: Disk I/O error while reading block file",
        "ERROR DataXceiver: Data transfer error on block stream",
    ]
    return {"source": "datanode", "log": random.choice(samples), "incident_type": "db_error"}


def main():
    df = pd.read_csv(RAW_PATH)

    base_text = df["EventTemplate"].fillna(df["Content"]) if "EventTemplate" in df.columns else df["Content"]
    labels = base_text.apply(label_from_text)

    out = pd.DataFrame({
        "log_id": range(len(df)),
        "source": df.get("Component", "hdfs").fillna("hdfs"),
        "log": df["Content"].astype(str),
        "incident_type": labels.astype(str),
    })

    out["incident_type"] = out["incident_type"].where(out["incident_type"].isin(ALLOWED), "unknown")

    # ---- Augmentation to ensure at least 4 classes and balance ----
    # Target minimums (tune as needed)
    target = {"timeout": 200, "auth": 200, "db_error": 200}

    counts = out["incident_type"].value_counts().to_dict()

    rows = []
    next_id = len(out)

    # Add missing/rare classes
    need_timeout = max(0, target["timeout"] - counts.get("timeout", 0))
    need_auth = max(0, target["auth"] - counts.get("auth", 0))
    need_db = max(0, target["db_error"] - counts.get("db_error", 0))

    for i in range(need_timeout):
        r = synth_timeout(i)
        r["log_id"] = next_id; next_id += 1
        rows.append(r)

    for i in range(need_auth):
        r = synth_auth(i)
        r["log_id"] = next_id; next_id += 1
        rows.append(r)

    for i in range(need_db):
        r = synth_db_error(i)
        r["log_id"] = next_id; next_id += 1
        rows.append(r)

    if rows:
        out = pd.concat([out, pd.DataFrame(rows)], ignore_index=True)

    # Keep dataset around ~2000-2300 rows; no need to shrink unless you want exactly 2000
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)

    vc = out["incident_type"].value_counts()
    print(f"Saved {len(out)} rows → {OUT_PATH}")
    print("Class distribution:")
    print(vc.to_string())


if __name__ == "__main__":
    main()

