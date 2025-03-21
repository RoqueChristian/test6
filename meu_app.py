import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

def formatar_moeda(valor, simbolo_moeda="R$"):
    if pd.isna(valor):
        return ''
    return f"{simbolo_moeda} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_metricas(df):
    total_nf = len(df['NF'].unique())
    total_qtd_produto = df['Qtd_Produto'].sum()
    valor_total_item = df['Valor_Total_Item'].sum()
    total_custo_compra = df['Total_Custo_Compra'].sum()
    total_lucro_venda = df['Total_Lucro_Venda_Item'].sum()
    return total_nf, total_qtd_produto, valor_total_item, total_custo_compra, total_lucro_venda

def agrupar_e_somar(df, coluna_agrupamento):
    return df.groupby(coluna_agrupamento).agg(
        {'Valor_Total_Item': 'sum', 'Total_Custo_Compra': 'sum', 'Total_Lucro_Venda_Item': 'sum'}
    ).reset_index()

def produtos_mais_vendidos(df, top_n=10, ordenar_por='Valor_Total_Item'):
    df_agrupado = df.groupby('Descricao_produto')[ordenar_por].sum().reset_index()
    df_ordenado = df_agrupado.sort_values(by=ordenar_por, ascending=False)
    return df_ordenado.head(top_n)


def aplicar_filtros(df, vendedor='Todos', mes='Todos', ano='Todos', situacao='Faturada'):

    df_filtrado = df.copy()

    if vendedor != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Vendedor'] == vendedor]
    if mes != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Mes'] == mes]
    if ano != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Ano'] == ano]
    if situacao != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['situacao'] == situacao]

    return df_filtrado

def criar_grafico_barras(df, x, y, title, labels):
    
    df['Valor_Monetario'] = df[y].apply(formatar_moeda)

    fig = px.bar(df, x=x, y=y, title=title, labels=labels, 
                 color=y, text=df['Valor_Monetario'], template="plotly_white", 
                 hover_data={x: False, y: False, 'Valor_Monetario': True})  

    fig.update_traces(marker=dict(line=dict(color='black', width=1)), 
                      hoverlabel=dict(bgcolor="black", font_size=22, 
                                      font_family="Arial, sans-serif"))

    fig.update_layout(yaxis_title=labels.get(y, y), 
                      xaxis_title=labels.get(x, x), 
                      showlegend=False, height=400)

    return fig

def criar_grafico_vendas_diarias(df, mes, ano):
    df_filtrado = df[(df['Mes'] == mes) & (df['Ano'] == ano)]

    vendas_diarias = df_filtrado.groupby('Dia')['Valor_Total_Item'].sum().reset_index()

    vendas_diarias["Valor_Monetario"] = vendas_diarias["Valor_Total_Item"].apply(formatar_moeda)

    fig = px.bar(vendas_diarias, x='Dia', y='Valor_Total_Item',
                 title=f'Vendas Diárias em {mes}/{ano}',
                 labels={'Dia': 'Dia', 'Valor_Total_Item': 'Valor Total de Venda'},
                 color='Valor_Total_Item', text_auto=True,
                 template="plotly_white", hover_data={'Valor_Total_Item': False,'Valor_Monetario': True})

    fig.update_traces(marker=dict(line=dict(color='black', width=1)),
                      hoverlabel=dict(bgcolor="black", font_size=22,
                                       font_family="Arial-bold, sans-serif"))
    

    fig.update_layout(yaxis_title='Valor Total de Venda',
                      xaxis_title='Dia',
                      showlegend=False, height=400)

    return fig



##########################################################################################################################################



def renderizar_pagina_vendas(df):
    
    print(f"Número de valores NaN na coluna 'Mes': {df['Mes'].isnull().sum()}")

    vendedores = df['Vendedor'].unique().tolist()
    meses_abreviados = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    
    meses_numericos = sorted(df['Mes'].unique().tolist(), key=int)
    meses_para_exibir = [meses_abreviados[mes] for mes in meses_numericos]
    ano = sorted(df['Ano'].unique().tolist(), key=int)
    situacao = df['situacao'].unique().tolist()
    cliente = df['Cliente'].unique().tolist()

    with st.expander("Filtros"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            vendedor_selecionado = st.selectbox("Selecionar Vendedor", options=['Todos'] + vendedores)
        with col2:
            mes_selecionado = st.selectbox("Selecionar Mes", options=['Todos'] + meses_para_exibir)
        with col3:
            ano_selecionado = st.selectbox("Selecionar Ano", options=['Todos'] + ano)
        with col4:
            situacao_selecionada = st.selectbox('Selecione a Situação', options=['Faturada'] + [s for s in situacao if s != 'Faturada'])

    
    if mes_selecionado != 'Todos':
        meses_revertidos = {v: k for k, v in meses_abreviados.items()}
        if mes_selecionado in meses_revertidos: 
            mes_selecionado_num = meses_revertidos[mes_selecionado]
        else:
            st.error(f"Erro: Mês selecionado '{mes_selecionado}' não encontrado.")
            return  
    else:
        mes_selecionado_num = 'Todos'

    df_filtrado = aplicar_filtros(df, vendedor_selecionado, mes_selecionado_num, ano_selecionado, situacao_selecionada)
  
    total_nf, total_qtd_produto, valor_total_item, total_custo_compra, total_lucro_venda = calcular_metricas(df_filtrado)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total de Notas", f"{total_nf}")
    col2.metric("Total de Produtos", f"{total_qtd_produto}")
    col3.metric("Faturamento Total", formatar_moeda(valor_total_item))
    col4.metric("Custo Total", formatar_moeda(total_custo_compra))
    col5.metric("Lucro Total", formatar_moeda(total_lucro_venda))

    

    if mes_selecionado != 'Todos' and ano_selecionado != 'Todos':
        mes_numero = meses_revertidos[mes_selecionado]

        if 'Dia' in df.columns:
            fig_vendas_diarias = criar_grafico_vendas_diarias(df_filtrado, mes_numero, ano_selecionado)
            st.plotly_chart(fig_vendas_diarias)
        else:
            st.warning("A coluna 'Dia' não está presente nos dados. Impossível gerar gráfico de vendas diárias.")
    else:
        def criar_grafico_meses(df):
            df_meses = df.groupby('Mes').agg({'Valor_Total_Item': 'sum'}).reset_index()
            df_meses = df_meses.sort_values(by='Mes') 
            df_meses["Valor_Monetario"] = df_meses["Valor_Total_Item"].apply(formatar_moeda)

            labels = {'Mes': 'Mês', 'Valor_Total_Item': 'Valor Total de Venda'}
            
            fig = px.bar(df_meses, x='Mes', y='Valor_Total_Item', title='Vendas por Mês', 
                        labels=labels, color='Valor_Total_Item', text=df_meses["Valor_Monetario"], 
                        template="plotly_white", hover_data={'Valor_Total_Item': False, 'Valor_Monetario': True})

            fig.update_traces(marker=dict(line=dict(color='black', width=1)),
                                hoverlabel=dict(bgcolor="black", font_size=22,
                                                font_family="Arial, sans-serif"))

            fig.update_layout(
                yaxis_title=labels['Valor_Total_Item'],
                xaxis_title=labels['Mes'],
                showlegend=False,
                height=400,
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(1, 13)),
                    ticktext=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                                'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                )
            )

            return fig
        
        fig_meses = criar_grafico_meses(df_filtrado)
        st.plotly_chart(fig_meses)
    
    
    def ranking_clientes(df, top_n=20):
        """Retorna os top N clientes com maior faturamento total, incluindo o número do ranking."""
        df_clientes = df.groupby('Cliente').agg({'Valor_Total_Item': 'sum'}).reset_index()
        df_clientes = df_clientes.sort_values(by='Valor_Total_Item', ascending=False).head(top_n)
        df_clientes['Ranking'] = range(1, len(df_clientes) + 1)  
        df_clientes['Valor_Total_Item'] = df_clientes['Valor_Total_Item'].apply(formatar_moeda)  
        df_clientes = df_clientes[['Ranking', 'Cliente', 'Valor_Total_Item']] 
        return df_clientes

    fig_linha = criar_grafico_barras(agrupar_e_somar(df_filtrado, 'Linha'), 'Linha', 'Valor_Total_Item',
                                    'Vendas por Linha de Produto', {'Valor_Total_Item': 'Valor Total de Venda'})
    st.plotly_chart(fig_linha)

    fig_vendedor = criar_grafico_barras(agrupar_e_somar(df_filtrado, 'Vendedor'), 'Vendedor', 'Valor_Total_Item',
                                        'Vendas por Vendedor', {'Valor_Total_Item': 'Valor Total de Venda'})
    st.plotly_chart(fig_vendedor)
    
    fig_produtos = criar_grafico_barras(produtos_mais_vendidos(df_filtrado), 'Descricao_produto', 'Valor_Total_Item',
                                        'Top 10 Produtos Mais Vendidos',
                                        {'Descricao_produto': 'Produto', 'Valor_Total_Item': 'Valor Total de Venda'})
    st.plotly_chart(fig_produtos)

    st.subheader("Top 20 Clientes por Faturamento Total")
    df_ranking = ranking_clientes(df_filtrado)
    df_ranking = df_ranking.reset_index(drop=True)

    st.dataframe(df_ranking, use_container_width=True)


######################################################################################################################


def renderizar_pagina_comparativo(df):
    st.title('Dashboard de Vendas Comparativo de Períodos')

    col1, col2 = st.columns(2)

    with col1:
        periodo1_opcao = st.selectbox("Período 1", ["Personalizado", "Últimos 30 dias", "Mês atual", "Ano anterior", "Mês anterior"])
        
        if periodo1_opcao == "Personalizado":
            data_inicio_1 = st.date_input("Início do Período 1", pd.to_datetime("2024-01-01").date(), format="DD/MM/YYYY")
            data_fim_1 = st.date_input("Fim do Período 1", pd.to_datetime("2024-02-28").date(), format="DD/MM/YYYY")
        elif periodo1_opcao == "Últimos 30 dias":
            data_fim_1 = pd.to_datetime("today").date()
            data_inicio_1 = (pd.to_datetime("today") - pd.Timedelta(days=30)).date()
        elif periodo1_opcao == "Mês atual":
            data_fim_1 = pd.to_datetime("today").date()
            data_inicio_1 = pd.to_datetime(f"{data_fim_1.year}-{data_fim_1.month}-01").date()
        elif periodo1_opcao == "Ano anterior":
            data_fim_1 = (pd.to_datetime("today") - pd.Timedelta(days=365)).date()
            data_inicio_1 = (pd.to_datetime(f"{data_fim_1.year}-01-01")).date()
        elif periodo1_opcao == "Mês anterior":
            data_fim_1 = pd.to_datetime("today").replace(day=1) - pd.Timedelta(days=1)  
            data_inicio_1 = data_fim_1.replace(day=1) 

    with col2:
        periodo2_opcao = st.selectbox("Período 2", ["Personalizado", "Últimos 30 dias", "Mês atual", "Ano anterior", "Comparar com ano anterior", "Mês anterior"])
        
        if periodo2_opcao == "Personalizado":
            data_inicio_2 = st.date_input("Início do Período 2", pd.to_datetime("2024-03-01").date(), format="DD/MM/YYYY")
            data_fim_2 = st.date_input("Fim do Período 2", pd.to_datetime("2024-03-31").date(), format="DD/MM/YYYY")
        elif periodo2_opcao == "Últimos 30 dias":
            data_fim_2 = pd.to_datetime("today").date()
            data_inicio_2 = (pd.to_datetime("today") - pd.Timedelta(days=30)).date()
        elif periodo2_opcao == "Mês atual":
            data_fim_2 = pd.to_datetime("today").date()
            data_inicio_2 = pd.to_datetime(f"{data_fim_2.year}-{data_fim_2.month}-01").date()
        elif periodo2_opcao == "Ano anterior":
            data_fim_2 = (pd.to_datetime("today") - pd.Timedelta(days=365)).date()
            data_inicio_2 = (pd.to_datetime(f"{data_fim_2.year}-01-01")).date()
        elif periodo2_opcao == "Comparar com ano anterior":
            data_inicio_2 = (pd.to_datetime(data_inicio_1) - pd.Timedelta(days=365)).date()
            data_fim_2 = (pd.to_datetime(data_fim_1) - pd.Timedelta(days=365)).date()
        elif periodo2_opcao == "Mês anterior":
            # Mês anterior
            data_fim_2 = pd.to_datetime("today").replace(day=1) - pd.Timedelta(days=1) 
            data_inicio_2 = data_fim_2.replace(day=1)  

    if st.button("Atualizar"):
        try:
            data_inicio_1 = pd.to_datetime(data_inicio_1)
            data_fim_1 = pd.to_datetime(data_fim_1)
            data_inicio_2 = pd.to_datetime(data_inicio_2)
            data_fim_2 = pd.to_datetime(data_fim_2)
        except ValueError:
            st.error("Datas inválidas. Verifique os formatos.")
            return

        df['Data_Emissao'] = pd.to_datetime(df['Data_Emissao'], format='mixed', dayfirst=True)
        df_faturado = df[df['situacao'] == 'Faturada'].copy()

        def filtrar_soma_vendas(df, data_col, valor_col, data_inicio, data_fim):
            df_filtrado = df[(df[data_col] >= data_inicio) & (df[data_col] <= data_fim)]
            return df_filtrado[valor_col].sum()

        def comparar_periodos(df, data_col, valor_col, periodo1, periodo2):
            soma_periodo1 = filtrar_soma_vendas(df, data_col, valor_col, *periodo1)
            soma_periodo2 = filtrar_soma_vendas(df, data_col, valor_col, *periodo2)

            if soma_periodo1 == 0:
                variacao = "Indefinida" if soma_periodo2 != 0 else "Sem variação"
            else:
                variacao = ((soma_periodo2 - soma_periodo1) / soma_periodo1) * 100

            return soma_periodo1, soma_periodo2, variacao

        soma_periodo1, soma_periodo2, variacao = comparar_periodos(df_faturado, 'Data_Emissao', 'Valor_Total_Item', (data_inicio_1, data_fim_1), (data_inicio_2, data_fim_2))

        st.subheader("Comparação entre os períodos selecionados:")
        col3, col4, col5 = st.columns(3)
        col3.metric("Vendas Período 1", formatar_moeda(soma_periodo1))
        col4.metric("Vendas Período 2", formatar_moeda(soma_periodo2))
        col5.metric("Variação (%)", f"{variacao:.2f}%" if isinstance(variacao, (int, float)) else variacao)

        st.subheader(" Comparação de Vendas por Período")

        dados_grafico = pd.DataFrame({
            "Período": ["Período 1", "Período 2"],
            "Valor": [soma_periodo1, soma_periodo2]
        })

        labels = {"Período": "Período", "Valor": "Valor Total"}
        fig_bar = criar_grafico_barras(dados_grafico, "Período", "Valor", "Comparação de Vendas Entre os Perírios", labels)

        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("Tendências Temporais")

        df_periodo1 = df_faturado[(df_faturado['Data_Emissao'] >= data_inicio_1) & (df_faturado['Data_Emissao'] <= data_fim_1)].copy()
        df_periodo2 = df_faturado[(df_faturado['Data_Emissao'] >= data_inicio_2) & (df_faturado['Data_Emissao'] <= data_fim_2)].copy()

        df_periodo1['Data'] = df_periodo1['Data_Emissao'].dt.date
        df_periodo2['Data'] = df_periodo2['Data_Emissao'].dt.date

        vendas_diarias_periodo1 = df_periodo1.groupby('Data')['Valor_Total_Item'].sum().reset_index()
        vendas_diarias_periodo2 = df_periodo2.groupby('Data')['Valor_Total_Item'].sum().reset_index()

        vendas_diarias_periodo1['Média Móvel'] = vendas_diarias_periodo1['Valor_Total_Item'].rolling(window=7, min_periods=1).mean()
        vendas_diarias_periodo2['Média Móvel'] = vendas_diarias_periodo2['Valor_Total_Item'].rolling(window=7, min_periods=1).mean()

        col_linha1, col_linha2 = st.columns(2)

        with col_linha1:
            fig_linha_periodo1 = px.line(
                vendas_diarias_periodo1, 
                x='Data', 
                y='Valor_Total_Item', 
                title='📊 Tendência Período 1', 
                labels={'Valor_Total_Item': 'Valor Total de Vendas', 'Data': 'Data'},
                line_shape="spline",  
                color_discrete_sequence=['#636EFA'],
                hover_data={'Data': False, 'Valor_Total_Item': False}
            )

            fig_linha_periodo1.add_scatter(
                x=vendas_diarias_periodo1['Data'], 
                y=vendas_diarias_periodo1['Média Móvel'],
                mode='lines', 
                name="Média Móvel (7 dias)", 
                line=dict(dash='dot', color='red')
            )

            st.plotly_chart(fig_linha_periodo1, use_container_width=True)

        with col_linha2:
            fig_linha_periodo2 = px.line(
                vendas_diarias_periodo2, 
                x='Data', 
                y='Valor_Total_Item', 
                title='📊 Tendência Período 2', 
                labels={'Valor_Total_Item': 'Valor Total de Vendas', 'Data': 'Data'},
                line_shape="spline",  
                color_discrete_sequence=['#EF553B'],
                hover_data={'Data': False, 'Valor_Total_Item': False}
            )

            fig_linha_periodo2.add_scatter(
                x=vendas_diarias_periodo2['Data'], 
                y=vendas_diarias_periodo2['Média Móvel'],
                mode='lines', 
                name="Média Móvel (7 dias)", 
                line=dict(dash='dot', color='red')
            )

            st.plotly_chart(fig_linha_periodo2, use_container_width=True)



        st.subheader("📅 Análise de Sazonalidade")

        traducao_dias = {
            "Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
            "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo"
        }

        dias_da_semana_ordem = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

        for df in [df_periodo1, df_periodo2]:
            df['Dia_da_Semana'] = df['Data_Emissao'].dt.day_name().map(traducao_dias)
            df['Período'] = 'Período 1' if df is df_periodo1 else 'Período 2'

        df_sazonalidade_combinada = pd.concat([
            df_periodo1[['Dia_da_Semana', 'Valor_Total_Item', 'Período']],
            df_periodo2[['Dia_da_Semana', 'Valor_Total_Item', 'Período']]
        ])

        df_sazonalidade_combinada['Dia_da_Semana'] = pd.Categorical(
            df_sazonalidade_combinada['Dia_da_Semana'], categories=dias_da_semana_ordem, ordered=True
        )

        df_sazonalidade_combinada['Total Vendido'] = df_sazonalidade_combinada['Valor_Total_Item'].apply(formatar_moeda)

        fig_boxplot_combinado = px.box(
            df_sazonalidade_combinada,
            x='Dia_da_Semana',
            y='Valor_Total_Item',
            color='Período',
            title='Comparação da Sazonalidade das Vendas por Dia da Semana',
            labels={'Valor_Total_Item': 'Valor Total de Vendas', 'Dia_da_Semana': 'Dia da Semana'},
            hover_data={'Dia_da_Semana': False, 'Período': False, 'Valor_Total_Item': False, 'Total Vendido': True}
        )

        fig_boxplot_combinado.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
        fig_boxplot_combinado.update_xaxes(categoryorder='array', categoryarray=dias_da_semana_ordem)
        fig_boxplot_combinado.update_layout(
            boxmode='group',
            margin=dict(l=40, r=40, t=60, b=40)
        )

        fig_boxplot_combinado.update_layout(
            hoverlabel=dict(
                bgcolor="black",
                font_size=22,
                font_family="Arial, sans-serif"
            )
        )
        st.plotly_chart(fig_boxplot_combinado, use_container_width=True)



################################################################################################################################################

def renderizar_pagina_vendedor(df):
    def processar_dados(df):
        df['Data_Emissao'] = pd.to_datetime(df['Data_Emissao'], format='mixed', dayfirst=True)
        df['Semana'] = df['Data_Emissao'].dt.isocalendar().week
        colunas_nf_unicas = ['NF', 'Data_Emissao', 'Vendedor', 'Valor_Total_Nota', 'Mes', 'Ano', 'Semana', 'situacao']
        df_nf_unicas = df.drop_duplicates(subset='NF')[colunas_nf_unicas].copy()
        df_nf_unicas = df_nf_unicas[df_nf_unicas['situacao'] == 'Faturada']

        meses_abreviados = {
            1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        }

        meses_numericos = sorted(df_nf_unicas['Mes'].unique().tolist(), key=int)
        mes = [meses_abreviados[mes] for mes in meses_numericos]

        ano = sorted(df_nf_unicas['Ano'].unique().tolist(), key=int)

        with st.expander("Filtros"):
            col1, col2 = st.columns(2)
            with col1:
                mes_selecionado = st.selectbox("Selecionar Mes", options=['Todos'] + mes, key="mes_selectbox")
            with col2:
                ano_selecionado = st.selectbox("Selecionar Ano", options=['Todos'] + ano, key="ano_selectbox")

        def aplicar_filtros(df, mes_selecionado, ano_selecionado):
            if mes_selecionado != 'Todos':
                meses_invertidos = {v: k for k, v in meses_abreviados.items()}
                mes_numero = meses_invertidos[mes_selecionado]
                df = df[df['Mes'] == mes_numero]
            if ano_selecionado != 'Todos':
                df = df[df['Ano'] == ano_selecionado]
            return df

        df_nf_unicas = aplicar_filtros(df_nf_unicas, mes_selecionado, ano_selecionado)

        df_resumo = df_nf_unicas.groupby(['Ano', 'Mes', 'Semana', 'Vendedor'])['NF'].count().reset_index(name='Quantidade_Notas_Semana')
        df_nf_unicas = pd.merge(df_nf_unicas, df_resumo, on=['Ano', 'Mes', 'Semana', 'Vendedor'], how='left')
        df_nf_unicas['Quantidade_Notas_Semana'] = df_nf_unicas['Quantidade_Notas_Semana'].fillna(0).astype(int)

        df_resumo_vendas = df_nf_unicas.groupby(['Ano', 'Mes', 'Semana', 'Vendedor'])['Valor_Total_Nota'].sum().reset_index(name='Soma_Venda_Semana')
        df_nf_unicas = pd.merge(df_nf_unicas, df_resumo_vendas, on=['Ano', 'Mes', 'Semana', 'Vendedor'], how='left')

        total_notas = df_nf_unicas['NF'].nunique()
        faturamento_total = df_nf_unicas['Valor_Total_Nota'].sum()

        col1, col2 = st.columns(2)
        col1.metric("Total de Notas", f"{total_notas}")
        col2.metric("Faturamento Total", formatar_moeda(faturamento_total))

        if mes_selecionado != 'Todos':
            df_ticket_medio = df_nf_unicas.groupby(['Vendedor', 'Semana'])['Valor_Total_Nota'].mean().reset_index(name='Ticket_Medio')
            df_pivot = df_ticket_medio.pivot(index='Vendedor', columns='Semana', values='Ticket_Medio')

            # Criando uma nova coluna com os valores formatados
            df_ticket_medio['Ticket Medio'] = df_ticket_medio['Ticket_Medio'].apply(formatar_moeda)

            st.subheader("Ticket Médio por Vendedor e Semana (Tabela)")


            df_pivot = df_pivot.applymap(formatar_moeda)

            html_table = df_pivot.to_html(classes='data', index=True)

            css = """
            <style type="text/css">
            table.data {
                border-collapse: collapse;
                width: 100%;
                background-color: #8FBC8F; /* Verde Médio para o fundo geral */
                color: #000; /* Cor do texto para contraste no fundo verde */
            }

            table.data th, table.data td {
                border: 2px solid black;
                padding: 8px;
                text-align: center;
                background-color: inherit; /* Herda o fundo verde da tabela */
            }

            table.data th {
                background-color: #2E8B57; /* Verde Marinho para o cabeçalho */
                color: #000000; /* Cor do texto branca para contraste no cabeçalho */
            }

            table.data tr:nth-child(even) {
                background-color: inherit; /* Herda o fundo verde da tabela */
            }

            table.data tr {
                color: #000; /* Cor do texto preta para contraste nas linhas */
            }
            </style>
            """
            components.html(css + html_table, height=300)

            st.subheader("Ticket Médio por Vendedor e Semana (Gráfico de Barras Agrupadas)")
            fig = px.bar(df_ticket_medio, x='Semana', y='Ticket_Medio', color='Vendedor', barmode='group',
                        title='Ticket Médio por Vendedor e Semana',
                        labels={'Ticket_Medio': 'Ticket Médio', 'Semana': 'Semana'},
                        color_continuous_scale=px.colors.sequential.Plasma,
                        text='Ticket Medio',
                        hover_data={'Semana': False, 'Ticket_Medio': False, 'Ticket Medio': True})  

           
            fig.update_traces(marker=dict(line=dict(color='black', width=1)),
                            hoverlabel=dict(bgcolor="black", font_size=22, font_family="Arial_bold, sans-serif"))

            fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

            # Definindo a ordem das semanas
            semanas_unicas = sorted(df_ticket_medio['Semana'].unique())
            fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=semanas_unicas,
                    ticktext=[str(semana) for semana in semanas_unicas]
                ),
                yaxis_title='Ticket Médio',
                template="plotly_white"
            )

            
            st.plotly_chart(fig)

        return df_nf_unicas

    df = processar_dados(df)

    df_styled = df.style.format({
        'Data_Emissao': lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '',
        'Valor_Total_Nota': formatar_moeda,
        'Soma_Venda_Semana': formatar_moeda, 
        'Quantidade_Notas_Semana': '{:,.0f}'
    }).applymap(lambda val: 'background-color: #ADD8E6; color: black' if isinstance(val, (int, float)) and val > 10000 else '', subset=['Valor_Total_Nota'])

    
    st.dataframe(df_styled, use_container_width=True)
