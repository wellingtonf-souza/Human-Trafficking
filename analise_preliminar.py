
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
import plotly.express as px        # basics charts
import plotly.figure_factory as ff # density

#TODO lendo os dados

dados = pd.read_csv('The Global Dataset 14 Apr 2020.csv',na_values='-99')
dados.shape # 48801, 63
dados.columns
dados.dtypes

pd.set_option('display.max_columns',15)
dados.head()

lon_lat_country = pd.read_excel('lon_lat_country.xlsx')
lon_lat_country.shape # 244, 4
lon_lat_country.head()

#TODO analise de valores ausentes
ausentes = pd.DataFrame(\
    dict(\
        colunas = dados.columns,\
        missing_porc = dados.apply(lambda col: col.isna().sum()/dados.shape[0]*100)\
        )\
    ).reset_index(drop = True)
ausentes.sort_values(ascending=False,by = 'missing_porc',inplace=True)
ausentes

sns.barplot(
    x = 'missing_porc', 
    y = 'colunas', 
    data = ausentes, 
    palette = 'viridis',
    orient='h')\
;plt.show()

ausentes['missing_porc'].describe()

fig_plotly = px.bar(
    ausentes.query('missing_porc > 50'), 
    x = 'missing_porc',
    y = 'colunas',
    template='plotly_white', 
    orientation='h')
fig_plotly.show()

#TODO Quantidade de casos ao longo dos anos
(
dados
.groupby('yearOfRegistration')
.agg(contagem_casos = ('yearOfRegistration','count'))
.reset_index()
)

sns.lineplot(
    x='yearOfRegistration', y = 'contagem_casos',
    data = dados
    .groupby('yearOfRegistration')
    .agg(contagem_casos = ('yearOfRegistration','count'))
    .reset_index(),
    palette='viridis'
    )\
;plt.show()

fig_plotly = px.line(
    data_frame = dados
    .groupby('yearOfRegistration')
    .agg(contagem_casos = ('yearOfRegistration','count'))
    .reset_index(),
    x='yearOfRegistration', 
    y = 'contagem_casos',
    template = 'plotly_white'
    )
fig_plotly.show()

# Ha um pico em 2016 e aparentemente os dados de 2019 
# ainda estao sendo introduzidos na base de dados

# retirando os dados de 2019

dados.query('yearOfRegistration != 2019',inplace=True)

dados.get('citizenship').value_counts() # nacionalidade da pessoa explorada

dados.get('CountryOfExploitation').value_counts() # pais de exploracao

#! tanto no pais de exploracao como na nacionalidade há o código 0,
#! este nao corresponde a nenhum codigo da ISO 3166-1 e nao ha
#! referencia deste no dicinario, acredito fortemente 
#! que tbm correspondam a informacoes ausentes 

dados.query('citizenship != "0" & CountryOfExploitation != "0"',inplace=True)

dados.shape # 39071

#TODO sexo das pessoas
dados.get('gender').value_counts(dropna = False)/dados.shape[0]*100

#TODO faixa etaria 
(
(dados
.get('ageBroad')
.value_counts(dropna = False)/dados.shape[0]*100).reset_index().sort_values(by = 'index')
)

# definindo as categorias de ageBroad para ficarem ordenadas em tabelas e graficos

list(dados.get('ageBroad').value_counts(dropna = False).reset_index().get('index'))

levels_ageBroad = pd.CategoricalDtype(
    categories = ['0--8','9--17','18--20','21--23','24--26','27--29','30--38','39--47', '48+'],
    ordered = True
    )

dados['ageBroad'] = dados['ageBroad'].astype(levels_ageBroad)
(dados.get('ageBroad').value_counts(dropna = False)/dados.shape[0]*100).reset_index().sort_values(by = 'index')

fig_plotly = px.bar(
    (dados.get('ageBroad').value_counts()/dados.shape[0]*100).reset_index().sort_values(by = 'index'),
    x = 'index',
    y = 'ageBroad',
    template='plotly_white'
)
fig_plotly.update_layout(
    title = "Faixa etária",
    xaxis_title = "Age",
    yaxis_title = "%"
    )
fig_plotly.show()

sns.countplot(x = 'ageBroad', data = dados,color='blue')\
;plt.show()

#TODO status maioridade 
#? Indica se o indivíduo tinha menos de 18 no momento em que foi registrado 
dados.get('majorityStatus').value_counts(dropna = False)
# Adult    20840
# NaN      12348
# Minor     5883

#TODO Status Maioridade Na Exploracao
#? A idade do indivíduo na época que a exploração do indivíduo começou
dados.get('majorityStatusAtExploit').value_counts(dropna = False)
# NaN      34998
# Minor     2524
# Adult     1549

#TODO Maioridade Entrada
#? Indica a idade de um indivíduo no momento em que entrou no processo de tráfico. 
#? A exploração não ocorreu necessariamente no momento da entrada.
dados.get('majorityEntry').value_counts(dropna = False)
# NaN      32882
# Adult     5301
# Minor      888

#TODO adicionando os nomes dos paises de nascimento e exploracao além de longitude e latitude
dados.get('citizenship').head()
lon_lat_country.head()

dados = dados.merge(
    lon_lat_country,
    left_on = 'citizenship',
    right_on = 'country',
    how = 'left'
)

dados.rename(
    columns={'name':'nacionalidade',
    'latitude':'nacionalidade_lat',
    'longitude':'nacionalidade_long'},
     inplace = True) 

dados.columns
dados.drop(columns = 'country',inplace=True)

dados = dados.merge(
    lon_lat_country,
    left_on = 'CountryOfExploitation',
    right_on = 'country',
    how = 'left'
)

dados.rename(
    columns={'name':'pais_exploracao',
    'latitude':'pais_exploracao_lat',
    'longitude':'pais_exploracao_long'},
     inplace = True) 

dados.drop(columns = 'country',inplace=True)
dados.columns

# TODO: Meios de controle 
# meansOfControlConcatenated simplesmente concatena os demais meios
dados.drop(columns = 'meansOfControlConcatenated',inplace = True)

dados.columns[dados.columns.str.startswith('means')]

means = (
    dados.
    get(
        dados.columns[dados.columns.str.startswith('means')]
        )
        .apply(lambda coluna: coluna.value_counts(dropna = False)/dados.shape[0])
).reset_index()

means

means = means.melt(
    value_vars = dados.columns[dados.columns.str.startswith('means')],
    id_vars=['index'],
    value_name = 'Porcentagem',
    var_name = 'Meio de controle'
)

means

means.query('index!=index').sort_values(by = 'Porcentagem')
# com excecao de ControlNotSpecified todos os demais 
# meios de controle apresentam no minimo 89% de NaN

# NaN              meansOfControlNotSpecified     0.305700
# NaN        meansOfControlPsychologicalAbuse     0.890917
# NaN         meansOfControlRestrictsMovement     0.900719
# NaN                   meansOfControlThreats     0.904942
# NaN             meansOfControlFalsePromises     0.907092
# NaN             meansOfControlTakesEarnings     0.909600
# NaN             meansOfControlPhysicalAbuse     0.912032
# NaN     meansOfControlExcessiveWorkingHours     0.916844
# NaN        meansOfControlWithholdsDocuments     0.919941
# NaN      meansOfControlRestrictsMedicalCare     0.937908
# NaN      meansOfControlWithholdsNecessities     0.942515
# NaN               meansOfControlDebtBondage     0.943129
# NaN    meansOfControlPsychoactiveSubstances     0.946636
# NaN               meansOfControlSexualAbuse     0.948530
# NaN                     meansOfControlOther     0.949246
# NaN    meansOfControlThreatOfLawEnforcement     0.950552
# NaN  meansOfControlRestrictsFinancialAccess     0.995879
# NaN              meansOfControlUsesChildren     0.997722

#TODO investigando alguns meios de controle especificos ao longo do tempo
# controle por ameacas
pd.crosstab(
    index = dados.get('yearOfRegistration'),
    columns= dados.get('meansOfControlThreats').fillna('missing')
)

# controle por abuso fisico
pd.crosstab(
    index = dados.get('yearOfRegistration'),
    columns= dados.get('meansOfControlPhysicalAbuse').fillna('missing')
)

# controle por abuso sexual
pd.crosstab(
    index = dados.get('yearOfRegistration'),
    columns= dados.get('meansOfControlSexualAbuse').fillna('missing')
)

# controle por falsas promessas
pd.crosstab(
    index = dados.get('yearOfRegistration'),
    columns= dados.get('meansOfControlFalsePromises').fillna('missing')
)

# controle por substancias psicoativas
pd.crosstab(
    index = dados.get('yearOfRegistration'),
    columns= dados.get('meansOfControlPsychoactiveSubstances').fillna('missing')
)

# controle por trabalho excessivo
pd.crosstab(
    index = dados.get('yearOfRegistration'),
    columns= dados.get('meansOfControlExcessiveWorkingHours').fillna('missing')
)

# controle restricao de documentos
pd.crosstab(
    index = dados.get('yearOfRegistration'),
    columns= dados.get('meansOfControlWithholdsDocuments').fillna('missing')
)

# TODO: Propósito para o qual as vítimas foram traficadas

dados.columns[dados.columns.str.startswith('is')]

proposito = (
    dados.
    get(
        dados.columns[dados.columns.str.startswith('is')]
        )
        .apply(lambda coluna: coluna.value_counts(dropna = False)/dados.shape[0])
).reset_index()

proposito

#TODO investigando alguns propositos especificos ao longo do tempo

pd.crosstab(
    index = dados.get('yearOfRegistration'),
    columns= dados.get('isForcedLabour').fillna('missing')
)

pd.crosstab(
    index = dados.get('yearOfRegistration'),
    columns= dados.get('isSexualExploit').fillna('missing')
)

pd.crosstab(
    index = dados.get('yearOfRegistration'),
    columns= dados.get('isOtherExploit').fillna('missing')
)

# TODO: Tipos de trabalho que as vitimas foram forcadas a realizar

dados.drop(
    columns = ['typeOfSexConcatenated','typeOfLabourConcatenated','typeOfExploitConcatenated'], 
    inplace = True
    )

dados.columns[dados.columns.str.startswith('type')]

trabalho = (
    dados.
    get(
        dados.columns[dados.columns.str.startswith('type')]
        )
        .apply(lambda coluna: coluna.value_counts(dropna = False)/dados.shape[0])
).reset_index()

trabalho

# TODO: O tipo de relacionamento que a pessoa ou pessoas que inicialmente seduziram 
# TODO: ou obtiveram o indivíduo na situação de exploração tinham com o indivíduo.

dados.columns[dados.columns.str.startswith('recruiter')]

relacionamento = (
    dados.
    get(
        dados.columns[dados.columns.str.startswith('recruiter')]
        )
        .apply(lambda coluna: coluna.value_counts(dropna = False)/dados.shape[0])
).reset_index()

relacionamento

# TODO: Mapas Choropleth

import plotly.graph_objects as go

# * citizenship: nacionalidade

map_chor = dados.get('citizenship').value_counts().reset_index()
map_chor.rename(columns={'index':'code','citizenship':'contagem'}, inplace=True)
map_chor.head()
map_chor.shape # 44

lon_lat_country.head()
map_chor = map_chor.merge(
    lon_lat_country.get(['country','name']),
    how="left",
    left_on='code',
    right_on="country")

map_chor.drop(columns=['country'],inplace = True)

map_chor.head()

# o padrao de codigo do plotly é o de alpha 3
alpha = pd.read_csv('alpha2_alpha3.csv')
alpha

map_chor = map_chor.merge(alpha, how='left',left_on='code',right_on='alpha_2')
map_chor.drop(columns=['alpha_2'],inplace = True)

fig = go.Figure(data=go.Choropleth(
    locations = map_chor['alpha_3'],
    z = map_chor['contagem'],
    text = map_chor['name'],
    colorscale = 'Blues',
    autocolorscale=False,
    reversescale=True,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    colorbar_title = 'Quantidade',
))

fig.update_layout(
    title_text='Nacionalidade das pessoas exploradas',
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    )
)

fig.show()

# plotando como orthographic

fig = go.Figure(data=go.Choropleth(
    locations = map_chor['alpha_3'],
    z = map_chor['contagem'],
    text = map_chor['name'],
    colorscale = 'Blues',
    autocolorscale=False,
    reversescale=True,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    colorbar_title = 'Quantidade',
))

fig.update_layout(
    title_text='Nacionalidade das pessoas exploradas',
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='orthographic'
    )
)

fig.show()

# * CountryOfExploitation: pais onde a pessoa foi explorada

map_chor = dados.get('CountryOfExploitation').value_counts().reset_index()
map_chor.rename(columns={'index':'code','CountryOfExploitation':'contagem'}, inplace=True)
map_chor.head()
map_chor.shape # 58

lon_lat_country.head()
map_chor = map_chor.merge(
    lon_lat_country.get(['country','name']),
    how="left",
    left_on='code',
    right_on="country")

map_chor.drop(columns=['country'],inplace = True)

map_chor.head()

# o padrao de codigo do plotly é o de alpha 3
alpha = pd.read_csv('alpha2_alpha3.csv')
alpha

map_chor = map_chor.merge(alpha, how='left',left_on='code',right_on='alpha_2')
map_chor.drop(columns=['alpha_2'],inplace = True)

fig = go.Figure(data=go.Choropleth(
    locations = map_chor['alpha_3'],
    z = map_chor['contagem'],
    text = map_chor['name'],
    colorscale = 'Blues',
    autocolorscale=False,
    reversescale=True,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    colorbar_title = 'Quantidade',
))

fig.update_layout(
    title_text='Último país em que a vítima foi explorada',
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    )
)

fig.show()

# plotando como orthographic

fig = go.Figure(data=go.Choropleth(
    locations = map_chor['alpha_3'],
    z = map_chor['contagem'],
    text = map_chor['name'],
    colorscale = 'Blues',
    autocolorscale=False,
    reversescale=True,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    colorbar_title = 'Quantidade',
))

fig.update_layout(
    title_text='Último país em que a vítima foi explorada',
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='orthographic'
    )
)

fig.show()

# TODO: Mapas de linhas

dados_lines = (
    dados
    .get(['nacionalidade_lat',
    'nacionalidade_long',
    'nacionalidade',
    'pais_exploracao_lat',
    'pais_exploracao_long',
    'pais_exploracao'])
)

dados_lines.head()
dados_lines.shape

dados_lines_group = (
    dados_lines
    .get(['nacionalidade','pais_exploracao'])
    .groupby(['nacionalidade','pais_exploracao'])
    .agg(
       quantidade = ('pais_exploracao','count')
    )
    .reset_index()
)

dados_lines_group.head()
dados_lines_group.shape

dados_lines_group = (
    dados_lines_group
    .merge(
        dados_lines
        .get(['nacionalidade','nacionalidade_long','nacionalidade_lat'])
        .drop_duplicates(),
        how = 'outer',
        on = 'nacionalidade'
        )
)
dados_lines_group.head()
dados_lines_group.shape

dados_lines_group = dados_lines_group.merge(
        dados_lines
        .get(['pais_exploracao','pais_exploracao_long','pais_exploracao_lat'])
        .drop_duplicates(),
        how = 'left',
        on = 'pais_exploracao'
        )

dados_lines_group.head()
dados_lines_group.shape


dados_lines_group = ( 
dados_lines_group
.assign(
    texto = 'Nacionalidade: '+ 
    dados_lines_group['nacionalidade'] + 
    '<br>' +
    'Pais exploração: ' + 
    dados_lines_group['pais_exploracao']+
    '<br>' +
    'Quantidade de pessoas: ' +
    dados_lines_group['quantidade'].astype(str)
)
)

cores = pd.DataFrame(
    dict(nacionalidade = dados_lines_group.get('nacionalidade').drop_duplicates(),
    cor = sns.color_palette('hls', dados_lines_group.get('nacionalidade').drop_duplicates().shape[0]).as_hex()
    )
    )
cores

dados_lines_group = dados_lines_group.merge(
    cores,
    how = 'left',
    on = 'nacionalidade'
)
dados_lines_group.head()

# filtrando as pessoas com nacionalidade e pais diferentes para melhorar a visualizacao

dados_lines_group = dados_lines_group.query('nacionalidade != pais_exploracao')

dados_lines_group.shape
dados_lines_group.head()

dados_lines_group = dados_lines_group.reset_index(drop = True)

fig = go.Figure()

for i in range(0,dados_lines_group.shape[0]):
    fig.add_trace(
        go.Scattergeo(
            lon = [dados_lines_group['nacionalidade_long'][i], dados_lines_group['pais_exploracao_long'][i]],
            lat = [dados_lines_group['nacionalidade_lat'][i], dados_lines_group['pais_exploracao_lat'][i]],
            mode = 'lines',
            line = dict(
                width = 2, color = dados_lines_group['cor'][i]
            ),
            text = dados_lines_group['texto'][i],
        )
    )


fig.update_layout(
    title_text='Fluxo do tráfico de pessoas',
    showlegend = False,
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='orthographic'
    )
)

fig.show()



fig = go.Figure()

for i in range(0,dados_lines_group.shape[0]):
    fig.add_trace(
        go.Scattergeo(
            lon = [dados_lines_group['nacionalidade_long'][i], dados_lines_group['pais_exploracao_long'][i]],
            lat = [dados_lines_group['nacionalidade_lat'][i], dados_lines_group['pais_exploracao_lat'][i]],
            mode = 'lines',
            line = dict(
                width = 2, color = dados_lines_group['cor'][i]
            ),
            text = dados_lines_group['texto'][i],
        )
    )


fig.update_layout(
    title_text='Fluxo do tráfico de pessoas',
    showlegend = False,
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    )
)

fig.show()