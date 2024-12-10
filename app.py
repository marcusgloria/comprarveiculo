import streamlit as st  
import pandas as pd  
import plotly.graph_objects as go  
import plotly.express as px  
from datetime import datetime  

class CalculadoraCombustivel:  
    def __init__(self):  
        self.preco_gasolina = 0  
        self.preco_etanol = 0  
        self.consumo_gasolina = 0  
        self.consumo_etanol = 0  

    def calcular_custo_por_km(self, preco, consumo):  
        return preco / consumo if consumo > 0 else 0  

    def combustivel_mais_vantajoso(self, preco_gasolina, preco_etanol, consumo_gasolina, consumo_etanol):  
        custo_km_gasolina = self.calcular_custo_por_km(preco_gasolina, consumo_gasolina)  
        custo_km_etanol = self.calcular_custo_por_km(preco_etanol, consumo_etanol)  

        if custo_km_etanol < custo_km_gasolina:  
            return "Etanol", custo_km_etanol, custo_km_gasolina  
        return "Gasolina", custo_km_gasolina, custo_km_etanol  

class AnalisadorCompraVeiculo:  
    def __init__(self, renda_mensal, patrimonio, custos_customizados=None):  
        self.renda_mensal = renda_mensal  
        self.patrimonio = patrimonio  
        self.limite_mensal = self.renda_mensal * 0.30  
        self.custos_customizados = custos_customizados or {}  

    def calcular_custos_fixos(self, valor_carro):  
        custos_padrao = {  
            'Combustível': self.custos_customizados.get('combustivel', 300),  
            'Seguro': self.custos_customizados.get('seguro_percentual', 0.04) * valor_carro / 12,  
            'IPVA': self.custos_customizados.get('ipva_percentual', 0.04) * valor_carro / 12,  
            'Manutenção': self.custos_customizados.get('manutencao_percentual', 0.02) * valor_carro / 12  
        }  

        # Adicionar custos extras customizados  
        for nome, valor in self.custos_customizados.get('custos_extras', {}).items():  
            custos_padrao[nome] = valor  

        return custos_padrao  

    def calcular_valor_financiamento(self, taxa_juros_anual, prazo_meses, valor_entrada=0):  
        taxa_mensal = taxa_juros_anual / 12 / 100  
        custos_fixos = sum(self.calcular_custos_fixos(40000).values())  
        parcela_maxima = self.limite_mensal - custos_fixos  
        valor_financiamento = parcela_maxima * (1 - (1 + taxa_mensal) ** -prazo_meses) / taxa_mensal  
        return valor_financiamento + valor_entrada  

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
    considerando sua renda mensal, patrimônio disponível e custos personalizados.  
    """)  

    # Tabs para diferentes análises  
    tab1, tab2, tab3 = st.tabs(["Análise Financeira", "Calculadora de Combustível", "Custos Personalizados"])  

    with tab1:  
        # Sidebar para inputs financeiros  
        with st.sidebar:  
            st.header("Dados Financeiros")  
            renda_mensal = st.number_input("Renda Mensal (R$)", min_value=0.0, value=5000.0, step=100.0)  
            patrimonio = st.number_input("Patrimônio Total (R$)", min_value=0.0, value=10000.0, step=1000.0)  
            valor_entrada = st.number_input("Valor de Entrada (R$)", min_value=0.0, value=0.0, step=1000.0)  

            st.header("Personalizar Análise")  
            valor_carro_exemplo = st.number_input("Valor do Carro para Análise (R$)",   
                                                min_value=0.0, value=40000.0, step=1000.0)  

        # Custos personalizados do usuário  
        custos_customizados = st.session_state.get('custos_customizados', {})  

        # Criar instância do analisador  
        analise = AnalisadorCompraVeiculo(renda_mensal, patrimonio, custos_customizados)  

        # Mostrar informações básicas  
        col1, col2, col3 = st.columns(3)  
        with col1:  
            st.metric("Limite Mensal (30% da renda)", f"R$ {analise.limite_mensal:.2f}")  
        with col2:  
            st.metric("Máximo à Vista (10% do patrimônio)", f"R$ {patrimonio * 0.1:.2f}")  
        with col3:  
            st.metric("Custos Fixos Estimados",   
                     f"R$ {sum(analise.calcular_custos_fixos(valor_carro_exemplo).values()):.2f}")  

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

        # Inputs personalizados para financiamento  
        col1, col2 = st.columns(2)  
        with col1:  
            taxas = st.multiselect(  
                "Selecione as taxas de juros anuais (%)",  
                options=[8, 10, 12, 15, 18, 20, 23, 25],  
                default=[12, 15, 18, 23]  
            )  
        with col2:  
            prazos = st.multiselect(  
                "Selecione os prazos (meses)",  
                options=[24, 36, 48, 60, 72],  
                default=[36, 48, 60]  
            )  

        # Criar DataFrame com cenários  
        dados = []  
        for taxa in taxas:  
            for prazo in prazos:  
                valor = analise.calcular_valor_financiamento(taxa, prazo, valor_entrada)  
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

    with tab2:  
        st.header("⛽ Calculadora de Combustível")  

        calc = CalculadoraCombustivel()  

        col1, col2 = st.columns(2)  
        with col1:  
            st.subheader("Preços")  
            calc.preco_gasolina = st.number_input("Preço da Gasolina (R$/L)",   
                                                min_value=0.0, value=5.0, step=0.01)  
            calc.preco_etanol = st.number_input("Preço do Etanol (R$/L)",   
                                              min_value=0.0, value=3.5, step=0.01)  

        with col2:  
            st.subheader("Consumo")  
            calc.consumo_gasolina = st.number_input("Consumo com Gasolina (km/L)",   
                                                  min_value=0.0, value=12.0, step=0.1)  
            calc.consumo_etanol = st.number_input("Consumo com Etanol (km/L)",   
                                                min_value=0.0, value=8.0, step=0.1)  

        if st.button("Calcular Combustível Mais Vantajoso"):  
            combustivel, custo_vantajoso, custo_alternativo = calc.combustivel_mais_vantajoso(  
                calc.preco_gasolina, calc.preco_etanol,   
                calc.consumo_gasolina, calc.consumo_etanol  
            )  

            st.success(f"O combustível mais vantajoso é: {combustivel}")  
            st.write(f"Custo por km com {combustivel}: R$ {custo_vantajoso:.3f}")  
            st.write(f"Custo por km com o combustível alternativo: R$ {custo_alternativo:.3f}")  

            # Calcular economia mensal estimada  
            km_mes = st.number_input("Quilometragem mensal estimada",   
                                   min_value=0, value=1000, step=100)  
            economia = abs(custo_vantajoso - custo_alternativo) * km_mes  
            st.info(f"Economia mensal estimada: R$ {economia:.2f}")  

    with tab3:  
        st.header("🔧 Personalização de Custos")  

        # Custos básicos  
        st.subheader("Custos Básicos Mensais")  
        combustivel = st.number_input("Gasto mensal com Combustível (R$)",   
                                    min_value=0.0, value=300.0, step=50.0)  

        # Percentuais  
        st.subheader("Percentuais sobre o valor do carro (ao ano)")  
        seguro_percentual = st.slider("Percentual do Seguro", 0.0, 10.0, 4.0) / 100  
        ipva_percentual = st.slider("Percentual do IPVA", 0.0, 10.0, 4.0) / 100  
        manutencao_percentual = st.slider("Percentual de Manutenção", 0.0, 10.0, 2.0) / 100  

        # Custos extras  
        st.subheader("Custos Extras Mensais")  
        num_custos_extras = st.number_input("Número de custos extras",   
                                          min_value=0, max_value=5, value=0)  

        custos_extras = {}  
        for i in range(num_custos_extras):  
            col1, col2 = st.columns(2)  
            with col1:  
                nome = st.text_input(f"Nome do custo extra {i+1}")  
            with col2:  
                valor = st.number_input(f"Valor do custo extra {i+1}",   
                                      min_value=0.0, step=50.0)  
            if nome and valor > 0:  
                custos_extras[nome] = valor  

        # Salvar custos personalizados  
        if st.button("Salvar Configurações de Custos"):  
            st.session_state.custos_customizados = {  
                'combustivel': combustivel,  
                'seguro_percentual': seguro_percentual,  
                'ipva_percentual': ipva_percentual,  
                'manutencao_percentual': manutencao_percentual,  
                'custos_extras': custos_extras  
            }  
            st.success("Configurações de custos salvas com sucesso!")  

    # Recomendações  
    st.header("📋 Recomendações")  
    recomendacoes = [  
        "Procure carros usados para evitar depreciação inicial",  
        "Compare diferentes opções de financiamento",  
        "Considere fazer uma entrada maior para reduzir juros",  
        "Mantenha uma reserva de emergência para manutenção",  
        "Compare os custos de combustível na sua região",  
        "Pesquise diferentes seguradoras para encontrar o melhor preço",  
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