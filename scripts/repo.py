import json
import os
import requests
import csv

def get_token():
    with open("./scripts/github_token.txt", "r") as token_file:
        return token_file.read().strip()

API_URL = 'https://api.github.com/graphql'

def run_query(query, headers):
    request = requests.post(API_URL, json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

def get_repositories_with_prs(chave, after_cursor=None):
    headers = {'Authorization': f'Bearer {chave}'}
    after = f', after: "{after_cursor}"' if after_cursor else ''
    query = f"""
        query {{
            search(query: "is:public stars:>1", type: REPOSITORY, first: 10{after}) {{
                nodes {{
                    ... on Repository {{
                        name
                        url
                        pullRequests(states: MERGED, first: 100) {{
                            totalCount
                        }}
                    }}
                }}
                pageInfo {{
                    endCursor
                    hasNextPage
                }}
            }}
        }}
        """
    result = run_query(query, headers)
    return result.get("data", {}).get("search", {}).get("nodes", []), result.get("data", {}).get("search", {}).get("pageInfo", {}).get("endCursor")

def write_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Nome', 'QuantidadePRsMerged', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for repo in data:
            writer.writerow({'Nome': repo.get('name', ''), 'QuantidadePRsMerged': repo.get('pullRequests', {}).get('totalCount', 0), 'url': repo.get('url', '')})

def main():
    chave = get_token()
    repositories = []
    after_cursor = None
    while len(repositories) < 200:  
        repos, after_cursor = get_repositories_with_prs(chave, after_cursor)
        repositories += repos
        if not after_cursor:
            break
    output_filename = './scripts/dataset/repo.csv'
    write_to_csv(repositories[:200], output_filename)  
    print(f'Results written to {output_filename}')

if __name__ == "__main__":
    main()
