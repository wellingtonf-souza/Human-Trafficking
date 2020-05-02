import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px        
import plotly.graph_objects as go

dados = pd.read_csv('dados_app.csv')
# definindo as categorias de ageBroad para ficarem ordenadas
levels_ageBroad = pd.CategoricalDtype(
    categories = ['0--8','9--17','18--20','21--23','24--26','27--29','30--38','39--47', '48+'],
    ordered = True)

dados['ageBroad'] = dados['ageBroad'].astype(levels_ageBroad)

def constr_dado_perfil(
    dados,
    perfil_slider,
    perfil_select_gender,
    perfil_select_age,
    perfil_select_proposito):
    dados_perfil = dados.query('yearOfRegistration >= @perfil_slider[0] & yearOfRegistration <= @perfil_slider[1]')
    if perfil_select_gender != 'Ambos':
        dados_perfil =  dados_perfil.query('gender == @perfil_select_gender')
    if ('Todas' not in perfil_select_age):
        dados_perfil = dados_perfil.query('ageBroad in @perfil_select_age')
    if perfil_select_proposito != 'Todos':
        if perfil_select_proposito == 'Trabalho forçado':
            dados_perfil =  dados_perfil.query('isForcedLabour == 1')
        elif perfil_select_proposito == 'Exploração sexual':
            dados_perfil = dados_perfil.query('isSexualExploit == 1')
    return dados_perfil

def graph_lines_year(dados):
    fig_lines_year = px.line(
        data_frame = (
            dados
            .groupby('yearOfRegistration')
            .agg(contagem_casos = ('yearOfRegistration','count'))
            .reset_index()
            ),
        x = 'yearOfRegistration', 
        y = 'contagem_casos',
        template = 'plotly_white')
    fig_lines_year.update_layout(title="Quantidade de registros ao longo dos anos",
        xaxis_title = "Ano do registro",
        yaxis_title = "N")
    return fig_lines_year

def graph_gender(dados):
    fig_gender = px.pie(
        (
            dados
            .get('gender')
            .value_counts()
            .reset_index()
            .rename(columns = {'index':'Gender','gender':'Quantidade'})
            ),
    values='Quantidade',
    names='Gender',
    hole= 0.75,
    template = 'plotly_white')
    fig_gender.update_layout(
        title = "Gênero"
    )
    return fig_gender

def graph_ageBroad(dados):
    fig_ageBroad = px.bar(
        (
            dados
            .get('ageBroad')
            .value_counts()
            .reset_index()
            .sort_values(by = 'index')
            .rename(columns = {'index':'ageBroad','ageBroad':'Quantidade'})
        ),
        x = 'ageBroad',
        y = 'Quantidade',
        template='plotly_white')
    fig_ageBroad.update_layout(title = "Faixa etária",
        xaxis_title = "Age",
        yaxis_title = "N")
    return fig_ageBroad

def constr_dado_nac_exp(
    dados,
    nac_exp_slider,
    nac_exp_select_gender,
    nac_exp_select_age,
    nac_exp_select_proposito):
    dados_nac_exp = dados.query('yearOfRegistration >= @nac_exp_slider[0] & yearOfRegistration <= @nac_exp_slider[1]')
    if nac_exp_select_gender != 'Ambos':
        dados_nac_exp =  dados_nac_exp.query('gender == @nac_exp_select_gender')
    if ('Todas' not in nac_exp_select_age):
        dados_nac_exp = dados_nac_exp.query('ageBroad in @nac_exp_select_age')
    if nac_exp_select_proposito != 'Todos':
        if nac_exp_select_proposito == 'Trabalho forçado':
            dados_nac_exp =  dados_nac_exp.query('isForcedLabour == 1')
        elif nac_exp_select_proposito == 'Exploração sexual':
            dados_nac_exp = dados_nac_exp.query('isSexualExploit == 1')
    return dados_nac_exp

def choropleth_nacionalidade(dados_nac_exp, nac_exp_type):
    if nac_exp_type=='equirectangular':
        dados_nac_exp = dados_nac_exp.query('citizenship != "0"')
        dados_nac_exp = (
            dados_nac_exp
            .get(['nacionalidade','nacionalidade_alpha3'])
            .groupby(['nacionalidade','nacionalidade_alpha3'])
            .size()
            .reset_index(name = 'Quantidade')
            )
        fig_choropleth_nac = go.Figure(data=go.Choropleth(
            locations = dados_nac_exp['nacionalidade_alpha3'],
            z = dados_nac_exp['Quantidade'],
            text = dados_nac_exp['nacionalidade'],
            colorscale = 'Viridis',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title = 'Quantidade')
        )
        fig_choropleth_nac.update_layout(
            title_text='Nacionalidade das pessoas exploradas',
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular')
            )
    if nac_exp_type=='orthographic':
        dados_nac_exp = dados_nac_exp.query('citizenship != "0"')
        dados_nac_exp = (
            dados_nac_exp
            .get(['nacionalidade','nacionalidade_alpha3'])
            .groupby(['nacionalidade','nacionalidade_alpha3'])
            .size()
            .reset_index(name = 'Quantidade')
            )
        fig_choropleth_nac = go.Figure(data=go.Choropleth(
            locations = dados_nac_exp['nacionalidade_alpha3'],
            z = dados_nac_exp['Quantidade'],
            text = dados_nac_exp['nacionalidade'],
            colorscale = 'Viridis',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title = 'Quantidade')
        )
        fig_choropleth_nac.update_layout(
            title_text='Nacionalidade das pessoas exploradas',
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='orthographic')
            )
    return fig_choropleth_nac

def choropleth_pais_exploracao(dados_nac_exp, nac_exp_type):
    if nac_exp_type=='equirectangular':
        dados_nac_exp = dados_nac_exp.query('CountryOfExploitation != "0"')
        dados_nac_exp = (
            dados_nac_exp
            .get(['pais_exploracao','pais_exploracao_alpha3'])
            .groupby(['pais_exploracao','pais_exploracao_alpha3'])
            .size()
            .reset_index(name = 'Quantidade')
            )
        fig_choropleth_exp = go.Figure(data=go.Choropleth(
            locations = dados_nac_exp['pais_exploracao_alpha3'],
            z = dados_nac_exp['Quantidade'],
            text = dados_nac_exp['pais_exploracao'],
            colorscale = 'Viridis',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title = 'Quantidade')
        )
        fig_choropleth_exp.update_layout(
            title_text='Último país em que a vítima foi explorada',
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular')
            )
    if nac_exp_type=='orthographic':
        dados_nac_exp = dados_nac_exp.query('CountryOfExploitation != "0"')
        dados_nac_exp = (
            dados_nac_exp
            .get(['pais_exploracao','pais_exploracao_alpha3'])
            .groupby(['pais_exploracao','pais_exploracao_alpha3'])
            .size()
            .reset_index(name = 'Quantidade')
            )
        fig_choropleth_exp = go.Figure(data=go.Choropleth(
            locations = dados_nac_exp['pais_exploracao_alpha3'],
            z = dados_nac_exp['Quantidade'],
            text = dados_nac_exp['pais_exploracao'],
            colorscale = 'Viridis',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title = 'Quantidade')
        )
        fig_choropleth_exp.update_layout(
            title_text='Último país em que a vítima foi explorada',
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='orthographic')
            )
    return fig_choropleth_exp


def constr_dado_fluxo(
    dados,
    fluxo_slider,
    fluxo_select_gender,
    fluxo_select_age,
    fluxo_select_proposito):
    dados_fluxo = dados.query('citizenship != "0" & CountryOfExploitation != "0"')

    dados_fluxo = dados_fluxo.query('yearOfRegistration >= @fluxo_slider[0] & yearOfRegistration <= @fluxo_slider[1]')

    if fluxo_select_gender != 'Ambos':
        dados_fluxo =  dados_fluxo.query('gender == @fluxo_select_gender')
    if ('Todas' not in fluxo_select_age):
        dados_fluxo = dados_fluxo.query('ageBroad in @fluxo_select_age')
    if fluxo_select_proposito != 'Todos':
        if fluxo_select_proposito == 'Trabalho forçado':
            dados_fluxo =  dados_fluxo.query('isForcedLabour == 1')
        elif fluxo_select_proposito == 'Exploração sexual':
            dados_fluxo = dados_fluxo.query('isSexualExploit == 1')
    dados_fluxo = (
        dados_fluxo
        .get(['nacionalidade_lat',
        'nacionalidade_long',
        'nacionalidade',
        'pais_exploracao_lat',
        'pais_exploracao_long',
        'pais_exploracao'])
        )
    dados_fluxo = dados_fluxo.dropna()   
    return dados_fluxo


def map_lines(dados_fluxo, fluxo_type,fluxo_select_nacionalidade,fluxo_select_pais_exploracao):
    if fluxo_type=='equirectangular':
        if ('Todas' not in fluxo_select_nacionalidade):
            dados_fluxo = dados_fluxo.query('nacionalidade in @fluxo_select_nacionalidade')
        if ('Todos' not in fluxo_select_pais_exploracao):
            dados_fluxo = dados_fluxo.query('pais_exploracao in @fluxo_select_pais_exploracao')
        dados_lines_group = (
            dados_fluxo
            .groupby(['nacionalidade_lat','nacionalidade_long','nacionalidade',
                'pais_exploracao_lat','pais_exploracao_long','pais_exploracao'])
            .size()
            .reset_index(name = 'quantidade')
            )
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
                cor = sns.color_palette('hls', dados_lines_group.get('nacionalidade').drop_duplicates().shape[0]).as_hex())
            )
        dados_lines_group = dados_lines_group.merge(
            cores,
            how = 'left',
            on = 'nacionalidade'
            )
        # filtrando as pessoas com nacionalidade e pais diferentes para melhorar a visualizacao
        dados_lines_group = dados_lines_group.query('nacionalidade != pais_exploracao')
        dados_lines_group = dados_lines_group.reset_index(drop = True)

        fig_map_lines = go.Figure()

        for i in range(0,dados_lines_group.shape[0]):
            fig_map_lines.add_trace(
                go.Scattergeo(
                    lon = [dados_lines_group['nacionalidade_long'][i], dados_lines_group['pais_exploracao_long'][i]],
                    lat = [dados_lines_group['nacionalidade_lat'][i], dados_lines_group['pais_exploracao_lat'][i]],
                    mode = 'lines',
                    line = dict(
                        width = 2, color = dados_lines_group['cor'][i]
                        ),
                    text = dados_lines_group['texto'][i]
                    )
                )
        fig_map_lines.update_layout(
            title_text='Fluxo do tráfico de pessoas',
            showlegend = False,
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
                )
        )
    if fluxo_type=='orthographic':
        if ('Todas' not in fluxo_select_nacionalidade):
            dados_fluxo = dados_fluxo.query('nacionalidade in @fluxo_select_nacionalidade')
        if ('Todos' not in fluxo_select_pais_exploracao):
            dados_fluxo = dados_fluxo.query('pais_exploracao in @fluxo_select_pais_exploracao')
        dados_lines_group = (
            dados_fluxo
            .groupby(['nacionalidade_lat','nacionalidade_long','nacionalidade',
                'pais_exploracao_lat','pais_exploracao_long','pais_exploracao'])
            .size()
            .reset_index(name = 'quantidade')
            )
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
                cor = sns.color_palette('hls', dados_lines_group.get('nacionalidade').drop_duplicates().shape[0]).as_hex())
            )
        dados_lines_group = dados_lines_group.merge(
            cores,
            how = 'left',
            on = 'nacionalidade'
            )
        # filtrando as pessoas com nacionalidade e pais diferentes para melhorar a visualizacao
        dados_lines_group = dados_lines_group.query('nacionalidade != pais_exploracao')
        dados_lines_group = dados_lines_group.reset_index(drop = True)

        fig_map_lines = go.Figure()

        for i in range(0,dados_lines_group.shape[0]):
            fig_map_lines.add_trace(
                go.Scattergeo(
                    lon = [dados_lines_group['nacionalidade_long'][i], dados_lines_group['pais_exploracao_long'][i]],
                    lat = [dados_lines_group['nacionalidade_lat'][i], dados_lines_group['pais_exploracao_lat'][i]],
                    mode = 'lines',
                    line = dict(
                        width = 2, color = dados_lines_group['cor'][i]
                        ),
                    text = dados_lines_group['texto'][i]
                    )
                )
        fig_map_lines.update_layout(
            title_text='Fluxo do tráfico de pessoas',
            showlegend = False,
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='orthographic'
                )
        )

    return fig_map_lines

def main():
    st.sidebar.image('logo.png', use_column_width=True)
    menu = (st.sidebar.selectbox("Menu",
        options = ('Sobre','Perfil','Nacionalidade e pais de exploração','Fluxo do tráfico')
        )
    )

    if(menu=='Sobre'):
        st.title('Human Trafficking')
        st.markdown(
            '<p style="text-align: justify">Estes dados consistem em informações sobre vítimas identificadas e'
            ' relatadas de tráfico humano. As variáveis captam informações do perfil'
            ' sociodemográfico das vítimas, o processo de tráfico (como meios de controle'
            ' utilizados nas vítimas) e tipo de exploração.</p>',
            unsafe_allow_html=True
            )
        st.markdown(
            '<p style="text-align: justify">Este conjunto de dados pode ser baixado do site da '
            '<a href="https://www.ctdatacollaborative.org/"> <i> Counter Trafficking Data Collaborative </i> </a> '
            ' por qualquer pessoa interessada em realizar suas próprias análises.'
            ' O conjunto de dados global combina dados de diversos parceiros e é submetido'
            ' a duas fases de desidentificação de dados. Primeiramente todos os nomes e'
            ' detalhes de identificação são removidos dos dados antes da combinação e, '
            'após a combinação os dados são k-anonimizados (k=11).</p>',
            unsafe_allow_html=True
            )
        st.markdown(
            '<p style="text-align: justify">K-anonimização (<i>K-anonymization</i>) é uma técnica de anonimização de dados'
            ' que redige casos caindo em conjuntos com menos de k-1 membros, onde cada '
            'conjunto é definido por uma combinação única de valores das diferentes '
            'variáveis em um conjunto de dados. Isso significa que não é possível '
            'consultar o conjunto de dados e ter retorno inferior a um número pré-determinado '
            '(k-1) de resultados, independentemente da consulta. Com base em pesquisas e '
            'testes, adotou-se k=11 para os dados CTDC, o que significa que os casos '
            'foram redigidos a partir do conjunto de dados global de tal forma que as '
            'consultas não podem retornar menos de 10 resultados.</p>',
            unsafe_allow_html=True
            )
        st.markdown(
            '<p style="text-align: justify">Salienta-se que este conjunto de dados não pode ser considerado uma amostra '
            'aleatória ou necessariamente representativa de todas as vítimas do tráfico '
            'de seres humanos a nível mundial, devido à natureza deste crime oculto.  O '
            'conjunto de dados é composto por casos identificados ou auto notificados de'
            ' vítimas de tráfico. Na medida em que certos tipos de tráfico humano podem '
            'ser mais propensos a serem identificados, reconhecidos ou relatados, esse '
            'conjunto de dados será tendencioso em relação a esses tipos de tráfico em '
            'comparação com a população de vítimas de tráfico no mundo (identificadas e '
            'não identificadas). Os dados também podem ter um viés geográfico à medida que'
            ' são coletados em locais onde as operações de combate ao tráfico são conduzidas.</p>',
            unsafe_allow_html=True
            ) 
        st.markdown(
            '<p style="text-align: justify">Caso ache interessante este app todo o código para seu desenvolvimento '
            'encontra-se no <a href="https://github.com/wellingtonf-souza/Human-Trafficking/"> <i>Github</i> </a>. '
            'Além disso, caso queira me adicionar: <a href="https://www.linkedin.com/in/wellington-ferr-souza/"> <i>Linkedin</i> </a>.</p>',
            unsafe_allow_html=True
            )
    if(menu =='Perfil'):
        st.title('Perfil sociodemográfico')
        perfil_slider = st.sidebar.slider('Selecione o intervalo:',2002, 2018, (2002, 2018))
        
        perfil_select_gender = st.sidebar.selectbox(
            label = 'Selecione o gênero:',
            options = ('Ambos','Female','Male')
        )
        perfil_select_age = st.sidebar.multiselect(
            label = 'Selecione a faixa etária:',
            options = ('Todas','0--8','9--17','18--20','21--23','24--26','27--29','30--38','39--47', '48+'),
            default = 'Todas'
        )
        perfil_select_proposito = st.sidebar.selectbox(
            label = 'Propósito para o qual as vítimas foram traficadas:',
            options = ('Todos','Trabalho forçado','Exploração sexual')
        )
        dados_perfil = constr_dado_perfil(dados,
            perfil_slider,
            perfil_select_gender,
            perfil_select_age,
            perfil_select_proposito
            )
        st.plotly_chart(graph_lines_year(dados_perfil))
        st.plotly_chart(graph_gender(dados_perfil))
        st.plotly_chart(graph_ageBroad(dados_perfil))
    if(menu =='Nacionalidade e pais de exploração'):
        st.title('Nacionalidade das vitimas e último pais de exploração')
        nac_exp_type = st.sidebar.radio(
            label = 'Selecione o tipo de gráfico:',
            options = ('equirectangular','orthographic')
            )
        nac_exp_slider = st.sidebar.slider('Selecione o intervalo:',2002, 2018, (2002, 2018))
        
        nac_exp_select_gender = st.sidebar.selectbox(
            label = 'Selecione o gênero:',
            options = ('Ambos','Female','Male')
        )
        nac_exp_select_age = st.sidebar.multiselect(
            label = 'Selecione a faixa etária:',
            options = ('Todas','0--8','9--17','18--20','21--23','24--26','27--29','30--38','39--47', '48+'),
            default = 'Todas'
        )
        nac_exp_select_proposito = st.sidebar.selectbox(
            label = 'Propósito para o qual as vítimas foram traficadas:',
            options = ('Todos','Trabalho forçado','Exploração sexual')
        )
        dados_nac_exp = constr_dado_nac_exp(
            dados,
            nac_exp_slider,
            nac_exp_select_gender,
            nac_exp_select_age,
            nac_exp_select_proposito)
        st.plotly_chart(choropleth_nacionalidade(dados_nac_exp,nac_exp_type))
        st.plotly_chart(choropleth_pais_exploracao(dados_nac_exp,nac_exp_type))
    if(menu == 'Fluxo do tráfico'):
        st.title('Fluxo do tráfico de pessoas no mundo')
        fluxo_type = st.sidebar.radio(
            label = 'Selecione o tipo de gráfico:',
            options = ('equirectangular','orthographic')
            )
        fluxo_slider = st.sidebar.slider('Selecione o intervalo:',2002, 2018, (2002, 2018))
        
        fluxo_select_gender = st.sidebar.selectbox(
            label = 'Selecione o gênero:',
            options = ('Ambos','Female','Male')
        )
        fluxo_select_age = st.sidebar.multiselect(
            label = 'Selecione a faixa etária:',
            options = ('Todas','0--8','9--17','18--20','21--23','24--26','27--29','30--38','39--47', '48+'),
            default = 'Todas'
        )
        fluxo_select_proposito = st.sidebar.selectbox(
            label = 'Propósito para o qual as vítimas foram traficadas:',
            options = ('Todos','Trabalho forçado','Exploração sexual')
        )

        dados_fluxo = constr_dado_fluxo(dados,
        fluxo_slider,
        fluxo_select_gender,
        fluxo_select_age,
        fluxo_select_proposito)

        nacionalidades_select = sorted(list(dados_fluxo.get('nacionalidade').unique()))
        nacionalidades_select = np.insert(np.array(nacionalidades_select), 0, "Todas")
        fluxo_select_nacionalidade = st.sidebar.multiselect(
            label = 'Selecione a nacionalidade:',
            options = list(nacionalidades_select),
            default = 'Todas'
        )

        pais_exploracao_select = sorted(list(dados_fluxo.get('pais_exploracao').unique()))
        pais_exploracao_select = np.insert(np.array(pais_exploracao_select), 0, "Todos")
        fluxo_select_pais_exploracao = st.sidebar.multiselect(
            label = 'Selecione o país de exploração:',
            options = list(pais_exploracao_select),
            default = 'Todos'
        )
        st.plotly_chart(map_lines(dados_fluxo,fluxo_type,fluxo_select_nacionalidade,fluxo_select_pais_exploracao))
        st.sidebar.info('Importante salientar que neste mapa não estão presentes os indivíduos explorados no próprio país.')
 
if __name__ == '__main__':
	main()

