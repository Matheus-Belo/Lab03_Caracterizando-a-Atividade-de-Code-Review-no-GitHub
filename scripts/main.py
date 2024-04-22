from scripts.metricas import get_repo_data, get_pr_data, summarized_data
from scripts.dados import salvarcsv, ler_csv, merge

REPOSITORIOS = 200
PAGINA = 1

def main():
    repo_results = ler_csv("repositorios.csv")
    if repo_results is None or len(repo_results) < REPOSITORIOS:
        repo_results = get_repo_data(
            num_repos=REPOSITORIOS, per_page=PAGINA)
        salvarcsv(repo_results, "repositorios.csv")

    pr_results = ler_csv("pullRequests.csv")
    if pr_results is None or len(repo_results) < REPOSITORIOS * 100:
        pr_results = get_pr_data(repos=repo_results, results=pr_results)
        salvarcsv(pr_results, "pullRequests.csv")

    repo_results = ler_csv("repositorios.csv")
    data_results = merge(repo_results, pr_results,
                              column_join='Repositório')
    if data_results is not None:
        salvarcsv(data_results, "data.csv")
    
    data = summarized_data(data_results)
    if data is not None:
        salvarcsv(data, "dadosProcessados.csv")


if __name__ == "__main__":
    main()