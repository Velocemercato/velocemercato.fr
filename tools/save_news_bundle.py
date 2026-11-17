"""Save generated news against current main without repeating API generation.

Only already-staged files are captured. Concurrent JSON-list additions survive;
conflicting edits to other files stop explicitly instead of reporting success.
"""
import argparse
import json
import subprocess
import time


def git(*args, check=True):
    return subprocess.run(['git', *args], check=check, capture_output=True)


def read(ref, path):
    r = git('show', f'{ref}:{path}', check=False)
    return r.stdout if r.returncode == 0 else None


def identity(row):
    if isinstance(row, dict) and row.get('id') is not None:
        return 'id:' + str(row['id'])
    return json.dumps(row, sort_keys=True, ensure_ascii=False)


def reconcile(base, generated, remote, path):
    if remote == base or remote == generated:
        return generated
    if generated == base:
        return remote
    if path.endswith('.json'):
        old = json.loads(base or b'[]')
        new = json.loads(generated)
        current = json.loads(remote or b'[]')
        if all(isinstance(x, list) for x in (old, new, current)):
            baseline = {identity(row) for row in old}
            seen = {identity(row) for row in new}
            result = list(new)
            for row in current:
                key = identity(row)
                if key not in baseline and key not in seen:
                    result.append(row)
                    seen.add(key)
            return (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode()
    if path.endswith('robot-log.txt'):
        return generated
    raise RuntimeError(f'Concurrent edit needs review: {path}')


def main():
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument('--message', required=True)
    args = p.parse_args()
    names = git('diff', '--cached', '--name-only', '--diff-filter=ACM', '-z').stdout.decode().split('\0')
    names = [name for name in names if name]
    if not names:
        print('No generated changes to save.')
        return
    if git('diff', '--cached', '--name-only', '--diff-filter=D').stdout.strip():
        raise RuntimeError('Unexpected staged deletion: review required')
    snapshots = {name: (read('HEAD', name), read('', name)) for name in names}
    for attempt in range(5):
        git('fetch', '--quiet', 'origin', 'main')
        remote = {name: read('origin/main', name) for name in names}
        resolved = {name: reconcile(base, data, remote[name], name)
                    for name, (base, data) in snapshots.items()}
        git('reset', '--hard', '--quiet', 'origin/main')
        for name, data in resolved.items():
            dest = Path(name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        git('add', '--', *names)
        if git('diff', '--cached', '--quiet', check=False).returncode == 0:
            print('Generated changes are already on main.')
            return
        git('config', 'user.name', 'github-actions[bot]')
        git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
        git('commit', '--quiet', '-m', args.message)
        r = git('push', '--quiet', 'origin', 'HEAD:main', check=False)
        if r.returncode == 0:
            print('Generated news saved on main: ' + git('rev-parse', 'HEAD').stdout.decode().strip())
            return
        time.sleep(2 + attempt)
    raise RuntimeError('Unable to save generated news after five attempts; no publication claimed')


if __name__ == '__main__':
    main()
