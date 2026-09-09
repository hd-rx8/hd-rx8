"""Public GitHub stats. Optional GH_TOKEN enables 12-month contribution stats."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
USER = json.loads((ROOT / 'profile.json').read_text(encoding='utf-8-sig'))['username']
TOKEN = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')

def request(path, data=None):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'profile-readme'}
    if TOKEN:
        headers['Authorization'] = f'Bearer {TOKEN}'
    body = json.dumps(data).encode() if data else None
    if body:
        headers['Content-Type'] = 'application/json'
    with urlopen(Request('https://api.github.com' + path, data=body, headers=headers), timeout=30) as response:
        return json.load(response)

def collect():
    user = request(f'/users/{USER}')
    repos = []
    page = 1
    while True:
        batch = request(f'/users/{USER}/repos?type=owner&per_page=100&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    result = {'repos': user['public_repos'], 'followers': user['followers'],
              'stars': sum(repo['stargazers_count'] for repo in repos),
              'updated_at': datetime.now(timezone.utc).isoformat()}
    if TOKEN:
        query = '''query($login:String!){user(login:$login){contributionsCollection{
          totalCommitContributions contributionCalendar{totalContributions}
        }}}'''
        payload = request('/graphql', {'query': query, 'variables': {'login': USER}})
        if payload.get('errors'):
            raise RuntimeError('GitHub GraphQL: ' + str(payload['errors']))
        contributions = payload['data']['user']['contributionsCollection']
        result['commits'] = contributions['totalCommitContributions']
        result['contributions'] = contributions['contributionCalendar']['totalContributions']
    else:
        print('No GH_TOKEN: 12-month commits and contributions remain unavailable.')
    (ROOT / 'stats.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    collect()
