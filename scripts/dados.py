import os
from typing import Union
import pandas as pd

ROOT_PATH = os.getcwd().replace('\\', '/')
SAVE_PATH = ROOT_PATH + '/scripts/dataset/csv/'


def salvarcsv(results: Union[list, pd.DataFrame], filename: str):
    try:
        if isinstance(results, list):
            if len(results) == 0:
                return
            df = pd.DataFrame(results)
        elif isinstance(results, pd.DataFrame):
            df = results

        df.to_csv(SAVE_PATH + filename, index=False)
        print(f"Resultados salvos em '{filename}'")

    except Exception as e:
        print(f"Erro ao salvar")


def ler_csv(filename: str, type='list', columns: list = None):
    try:
        df = pd.read_csv(SAVE_PATH + filename)
        print(df.head())
        print()

        if type == 'list':
            df = df[columns] if columns else df
            results = df.to_dict('records')
            if len(results) > 0:
                return results
        
        return df
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado")


def merge(repo_df: list, pr_df: list, column_join: str):
    try:
        repo_df = pd.DataFrame(repo_df)
        pr_df = pd.DataFrame(pr_df)

        combined_data = pd.merge(repo_df, pr_df, on=column_join, how='inner')
        return combined_data
    except Exception as e:
        print(f"Erro: Não foi possível fazer o merge {e}")