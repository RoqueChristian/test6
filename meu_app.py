import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

def formatar_moeda(valor, simbolo_moeda="R$"):
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
    """Aplica filtros ao DataFrame com ordenação numérica de mês e ano."""
    df_filtrado = df.copy()

    # Filtro por vendedor
    if vendedor != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Vendedor'] == vendedor]

    # Filtro por mês
    if mes != 'Todos':
        meses_abreviados = {
            'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
            'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12
        }
        mes_numero = meses_abreviados[mes]
        df_filtrado = df_filtrado[df_filtrado['Mes'] == mes_numero]

    # Filtro por ano
    if ano != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Ano'] == ano]

    # Filtro por situação
    if situacao != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['situacao'] == situacao]

    return df_filtrado

def criar_grafico_barras(df, x, y, title, labels):
    fig = px.bar(df, x=x, y=y, title=title, labels=labels, 
                 color=y, text_auto=True, template="plotly_white", 
                 hover_data={x: False, y: ":,.2f"})

    fig.update_traces(marker=dict(line=dict(color='black', width=1)), 
                      hoverlabel=dict(bgcolor="white", font_size=14, 
                                      font_family="Arial, sans-serif"))

    fig.update_layout(yaxis_title=labels.get(y, y), 
                      xaxis_title=labels.get(x, x), 
                      showlegend=False, height=400)

    return fig



##########################################################################################################################################



def renderizar_pagina_vendas(df):
    
    vendedores = df['Vendedor'].unique().tolist()

    meses_abreviados = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    meses_numericos = sorted(df['Mes'].unique().tolist(), key=int)
    mes = [meses_abreviados[mes] for mes in meses_numericos]

    ano = sorted(df['Ano'].unique().tolist(), key=int)
    situacao = df['situacao'].unique().tolist()
    cliente = df['Cliente'].unique().tolist()

    with st.expander("Filtros"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            vendedor_selecionado = st.selectbox("Selecionar Vendedor", options=['Todos'] + vendedores)
        with col2:
            mes_selecionado = st.selectbox("Selecionar Mes", options=['Todos'] + mes)
        with col3:
            ano_selecionado = st.selectbox("Selecionar Ano", options=['Todos'] + ano)
        with col4:
            situacao_selecionada = st.selectbox('Selecione a Situação', options=['Faturada'] + [s for s in situacao if s != 'Faturada'])

    df_filtrado = aplicar_filtros(df, vendedor_selecionado, mes_selecionado, ano_selecionado, situacao_selecionada)


        
    total_nf, total_qtd_produto, valor_total_item, total_custo_compra, total_lucro_venda = calcular_metricas(df_filtrado)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total de Notas", f"{total_nf}")
    col2.metric("Total de Produtos", f"{total_qtd_produto}")
    col3.metric("Faturamento Total", formatar_moeda(valor_total_item))
    col4.metric("Custo Total", formatar_moeda(total_custo_compra))
    col5.metric("Lucro Total", formatar_moeda(total_lucro_venda))

    def criar_grafico_meses(df):
        df_meses = df.groupby('Mes').agg({'Valor_Total_Item': 'sum'}).reset_index()
        df_meses = df_meses.sort_values(by='Mes') 

        labels = {'Mes': 'Mês', 'Valor_Total_Item': 'Valor Total de Venda'}
        fig = criar_grafico_barras(df_meses, 'Mes', 'Valor_Total_Item', 'Vendas por Mês', labels)

        
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            )
        )

        return fig
    
    def criar_grafico_dias(df, mes_selecionado):
        if mes_selecionado == 'Todos':
            return None  

        df_dias = df[df['Mes'] == mes_selecionado].groupby('Dia').agg({'Valor_Total_Item': 'sum'}).reset_index()
        df_dias = df_dias.sort_values(by='Dia')  

        labels = {'Dia': 'Dia do Mês', 'Valor_Total_Item': 'Valor Total de Venda'}
        fig = criar_grafico_barras(df_dias, 'Dia', 'Valor_Total_Item', f'Vendas por Dia - Mês {mes_selecionado}', labels)

        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1, 32)), 
                ticktext=[str(i) for i in range(1, 32)]
            )
        )

        return fig

    if mes_selecionado != 'Todos':
        st.subheader(f"Vendas por Dia no Mês {mes_selecionado}")
        fig_dias = criar_grafico_dias(df_filtrado, mes_selecionado)
        if fig_dias:
            st.plotly_chart(fig_dias)

    def ranking_clientes(df, top_n=20):
        """Retorna os top N clientes com maior faturamento total, incluindo o número do ranking."""
        df_clientes = df.groupby('Cliente').agg({'Valor_Total_Item': 'sum'}).reset_index()
        df_clientes = df_clientes.sort_values(by='Valor_Total_Item', ascending=False).head(top_n)
        df_clientes['Ranking'] = range(1, len(df_clientes) + 1)  
        df_clientes['Valor_Total_Item'] = df_clientes['Valor_Total_Item'].apply(formatar_moeda)  
        df_clientes = df_clientes[['Ranking', 'Cliente', 'Valor_Total_Item']] 
        return df_clientes


    fig_meses = criar_grafico_meses(df_filtrado)
    st.plotly_chart(fig_meses)

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
        data_inicio_1 = st.date_input("Início do Período 1", pd.to_datetime("2024-01-01").date())
        data_fim_1 = st.date_input("Fim do Período 1", pd.to_datetime("2024-02-28").date())

    with col2:
        data_inicio_2 = st.date_input("Início do Período 2", pd.to_datetime("2024-03-01").date())
        data_fim_2 = st.date_input("Fim do Período 2", pd.to_datetime("2024-03-31").date())


    data_inicio_1 = pd.to_datetime(data_inicio_1)
    data_fim_1 = pd.to_datetime(data_fim_1)
    data_inicio_2 = pd.to_datetime(data_inicio_2)
    data_fim_2 = pd.to_datetime(data_fim_2)


    df['Data_Emissao'] = pd.to_datetime(df['Data_Emissao'], format='mixed', dayfirst=True)

    # Filtrar para incluir apenas notas com situação "Faturada"
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
    col3.metric("Vendas Período 1", f"R$ {soma_periodo1:,.2f}")
    col4.metric("Vendas Período 2", f"R$ {soma_periodo2:,.2f}")
    col5.metric("Variação (%)", f"{variacao:.2f}%" if isinstance(variacao, (int, float)) else variacao)

    # ---------------------  GRÁFICO DE BARRAS COMPARATIVO ---------------------

    st.subheader(" Comparação de Vendas por Período")

    fig_bar = px.bar(
        x=["Período 1", "Período 2"],
        y=[soma_periodo1, soma_periodo2],
        text=[f"R$ {soma_periodo1:,.2f}", f"R$ {soma_periodo2:,.2f}"],
        color=["Período 1", "Período 2"],
        color_discrete_sequence=["blue", "green"]
    )

    fig_bar.update_layout(
        title="Comparação de Vendas Entre os Períodos",
        xaxis_title="Período",
        yaxis_title="Valor Total",
        showlegend=False
    )

    st.plotly_chart(fig_bar, use_container_width=True)



########################################################################################################3########3



# def renderizar_pagina_vendedor(df):
#     def processar_dados(df):
#         df['Data_Emissao'] = pd.to_datetime(df['Data_Emissao'], format='mixed', dayfirst=True)
#         df['Semana'] = df['Data_Emissao'].dt.isocalendar().week
#         colunas_nf_unicas = ['NF', 'Data_Emissao', 'Vendedor', 'Valor_Total_Nota', 'Mes', 'Ano', 'Semana', 'situacao']
#         df_nf_unicas = df.drop_duplicates(subset='NF')[colunas_nf_unicas].copy()

#         # Filtrar diretamente por "Faturada"
#         df_nf_unicas = df_nf_unicas[df_nf_unicas['situacao'] == 'Faturada']

#         meses_abreviados = {
#             1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
#             7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
#         }

#         meses_numericos = sorted(df_nf_unicas['Mes'].unique().tolist(), key=int)
#         mes = [meses_abreviados[mes] for mes in meses_numericos]

#         ano = sorted(df_nf_unicas['Ano'].unique().tolist(), key=int)

#         with st.expander("Filtros"):
#             col1, col2 = st.columns(2)
#             with col1:
#                 mes_selecionado = st.selectbox("Selecionar Mes", options=['Todos'] + mes, key="mes_selectbox")
#             with col2:
#                 ano_selecionado = st.selectbox("Selecionar Ano", options=['Todos'] + ano, key="ano_selectbox")

#         def aplicar_filtros(df, mes_selecionado, ano_selecionado):
#             if mes_selecionado != 'Todos':
#                 meses_invertidos = {v: k for k, v in meses_abreviados.items()}
#                 mes_numero = meses_invertidos[mes_selecionado]
#                 df = df[df['Mes'] == mes_numero]
#             if ano_selecionado != 'Todos':
#                 df = df[df['Ano'] == ano_selecionado]
#             return df

#         df_nf_unicas = aplicar_filtros(df_nf_unicas, mes_selecionado, ano_selecionado)

#         df_resumo = df_nf_unicas.groupby(['Ano', 'Mes', 'Semana', 'Vendedor'])['NF'].count().reset_index(name='Quantidade_Notas_Semana')
#         df_nf_unicas = pd.merge(df_nf_unicas, df_resumo, on=['Ano', 'Mes', 'Semana', 'Vendedor'], how='left')
#         df_nf_unicas['Quantidade_Notas_Semana'] = df_nf_unicas['Quantidade_Notas_Semana'].fillna(0).astype(int)

#         df_resumo_vendas = df_nf_unicas.groupby(['Ano', 'Mes', 'Semana', 'Vendedor'])['Valor_Total_Nota'].sum().reset_index(name='Soma_Venda_Semana')
#         df_nf_unicas = pd.merge(df_nf_unicas, df_resumo_vendas, on=['Ano', 'Mes', 'Semana', 'Vendedor'], how='left')

#         total_notas = df_nf_unicas['NF'].nunique()
#         faturamento_total = df_nf_unicas['Valor_Total_Nota'].sum()

#         col1, col2 = st.columns(2)
#         col1.metric("Total de Notas", f"{total_notas}")
#         col2.metric("Faturamento Total", formatar_moeda(faturamento_total))

#         if mes_selecionado != 'Todos':
#             df_ticket_medio = df_nf_unicas.groupby(['Vendedor', 'Semana'])['Valor_Total_Nota'].mean().reset_index(name='Ticket_Medio')
#             df_pivot = df_ticket_medio.pivot(index='Vendedor', columns='Semana', values='Ticket_Medio')

#             st.subheader("Ticket Médio por Vendedor e Semana (Tabela)")
#             st.dataframe(df_pivot, use_container_width=True)

#             st.subheader("Ticket Médio por Vendedor e Semana (Gráfico de Barras Agrupadas)")
#             fig = px.bar(df_ticket_medio, x='Semana', y='Ticket_Medio', color='Vendedor', barmode='group',
#                          title='Ticket Médio por Vendedor e Semana',
#                          labels={'Ticket_Medio': 'Ticket Médio', 'Semana': 'Semana'},
#                          color_continuous_scale=px.colors.sequential.Plasma,
#                          text_auto=True,
#                          hover_data={'Semana': False, 'Ticket_Medio': ":,.2f"})

#             fig.update_traces(marker=dict(line=dict(color='black', width=1)),
#                               hoverlabel=dict(bgcolor="white", font_size=16,
#                                               font_family="Arial_bold, sans-serif"))

#             fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

#             semanas_unicas = sorted(df_ticket_medio['Semana'].unique())
#             fig.update_layout(
#                 xaxis=dict(
#                     tickmode='array',
#                     tickvals=semanas_unicas,
#                     ticktext=[str(semana) for semana in semanas_unicas]
#                 ),
#                 yaxis_title='Ticket Médio',
#                 template="plotly_white"
#             )

#             fig.update_traces(marker=dict(line=dict(color='black', width=1)))
#             st.plotly_chart(fig)

#         return df_nf_unicas

#     df = processar_dados(df)
#     st.dataframe(df, use_container_width=True)


def renderizar_pagina_vendedor(df):
    def processar_dados(df):
        df['Data_Emissao'] = pd.to_datetime(df['Data_Emissao'], format='mixed', dayfirst=True)
        df['Semana'] = df['Data_Emissao'].dt.isocalendar().week
        colunas_nf_unicas = ['NF', 'Data_Emissao', 'Vendedor', 'Valor_Total_Nota', 'Mes', 'Ano', 'Semana', 'situacao']
        df_nf_unicas = df.drop_duplicates(subset='NF')[colunas_nf_unicas].copy()

        # Filtrar diretamente por "Faturada"
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

            st.subheader("Ticket Médio por Vendedor e Semana (Tabela)")

            # Formatar os valores como moeda brasileira com vírgula como separador decimal
            def format_currency(val):
                if pd.isna(val):
                    return ''
                return f'R$ {val:,.2f}'.replace('.', ',').replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')

            df_pivot = df_pivot.applymap(format_currency)

            # Exibir os números das semanas como cabeçalho das colunas
            html_table = df_pivot.to_html(classes='data', index=True)

            css = """
            <style type="text/css">
            table.data {
              border-collapse: collapse;
              width: 100%;
            }
            table.data th, table.data td {
              border: 2px solid black;
              padding: 8px;
              text-align: center;
            }
            table.data th {
              background-color: #f2f2f2;
            }
            table.data tr:nth-child(even) {
              background-color: #f9f9f9;
            }
            </style>
            """
            components.html(css + html_table, height=300)

            st.subheader("Ticket Médio por Vendedor e Semana (Gráfico de Barras Agrupadas)")
            fig = px.bar(df_ticket_medio, x='Semana', y='Ticket_Medio', color='Vendedor', barmode='group',
                         title='Ticket Médio por Vendedor e Semana',
                         labels={'Ticket_Medio': 'Ticket Médio', 'Semana': 'Semana'},
                         color_continuous_scale=px.colors.sequential.Plasma,
                         text_auto=True,
                         hover_data={'Semana': False, 'Ticket_Medio': ":,.2f"})

            fig.update_traces(marker=dict(line=dict(color='black', width=1)),
                              hoverlabel=dict(bgcolor="white", font_size=16,
                                              font_family="Arial_bold, sans-serif"))

            fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

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

            fig.update_traces(marker=dict(line=dict(color='black', width=1)))
            st.plotly_chart(fig)

        return df_nf_unicas

    df = processar_dados(df)
    st.dataframe(df, use_container_width=True)
