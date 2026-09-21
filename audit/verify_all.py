"""Audit published text certificates and check or rebuild their hash manifest."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='require the committed manifest to match')
    args = parser.parse_args()
    checker = ROOT / 'audit/independent_check.py'
    upstream = json.loads((ROOT / 'audit/upstream.json').read_text())
    if digest(checker) != upstream['sha256']:
        raise SystemExit('Auditor differs from pinned upstream source')
    records = []
    for cover in sorted((ROOT / 'results').rglob('cover.txt')):
        directory = cover.parent
        files = [directory / f for f in ['cover.txt', 'planners.txt', 'summary.json']]
        if not all(f.is_file() for f in files):
            raise SystemExit(f'Incomplete certificate directory: {directory}')
        run = subprocess.run([sys.executable, str(checker), str(directory)],capture_output=True,text=True)
        if run.returncode:
            print(run.stdout + run.stderr, file=sys.stderr)
            return run.returncode
        summary = json.loads(files[-1].read_text())
        records.append(dict(path=directory.relative_to(ROOT).as_posix(),
            audit='passed', sha256={p.name:digest(p) for p in files},
            complex=summary['complex'], n_domains=summary['n_domains'],
            domain_sizes=summary.get('domain_sizes', [len(d) for d in summary['domains']]),
            chain_lengths=summary.get('chain_lengths'), params=summary.get('params'),
            reported_search_elapsed_s=summary.get('elapsed_s'),
            generating_commit=summary.get('provenance',{}).get('git_commit')))
        print(f'PASS {directory.relative_to(ROOT)}')
    if not records:
        raise SystemExit('No text certificates found')
    manifest=dict(schema_version=1, auditor=upstream,
        scope='Checks saved certificates, not GPU performance, search replay, novelty or optimality. Historical generating commits remain null when unrecorded.',
        certificates=records)
    destination=ROOT/'audit/manifest.json'
    if args.check:
        if not destination.exists() or json.loads(destination.read_text()) != manifest:
            raise SystemExit('Manifest differs; audit and regenerate with python3 audit/verify_all.py')
    else:
        destination.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    print(f'All {len(records)} certificates passed; manifest {"checked" if args.check else "written"}.')
    return 0


if __name__=='__main__':
    sys.exit(main())
