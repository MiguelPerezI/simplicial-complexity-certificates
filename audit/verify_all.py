"""Audit published text certificates and check or rebuild their hash manifest.

results/   every certificate is re-checked by the pinned independent auditor.
internal/  certificates on complexes the auditor cannot rebuild yet; only their
           search-side verification flags and file hashes are checked.

A certificate file may be stored xz-compressed (cover.txt.xz, ...); it is then
decompressed into a temporary directory for the audit and hashed compressed.
"""
import argparse
import hashlib
import json
import lzma
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['cover.txt', 'planners.txt', 'summary.json']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def certificate_files(directory):
    files = []
    for name in NAMES:
        plain, packed = directory / name, directory / (name + '.xz')
        if plain.is_file():
            files.append(plain)
        elif packed.is_file():
            files.append(packed)
        else:
            raise SystemExit(f'Incomplete certificate directory: {directory}')
    return files


def read_text(path):
    return lzma.decompress(path.read_bytes()).decode() if path.suffix == '.xz' else path.read_text()


def audit(checker, directory, files):
    if not any(f.suffix == '.xz' for f in files):
        return subprocess.run([sys.executable, str(checker), str(directory)], capture_output=True, text=True)
    with tempfile.TemporaryDirectory() as tmp:
        for f in files:
            (Path(tmp) / f.name.removesuffix('.xz')).write_text(read_text(f))
        return subprocess.run([sys.executable, str(checker), tmp], capture_output=True, text=True)


def record(directory, files, status):
    summary = json.loads(read_text(files[-1]))
    return dict(path=directory.relative_to(ROOT).as_posix(),
        audit=status, sha256={p.name:digest(p) for p in files},
        complex=summary['complex'], n_domains=summary['n_domains'],
        domain_sizes=summary.get('domain_sizes', [len(d) for d in summary['domains']]),
        chain_lengths=summary.get('chain_lengths'), params=summary.get('params'),
        reported_search_elapsed_s=summary.get('elapsed_s'),
        generating_commit=summary.get('provenance',{}).get('git_commit'))


def directories(top):
    return sorted({cover.parent for cover in (ROOT / top).rglob('cover.txt*')})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='require the committed manifest to match')
    args = parser.parse_args()
    checker = ROOT / 'audit/independent_check.py'
    upstream = json.loads((ROOT / 'audit/upstream.json').read_text())
    if digest(checker) != upstream['sha256']:
        raise SystemExit('Auditor differs from pinned upstream source')
    records = []
    for directory in directories('results'):
        files = certificate_files(directory)
        run = audit(checker, directory, files)
        if run.returncode:
            print(run.stdout + run.stderr, file=sys.stderr)
            return run.returncode
        records.append(record(directory, files, 'passed'))
        print(f'PASS {directory.relative_to(ROOT)}')
    for directory in directories('internal'):
        files = certificate_files(directory)
        summary = json.loads(read_text(files[-1]))
        if not (summary.get('all_domains_verified') and summary.get('n_verified') == summary['n_domains']
                and summary.get('sc_strict_bound') == summary['n_domains'] - 1):
            raise SystemExit(f'Internal certificate not verified by its search: {directory}')
        records.append(record(directory, files, 'internal verifier only'))
        print(f'INTERNAL {directory.relative_to(ROOT)}')
    if not records:
        raise SystemExit('No text certificates found')
    manifest=dict(schema_version=1, auditor=upstream,
        scope='Checks saved certificates, not GPU performance, search replay, novelty or optimality. '
              'Entries marked "internal verifier only" are hashed but not re-checked by the independent auditor. '
              'Historical generating commits remain null when unrecorded.',
        certificates=records)
    destination=ROOT/'audit/manifest.json'
    if args.check:
        if not destination.exists() or json.loads(destination.read_text()) != manifest:
            raise SystemExit('Manifest differs; audit and regenerate with python3 audit/verify_all.py')
    else:
        destination.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    passed = sum(r['audit'] == 'passed' for r in records)
    print(f'{passed} certificates passed the independent audit, {len(records) - passed} internal; '
          f'manifest {"checked" if args.check else "written"}.')
    return 0


if __name__=='__main__':
    sys.exit(main())
