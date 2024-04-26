import csv
import requests
import os
from datetime import datetime, timedelta
import time

MAX_RETRIES = 2
WAIT_TIME = 300  # 5 min
MAX_PRS_TO_WRITE = 101  # Número máximo de PRs a serem escritos no arquivo de saída

def get_token():
    with open("./scripts/token.txt", "r") as token_file:
        return token_file.read().strip()

def run_query_with_retry(query, headers):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
            request.raise_for_status()
            return request.json()
        except requests.exceptions.RequestException as e:
            print(f"Error while making request: {e}")
            retries += 1
            print(f"Retrying... Attempt {retries} of {MAX_RETRIES}")
            time.sleep(WAIT_TIME)
    print("Max retries reached. Unable to fetch data.")
    return None

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
    cursor = ""
    while True:
        query = query_template.format(username=username, repo_name=repo_name, cursor=f"after: \"{cursor}\"" if cursor else "")
        result = run_query_with_retry(query, headers)

        if result is None:
            return None

        repository_data = result.get("data", {}).get("repository", {})
        if repository_data is None:
            return None

        prs_data = repository_data.get("pullRequests", {}).get("nodes")
        if not prs_data:
            break

        page_info = repository_data.get("pullRequests", {}).get("pageInfo", {})
        for pr in prs_data:
            if pr is None:
                continue

            # Tratar campos vazios ou nulos
            title = pr.get('title', 'null')
            bodyText = pr.get('bodyText', 'null')
            mergedAt = pr.get('mergedAt', None)
            closedAt = pr.get('closedAt', None)

            # Calcular tempo para mesclar ou fechar, se aplicável
            time_to_merge_or_close = 0
            if mergedAt and closedAt:
                try:
                    start_time = datetime.strptime(pr.get('createdAt'), "%Y-%m-%dT%H:%M:%SZ")
                    end_time = datetime.strptime(mergedAt, "%Y-%m-%dT%H:%M:%SZ") if pr.get('merged') else datetime.strptime(closedAt, "%Y-%m-%dT%H:%M:%SZ")
                    time_to_merge_or_close = (end_time - start_time).total_seconds()
                except ValueError as e:
                    print(f"Error calculating time to merge or close for PR {pr.get('number')}: {e}")

            pr_info = {
                'Number': pr.get('number', ''),
                'Title': title,
                'Body': len(bodyText), 
                'Closed': pr.get('closed', False),
                'Merged': pr.get('merged', False),
                'MergedAt': mergedAt,
                'ClosedAt': closedAt,
                'ReviewComments': pr.get('reviews', {}).get('totalCount', 0),
                'Participants': pr.get('participants', {}).get('totalCount', 0),
                'Comments': pr.get('comments', {}).get('totalCount', 0),
                'Files': pr.get('files', {}).get('totalCount', 0) if pr.get('files') is not None else 0,
                'Additions': pr.get('additions', 0),
                'Deletions': pr.get('deletions', 0),
                'Modifications': pr.get('additions', 0) + pr.get('deletions', 0),  
                'TimeToMergeOrClose': time_to_merge_or_close, 
            }
            prs_info.append(pr_info)

        if not page_info.get("hasNextPage"):
            break
        cursor = page_info["endCursor"]

    return prs_info


def write_prs_to_csv(repo_name, prs_info, output_filename):
    if not os.path.exists(output_filename):  # Check if the file already exists
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Number', 'Title', 'Body', 'Closed', 'Merged', 'MergedAt', 'ClosedAt', 'ReviewComments', 'Participants', 'Comments', 'Files', 'Additions', 'Deletions', 'Modifications', 'TimeToMergeOrClose']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for pr in prs_info:
                writer.writerow(pr)
        print(f'Results written to {output_filename}')
    else:
        print(f"File '{output_filename}' already exists. Skipping writing results.")

def analyze_repositories(csv_filename, token):
    try:
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                repo_name = row.get('Nome', '')
                repo_url = row.get('url', '')

                if not repo_name or not repo_url:
                    print("Missing repository name or URL.")
                    continue

                output_filename = f"./scripts/dataset/pullr/{repo_name}_prs.csv"
                if os.path.exists(output_filename):
                    print(f"Skipping repository {repo_name}. Results already exist.")
                    continue

                print(f'Analyzing repository: {repo_name}')

                prs_info = get_prs_info(repo_url, token)
                if prs_info:
                    write_prs_to_csv(repo_name, prs_info, output_filename)
    except Exception as e:
        print(f"An error occurred: {e}")

print("SLEEP")
time.sleep(10)

token = get_token()

# repo_name = "linux"
# repo_url = "https://github.com/torvalds/linux"
# print(f'Analyzing repository: {repo_name}')
# prs_info = get_prs_info(repo_url, token)
# if prs_info:
#     write_prs_to_csv(repo_name, prs_info)

analyze_repositories('./scripts/dataset/repo.csv', token)