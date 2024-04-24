import csv
import requests
import os
from datetime import datetime, timedelta

def get_token():
    with open("./scripts/github_token.txt", "r") as token_file:
        return token_file.read().strip()
    
def run_query(query, headers):
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f"Query failed to run by returning code of {request.status_code}. {query}")

def get_prs_info(repo_url, token):
    _, username, repo_name = repo_url.rstrip('/').split('/')[-3:]

    query_template = """
    query {{
        repository(owner:"{username}", name:"{repo_name}") {{
            pullRequests(first: 20, states: [CLOSED, MERGED], orderBy: {{field: UPDATED_AT, direction: DESC}}, {cursor}) {{
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    number
                    title
                    bodyText
                    closed
                    merged
                    createdAt
                    mergedAt
                    closedAt
                    reviews {{
                        totalCount
                    }}
                    participants {{
                        totalCount
                    }}
                    comments {{
                        totalCount
                    }}
                    files {{
                        totalCount
                    }}
                    additions
                    deletions
                    commits {{
                        totalCount
                    }}
                }}
            }}
        }}
    }}
    """

    headers = {'Authorization': f'Bearer {token}'}

    prs_info = []
    current_time = datetime.utcnow()
    cursor = ""
    while len(prs_info) < 100:
        query = query_template.format(username=username, repo_name=repo_name, cursor= f"after: \"{cursor}\"" if cursor else "")
        result = run_query(query, headers)
        prs_data = result.get("data", {}).get("repository", {}).get("pullRequests", {}).get("nodes", [])
        page_info = result.get("data", {}).get("repository", {}).get("pullRequests", {}).get("pageInfo", {})
        
        for pr in prs_data:
            pr_created_at = datetime.strptime(pr['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
            if 'closedAt' in pr:
                pr_closed_at = datetime.strptime(pr['closedAt'], "%Y-%m-%dT%H:%M:%SZ")
                time_diff = pr_closed_at - pr_created_at
            elif 'mergedAt' in pr:
                pr_merged_at = datetime.strptime(pr['mergedAt'], "%Y-%m-%dT%H:%M:%SZ")
                time_diff = pr_merged_at - pr_created_at
            else:
                continue
            
            if pr['reviews']['totalCount'] != 0 and time_diff >= timedelta(hours=1):
                pr_info = {
                    'Number': pr['number'],
                    'Title': pr['title'],
                    'Body': len(pr['bodyText']), 
                    'Closed': pr['closed'],
                    'Merged': pr['merged'],
                    'MergedAt': pr.get('mergedAt', ''),
                    'ClosedAt': pr.get('closedAt', ''),
                    'ReviewComments': pr['reviews']['totalCount'],
                    'Participants': pr['participants']['totalCount'],
                    'Comments': pr['comments']['totalCount'],
                    'Files': pr['files']['totalCount'], 
                    'Additions': pr['additions'],
                    'Deletions': pr['deletions'],
                    'Modifications': pr['additions'] + pr['deletions'],  
                    'TimeToAnalysis': (datetime.utcnow() - pr_created_at).total_seconds(), 
                }
                prs_info.append(pr_info)
                
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info["endCursor"]

    return prs_info[:100]  

def write_prs_to_csv(repo_name, prs_info):
    output_dir = './scripts/dataset/prs/'
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f'{repo_name}_prs.csv')

    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Number', 'Title', 'Body', 'Closed', 'Merged', 'MergedAt', 'ClosedAt', 'ReviewComments', 'Participants', 'Comments', 'Files', 'Additions', 'Deletions', 'Modifications', 'TimeToAnalysis']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for pr in prs_info:
            writer.writerow(pr)

    print(f'Results written to {output_filename}')

def analyze_repositories(csv_filename, token):
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repo_name = row['Nome']
            repo_url = row['url']

            print(f'Analyzing repository: {repo_name}')

            prs_info = get_prs_info(repo_url, token)
            write_prs_to_csv(repo_name, prs_info)

token = get_token()
analyze_repositories('./scripts/dataset/repo.csv', token)