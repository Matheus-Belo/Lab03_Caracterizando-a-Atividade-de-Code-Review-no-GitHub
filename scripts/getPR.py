import csv
import os
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv("key")
url = 'https://api.github.com/graphql'

headers = {'Authorization': 'Bearer %s' % API_KEY}


def load_repositories_from_csv(csv_file):
    repositories = []
    with open(csv_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            repositories.append(row['nameWithOwner'])
    return repositories

def get_pull_requests(repository_name):

    query = """
    query($repositoryName: String!) {
      repository(name: $repositoryName) {
        nameWithOwner
        pullRequests(first: 10) {
          nodes {
            title
            createdAt
            author {
              login
            }
            comments {
              totalCount
            }
            reviews {
              totalCount
            }
          }
        }
      }
    }
    """
    
    response = requests.post(url, json={'query': query, 'variables': {'repositoryName': repository_name}}, headers=headers)
    data = response.json()
    
    pull_requests = []
    if 'data' in data and 'repository' in data['data']:
        for pr_node in data['data']['repository']['pullRequests']['nodes']:
            pr_info = {
                'title': pr_node['title'],
                'createdAt': pr_node['createdAt'],
                'author': pr_node['author']['login'],
                'commentsCount': pr_node['comments']['totalCount'],
                'reviewsCount': pr_node['reviews']['totalCount']
            }
            pull_requests.append(pr_info)
    else:
        print("Repositório não encontrado ou erro na resposta.")
    
    return pull_requests

# Função principal para obter detalhes dos pull requests para todos os repositórios no CSV
def get_pull_requests_for_all_repositories(csv_file):
    repositories = load_repositories_from_csv(csv_file)
    repositories_with_pull_requests = []
    for repo_name in repositories:
        pull_requests = get_pull_requests(repo_name)
        repositories_with_pull_requests.append({'nameWithOwner': repo_name, 'pullRequests': pull_requests})
    return repositories_with_pull_requests

if __name__ == "__main__":
    csv_file = 'repositories.csv'  # Substitua pelo nome do seu arquivo CSV
    repositories_with_pull_requests = get_pull_requests_for_all_repositories(csv_file)
    print(repositories_with_pull_requests)