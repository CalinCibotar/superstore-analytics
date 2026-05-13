import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from pathlib import Path

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, silhouette_score
)

import statsmodels.api as sm


DATA_PATH = Path(__file__).parent.parent.parent / "data" / "Sample - Superstore.csv"


@st.cache_data
def load_and_clean_data():
    try:
        df = pd.read_csv(DATA_PATH, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(DATA_PATH, encoding='latin-1')

    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%m/%d/%Y')

    # feature nou: cate zile dureaza livrarea
    df['Ship_Days'] = (df['Ship Date'] - df['Order Date']).dt.days

    return df


df = load_and_clean_data()

st.title("🤖 Modele Predictive")
st.markdown(f"""
Această pagină aplică **3 modele de Machine Learning** pe datele Superstore pentru a 
răspunde la întrebări de business critice.

**Date folosite:** {len(df):,} comenzi.
""")
st.markdown("---")

# ---------- 1. Pregatirea datelor ----------
st.header("1️⃣ Pregătirea datelor: scalare și codificare")

st.markdown("""
Înainte de modele, aplicăm două transformări obligatorii:
- **Scalare** (StandardScaler) - aducem features la aceeași scară (medie=0, std=1)
- **Codificare** (LabelEncoder) - convertim variabile categoriale în numerice
""")

features_numerice = ['Sales', 'Quantity', 'Discount', 'Ship_Days']
features_categoriale = ['Segment', 'Region', 'Category', 'Sub-Category', 'Ship Mode']

col1, col2 = st.columns(2)

with col1:
    st.subheader("📏 Scalare features numerice")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features_numerice])
    df_scaled = pd.DataFrame(X_scaled, columns=features_numerice)

    st.markdown("**Înainte de scalare** (primele 3 rânduri):")
    st.dataframe(df[features_numerice].head(3).round(2), use_container_width=True)

    st.markdown("**După scalare** (medie≈0, std≈1):")
    st.dataframe(df_scaled.head(3).round(2), use_container_width=True)

with col2:
    st.subheader("🏷️ Codificare variabile categoriale")

    df_encoded = df.copy()
    encoders = {}

    for col in features_categoriale:
        le = LabelEncoder()
        df_encoded[col + '_encoded'] = le.fit_transform(df[col])
        encoders[col] = le

    st.markdown("**Mapare Region → cod numeric:**")
    mapare_region = pd.DataFrame({
        'Region': encoders['Region'].classes_,
        'Cod': range(len(encoders['Region'].classes_))
    })
    st.dataframe(mapare_region, use_container_width=True, hide_index=True)

    st.markdown("**Statistici codificare:**")
    st.code(f"""
Segment:       {len(encoders['Segment'].classes_)} valori → 0 - {len(encoders['Segment'].classes_)-1}
Region:        {len(encoders['Region'].classes_)} valori → 0 - {len(encoders['Region'].classes_)-1}
Category:      {len(encoders['Category'].classes_)} valori → 0 - {len(encoders['Category'].classes_)-1}
Sub-Category:  {len(encoders['Sub-Category'].classes_)} valori → 0 - {len(encoders['Sub-Category'].classes_)-1}
Ship Mode:     {len(encoders['Ship Mode'].classes_)} valori → 0 - {len(encoders['Ship Mode'].classes_)-1}
    """)

st.markdown("---")

# ---------- 2. K-Means: segmentare clienti ----------
st.header("2️⃣ K-Means Clustering: Segmentarea Clienților")

st.markdown("""
**Întrebarea de business:** Cum segmentăm cei ~793 de clienți unici în grupuri 
pentru strategii de marketing diferite?

**Abordare:** Agregăm datele la nivel de **client** (nu de comandă), apoi aplicăm K-Means 
pe features comportamentale.
""")

# agregare la nivel de client
clienti_agg = df.groupby('Customer ID').agg(
    nr_comenzi=('Order ID', 'nunique'),
    sales_total=('Sales', 'sum'),
    profit_total=('Profit', 'sum'),
    quantity_total=('Quantity', 'sum'),
    discount_mediu=('Discount', 'mean'),
    sales_mediu_per_comanda=('Sales', 'mean')
).round(2)

st.write(f"**Date agregate:** {len(clienti_agg)} clienți unici.")

n_clusters = st.slider("Numărul de segmente (clustere)", min_value=3, max_value=7, value=4)

features_clustering = ['nr_comenzi', 'sales_total', 'profit_total',
                       'quantity_total', 'discount_mediu', 'sales_mediu_per_comanda']

scaler_kmeans = StandardScaler()
X_clienti_scaled = scaler_kmeans.fit_transform(clienti_agg[features_clustering])

with st.spinner(f"Se rulează K-Means cu {n_clusters} clustere..."):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clienti_agg['cluster'] = kmeans.fit_predict(X_clienti_scaled)
    sil_score = silhouette_score(X_clienti_scaled, clienti_agg['cluster'])

st.success(f"✅ Clustering completat pe {len(clienti_agg)} clienți")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Silhouette Score", f"{sil_score:.3f}",
              help="Range: -1 la +1. >0.25 acceptabil, >0.5 foarte bun")

with col2:
    st.metric("Inertia (WCSS)", f"{kmeans.inertia_:,.0f}")

with col3:
    st.metric("Iterații până la convergență", kmeans.n_iter_)

st.subheader("📋 Profilul fiecărui segment de clienți")

cluster_profile = clienti_agg.groupby('cluster').agg(
    nr_clienti=('nr_comenzi', 'count'),
    medie_nr_comenzi=('nr_comenzi', 'mean'),
    medie_sales_total=('sales_total', 'mean'),
    medie_profit_total=('profit_total', 'mean'),
    medie_discount=('discount_mediu', 'mean')
).round(2)

st.dataframe(cluster_profile, use_container_width=True)

st.subheader("🏷️ Etichete descriptive ale segmentelor")

# eticheta automata in functie de profit si sales medii per cluster
profile_data = []
for cid in sorted(clienti_agg['cluster'].unique()):
    grup = clienti_agg[clienti_agg['cluster'] == cid]
    sales_med = grup['sales_total'].mean()
    profit_med = grup['profit_total'].mean()

    if profit_med > 500 and sales_med > 3000:
        eticheta = "💎 VIP Profitabili"
        strategie = "Loyalty programs, early access produse noi"
    elif profit_med > 0 and sales_med > 1500:
        eticheta = "⭐ Clienți Standard Profitabili"
        strategie = "Up-sell, cross-sell"
    elif profit_med > 0:
        eticheta = "🌱 Clienți Mici Profitabili"
        strategie = "Email marketing, retenție"
    else:
        eticheta = "⚠️ Clienți Riscanți (în pierdere)"
        strategie = "Revizuire politici discount pentru acești clienți"

    profile_data.append({
        'Cluster': cid,
        'Etichetă': eticheta,
        'Nr. clienți': len(grup),
        'Profit mediu': f"${profit_med:.2f}",
        'Strategie recomandată': strategie
    })

st.dataframe(pd.DataFrame(profile_data), use_container_width=True, hide_index=True)

st.subheader("🎨 Vizualizarea segmentelor de clienți")

fig_cluster = px.scatter(
    clienti_agg.reset_index(),
    x='sales_total', y='profit_total',
    color='cluster',
    size='nr_comenzi',
    hover_data=['Customer ID', 'discount_mediu'],
    title=f"Segmente de clienți: Sales total vs Profit total ({n_clusters} segmente)",
    labels={
        'sales_total': 'Vânzări totale per client ($)',
        'profit_total': 'Profit total per client ($)'
    },
    color_continuous_scale='Viridis',
    height=500
)
fig_cluster.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Profit = 0")
st.plotly_chart(fig_cluster, use_container_width=True)

st.info("""
💡 **Interpretare K-Means:** Fiecare punct = un client. Clusterele se diferențiază pe 
axa **Sales** (cât cheltuie) și **Profit** (cât profit aduc). Clienții sub linia roșie 
sunt în **pierdere** pentru Superstore — pentru ei trebuie revizuită strategia.
""")

st.markdown("---")

# ---------- 3. Regresie logistica: predictie pierderi ----------
st.header("3️⃣ Regresie Logistică: Predicția Comenzilor cu Pierderi")

st.markdown("""
**Întrebarea de business:** Putem prezice dacă o comandă va fi **în pierdere** 
(Profit < 0) **înainte** de a o procesa? Asta ar permite Superstore să respingă 
comenzile riscante sau să ajusteze condițiile.

**Abordare:** Regresie logistică binară pe features numerice + categoriale codificate.
""")

# target binar: 1 daca comanda e in pierdere
df_encoded['is_loss'] = (df_encoded['Profit'] < 0).astype(int)

st.markdown("**Distribuția claselor:**")
col1, col2 = st.columns(2)
with col1:
    st.metric("Comenzi profitabile (Profit ≥ 0)", f"{(df_encoded['is_loss'] == 0).sum():,}")
with col2:
    st.metric("Comenzi în pierdere (Profit < 0)", f"{(df_encoded['is_loss'] == 1).sum():,}")

balanta = df_encoded['is_loss'].mean() * 100
if balanta < 25:
    st.warning(f"⚠️ Clase moderat dezechilibrate ({balanta:.1f}% pierderi). Folosim `class_weight='balanced'`.")
else:
    st.info(f"ℹ️ Clase rezonabil echilibrate ({balanta:.1f}% pierderi).")

features_model = features_numerice + [col + '_encoded' for col in features_categoriale]

X = df_encoded[features_model]
y = df_encoded['is_loss']

scaler_log = StandardScaler()
X_scaled_log = scaler_log.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled_log, y, test_size=0.2, random_state=42, stratify=y
)

with st.spinner("Se antrenează modelul de regresie logistică..."):
    log_reg = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    log_reg.fit(X_train, y_train)
    y_pred = log_reg.predict(X_test)
    y_proba = log_reg.predict_proba(X_test)[:, 1]

st.success("✅ Model antrenat")

st.subheader("📊 Metrici de evaluare")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Accuracy", f"{accuracy_score(y_test, y_pred):.3f}")
with col2:
    st.metric("Precision", f"{precision_score(y_test, y_pred):.3f}")
with col3:
    st.metric("Recall", f"{recall_score(y_test, y_pred):.3f}")
with col4:
    st.metric("F1-Score", f"{f1_score(y_test, y_pred):.3f}")

st.metric("ROC-AUC", f"{roc_auc_score(y_test, y_proba):.3f}",
          help="> 0.8 = excelent, > 0.7 = bun")

st.subheader("🎯 Matricea de confuzie")

cm = confusion_matrix(y_test, y_pred)
fig_cm, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Profitabilă', 'Pierdere'],
            yticklabels=['Profitabilă', 'Pierdere'],
            ax=ax, cbar=False)
ax.set_xlabel('Predicție')
ax.set_ylabel('Realitate')
ax.set_title('Confusion Matrix - Predicție Comenzi în Pierdere')
st.pyplot(fig_cm)

tn, fp, fn, tp = cm.ravel()
st.markdown(f"""
**Interpretare confusion matrix:**
- ✅ **{tn:,}** comenzi profitabile prezise corect (True Negatives)
- ✅ **{tp:,}** pierderi prezise corect (True Positives)
- ⚠️ **{fp:,}** false alarms (am crezut că e pierdere, dar a fost profitabilă)
- ❌ **{fn:,}** pierderi ratate (le-am procesat ca profitabile, dar au fost în pierdere)
""")

st.subheader("🔝 Importanța features în predicție")

importance_df = pd.DataFrame({
    'Feature': features_model,
    'Coeficient': log_reg.coef_[0]
}).sort_values('Coeficient', key=abs, ascending=False)

fig_imp = px.bar(
    importance_df,
    x='Coeficient', y='Feature',
    orientation='h',
    title='Coeficienții regresiei logistice (impact asupra probabilității de pierdere)',
    color='Coeficient',
    color_continuous_scale='RdBu_r'
)
fig_imp.update_layout(height=400)
st.plotly_chart(fig_imp, use_container_width=True)

st.info("""
💡 **Interpretare:**
- Coeficienți **pozitivi** = feature-ul **crește** probabilitatea de pierdere
- Coeficienți **negativi** = feature-ul **scade** probabilitatea de pierdere

**Aplicație business:** Modelul poate fi integrat în sistemul de aprobare a comenzilor — 
dacă probabilitatea de pierdere > 50%, comanda merge la review manual.
""")

st.markdown("---")

# ---------- 4. Regresie multipla OLS ----------
st.header("4️⃣ Regresie Multiplă (statsmodels): Predicția Profitului")

st.markdown("""
**Întrebarea de business:** Cu cât crește/scade profitul pentru fiecare unitate de 
schimbare în Sales, Discount, Quantity? Care features au impact **semnificativ statistic**?

**Abordare:** OLS (Ordinary Least Squares) cu statsmodels - obținem coeficienți 
interpretabili, p-values și R².
""")

X_ols = df_encoded[features_model].copy()
y_ols = df_encoded['Profit']

# statsmodels nu adauga interceptul automat, il punem manual
X_ols = sm.add_constant(X_ols)

with st.spinner("Se antrenează modelul OLS..."):
    ols_model = sm.OLS(y_ols, X_ols).fit()

st.success("✅ Model OLS antrenat")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("R²", f"{ols_model.rsquared:.4f}")
with col2:
    st.metric("R² ajustat", f"{ols_model.rsquared_adj:.4f}")
with col3:
    st.metric("F-statistic", f"{ols_model.fvalue:.1f}")

st.subheader("📋 Coeficienți, p-values și interpretare")

coef_df = pd.DataFrame({
    'Feature': ols_model.params.index,
    'Coeficient': ols_model.params.values.round(4),
    'Std Error': ols_model.bse.values.round(4),
    'P-value': ols_model.pvalues.values.round(4),
    'Semnificativ?': ['✅ Da' if p < 0.05 else '❌ Nu' for p in ols_model.pvalues.values]
})

st.dataframe(coef_df, use_container_width=True, hide_index=True)

with st.expander("📄 Sumar complet OLS (pentru documentația proiectului)"):
    st.text(str(ols_model.summary()))

st.info(f"""
💡 **Interpretare modelului OLS:**
- **R² = {ols_model.rsquared:.3f}** → modelul explică {ols_model.rsquared * 100:.1f}% din varianța profitului
- Toți coeficienții cu **p-value < 0.05** au efect **semnificativ statistic**
- Modelul poate fi folosit pentru **estimarea profitului** unei comenzi noi
""")

st.markdown("---")
st.header("🎓 Concluzii modele predictive")

st.success(f"""
**Cele 3 modele formează un sistem complet de decizie pentru Superstore:**

1. **K-Means** ({n_clusters} segmente, Silhouette = {sil_score:.3f})
   → Strategii diferențiate pe profile de clienți

2. **Regresie Logistică** (ROC-AUC = {roc_auc_score(y_test, y_proba):.3f})
   → Sistem de early warning pentru comenzi în pierdere

3. **Regresie Multiplă** (R² = {ols_model.rsquared:.3f})
   → Estimare cantitativă a profitului pentru comenzi noi

**Aceste 3 modele pot fi integrate într-un sistem unitar de decizie:**
- Identifică profilul clientului (K-Means)
- Estimează profitul comenzii (OLS)
- Verifică riscul de pierdere (Regresie Logistică)
- Aprobă/respinge automat sau trimite la review manual
""")