import pandas as pd
import numpy as np

pd.set_option('display.max_columns',15)

dados = pd.read_csv('The Global Dataset 14 Apr 2020.csv',na_values='-99')
dados.head()
# retirando os dados de 2019
dados.query('yearOfRegistration != 2019',inplace=True)

# definindo as categorias de ageBroad para ficarem ordenadas em tabelas e graficos
levels_ageBroad = pd.CategoricalDtype(
    categories = ['0--8','9--17','18--20','21--23','24--26','27--29','30--38','39--47', '48+'],
    ordered = True
    )
dados['ageBroad'] = dados['ageBroad'].astype(levels_ageBroad)

dados = (
    dados
    .get(
        ['yearOfRegistration',
        'gender',
        'ageBroad',
        'citizenship',
        'isForcedLabour',
        'isSexualExploit',
        'CountryOfExploitation'])
)
dados.head()

# adicionando os nomes dos paises de nascimento e exploracao além de longitude e latitude
lon_lat_country = pd.read_excel('lon_lat_country.xlsx')
lon_lat_country.head()
lon_lat_country.isna().sum()
lon_lat_country.query('country!=country') 
# o código de Namibia é NA mas esta sendo considerado
# como ausente isto irá afetar os merges posteriores

lon_lat_country['country'] = np.where(lon_lat_country['country'].isna(),'NA',lon_lat_country['country'])

dados = dados.merge(
    lon_lat_country,
    left_on = 'citizenship',
    right_on = 'country',
    how = 'left'
)

dados.drop(columns = 'country',inplace=True)

dados.rename(
    columns={'name':'nacionalidade',
    'latitude':'nacionalidade_lat',
    'longitude':'nacionalidade_long'},
     inplace = True) 

dados = dados.merge(
    lon_lat_country,
    left_on = 'CountryOfExploitation',
    right_on = 'country',
    how = 'left'
)

dados.drop(columns = 'country',inplace=True)

dados.rename(
    columns={'name':'pais_exploracao',
    'latitude':'pais_exploracao_lat',
    'longitude':'pais_exploracao_long'},
     inplace = True) 

dados.head()

# o padrao de codigo do plotly é o de alpha 3
alpha = pd.read_csv('alpha2_alpha3.csv')
alpha.isna().sum()
alpha.query('alpha_2!=alpha_2') 
# Novamente o código de Namibia é NA mas esta sendo considerado como ausente

alpha['alpha_2'] = np.where(alpha['alpha_2'].isna(),'NA',alpha['alpha_2'])

dados = dados.merge(alpha, how='left',left_on='citizenship',right_on='alpha_2')
dados.drop(columns=['alpha_2'],inplace = True)
dados.rename(columns={'alpha_3':'nacionalidade_alpha3'},inplace=True)
 
dados = dados.merge(alpha, how='left',left_on='CountryOfExploitation',right_on='alpha_2')
dados.drop(columns=['alpha_2'],inplace = True)
dados.rename(columns={'alpha_3':'pais_exploracao_alpha3'},inplace=True)

dados.head()

dados.to_csv('dados_app.csv', index=False)

#! para o desenvolvimento dos mapas devesse filtrar observacoes sem citizenship ou CountryOfExploitation
# dados.query('citizenship != "0" & CountryOfExploitation != "0"',inplace=True)

#! Alem disso para os mapas de fluxo deve-se atentar a: 
#TODO filtrar somente quem tem citizenship e CountryOfExploitation
# dados_lines.dropna(inplace = True) 
#TODO filtrar as pessoas com nacionalidade e CountryOfExploitation diferentes para melhorar a visualizacao
# dados_lines_group = dados_lines_group.query('nacionalidade != pais_exploracao')
