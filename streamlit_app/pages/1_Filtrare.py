import streamlit as st
import pandas as pd
from pathlib import Path


DATA_PATH = Path(__file__).parent.parent.parent / "data" / "Sample - Superstore.csv"


@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(DATA_PATH, encoding='latin-1')

    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%m/%d/%Y')
    return df


df = load_data()

st.title("🔍 Filtrare interactivă a comenzilor")
st.markdown("""
Folosește filtrele din **bara laterală (sidebar)** pentru a explora comenzile 
Superstore după regiune, segment, categorie și caracteristici financiare.
""")
st.markdown("---")

# filtre in sidebar
st.sidebar.header("🎛️ Filtre")

regiuni = sorted(df['Region'].unique())
regiuni_sel = st.sidebar.multiselect("🌎 Regiuni", options=regiuni, default=regiuni)

segmente = sorted(df['Segment'].unique())
segmente_sel = st.sidebar.multiselect("👥 Segmente clienți", options=segmente, default=segmente)

categorii = sorted(df['Category'].unique())
categorii_sel = st.sidebar.multiselect("📂 Categorii produse", options=categorii, default=categorii)

discount_min, discount_max = st.sidebar.slider(
    "💸 Interval Discount",
    min_value=0.0,
    max_value=0.8,
    value=(0.0, 0.8),
    step=0.05,
    format="%.0f%%"
)

sales_max = float(df['Sales'].max())
sales_range = st.sidebar.slider(
    "💵 Interval Vânzări ($)",
    min_value=0.0,
    max_value=sales_max,
    value=(0.0, sales_max),
    step=100.0
)

ship_optiuni = ["Toate"] + sorted(df['Ship Mode'].unique().tolist())
ship_sel = st.sidebar.selectbox("🚚 Mod de livrare", options=ship_optiuni)

profit_filter = st.sidebar.radio(
    "💰 Tipul de comenzi",
    options=["Toate", "Doar profitabile (Profit > 0)", "Doar în pierdere (Profit < 0)"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Modifică filtrele și rezultatele se actualizează automat")

# aplicam filtrele folosind loc
df_filtrat = df.loc[
    (df['Region'].isin(regiuni_sel)) &
    (df['Segment'].isin(segmente_sel)) &
    (df['Category'].isin(categorii_sel)) &
    (df['Discount'] >= discount_min) &
    (df['Discount'] <= discount_max) &
    (df['Sales'] >= sales_range[0]) &
    (df['Sales'] <= sales_range[1])
]

if ship_sel != "Toate":
    df_filtrat = df_filtrat.loc[df_filtrat['Ship Mode'] == ship_sel]

if profit_filter == "Doar profitabile (Profit > 0)":
    df_filtrat = df_filtrat.loc[df_filtrat['Profit'] > 0]
elif profit_filter == "Doar în pierdere (Profit < 0)":
    df_filtrat = df_filtrat.loc[df_filtrat['Profit'] < 0]

if len(df_filtrat) == 0:
    st.warning("⚠️ Nicio comandă nu corespunde filtrelor selectate. Modifică criteriile.")
    st.stop()

st.subheader("📊 Sumar rezultate filtrate")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📦 Comenzi găsite",
        f"{len(df_filtrat):,}",
        f"{len(df_filtrat) / len(df) * 100:.1f}% din total"
    )

with col2:
    st.metric("💵 Vânzări totale", f"${df_filtrat['Sales'].sum():,.0f}")

with col3:
    profit_filtrat = df_filtrat['Profit'].sum()
    marja_filtrat = (profit_filtrat / df_filtrat['Sales'].sum() * 100) if df_filtrat['Sales'].sum() > 0 else 0
    st.metric("💰 Profit total", f"${profit_filtrat:,.0f}", f"Marjă: {marja_filtrat:.1f}%")

with col4:
    pierderi = (df_filtrat['Profit'] < 0).sum()
    st.metric(
        "⚠️ Comenzi în pierdere",
        f"{pierderi:,}",
        f"{pierderi / len(df_filtrat) * 100:.1f}%",
        delta_color="inverse"
    )

st.markdown("---")

st.subheader("📋 Primele 20 comenzi filtrate")

# iloc - acces pozitional la primele 20
primele_20 = df_filtrat.iloc[:20].reset_index(drop=True)

coloane = ['Order Date', 'Customer Name', 'Segment', 'Region',
           'Category', 'Sub-Category', 'Sales', 'Discount', 'Profit']

df_afisare = primele_20[coloane].copy()
df_afisare['Order Date'] = df_afisare['Order Date'].dt.strftime('%Y-%m-%d')

st.dataframe(df_afisare, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("🏆 Top 10 cele mai profitabile comenzi (din selecție)")

# loc cu slice de coloane + sortare
top_10_profit = df_filtrat.loc[:, coloane].sort_values(by='Profit', ascending=False).head(10).reset_index(drop=True)
top_10_profit['Order Date'] = top_10_profit['Order Date'].dt.strftime('%Y-%m-%d')

st.dataframe(top_10_profit, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("📉 Top 10 cele mai mari pierderi (din selecție)")

top_10_pierderi = df_filtrat.loc[df_filtrat['Profit'] < 0, coloane].sort_values(by='Profit').head(10).reset_index(drop=True)

if len(top_10_pierderi) > 0:
    top_10_pierderi['Order Date'] = top_10_pierderi['Order Date'].dt.strftime('%Y-%m-%d')
    st.dataframe(top_10_pierderi, use_container_width=True, hide_index=True)
else:
    st.success("✅ Nu există comenzi în pierdere în selecția curentă!")

st.markdown("---")
st.subheader("📈 Distribuția comenzilor filtrate")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Pe Regiune:**")
    st.bar_chart(df_filtrat['Region'].value_counts())

with col2:
    st.markdown("**Pe Categorie:**")
    st.bar_chart(df_filtrat['Category'].value_counts())

st.markdown("---")
st.subheader("💡 Interpretare business a selecției curente")

profit_mediu = df_filtrat['Profit'].mean()
discount_mediu = df_filtrat['Discount'].mean()
sales_medii = df_filtrat['Sales'].mean()

# semafor in functie de profitabilitate
if profit_mediu > 30:
    semnal = "🟢 **Selecție foarte profitabilă**"
    recomandare = "Continuă strategia actuală"
elif profit_mediu > 0:
    semnal = "🟡 **Selecție moderat profitabilă**"
    recomandare = "Revizuiește politica de discount în această selecție"
else:
    semnal = "🔴 **Selecție în pierdere - necesită atenție**"
    recomandare = "URGENT: Reduce discount-urile sau elimină produsele care generează pierderi"

st.info(f"""
{semnal}

- **Profit mediu / comandă:** ${profit_mediu:.2f}
- **Discount mediu aplicat:** {discount_mediu * 100:.1f}%
- **Vânzare medie / comandă:** ${sales_medii:.2f}

**Recomandare:** {recomandare}
""")