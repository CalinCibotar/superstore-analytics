import streamlit as st
import pandas as pd
from pathlib import Path


st.set_page_config(
    page_title="Superstore Analytics",
    page_icon="🛍️",
    layout="wide"
)

DATA_PATH = Path(__file__).parent.parent / "data" / "Sample - Superstore.csv"


@st.cache_data
def load_data():
    # cache ca să nu recitească CSV-ul de fiecare dată
    try:
        df = pd.read_csv(DATA_PATH, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(DATA_PATH, encoding='latin-1')

    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%m/%d/%Y')

    return df


df = load_data()

st.title("🛍️ Superstore Analytics Dashboard")
st.markdown("### Analiza profitabilității și optimizarea strategiei comerciale")

st.markdown("""
---
### Despre proiect

Această aplicație analizează datele de vânzări ale **Superstore Inc.**, un retailer american B2B+B2C 
care operează în 4 regiuni SUA (East, West, Central, South), cu trei categorii principale 
de produse: Furniture, Office Supplies și Technology.

**Problema centrală:** Compania înregistrează creșteri în vânzări, dar **18.7% din comenzi 
generează pierderi**, iar marja totală de profit este de doar **12.5%**. Acest proiect 
identifică cauzele pierderilor și propune strategii cuantificabile de optimizare.

### Întrebări de business analizate

1. 💰 **Putem prezice cât profit va aduce o comandă?**
2. 🚨 **Putem identifica comenzile cu pierderi înainte de procesare?**
3. 👥 **Cum segmentăm clienții pentru strategii diferite?**
4. 📊 **Ce regiuni, categorii și politici de discount funcționează cel mai bine?**

### Structura aplicației

Folosește meniul din stânga pentru a naviga între pagini:

1. **Filtrare** - explorare interactivă cu filtre multiple
2. **Analiza Exploratorie** - curățarea datelor, statistici și vizualizări
3. **Modele Predictive** - K-Means, regresie logistică, regresie multiplă
4. **Concluzii** - recomandări strategice și posibilități de extindere
""")

st.markdown("---")

st.subheader("📊 KPI-uri executive")

profit_total = df['Profit'].sum()
sales_total = df['Sales'].sum()
marja = (profit_total / sales_total) * 100
comenzi_total = len(df)
comenzi_pierderi = (df['Profit'] < 0).sum()
pct_pierderi = (comenzi_pierderi / comenzi_total) * 100
nr_clienti = df['Customer ID'].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💵 Vânzări totale", f"${sales_total:,.0f}")

with col2:
    st.metric("💰 Profit total", f"${profit_total:,.0f}", f"Marjă: {marja:.1f}%")

with col3:
    st.metric("📦 Comenzi totale", f"{comenzi_total:,}", f"{nr_clienti:,} clienți unici")

with col4:
    st.metric(
        "⚠️ Comenzi în pierdere",
        f"{comenzi_pierderi:,}",
        f"{pct_pierderi:.1f}% din total",
        delta_color="inverse"
    )

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🛒 Profit mediu / comandă", f"${df['Profit'].mean():.2f}")

with col2:
    st.metric(
        "📅 Perioadă acoperită",
        f"{df['Order Date'].min().year} - {df['Order Date'].max().year}"
    )

with col3:
    st.metric("🌎 Regiuni", df['Region'].nunique(), ", ".join(df['Region'].unique()))

with col4:
    st.metric(
        "📂 Categorii produse",
        df['Category'].nunique(),
        f"{df['Sub-Category'].nunique()} sub-categorii"
    )

st.markdown("---")

st.subheader("👀 Primele 10 comenzi din catalog")

coloane = ['Order Date', 'Customer Name', 'Segment', 'Region',
           'Category', 'Sub-Category', 'Sales', 'Discount', 'Profit']

st.dataframe(df[coloane].head(10), use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("🔍 Calitatea datelor")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Verificare integritate:**")
    missing = df.isnull().sum().sum()
    if missing == 0:
        st.success("✅ Nu există valori lipsă (NaN) în dataset")
    else:
        st.warning(f"⚠️ Există {missing} valori lipsă - vor fi tratate în pagina următoare")

    if df.duplicated().sum() == 0:
        st.success("✅ Nu există rânduri duplicate")

with col2:
    st.markdown("**Insight-uri preliminare:**")
    profit_furniture = df[df['Category'] == 'Furniture']['Profit'].sum()
    profit_tech = df[df['Category'] == 'Technology']['Profit'].sum()

    st.info(f"""
    📉 **Discount-urile mari distrug profitul:**
    - 0% discount → profit mediu **$66.90**
    - 20-40% discount → profit mediu **-$77.86**
    - 60%+ discount → profit mediu **-$98.35**
    
    🏆 **Technology** = profitul cel mai mare (${profit_tech:,.0f})
    
    ⚠️ **Furniture** = profit aproape zero (${profit_furniture:,.0f})
    """)

st.markdown("---")
st.caption("Proiect Pachete Software | ASE București - CSIE | An III")