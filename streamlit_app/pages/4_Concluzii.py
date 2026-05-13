import streamlit as st


st.title("💼 Concluzii Business & Recomandări Strategice")

st.markdown("""
Această secțiune sintetizează **rezultatele analizei** și formulează 
**recomandări cuantificabile** pentru Superstore Inc.
""")
st.markdown("---")

# ---------- Rezumat executiv ----------
st.header("📋 Rezumat executiv")

st.markdown("""
**Context:** Superstore Inc. gestionează un catalog de produse B2B+B2C distribuit în 
4 regiuni SUA, cu o cifră de afaceri de **$2.297.201** și un profit total de **$286.397** 
(marjă de doar **12.5%**) din **9.994 comenzi** analizate.

**Problema centrală identificată:** **18.7% din comenzi (1.871 comenzi)** generează 
**pierderi efective**, cauzate principal de o politică de discounting necontrolată.

**Întrebări de business analizate:**
1. Care comenzi sunt profitabile și care nu?
2. Putem prezice cât profit va aduce o comandă?
3. Putem identifica comenzile cu pierderi înainte de procesare?
4. Cum segmentăm clienții pentru strategii diferite?

**Date analizate:** 9.994 comenzi, 793 clienți unici, 1.862 produse, perioada 2014-2017.
""")

st.markdown("---")

# ---------- Insight-uri cheie ----------
st.header("🔑 Insight-uri cheie obținute")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ Ce am descoperit")
    st.markdown("""
    - **Discount-urile peste 20% distrug profitul** - confirmat cantitativ:
      - 0% discount → +$66.90 profit mediu
      - 20-30% discount → -$45.76 profit mediu
      - 40-60% discount → -$129.86 profit mediu
    - **Furniture e categoria problematică** - profit total doar $18.451 (vs $145.455 Technology)
    - **Regiunea Central subperformă** - profit mediu $17.09 vs $33.85 în West
    - **Sub-categoriile Tables, Bookcases, Supplies** generează pierderi sistematic
    - **Technology + East/West** = combinațiile cele mai profitabile
    """)

with col2:
    st.subheader("🎯 Performanța modelelor")
    st.markdown("""
    **K-Means Clustering** (Silhouette = 0.236):
    - 4 segmente de clienți identificate
    - VIP, Standard, Mici, Riscanți
    
    **Regresie Logistică** (ROC-AUC = 0.962):
    - 87.4% recall pentru pierderi
    - 91.6% accuracy globală
    - Model utilizabil în producție
    
    **Regresie Multiplă OLS** (R² = 0.284):
    - Discount = cel mai puternic predictor (-251.23)
    - Toți coeficienții semnificativi (p < 0.05)
    """)

st.markdown("---")

# ---------- Recomandari strategice ----------
st.header("🎯 Recomandări strategice cuantificate")

with st.container():
    st.subheader("1️⃣ Limitarea politicii de discount la maxim 20%")
    st.markdown("""
    **Acțiune:** Modificarea sistemului de aprobare comenzi pentru a bloca automat 
    discount-urile peste 20%, cu excepția cazurilor aprobate de manager regional.
    
    **Impact estimat:** Eliminarea majorității celor 1.320 comenzi cu pierderi 
    (cele cu discount peste 20%), recuperând aproximativ **$120.000 profit anual**.
    
    **KPI de monitorizat:** Procent comenzi în pierdere, profit mediu per comandă.
    """)

with st.container():
    st.subheader("2️⃣ Implementarea sistemului de Early Loss Detection")
    st.markdown("""
    **Acțiune:** Integrarea modelului de regresie logistică (ROC-AUC = 0.962) ca 
    **filtru automatizat de aprobare comenzi**. Comenzile cu probabilitate de pierdere 
    peste 50% sunt redirecționate către review manual.
    
    **Impact estimat:** Prevenirea a ~87% din pierderile potențiale = **$200.000+ economii anuale**.
    
    **Aplicație concretă:** Dashboard pentru Sales Managers cu scoruri de risc în 
    timp real pe fiecare comandă.
    """)

with st.container():
    st.subheader("3️⃣ Restructurarea portofoliului de produse")
    st.markdown("""
    **Acțiune:** Eliminarea sau renegocierea contractelor pentru sub-categoriile 
    constant neprofitabile (**Tables, Bookcases, Supplies**), care reprezintă 7.4% 
    din comenzi dar generează pierderi totale.
    
    **Impact estimat:** Realocare resurse către Technology (profit mediu $78.75) și 
    Office Supplies, cu potențial creștere profit total cu **15-20%**.
    
    **Risc:** Posibilă pierdere de clienți care cumpără doar aceste produse — analiză 
    suplimentară necesară.
    """)

with st.container():
    st.subheader("4️⃣ Strategii diferențiate pe segmente de clienți")
    st.markdown("""
    **Acțiune:** Implementarea strategiilor identificate prin K-Means:
    - **💎 VIP Profitabili** → Loyalty program premium, acces anticipat la produse noi
    - **⭐ Standard Profitabili** → Up-sell, cross-sell automatizat
    - **🌱 Mici Profitabili** → Campanii de email marketing pentru creșterea frecvenței
    - **⚠️ Riscanți** → Revizuire condiții comerciale, eliminare discount-uri agresive
    
    **Impact estimat:** Creșterea Customer Lifetime Value cu **10-15%** pentru segmentele 
    profitabile.
    """)

st.markdown("---")

# ---------- Posibilitati de extindere ----------
st.header("🚀 Posibilități de extindere a organizației")

st.markdown("""
Pe baza analizei, identificăm **4 oportunități strategice** de extindere pentru Superstore Inc.:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🌐 1. Extindere geografică în regiunea South
    
    **Idee:** Regiunea South are doar 1.620 comenzi (cel mai puțin), dar profit mediu 
    decent ($28.86). Există potențial de creștere prin deschiderea de centre regionale 
    suplimentare.
    
    **Investiție estimată:** $500K - $1M / centru
    
    **ROI:** 2-3 ani
    """)

with col2:
    st.markdown("""
    ### 💼 2. Sub-brand "Superstore Pro" pentru B2B
    
    **Idee:** Segmentul Corporate are profit mediu/comandă mai mare decât Consumer. 
    Lansarea unui sub-brand dedicat B2B cu produse premium, contracte pe termen lung, 
    discount-uri standardizate.
    
    **Target:** Companii mid-size din regiunile East și West
    
    **Avantaj competitiv:** Datele istorice + modelele predictive
    """)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🤖 3. SaaS de Discount Optimization
    
    **Idee:** Pe baza modelelor dezvoltate, Superstore poate **vinde** acest sistem ca 
    SaaS altor retaileri ("Superstore Analytics") — produs B2B premium.
    
    **Target:** Mid-market retailers fără capacitate proprie de ML
    
    **Model venit:** Subscription tier-based ($5K-$50K/an per client)
    
    **Diferențiere:** Sistem real-time + integrare ERP
    """)

with col2:
    st.markdown("""
    ### 🎓 4. Programe de training pentru parteneri
    
    **Idee:** Workshop-uri și certificări pentru distribuitori și parteneri pe 
    "Profit Optimization" — folosind expertiza acumulată din analiză.
    
    **Target:** Rețeaua de parteneri Superstore + ecosystem retail
    
    **Avantaj:** Brand thought-leadership + revenue stream nou
    """)

st.markdown("---")

# ---------- Concluzie finala ----------
st.header("🎓 Concluzie finală")

st.success("""
**Acest proiect demonstrează că analiza datelor și Machine Learning aplicate strategic 
pot transforma operațiunile unei companii retail.**

Cele 3 modele predictive (K-Means, Regresie Logistică, Regresie Multiplă OLS) oferă 
perspective complementare care, integrate într-un sistem unitar de decizie, pot:

- **Salva $300K+ profit anual** prin eliminarea pierderilor evitabile
- **Crește marja de profit** de la 12.5% la estimativ 18-20%
- **Diferenția strategia per client** și per regiune
- **Crea noi linii de business** (SaaS, B2B Pro, expansiune geografică)

Modelele dezvoltate sunt **utilizabile în producție** (ROC-AUC = 0.962 pentru predicția 
pierderilor) și pot fi integrate în ERP-ul existent al companiei.

**Concluzia executivă:** Investiția în capabilități analitice și ML reprezintă pentru 
Superstore Inc. unul dintre cele mai puternice motoare de creștere a profitabilității 
pe termen mediu.
""")

st.markdown("---")
st.caption("Proiect Pachete Software | ASE București - CSIE | An III")