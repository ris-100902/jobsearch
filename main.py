from pathlib import Path

from app.collectors import sources
from config.db import Db

import argparse
import yaml

ROOT = Path(__file__).resolve().parent

def load_config(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"No config at path {Path}")
    return yaml.safe_load(path.read_text())

def job_scan(config: dict, db: Db) -> dict:
    all_jobs: list[dict] = []
    errors: list[str] = []
    for entry in config.get('companies'):
        jobs, err = sources.fetch_company(entry)
        if err:
            errors.append(f"{entry['name']}: {err}")
        else:
            all_jobs.extend(jobs)
    
    db.insert_jobs(all_jobs)
    return {'jobs': all_jobs, 'errors': errors}

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="jobsearch")
    parser.add_argument("--config", default=str(ROOT/"config/config.jobsearch.yaml"))

    subParser = parser.add_subparsers(dest="cmd", required=True)
    subParser.add_parser("scan")

    args = parser.parse_args(argv)
    config = load_config(Path(args.config))

    db = Db()

    if args.cmd == "scan":
        job_scan(config, db)


if __name__=="__main__":
    main()