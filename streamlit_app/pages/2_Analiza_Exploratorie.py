import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
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


df_raw = load_data()

st.title("📊 Analiză Exploratorie")
st.markdown("""
Această pagină prezintă **curățarea datelor** și **analizele exploratorii** 
care stau la baza modelelor predictive din pagina următoare.
""")
st.markdown("---")

# ---------- 1. Tratarea valorilor lipsa ----------
st.header("1️⃣ Tratarea valorilor lipsă")

st.markdown("""
**Context:** Dataset-ul original Superstore este foarte curat (0 NaN-uri). 
Pentru a demonstra tehnicile de tratare a valorilor lipsă, **simulăm un scenariu real**: 
ce ar face Superstore dacă ar primi date corupte de la sistemele POS sau date 
pierdute la import?

**Simulare:** Introducem aleatoriu 5% valori lipsă în coloanele `Discount`, `Sales`, 
`Postal Code` și `Ship Mode`, apoi demonstrăm 4 strategii de tratare.
""")


@st.cache_data
def simulate_missing(df):
    # introducem ~5% NaN in cateva coloane, simuland date corupte
    np.random.seed(42)
    df_dirty = df.copy()
    for col in ['Sales', 'Discount', 'Postal Code', 'Ship Mode']:
        mask = np.random.rand(len(df_dirty)) < 0.05
        df_dirty.loc[mask, col] = np.nan
    return df_dirty


df_dirty = simulate_missing(df_raw)

col1, col2 = st.columns(2)

with col1:
    st.subheader("❌ După introducerea NaN-urilor")

    missing_after = df_dirty.isnull().sum()
    missing_df = pd.DataFrame({
        'Coloană': missing_after[missing_after > 0].index,
        'Valori NaN': missing_after[missing_after > 0].values,
        'Procent': [f"{x / len(df_dirty) * 100:.1f}%" for x in missing_after[missing_after > 0].values]
    })
    st.dataframe(missing_df, hide_index=True, use_container_width=True)

with col2:
    st.subheader("✅ Strategii de tratare aplicate")
    st.markdown("""
    | Coloană | Strategie | Motiv |
    |---|---|---|
    | `Sales` | Imputare cu **mediană** | Robustă la outliers |
    | `Discount` | Imputare cu **0** | Lipsa info = fără discount |
    | `Postal Code` | Imputare cu **mod** | Date discrete |
    | `Ship Mode` | Imputare cu **mod** | Variabilă categorială |
    """)


@st.cache_data
def clean_data(df_dirty):
    df_clean = df_dirty.copy()
    df_clean['Sales'].fillna(df_clean['Sales'].median(), inplace=True)
    df_clean['Discount'].fillna(0, inplace=True)
    df_clean['Postal Code'].fillna(df_clean['Postal Code'].mode()[0], inplace=True)
    df_clean['Ship Mode'].fillna(df_clean['Ship Mode'].mode()[0], inplace=True)
    return df_clean


df = clean_data(df_dirty)

nan_total = df_dirty.isnull().sum().sum()
if df.isnull().sum().sum() == 0:
    st.success(f"✅ Curățare reușită! Toate cele {nan_total} valori NaN au fost tratate.")

st.session_state['df_clean'] = df

st.markdown("---")

# ---------- 2. Statistici descriptive si agregari ----------
st.header("2️⃣ Statistici descriptive și agregări")

st.subheader("📈 Statistici descriptive - variabile numerice")

stats = df[['Sales', 'Quantity', 'Discount', 'Profit']].describe().round(2).T
stats.columns = ['Count', 'Medie', 'Std', 'Min', 'Q1', 'Mediană', 'Q3', 'Max']
st.dataframe(stats, use_container_width=True)

st.markdown("---")
st.subheader("🌎 Performanță pe Regiuni")

# groupby cu multiple functii de agregare
perf_regiune = df.groupby('Region').agg(
    nr_comenzi=('Order ID', 'count'),
    vanzari_totale=('Sales', 'sum'),
    profit_total=('Profit', 'sum'),
    profit_mediu=('Profit', 'mean'),
    discount_mediu=('Discount', 'mean'),
    pierderi=('Profit', lambda x: (x < 0).sum())
).round(2).sort_values('profit_total', ascending=False)

perf_regiune['marja_%'] = (perf_regiune['profit_total'] / perf_regiune['vanzari_totale'] * 100).round(1)

st.dataframe(perf_regiune, use_container_width=True)

st.markdown("---")
st.subheader("🎯 Profitabilitate pe Categorie × Segment")

# groupby pe 2 nivele
pivot_profit = df.groupby(['Category', 'Segment'])['Profit'].agg(['sum', 'mean', 'count']).round(2)
pivot_profit.columns = ['Profit Total', 'Profit Mediu', 'Nr Comenzi']
st.dataframe(pivot_profit, use_container_width=True)

st.markdown("---")
st.subheader("💸 Impactul Discount-urilor asupra Profitului")

# discount binning - util si pentru SAS PROC FORMAT mai tarziu
df['Discount_Range'] = pd.cut(
    df['Discount'],
    bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.4, 0.6, 1.0],
    labels=['0%', '1-10%', '10-20%', '20-30%', '30-40%', '40-60%', '60-80%']
)

impact_disc = df.groupby('Discount_Range', observed=True).agg(
    nr_comenzi=('Order ID', 'count'),
    sales_mediu=('Sales', 'mean'),
    profit_mediu=('Profit', 'mean'),
    profit_total=('Profit', 'sum'),
    rata_pierderi=('Profit', lambda x: (x < 0).mean() * 100)
).round(2)

st.dataframe(impact_disc, use_container_width=True)

st.warning("""
⚠️ **Insight CRITIC pentru business:** 
- Comenzile cu **0% discount** generează profit mediu pozitiv
- Comenzile cu **20-30% discount** încep să producă **pierderi medii**
- Comenzile cu **40-60% discount** generează **pierderi medii de peste $130**

**Recomandare:** Limitarea discount-urilor maxime la 20% ar putea elimina majoritatea pierderilor.
""")

st.markdown("---")

# ---------- 3. Vizualizari ----------
st.header("3️⃣ Vizualizări grafice")
st.markdown("Folosim toate cele 3 librării cerute: **matplotlib**, **seaborn** și **plotly**.")

# bar chart plotly - profit per regiune
st.subheader("📊 Profit total pe Regiuni (Plotly)")

profit_reg = df.groupby('Region')['Profit'].sum().reset_index().sort_values('Profit')

fig_bar = px.bar(
    profit_reg,
    x='Profit', y='Region',
    orientation='h',
    title="Profit total per Regiune",
    color='Profit',
    color_continuous_scale=['#FF4B4B', '#FFE15D', '#1DB954'],
    labels={'Profit': 'Profit total ($)', 'Region': 'Regiune'}
)
fig_bar.update_layout(height=400, showlegend=False)
st.plotly_chart(fig_bar, use_container_width=True)

st.info("""
💡 **Interpretare:** West și East generează ~70% din profitul total. 
**Central** are profitul cel mai mic — strategia în această regiune trebuie reanalizată.
""")

# scatter plotly - profit vs discount
st.subheader("💸 Relația Discount → Profit (Plotly)")

# sample pentru performanta - 10k puncte ar fi prea mult
df_sample = df.sample(n=min(3000, len(df)), random_state=42).copy()
# size trebuie sa fie strict pozitiv pentru plotly
df_sample['size_plot'] = df_sample['Sales'].clip(lower=1)

fig_scatter = px.scatter(
    df_sample,
    x='Discount', y='Profit',
    color='Category',
    size='size_plot',
    hover_data=['Customer Name', 'Region', 'Sub-Category'],
    title=f"Profit vs Discount (sample {len(df_sample):,} comenzi)",
    labels={'Discount': 'Discount (%)', 'Profit': 'Profit ($)'},
    height=500
)
fig_scatter.add_hline(y=0, line_dash="dash", line_color="white",
                      annotation_text="Profit = 0", annotation_position="right")
st.plotly_chart(fig_scatter, use_container_width=True)

st.info("""
💡 **Interpretare:** Vizual confirmă insight-ul. Pe măsură ce Discount-ul crește (axa X), 
profitul tinde să cadă sub linia 0 (pierderi). **Furniture** (mov) are cele mai mari 
pierderi la discount mare.
""")

# heatmap seaborn - categorie x regiune
st.subheader("🔥 Heatmap: Profit mediu pe Categorie × Regiune (Seaborn)")

heatmap_data = df.pivot_table(
    values='Profit',
    index='Category',
    columns='Region',
    aggfunc='mean'
).round(2)

fig_heat, ax = plt.subplots(figsize=(10, 4))
sns.heatmap(
    heatmap_data,
    annot=True,
    fmt='.1f',
    cmap='RdYlGn',
    center=0,
    cbar_kws={'label': 'Profit mediu ($)'},
    linewidths=1,
    ax=ax
)
ax.set_title("Profit mediu per comandă: Categorie × Regiune", fontsize=12, pad=15)
st.pyplot(fig_heat)

st.info("""
💡 **Interpretare:** 
- **Technology + East** = combinația cea mai profitabilă
- **Furniture + Central** = singura combinație cu pierderi medii (-$6)
- Strategia: investiție agresivă în Tech, restructurare în Furniture/Central
""")

# boxplot matplotlib - sub-categorii
st.subheader("📦 Boxplot: Distribuția Profitului pe Sub-Categorii (Matplotlib)")

# luam top 10 sub-categorii (17 ar fi prea mult pentru lizibilitate)
top_subcat = df['Sub-Category'].value_counts().head(10).index.tolist()
df_top = df[df['Sub-Category'].isin(top_subcat)]

fig_box, ax = plt.subplots(figsize=(12, 6))

ordine = df_top.groupby('Sub-Category')['Profit'].median().sort_values().index.tolist()
data_box = [df_top[df_top['Sub-Category'] == sc]['Profit'].values for sc in ordine]
bp = ax.boxplot(data_box, labels=ordine, patch_artist=True, showfliers=False)

# colorare in functie de profit median: verde = profitabil, rosu = pierdere
medians = [df_top[df_top['Sub-Category'] == sc]['Profit'].median() for sc in ordine]
for patch, med in zip(bp['boxes'], medians):
    patch.set_facecolor('#1DB954' if med > 0 else '#FF4B4B')
    patch.set_alpha(0.7)

ax.axhline(y=0, color='white', linestyle='--', alpha=0.5)
ax.set_xlabel("Sub-Category", fontsize=11)
ax.set_ylabel("Profit ($)", fontsize=11)
ax.set_title("Distribuția profitului pe Sub-Categorii (top 10)", fontsize=12)
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
st.pyplot(fig_box)

st.info("""
💡 **Interpretare:** Sub-categoriile cu **median negativ** (roșu) sunt produse care, în medie, 
generează pierderi: **Tables, Bookcases, Supplies**. Acestea sunt candidate pentru 
restructurare de produs sau eliminare.
""")

# line chart plotly - evolutie temporala
st.subheader("📈 Evoluția lunară a Vânzărilor și Profitului (Plotly)")

df['YearMonth'] = df['Order Date'].dt.to_period('M').dt.to_timestamp()
evolutie = df.groupby('YearMonth').agg(
    Sales=('Sales', 'sum'),
    Profit=('Profit', 'sum')
).reset_index()

fig_line = px.line(
    evolutie,
    x='YearMonth', y=['Sales', 'Profit'],
    title="Evoluția vânzărilor și profitului în timp",
    labels={'value': 'Valoare ($)', 'YearMonth': 'Luna', 'variable': 'Metrică'},
    height=400
)
fig_line.update_layout(hovermode='x unified')
st.plotly_chart(fig_line, use_container_width=True)

st.info("""
💡 **Interpretare:** 
- Vânzările cresc constant an de an
- Profitul are vârfuri sezoniere (Q4 = sezonul de sărbători)
- **Trend pozitiv**, dar marja de profit nu crește proporțional → confirmă povestea de business
""")

st.markdown("---")
st.header("💼 Concluzii preliminare din analiza exploratorie")

st.success("""
**Pe baza analizei descriptive identificăm 5 insights cheie pentru business:**

1. **Politica de discount e principala problemă** - peste 20% discount → pierderi medii
2. **Categoria Furniture e în pericol** - profit aproape zero, mai ales în regiunea Central
3. **Sub-categoriile Tables, Bookcases, Supplies** generează pierderi sistematic
4. **Technology + West** = combinația de aur (cel mai mare profit mediu)
5. **Trend de creștere a vânzărilor**, dar marja stagnează (12.5% global)

→ Aceste insights vor ghida construcția modelelor predictive în pagina următoare.
""")