from dotenv import load_dotenv
import requests
import csv
import os
import tqdm

load_dotenv()

API_KEY = os.getenv("key")
url = 'https://api.github.com/graphql'

headers = {'Authorization': 'Bearer %s' % API_KEY}

query = """
query($cursor: String) {
  search(query: "language:java stars:>0", type: REPOSITORY, first: 100, after: $cursor) {
    nodes {
      ... on Repository {
        nameWithOwner
        createdAt
        stargazerCount
        pullRequests {
            totalCount
            }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""

def get_repositories(cursor=None):
    response = requests.post(url, json={'query': query, 'variables': {'cursor': cursor}}, headers=headers)
    return response.json()

def get_all_repos():
    cursor = None
    repos = []
    while True:
        response_data = get_repositories(cursor)
        
        # Verifica se a solicitação foi bem-sucedida
        if 'errors' in response_data:
            print("Erro na solicitação:", response_data['errors'])
            break
        
        # Verifica se a chave 'data' está presente na resposta
        if 'data' in response_data:
            for node in response_data['data']['search']['nodes']:
                pull_requests_count = node['pullRequests']['totalCount']
                if pull_requests_count > 100:
                    repository_info = {
                        'nameWithOwner': node['nameWithOwner'],
                        'createdAt' : node['createdAt'],
                        'stargazerCount': node['stargazerCount'],
                        'pullRequests': pull_requests_count,
                    }
                    repos.append(repository_info)

            pageInfo = response_data['data']['search']['pageInfo']
            hasNextPage = pageInfo['hasNextPage']
            if not hasNextPage or len(repos) >= 100:
                break
            cursor = pageInfo['endCursor']
        else:
            print("Resposta inesperada:", response_data)
            break

    return repos

def write_to_csv(repos):
    with open('./scripts/dataset/csv/repositorios.csv', 'w', newline='') as csvfile:
        fieldnames = ['nameWithOwner', 'createdAt', 'stargazerCount', 'pullRequests']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for repo in repos:
            writer.writerow(repo)

def main():
    repos = get_all_repos()
    write_to_csv(repos)

if __name__ == "__main__":
    main()