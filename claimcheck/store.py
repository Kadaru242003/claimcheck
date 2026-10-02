"""Checkpoints. One line per finished run in results/runs.jsonl, written and flushed to
disk the moment the run finishes. Transcripts go to results/transcripts/.

A run is "done" only if its key (model | condition | task | sample | prompt version) is in
runs.jsonl. A run cut off midway (daily limit, network trouble, Ctrl+C) is not written,
so it simply runs again later. Nothing finished is ever repeated.
"""
import json, os, re
from pathlib import Path

class Store:
    def __init__(self, root: Path):
        self.root = Path(root)
        (self.root / "transcripts").mkdir(parents=True, exist_ok=True)
        self.runs_path = self.root / "runs.jsonl"
        self.runs_path.touch(exist_ok=True)

    def done_keys(self) -> set[str]:
        return {r["key"] for r in self.runs()}

    def runs(self) -> list[dict]:
        out = []
        for line in self.runs_path.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass  # a line cut off by a crash is ignored; that run reruns
        return out

    def save(self, record: dict, transcript: list):
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", record["key"])
        tpath = self.root / "transcripts" / f"{safe}.json"
        tpath.write_text(json.dumps({"record": record, "messages": transcript}, indent=1))
        record = dict(record, transcript=str(tpath.relative_to(self.root)))
        with open(self.runs_path, "a") as f:
            f.write(json.dumps(record) + "\n")
            f.flush(); os.fsync(f.fileno())
