import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def filtrar_dados(df):
    df = df[(df['Merged'] == True) | (df['Closed'] == True)]
    return df

diretorio_dados = "./scripts/dataset/pullr/"
diretorio_graficos = "./scripts/dataset/graficos/"

dfs = []

for arquivo in os.listdir(diretorio_dados):
    if arquivo.endswith(".csv") and arquivo not in ['repo.csv', 'linux_prs.csv']:
        df = pd.read_csv(os.path.join(diretorio_dados, arquivo))
        if not df.empty and 'TimeToMergeOrClose' in df.columns:
            df = filtrar_dados(df)
            dfs.append(df)
        else:
            print(f"Arquivo {arquivo} está vazio ou não contém a coluna necessária. Pulando para o próximo arquivo.")

if len(dfs) == 0:
    print("Nenhum arquivo CSV válido encontrado.")
    exit()

df_concatenado = pd.concat(dfs, ignore_index=True)

print("Dataset Consolidado:")
print(df_concatenado)

metricas = ['Body', 'Additions', 'Deletions', 'ReviewComments', 'Participants', 'Comments', 'TimeToMergeOrClose']

correlacoes = df_concatenado[metricas].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(correlacoes, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
plt.title('Correlações entre as Métricas')
plt.savefig(os.path.join(diretorio_graficos, 'correlacoes.png'))  # Salvar o gráfico
plt.show()

# A. Feedback Final das Revisões (Status do PR):

# RQ 01. Qual a relação entre o tamanho dos PRs e o feedback final das revisões?
plt.figure(figsize=(8, 6))
sns.scatterplot(x='Additions', y='TimeToMergeOrClose', hue='Merged', data=df_concatenado, palette='Set1', legend='full')
plt.title('Tamanho dos PRs x Feedback')
plt.xlabel('Número de linhas adicionadas')
plt.ylabel('Tempo para fechamento/merge (em dias)')
plt.legend(title='Status do PR', loc='upper right', labels=['Fechado', 'Merged'])
plt.savefig(os.path.join(diretorio_graficos, 'additions_tempo.png'))  # Salvar o gráfico
plt.show()

# RQ 02. Qual a relação entre o tempo de análise dos PRs e o feedback final das revisões?
plt.figure(figsize=(8, 6))
sns.scatterplot(x='TimeToMergeOrClose', y='TimeToMergeOrClose', hue='Merged', data=df_concatenado, palette='Set1', legend='full')
plt.title('Tempo de análise x Feedback final')
plt.xlabel('Tempo de análise dos PRs (em dias)')
plt.ylabel('Tempo para fechamento/merge (em dias)')
plt.legend(title='Status do PR', loc='upper right', labels=['Fechado', 'Merged'])
plt.savefig(os.path.join(diretorio_graficos, 'tempo_analise_tempo.png'))  # Salvar o gráfico
plt.show()

# RQ 03. Qual a relação entre a descrição dos PRs e o feedback final das revisões?
plt.figure(figsize=(8, 6))
sns.scatterplot(x='Comments', y='TimeToMergeOrClose', hue='Merged', data=df_concatenado, palette='Set1', legend='full')
plt.title('Número de comentários na descrição dos PRs x Feedback final')
plt.xlabel('Número de comentários na descrição dos PRs')
plt.ylabel('Tempo para fechamento/merge (em dias)')
plt.legend(title='Status do PR', loc='upper right', labels=['Fechado', 'Merged'])
plt.savefig(os.path.join(diretorio_graficos, 'comments_tempo.png'))  # Salvar o gráfico
plt.show()

# RQ 04. Qual a relação entre as interações nos PRs e o feedback final das revisões?
plt.figure(figsize=(8, 6))
sns.scatterplot(x='Participants', y='TimeToMergeOrClose', hue='Merged', data=df_concatenado, palette='Set1', legend='full')
plt.title('Interações nos PRs x Feedback final')
plt.xlabel('Número de participantes nos PRs')
plt.ylabel('Tempo para fechamento/merge (em dias)')
plt.legend(title='Status do PR', loc='upper right', labels=['Fechado', 'Merged'])
plt.savefig(os.path.join(diretorio_graficos, 'participants_tempo.png'))  # Salvar o gráfico
plt.show()

# B. Número de Revisões:

# RQ 05. Qual a relação entre o tamanho dos PRs e o número de revisões realizadas?
plt.figure(figsize=(8, 6))
sns.scatterplot(x='Body', y='ReviewComments', data=df_concatenado)
plt.title('Tamanho dos PRs x Número de revisões')
plt.xlabel('Tamanho dos PRs')
plt.ylabel('Número de revisões realizadas')
plt.savefig(os.path.join(diretorio_graficos, 'tamanho_revisoes.png'))  # Salvar o gráfico
plt.show()

# RQ 06. Qual a relação entre o tempo de análise dos PRs e o número de revisões realizadas?
plt.figure(figsize=(8, 6))
sns.scatterplot(x='TimeToMergeOrClose', y='ReviewComments', data=df_concatenado)
plt.title('Tempo de análise dos PRs x Número de revisões')
plt.xlabel('Tempo de análise dos PRs (em dias)')
plt.ylabel('Número de revisões realizadas')
plt.savefig(os.path.join(diretorio_graficos, 'tempo_analise_revisoes.png'))  # Salvar o gráfico
plt.show()

# RQ 07. Qual a relação entre a descrição dos PRs e o número de revisões realizadas?
plt.figure(figsize=(8, 6))
sns.scatterplot(x='Comments', y='ReviewComments', data=df_concatenado)
plt.title('Descrição dos PRs x Número de revisões')
plt.xlabel('Número de comentários na descrição dos PRs')
plt.ylabel('Número de revisões realizadas')
plt.savefig(os.path.join(diretorio_graficos, 'comments_revisoes.png'))  # Salvar o gráfico
plt.show()

# RQ 08. Qual a relação entre as interações nos PRs e o número de revisões realizadas?
plt.figure(figsize=(8, 6))
sns.scatterplot(x='Participants', y='ReviewComments', data=df_concatenado)
plt.title('Interações nos PRs x Número de revisões')
plt.xlabel('Número de participantes nos PRs')
plt.ylabel('Número de revisões realizadas')
plt.savefig(os.path.join(diretorio_graficos, 'participants_revisoes.png'))  # Salvar o gráfico
plt.show()