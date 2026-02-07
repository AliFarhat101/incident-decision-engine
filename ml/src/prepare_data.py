import argparse
import pandas as pd
import random
from pathlib import Path

RAW_PATH = Path("data/raw/HDFS_2k.log_structured.csv")

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


# ---- Synthetic generators with variability ----
NODES = ["dn-01", "dn-02", "dn-03", "nn-01", "nn-02"]
IPS = ["10.0.1.12", "10.0.1.20", "10.0.2.7", "10.0.3.9"]
USERS = ["hdfs", "spark", "hive", "guest", "service"]
PATHS = ["/user/data", "/tmp", "/user/hive/warehouse", "/var/log/hadoop", "/data/blocks"]
BLOCKS = ["blk_1073741825", "blk_1073741826", "blk_1073741827", "blk_1073741828"]


def synth_timeout() -> str:
    patterns = [
        "WARN IPC: RPC connection timed out to {node} after {ms} ms, retry={r}",
        "ERROR DFSClient: Read timed out while fetching block {blk} from {ip}, attempt {r}",
        "WARN LeaseRenewer: Lease renewal timed out for user={user}, retry={r}",
        "ERROR DataStreamer: Pipeline recovery failed due to timeout at {node}",
        "WARN Client: Operation slow (> {ms} ms) contacting NameNode {node}",
    ]
    return random.choice(patterns).format(
        node=random.choice(NODES),
        ip=random.choice(IPS),
        blk=random.choice(BLOCKS),
        user=random.choice(USERS),
        ms=random.choice([5000, 10000, 20000, 30000, 60000]),
        r=random.choice([1, 2, 3, 4]),
    )


def synth_auth() -> str:
    patterns = [
        "ERROR Authorization: Permission denied for user={user} on path={path}",
        "WARN Security: Unauthorized access attempt user={user}, token expired",
        "ERROR ACL: Access denied while opening file {path} for user={user}",
        "WARN Kerberos: Authentication failed for {user}, invalid ticket on {node}",
        "ERROR Permission: Forbidden operation for user={user} on {node}",
    ]
    return random.choice(patterns).format(
        user=random.choice(USERS),
        path=random.choice(PATHS),
        node=random.choice(NODES),
    )


def synth_db_error() -> str:
    patterns = [
        "ERROR DataNode: IOException while writing block {blk} to disk on {node}",
        "ERROR FSVolume: Disk I/O error while reading {blk} under {path}",
        "WARN DataXceiver: Failed to transfer {blk} to {ip}: connection refused",
        "ERROR BlockReceiver: Failed to receive {blk} due to connection reset by peer",
        "ERROR Storage: Corrupt block file detected for {blk} on {node}",
    ]
    return random.choice(patterns).format(
        blk=random.choice(BLOCKS),
        node=random.choice(NODES),
        ip=random.choice(IPS),
        path=random.choice(PATHS),
    )


def synth_config() -> str:
    patterns = [
        "ERROR Config: missing key {key} in configuration file",
        "ERROR NameNode: invalid config value for {key}, refusing to start",
        "WARN Config: property {key} not found, using default",
        "ERROR Startup: failed to load configuration from {path}",
        "WARN NameNode: configuration mismatch detected on {node}",
    ]
    return random.choice(patterns).format(
        key=random.choice(["fs.defaultFS", "dfs.replication", "hadoop.security.authentication", "dfs.blocksize"]),
        path=random.choice(["/etc/hadoop/core-site.xml", "/etc/hadoop/hdfs-site.xml", "/etc/hadoop/yarn-site.xml"]),
        node=random.choice(NODES),
    )


def build_base_df() -> pd.DataFrame:
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
    return out


def augment(out: pd.DataFrame, target: dict) -> pd.DataFrame:
    counts = out["incident_type"].value_counts().to_dict()
    rows = []
    next_id = int(out["log_id"].max()) + 1 if len(out) else 0

    def add_rows(label: str, n: int, gen_fn, source: str):
        nonlocal next_id
        for _ in range(n):
            rows.append({
                "log_id": next_id,
                "source": source,
                "log": gen_fn(),
                "incident_type": label,
            })
            next_id += 1

    need_timeout = max(0, target.get("timeout", 0) - counts.get("timeout", 0))
    need_auth = max(0, target.get("auth", 0) - counts.get("auth", 0))
    need_db = max(0, target.get("db_error", 0) - counts.get("db_error", 0))
    need_config = max(0, target.get("config", 0) - counts.get("config", 0))

    add_rows("timeout", need_timeout, synth_timeout, "hdfs")
    add_rows("auth", need_auth, synth_auth, "security")
    add_rows("db_error", need_db, synth_db_error, "datanode")
    add_rows("config", need_config, synth_config, "namenode")

    if rows:
        out = pd.concat([out, pd.DataFrame(rows)], ignore_index=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", choices=["v1", "v2"], default="v1")
    args = ap.parse_args()

    out = build_base_df()

    # v1: minimal augmentation to ensure coverage
    if args.version == "v1":
        target = {"timeout": 200, "auth": 200, "db_error": 200, "config": 224}
        out = augment(out, target)
        out_path = Path("data/processed/incidents_v1.csv")

    # v2: stronger augmentation (+200–500 variants per class) for better balance & robustness
    else:
        # Aim for ~400 each for minority classes (adds a few hundred new variants)
        target = {"timeout": 450, "auth": 450, "db_error": 450, "config": 450}
        out = augment(out, target)
        out_path = Path("data/processed/incidents_v2.csv")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)

    vc = out["incident_type"].value_counts()
    print(f"Saved {len(out)} rows → {out_path}")
    print("Class distribution:")
    print(vc.to_string())


if __name__ == "__main__":
    main()

