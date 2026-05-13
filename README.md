# 🛍️ Superstore Analytics Dashboard

Aplicație interactivă de analiză a performanței comerciale pentru un retailer SUA, 
construită cu **Streamlit** și **scikit-learn**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://superstore-analytics.streamlit.app)

## 📊 Funcționalități

- **Filtrare interactivă** a comenzilor după regiune, segment, categorie, discount, vânzări
- **Analiză exploratorie** cu vizualizări dinamice (Matplotlib, Seaborn, Plotly)
- **3 modele de Machine Learning:**
  - K-Means Clustering pentru segmentarea clienților
  - Regresie Logistică pentru predicția comenzilor în pierdere (ROC-AUC = 0.96)
  - Regresie Multiplă OLS pentru estimarea profitului
- **Concluzii business** cuantificate și posibilități de extindere

## 🛠️ Tehnologii folosite

- Python 3.11
- Streamlit
- pandas, numpy
- scikit-learn, statsmodels
- matplotlib, seaborn, plotly

## 📁 Structura proiectului

```
SmartCityFinal/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   └── Sample - Superstore.csv
└── streamlit_app/
    ├── Home.py
    └── pages/
        ├── 1_Filtrare.py
        ├── 2_Analiza_Exploratorie.py
        ├── 3_Modele_Predictive.py
        └── 4_Concluzii.py
```

## 🚀 Cum rulezi local

1. Clonează repository-ul:
```bash
   git clone https://github.com/CalinCibotar/superstore-analytics.git
   cd superstore-analytics
```

2. Instalează dependențele:
```bash
   pip install -r requirements.txt
```

3. Pornește aplicația:
```bash
   streamlit run streamlit_app/Home.py
```

4. Browser-ul se va deschide automat la `http://localhost:8501`

## 📈 Dataset

[Sample Superstore dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) 
de pe Kaggle — 9.994 comenzi, 793 clienți unici, perioada 2014-2017.

## 👤 Autor

**Calin Cibotar**

## 📄 Licență

MIT License

