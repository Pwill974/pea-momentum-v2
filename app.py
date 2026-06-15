import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ── Configuration de la page et Thème Sombre ──────────────────────────────────
st.set_page_config(page_title="TKL ZEN Portfolio", page_icon="📈", layout="wide")

# Injection CSS pour forcer le Dark Mode avec textes blancs et styliser les cartes
st.markdown("""
    <style>
    .stApp {
        background-color: #0B0F1A;
        color: #FFFFFF;
    }
    h1, h2, h3, p, span, label {
        color: #FFFFFF !important;
    }
    div[data-testid="metric-container"] {
        background-color: #161D2E;
        border: 1px solid #1E2D45;
        padding: 15px;
        border-radius: 12px;
    }
    div[data-testid="stMetricValue"] > div {
        color: #00D4AA !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #111827;
        border-radius: 8px 8px 0 0;
        padding: 5px 5px 0 5px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        color: #00D4AA !important;
        border-bottom: 2px solid #00D4AA;
    }
    </style>
""", unsafe_allow_html=True)

# ── Données Initiales ─────────────────────────────────────────────────────────
INITIAL_PORTFOLIO = [
    {"id": 1, "nom": "Amundi PEA MSCI World", "ticker": "EWLD", "type": "ETF", "secteur": "Monde", "couche": "Socle ZEN", "alloc": 20, "cours": 30.5, "quantite": 0, "prixAchat": 30.5},
    {"id": 2, "nom": "Amundi PEA S&P 500", "ticker": "PE500", "type": "ETF", "secteur": "USA", "couche": "Socle ZEN", "alloc": 15, "cours": 42.2, "quantite": 0, "prixAchat": 42.2},
    {"id": 3, "nom": "Amundi PEA Nasdaq-100", "ticker": "PUST", "type": "ETF", "secteur": "Tech US", "couche": "Socle ZEN", "alloc": 10, "cours": 55.8, "quantite": 0, "prixAchat": 55.8},
    {"id": 4, "nom": "Amundi PEA MSCI Europe", "ticker": "PCEU", "type": "ETF", "secteur": "Europe", "couche": "Socle ZEN", "alloc": 5, "cours": 118.4, "quantite": 0, "prixAchat": 118.4},
    {"id": 5, "nom": "BNP GUARD Défense", "ticker": "GUARD", "type": "ETF", "secteur": "Défense", "couche": "Momentum", "alloc": 10, "cours": 12.3, "quantite": 0, "prixAchat": 12.3},
    {"id": 6, "nom": "Schneider Electric", "ticker": "SU", "type": "Action", "secteur": "Industrie", "couche": "Momentum", "alloc": 5, "cours": 245.0, "quantite": 0, "prixAchat": 245.0},
    {"id": 7, "nom": "Air Liquide", "ticker": "AI", "type": "Action", "secteur": "Industrie", "couche": "Momentum", "alloc": 3, "cours": 148.5, "quantite": 0, "prixAchat": 148.5},
    {"id": 8, "nom": "Dassault Aviation", "ticker": "AM", "type": "Action", "secteur": "Défense", "couche": "Momentum", "alloc": 5, "cours": 298.0, "quantite": 0, "prixAchat": 298.0},
    {"id": 9, "nom": "Thales", "ticker": "HO", "type": "Action", "secteur": "Défense", "couche": "Momentum", "alloc": 5, "cours": 192.0, "quantite": 0, "prixAchat": 192.0},
    {"id": 10, "nom": "STMicroelectronics", "ticker": "STM", "type": "Action", "secteur": "Tech", "couche": "Momentum", "alloc": 5, "cours": 24.5, "quantite": 0, "prixAchat": 24.5},
    {"id": 11, "nom": "Sanofi", "ticker": "SAN", "type": "Action", "secteur": "Santé", "couche": "Satellite", "alloc": 7, "cours": 92.0, "quantite": 0, "prixAchat": 92.0},
    {"id": 12, "nom": "Amundi PEA Émergents", "ticker": "PAEEM", "type": "ETF", "secteur": "Émergents", "couche": "Satellite", "alloc": 5, "cours": 44.6, "quantite": 0, "prixAchat": 44.6},
    {"id": 13, "nom": "TotalEnergies", "ticker": "TTE", "type": "Action", "secteur": "Énergie", "couche": "Satellite", "alloc": 5, "cours": 58.2, "quantite": 0, "prixAchat": 58.2},
]

MOMENTUM_SCORES = {1:57, 2:62, 3:70, 4:55, 5:75, 6:68, 7:60, 8:86, 9:72, 10:48, 11:55, 12:61, 13:52}

COLORS = {
    "Socle ZEN": "#00D4AA", "Momentum": "#3B82F6", "Satellite": "#F59E0B",
    "Monde": "#00D4AA", "USA": "#3B82F6", "Tech US": "#8B5CF6", "Europe": "#06B6D4",
    "Défense": "#EF4444", "Industrie": "#F59E0B", "Tech": "#A78BFA", "Santé": "#10B981",
    "Émergents": "#F97316", "Énergie": "#FBBF24"
}

# ── Gestion de l'état (Session State) ─────────────────────────────────────────
if 'init' not in st.session_state:
    st.session_state.df = pd.DataFrame(INITIAL_PORTFOLIO)
    st.session_state.df['momentum'] = st.session_state.df['id'].map(MOMENTUM_SCORES)
    st.session_state.transactions = []
    st.session_state.capital_initial = 10000.0
    st.session_state.cash = 10000.0
    st.session_state.init = True

df = st.session_state.df

# Calculs globaux
df['valeur'] = df['cours'] * df['quantite']
df['pru_total'] = df['prixAchat'] * df['quantite']
df['plus_value'] = df['valeur'] - df['pru_total']

valeur_actifs = df['valeur'].sum()
fonds_investis = df['pru_total'].sum()
total_portefeuille = valeur_actifs + st.session_state.cash
plus_value_globale = total_portefeuille - st.session_state.capital_initial

# ── En-tête ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("## 📈 TKL ZEN Portfolio")
    st.caption("PEA Fortuneo · Stratégie Momentum")
with col2:
    nouveau_capital = st.number_input("Capital Initial Déposé (€)", value=st.session_state.capital_initial, step=100.0)
    if nouveau_capital != st.session_state.capital_initial:
        diff = nouveau_capital - st.session_state.capital_initial
        st.session_state.capital_initial = nouveau_capital
        st.session_state.cash += diff
        st.rerun()

# ── Navigation par Onglets ────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💼 Portefeuille", "📋 Transactions", "🔥 Momentum"])

# ── ONGLET 1 : DASHBOARD ──
with tab1:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Valeur Totale", f"{total_portefeuille:.0f} €", f"Actifs: {valeur_actifs:.0f} €", delta_color="off")
    m2.metric("Fonds Investis", f"{fonds_investis:.0f} €", f"{len(df[df['quantite'] > 0])} lignes actives")
    m3.metric("Plus-Value Globale", f"{plus_value_globale:+.0f} €", f"{(plus_value_globale/st.session_state.capital_initial)*100:+.2f} %")
    m4.metric("Liquidités (Cash)", f"{st.session_state.cash:.0f} €", f"{(st.session_state.cash/total_portefeuille)*100 if total_portefeuille>0 else 100:.1f} % du compte", delta_color="off")

    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### Répartition par Couches")
        if valeur_actifs > 0:
            df_couche = df[df['quantite'] > 0].groupby('couche')['valeur'].sum().reset_index()
            fig = px.pie(df_couche, values='valeur', names='couche', hole=0.6, 
                         color='couche', color_discrete_map=COLORS)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun actif en portefeuille pour le moment.")

    with c2:
        st.markdown("### Exposition Sectorielle Active")
        if valeur_actifs > 0:
            df_secteur = df[df['quantite'] > 0].groupby('secteur')['valeur'].sum().reset_index()
            fig2 = px.pie(df_secteur, values='valeur', names='secteur', hole=0.6,
                          color='secteur', color_discrete_map=COLORS)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Aucun actif en portefeuille pour le moment.")

# ── ONGLET 2 : PORTEFEUILLE ──
with tab2:
    st.markdown("### Gestion du Portefeuille Actif")
    st.caption("Modifiez directement la colonne 'cours' dans le tableau ci-dessous pour mettre à jour les prix du marché.")
    
    # Edition des cours
    colonnes_visibles = ['ticker', 'nom', 'couche', 'secteur', 'quantite', 'cours', 'prixAchat', 'valeur', 'plus_value']
    df_display = df[colonnes_visibles].copy()
    
    edited_df = st.data_editor(
        df_display,
        column_config={
            "cours": st.column_config.NumberColumn("Cours Actuel (€)", format="%.2f", step=0.1),
            "ticker": "Ticker", "nom": "Actif", "quantite": "Qté",
            "prixAchat": st.column_config.NumberColumn("PRU (€)", disabled=True, format="%.2f"),
            "valeur": st.column_config.NumberColumn("Valeur (€)", disabled=True, format="%.2f"),
            "plus_value": st.column_config.NumberColumn("+/- Value (€)", disabled=True, format="%.2f"),
        },
        disabled=["ticker", "nom", "couche", "secteur", "quantite", "prixAchat", "valeur", "plus_value"],
        hide_index=True,
        use_container_width=True
    )
    
    # Mise à jour des cours en session state si modifiés dans le data_editor
    for i, row in edited_df.iterrows():
        nouveau_cours = row['cours']
        if st.session_state.df.at[i, 'cours'] != nouveau_cours:
            st.session_state.df.at[i, 'cours'] = nouveau_cours
            st.rerun()

    st.divider()
    st.markdown("### 💱 Passage d'Ordres")
    
    col_actif, col_qty, col_action = st.columns([2, 1, 1])
    with col_actif:
        selected_ticker = st.selectbox("Sélectionner l'actif", df['ticker'] + " - " + df['nom'])
        ticker_pur = selected_ticker.split(" - ")[0]
        actif_idx = df.index[df['ticker'] == ticker_pur][0]
        actif = df.iloc[actif_idx]
    with col_qty:
        qty = st.number_input("Quantité", min_value=1, value=1, step=1)
    with col_action:
        st.write("") # Spacer
        st.write("") # Spacer
        c_achat, c_vente = st.columns(2)
        
        # Logique d'Achat
        if c_achat.button("✅ Acheter", use_container_width=True):
            cout = actif['cours'] * qty
            if cout <= st.session_state.cash:
                ancienne_qty = st.session_state.df.at[actif_idx, 'quantite']
                ancien_pru = st.session_state.df.at[actif_idx, 'prixAchat']
                nouvelle_qty = ancienne_qty + qty
                nouveau_pru = ((ancien_pru * ancienne_qty) + cout) / nouvelle_qty if nouvelle_qty > 0 else actif['cours']
                
                st.session_state.df.at[actif_idx, 'quantite'] = nouvelle_qty
                st.session_state.df.at[actif_idx, 'prixAchat'] = nouveau_pru
                st.session_state.cash -= cout
                
                st.session_state.transactions.insert(0, {
                    "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Type": "ACHAT", "Ticker": ticker_pur, "Actif": actif['nom'],
                    "Qté": qty, "Prix": actif['cours'], "Total (€)": -cout
                })
                st.success(f"Achat de {qty} {ticker_pur} réussi !")
                st.rerun()
            else:
                st.error("Liquidités insuffisantes.")
                
        # Logique de Vente
        if c_vente.button("❌ Vendre", use_container_width=True):
            gain = actif['cours'] * qty
            if qty <= actif['quantite']:
                st.session_state.df.at[actif_idx, 'quantite'] -= qty
                st.session_state.cash += gain
                
                st.session_state.transactions.insert(0, {
                    "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Type": "VENTE", "Ticker": ticker_pur, "Actif": actif['nom'],
                    "Qté": qty, "Prix": actif['cours'], "Total (€)": gain
                })
                st.success(f"Vente de {qty} {ticker_pur} réussie !")
                st.rerun()
            else:
                st.error("Quantité insuffisante en portefeuille.")

# ── ONGLET 3 : TRANSACTIONS ──
with tab3:
    st.markdown("### Journal d'audit des ordres exécutés")
    if st.session_state.transactions:
        if st.button("🗑️ Purger le journal"):
            st.session_state.transactions = []
            st.rerun()
        df_trans = pd.DataFrame(st.session_state.transactions)
        st.dataframe(df_trans, hide_index=True, use_container_width=True)
    else:
        st.info("Aucun mouvement enregistré pour le moment.")

# ── ONGLET 4 : MOMENTUM ──
with tab4:
    st.markdown("### 🔥 Matrice des Configurations Momentum")
    
    score_moyen = df['momentum'].mean()
    forts = len(df[df['momentum'] >= 70])
    faibles = len(df[df['momentum'] < 55])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Score Moyen Portefeuille", f"{score_moyen:.0f} pts")
    col2.metric("Configurations Fortes (≥70)", forts)
    col3.metric("Divergences Baissières (<55)", faibles)
    
    st.divider()
    st.markdown("#### Classement Force Relative (Momentum Score)")
    
    # Affichage stylisé des scores momentum
    df_mom = df[['ticker', 'nom', 'couche', 'secteur', 'momentum']].sort_values(by='momentum', ascending=False).reset_index(drop=True)
    
    def color_momentum(val):
        if val >= 70: return 'color: #10B981; font-weight: bold;' # Vert
        elif val >= 55: return 'color: #F59E0B; font-weight: bold;' # Orange
        else: return 'color: #EF4444; font-weight: bold;' # Rouge
        
    def momentum_action(val):
        if val >= 70: return "⚡ Achat / Renfort"
        elif val >= 55: return "⏸ Statu Quo"
        else: return "⚠️ Allègement"
        
    df_mom['Action'] = df_mom['momentum'].apply(momentum_action)
    
    st.dataframe(
        df_mom.style.map(color_momentum, subset=['momentum', 'Action']),
        hide_index=True,
        use_container_width=True
    )

