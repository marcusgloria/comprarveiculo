import streamlit as st  
import pandas as pd  
import plotly.graph_objects as go  
import plotly.express as px  
from datetime import datetime  

class AnalisadorCompraVeiculo:  
    def __init__(self, renda_mensal, patrimonio):  
        self.renda_mensal = renda_mensal  
        self.patrimonio = patrimonio  
        self.limite_mensal = self.renda_mensal * 0.30  

    def calcular_custos_fixos(self, valor_carro):  
        custos = {  
            'Combustível': 300,  
            'Seguro': valor_carro * 0.04 / 12,  
            'IPVA': valor_carro * 0.04 / 12,  
            'Manutenção': valor_carro * 0.02 / 12  
        }  
        return custos  

    def calcular_valor_financiamento(self, taxa_juros_anual, prazo_meses):  
        taxa_mensal = taxa_juros_anual / 12 / 100  
        custos_fixos = sum(self.calcular_custos_fixos(40000).values())  
        parcela_maxima = self.limite_mensal - custos_fixos  
        valor_financiamento = parcela_maxima * (1 - (1 + taxa_mensal) ** -prazo_meses) / taxa_mensal  
        return valor_financiamento  

def criar_grafico_custos(custos):  
    fig = px.pie(  
        values=list(custos.values()),  
        names=list(custos.keys()),  
        title='Distribuição dos Custos Mensais'  
    )  
    return fig  

def criar_grafico_financiamento(df):  
    fig = px.line(  
        df,  
        x='Prazo',  
        y='Valor Financiável',  
        color='Taxa',  
        title='Valores Financiáveis por Prazo e Taxa',  
        labels={'Prazo': 'Prazo (meses)', 'Valor Financiável': 'Valor Máximo Financiável (R$)'}  
    )  
    return fig  

def main():  
    st.set_page_config(page_title="Análise de Compra de Veículo", layout="wide")  

    # Título e descrição  
    st.title("📊 Analisador de Compra de Veículo")  
    st.markdown("""  
    Esta ferramenta ajuda você a analisar diferentes cenários para compra de um veículo,  
    considerando sua renda mensal e patrimônio disponível.  
    """)  

    # Sidebar para inputs  
    with st.sidebar:  
        st.header("Dados Financeiros")  
        renda_mensal = st.number_input("Renda Mensal (R$)", min_value=0.0, value=5000.0, step=100.0)  
        patrimonio = st.number_input("Patrimônio Total (R$)", min_value=0.0, value=10000.0, step=1000.0)  

        st.header("Personalizar Análise")  
        valor_carro_exemplo = st.number_input("Valor do Carro para Análise (R$)", min_value=0.0, value=40000.0, step=1000.0)  

    # Criar instância do analisador  
    analise = AnalisadorCompraVeiculo(renda_mensal, patrimonio)  

    # Mostrar informações básicas  
    col1, col2, col3 = st.columns(3)  
    with col1:  
        st.metric("Limite Mensal (30% da renda)", f"R$ {analise.limite_mensal:.2f}")  
    with col2:  
        st.metric("Máximo à Vista (10% do patrimônio)", f"R$ {patrimonio * 0.1:.2f}")  
    with col3:  
        st.metric("Custos Fixos Estimados", f"R$ {sum(analise.calcular_custos_fixos(valor_carro_exemplo).values()):.2f}")  

    # Análise de Custos  
    st.header("📈 Análise de Custos Mensais")  
    custos = analise.calcular_custos_fixos(valor_carro_exemplo)  
    col1, col2 = st.columns([2, 1])  

    with col1:  
        st.plotly_chart(criar_grafico_custos(custos), use_container_width=True)  

    with col2:  
        st.subheader("Detalhamento dos Custos")  
        for item, valor in custos.items():  
            st.write(f"{item}: R$ {valor:.2f}")  

    # Cenários de Financiamento  
    st.header("💰 Cenários de Financiamento")  

    # Criar DataFrame com cenários  
    dados = []  
    taxas = [12, 15, 18, 23]  
    prazos = [36, 48, 60]  

    for taxa in taxas:  
        for prazo in prazos:  
            valor = analise.calcular_valor_financiamento(taxa, prazo)  
            dados.append({  
                'Taxa': f'{taxa}%',  
                'Prazo': prazo,  
                'Valor Financiável': valor  
            })  

    df = pd.DataFrame(dados)  

    # Mostrar gráfico de cenários  
    st.plotly_chart(criar_grafico_financiamento(df), use_container_width=True)  

    # Mostrar tabela de cenários  
    st.subheader("Tabela de Cenários")  
    st.dataframe(df.style.format({'Valor Financiável': 'R$ {:,.2f}'}))  

    # Recomendações  
    st.header("📋 Recomendações")  
    recomendacoes = [  
        "Procure carros usados para evitar depreciação inicial",  
        "Compare diferentes opções de financiamento",  
        "Considere fazer uma entrada maior para reduzir juros",  
        "Mantenha uma reserva de emergência para manutenção",  
    ]  

    if patrimonio * 0.1 < 10000:  
        recomendacoes.insert(0, "Considere juntar mais dinheiro antes de comprar à vista")  

    for rec in recomendacoes:  
        st.write(f"• {rec}")  

    # Footer  
    st.markdown("---")  
    st.markdown(  
        """  
        <div style='text-align: center'>  
            <p>Desenvolvido com ❤️ | Última atualização: Dezembro 2023</p>  
        </div>  
        """,  
        unsafe_allow_html=True  
    )  

if __name__ == "__main__":  
    main()  

# Requirements (save as requirements.txt):  
# streamlit  
# pandas  
# plotly  
