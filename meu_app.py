import streamlit as st
import pandas as pd
import plotly.express as px


# Funções de Formatação
def formatar_moeda(valor, simbolo_moeda="R$"):
    """Formata um valor numérico como moeda."""
    return f"{simbolo_moeda} {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Funções de Agregação e Cálculo
def calcular_metricas(df):
    """Calcula e retorna métricas de vendas."""
    total_nf = len(df['NF'].unique())
    total_qtd_produto = df['Qtd_Produto'].sum()
    valor_total_item = df['Valor_Total_Item'].sum()
    total_custo_compra = df['Total_Custo_Compra'].sum()
    total_lucro_venda = df['Total_Lucro_Venda_Item'].sum()
    return total_nf, total_qtd_produto, valor_total_item, total_custo_compra, total_lucro_venda

def agrupar_e_somar(df, coluna_agrupamento):
    """Agrupa e soma vendas por uma coluna específica."""
    return df.groupby(coluna_agrupamento).agg(
        {'Valor_Total_Item': 'sum', 'Total_Custo_Compra': 'sum', 'Total_Lucro_Venda_Item': 'sum'}
    ).reset_index()

def produtos_mais_vendidos(df, top_n=10, ordenar_por='Valor_Total_Item'):
    """Retorna os top N produtos mais vendidos."""
    df_agrupado = df.groupby('Descricao_produto')[ordenar_por].sum().reset_index()
    df_ordenado = df_agrupado.sort_values(by=ordenar_por, ascending=False)
    return df_ordenado.head(top_n)

# Funções de Filtro
def aplicar_filtros(df, vendedor='Todos', mes='Todos', ano='Todos', situacao='Todos'):
    """Aplica filtros ao DataFrame."""
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

# Funções de Gráficos
def criar_grafico_barras(df, x, y, title, labels):
    """Cria e retorna um gráfico de barras com layout aprimorado."""
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


# Renderiza a página de vendas com filtros, métricas e gráficos.
def renderizar_pagina_vendas(df):
    vendedores = df['Vendedor'].unique().tolist()
    mes = df['Mes'].unique().tolist()
    ano = df['Ano'].unique().tolist()
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
            situacao_selecionada = st.selectbox('Selecione a Situação', options=['Todos'] + situacao)

    df_filtrado = aplicar_filtros(df, vendedor_selecionado, mes_selecionado, ano_selecionado, situacao_selecionada)

    # Métricas
    total_nf, total_qtd_produto, valor_total_item, total_custo_compra, total_lucro_venda = calcular_metricas(df_filtrado)
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total de Notas", f"{total_nf}")
    col2.metric("Total de Produtos", f"{total_qtd_produto}")
    col3.metric("Faturamento Total", formatar_moeda(valor_total_item))
    col4.metric("Custo Total", formatar_moeda(total_custo_compra))
    col5.metric("Lucro Total", formatar_moeda(total_lucro_venda))

    def criar_grafico_meses(df):
        """Cria um gráfico de vendas por mês com o mesmo layout padrão."""
        df_meses = df.groupby('Mes').agg({'Valor_Total_Item': 'sum'}).reset_index()
        df_meses = df_meses.sort_values(by='Mes')  # Garante que os meses estejam ordenados corretamente

        labels = {'Mes': 'Mês', 'Valor_Total_Item': 'Valor Total de Venda'}
        fig = criar_grafico_barras(df_meses, 'Mes', 'Valor_Total_Item', 'Vendas por Mês', labels)

        # Ajuste adicional para garantir que os meses sejam mostrados corretamente
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=[str(i) for i in range(1, 13)]
            )
        )

        return fig
    
    def criar_grafico_dias(df, mes_selecionado):
        """Cria um gráfico de vendas por dia dentro do mês selecionado."""
        if mes_selecionado == 'Todos':
            return None  # Se nenhum mês foi selecionado, não gera gráfico

        df_dias = df[df['Mes'] == mes_selecionado].groupby('Dia').agg({'Valor_Total_Item': 'sum'}).reset_index()
        df_dias = df_dias.sort_values(by='Dia')  # Ordena os dias corretamente

        labels = {'Dia': 'Dia do Mês', 'Valor_Total_Item': 'Valor Total de Venda'}
        fig = criar_grafico_barras(df_dias, 'Dia', 'Valor_Total_Item', f'Vendas por Dia - Mês {mes_selecionado}', labels)

        # Ajuste para garantir que todos os dias de 1 a 31 sejam exibidos
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1, 32)),  # De 1 a 31
                ticktext=[str(i) for i in range(1, 32)]
            )
        )

        return fig

    # Verifica se um mês específico foi escolhido e gera o gráfico
    if mes_selecionado != 'Todos':
        st.subheader(f"Vendas por Dia no Mês {mes_selecionado}")
        fig_dias = criar_grafico_dias(df_filtrado, mes_selecionado)
        if fig_dias:
            st.plotly_chart(fig_dias)

    # def criar_grafico_top_produtos(df, top_n=10):
    #     """Cria um gráfico dos top N produtos mais vendidos."""
    #     df_top_produtos = produtos_mais_vendidos(df, top_n)

    #     labels = {'Descricao_produto': 'Produto', 'Valor_Total_Item': 'Valor Total de Venda'}
    #     fig = criar_grafico_barras(df_top_produtos, 'Descricao_produto', 'Valor_Total_Item', 
    #                             f'Top {top_n} Produtos Mais Vendidos', labels)

    #     return fig

    # Adicionar o gráfico na página
    
    # fig_top_produtos = criar_grafico_top_produtos(df_filtrado)
    # st.plotly_chart(fig_top_produtos, key="top_produtos")

    def ranking_clientes(df, top_n=20):
        """Retorna os top N clientes com maior faturamento total, incluindo o número do ranking."""
        df_clientes = df.groupby('Cliente').agg({'Valor_Total_Item': 'sum'}).reset_index()
        df_clientes = df_clientes.sort_values(by='Valor_Total_Item', ascending=False).head(top_n)
        df_clientes['Ranking'] = range(1, len(df_clientes) + 1)  # Adiciona o número do ranking
        df_clientes['Valor_Total_Item'] = df_clientes['Valor_Total_Item'].apply(formatar_moeda)  # Formatar valores
        df_clientes = df_clientes[['Ranking', 'Cliente', 'Valor_Total_Item']]  # Organiza a ordem das colunas
        return df_clientes

    


    # Adicionar o gráfico na página
    fig_meses = criar_grafico_meses(df_filtrado)
    st.plotly_chart(fig_meses)

    # Gráficos
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

    # Exibir o ranking em formato de tabela
    st.subheader("Top 20 Clientes por Faturamento Total")
    df_ranking = ranking_clientes(df_filtrado)

    # Resetar o índice do DataFrame para remover o índice padrão
    df_ranking = df_ranking.reset_index(drop=True)

    # Exibir a tabela no Streamlit
    st.dataframe(df_ranking, use_container_width=True)

    