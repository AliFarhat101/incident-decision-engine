import pandas as pd
import re
from pathlib import Path

RAW_PATH = Path("data/raw/HDFS_2k.log_structured.csv")
OUT_PATH = Path("data/processed/incidents_v1.csv")


def map_incident(row):
    text = str(row["Content"]).lower()
    component = str(row["Component"]).lower()

    if re.search(r"(timeout|timed out|retry)", text):
        return "timeout"

    if any(k in component for k in ["datanode", "block", "disk"]):
        return "db_error"

    if re.search(r"(config|missing|namenode)", text):
        return "config"

    if re.search(r"(permission|access denied|unauthorized)", text):
        return "auth"

    return "unknown"


def main():
    df = pd.read_csv(RAW_PATH)

    out = pd.DataFrame({
        "log_id": range(len(df)),
        "source": df["Component"].fillna("hdfs"),
        "log": df["Content"],
        "incident_type": df.apply(map_incident, axis=1),
    })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_PATH, index=False)

    print(f"Saved {len(out)} rows → {OUT_PATH}")


if __name__ == "__main__":
    main()

