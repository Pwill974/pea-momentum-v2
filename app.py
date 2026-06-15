import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime

# ── Configuration de la page et Thème Sombre ──────────────────────────────────
st.set_page_config(page_title="TKL ZEN Portfolio", page_icon="📈", layout="wide")

# Injection CSS pour forcer le Dark Mode et styliser les conteneurs comme la maquette
st.markdown("""
    <style>
    .stApp {
        background-color: #0B0F1A;
        color: #FFFFFF;
    }
    h1, h2, h3, p, span, label {
        color: #FFFFFF !important;
    }
    /* Style des cartes de métriques */
    div[data-testid="metric-container"] {
        background-color: #111625;
        border: 1px solid #1E2D45;
        padding: 15px;
        border-radius: 12px;
    }
    div[data-testid="stMetricValue"] > div {
        color: #00D4AA !important;
    }
    /* Style des Onglets */
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
    /* Style de la carte personnalisée Dashboard */
    .dashboard-card {
        background-color: #111625;
        border: 1px solid #1E2D45;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)


# ── Fonction de Vérification du Mot de Passe Sécurisé ─────────────────────────
def check_password():
    """Retourne True si l'utilisateur est authentifié via st.secrets."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔒 Accès Sécurisé</h2>", unsafe_allow_html=True)
        password_input = st.text_input("Entrez le mot de passe :", type="password")
        
        if st.button("Se connecter", use_container_width=True):
            if password_input == st.secrets["password"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect.")
    return False


# ── Lancement de l'application après authentification ─────────────────────────
if check_password():

    # Configuration des Tickers Yahoo Finance
    YF_MAPPING = {
        "EWLD": "EWLD.PA", "PE500": "PE500.PA", "PUST": "PUST.PA", "PCEU": "PCEU.PA",
        "GUARD": "GUARD.PA", "SU": "SU.PA", "AI": "AI.PA", "AM": "AM.PA",
        "HO": "HO.PA", "STM": "STMPA.PA", "SAN": "SAN.PA", "PAEEM": "PAEEM.PA", "TTE": "TTE.PA"
    }

    @st.cache_data(ttl=900)
    def fetch_live_prices():
        live_prices = {}
        for ticker, yf_symbol in YF_MAPPING.items():
            try:
                stock = yf.Ticker(yf_symbol)
                hist = stock.history(period="1d")
                if not hist.empty:
                    live_prices[ticker] = float(hist['Close'].iloc[-1])
            except Exception:
                pass
        return live_prices

    # ── Données Initiales ─────────────────────────────────────────────────────
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

    if 'init' not in st.session_state:
        base_df = pd.DataFrame(INITIAL_PORTFOLIO)
        base_df['momentum'] = base_df['id'].map(MOMENTUM_SCORES)
        
        with st.spinner("Extraction des cours en direct..."):
            market_prices = fetch_live_prices()
            for tk, price in market_prices.items():
                base_df.loc[base_df['ticker'] == tk, 'cours'] = price
                
        st.session_state.df = base_df
        st.session_state.transactions = []
        st.session_state.capital_initial = 10000.0
        st.session_state.cash = 10000.0
        st.session_state.init = True

    df = st.session_state.df

    # ── Calculs Réactifs Globaux ──────────────────────────────────────────────
    df['valeur'] = df['cours'] * df['quantite']
    df['pru_total'] = df['prixAchat'] * df['quantite']
    df['plus_value'] = df['valeur'] - df['pru_total']

    valeur_actifs = df['valeur'].sum()
    total_portefeuille = valeur_actifs + st.session_state.cash
    fonds_investis = df['pru_total'].sum()
    plus_value_globale = total_portefeuille - st.session_state.capital_initial
    total_alloc_cible = df['alloc'].sum()

    # Calcul des allocations actuelles réelles
    if total_portefeuille > 0:
        df['alloc_actuelle'] = (df['valeur'] / total_portefeuille) * 100
    else:
        df['alloc_actuelle'] = 0.0

    # CALCUL DE LA QUANTITÉ CIBLE IDEALE (Basé sur la valeur totale du portefeuille)
    df['valeur_cible_theorique'] = total_portefeuille * (df['alloc'] / 100)
    df['qte_cible'] = df.apply(lambda r: int(r['valeur_cible_theorique'] / r['cours']) if r['cours'] > 0 else 0, axis=1)

    # ── En-tête ───────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("## 📈 TKL ZEN Portfolio")
        st.caption("PEA Fortuneo · Stratégie Momentum · Flux Temps Réel 🟢")
    with col2:
        nouveau_capital = st.number_input("Capital Initial (€)", value=st.session_state.capital_initial, step=100.0)
        if nouveau_capital != st.session_state.capital_initial:
            diff = nouveau_capital - st.session_state.capital_initial
            st.session_state.capital_initial = nouveau_capital
            st.session_state.cash += diff
            st.rerun()
    with col3:
        st.write("") 
        st.write("") 
        if st.button("🔄 Rafraîchir les cours", use_container_width=True):
            st.cache_data.clear()
            with st.spinner("Actualisation..."):
                market_prices = fetch_live_prices()
                for tk, price in market_prices.items():
                    st.session_state.df.loc[st.session_state.df['ticker'] == tk, 'cours'] = price
            st.rerun()

    # ── Onglets ───────────────────────────────────────────────────────────────
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
            st.markdown('<div class="dashboard-card"><h3>Répartition stratégique</h3>', unsafe_allow_html=True)
            if valeur_actifs > 0:
                df_couche = df[df['quantite'] > 0].groupby('couche')['valeur'].sum().reset_index()
                fig = px.pie(df_couche, values='valeur', names='couche', hole=0.7, 
                             color='couche', color_discrete_map=COLORS)
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                    font_color="white", margin=dict(t=10, b=10, l=10, r=10),
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1)
                )
                fig.update_traces(textinfo='percent', textfont_size=14)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucun actif en portefeuille. Les répartitions apparaîtront ici après vos achats.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="dashboard-card"><h3>Répartition sectorielle</h3>', unsafe_allow_html=True)
            if valeur_actifs > 0:
                df_secteur = df[df['quantite'] > 0].groupby('secteur')['valeur'].sum().reset_index()
                df_secteur['pct'] = (df_secteur['valeur'] / valeur_actifs) * 100
                df_secteur = df_secteur.sort_values(by='pct', ascending=False)
                
                html_progress_bars = ""
                for _, row in df_secteur.iterrows():
                    sect = row['secteur']
                    pct = row['pct']
                    color = COLORS.get(sect, "#3B82F6")
                    
                    html_progress_bars += f"""
                    <div style="margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                            <span style="color: #94A3B8; font-size: 14px; font-weight: 500;">{sect}</span>
                            <span style="color: {color}; font-weight: bold; font-size: 14px;">{pct:.0f}%</span>
                        </div>
                        <div style="background-color: #1E293B; border-radius: 999px; height: 8px; width: 100%;">
                            <div style="background-color: {color}; height: 8px; border-radius: 999px; width: {pct}%;"></div>
                        </div>
                    </div>
                    """
                st.markdown(html_progress_bars, unsafe_allow_html=True)
            else:
                st.info("Aucun actif en portefeuille pour calculer les secteurs.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── ONGLET 2 : PORTEFEUILLE (GESTION DES QUANTITÉS ET DE L'ALLOCATION AUTOMATIQUE) ──
    with tab2:
        st.markdown("### Gestion du Portefeuille Actif & Allocations")
        st.caption("Ajuste tes % cibles dans **Alloc. Cible (%)** puis utilise le bouton robot ci-dessous pour répartir tes lignes instantanément.")
        
        # Barre d'état des allocations
        if total_alloc_cible == 100:
            st.success(f"🎯 Total des allocations cibles : {total_alloc_cible}% (Parfaitement équilibré)")
        elif total_alloc_cible > 100:
            st.warning(f"⚠️ Total des allocations cibles : {total_alloc_cible}% (Supérieur à 100%, veuillez ajuster)")
        else:
            st.info(f"ℹ️ Total des allocations cibles : {total_alloc_cible}% (Le total cible actuel est inférieur à 100%)")

        # BOUTON ROBOT DE RÉPARTITION AUTOMATIQUE
        if st.button("🤖 Répartir automatiquement les quantités (Calibrage Cible)", use_container_width=True, type="primary"):
            capital_total_actuel = total_portefeuille
            valeur_totale_allouee = 0
            
            # Application de la formule sur chaque ligne de la session_state
            for idx, row in st.session_state.df.iterrows():
                # Calcul de la enveloppe budgétaire dédiée à cet actif
                budget_actif = capital_total_actuel * (row['alloc'] / 100)
                # Calcul du nombre de parts entières achetables
                qte_auto = int(budget_actif / row['cours']) if row['cours'] > 0 else 0
                
                st.session_state.df.at[idx, 'quantite'] = qte_auto
                # Si la ligne était à 0, on initialise le PRU au cours actuel du marché
                if qte_auto > 0 and st.session_state.df.at[idx, 'prixAchat'] == row['cours']:
                    st.session_state.df.at[idx, 'prixAchat'] = row['cours']
                
                valeur_totale_allouee += qte_auto * row['cours']
            
            # Ajustement du cash restant avec le reliquat non investi
            st.session_state.cash = capital_total_actuel - valeur_totale_allouee
            st.success("✅ Répartition automatique appliquée avec succès sur l'ensemble de vos actifs !")
            st.rerun()

        st.divider()

        # Liste complète incluant la colonne Qté Cible calculée
        colonnes_visibles = ['ticker', 'nom', 'alloc', 'alloc_actuelle', 'quantite', 'qte_cible', 'cours', 'valeur', 'plus_value']
        df_display = df[colonnes_visibles].copy()
        
        edited_df = st.data_editor(
            df_display,
            column_config={
                "alloc": st.column_config.NumberColumn("Alloc. Cible (%)", format="%d %%", min_value=0, max_value=100, step=1),
                "alloc_actuelle": st.column_config.NumberColumn("Alloc. Actuelle (%)", format="%.1f %%", disabled=True),
                "quantite": st.column_config.NumberColumn("Qté Actuelle", format="%d", disabled=True),
                "qte_cible": st.column_config.NumberColumn("⚠️ Qté Cible", format="%d", disabled=True, help="Quantité idéale théorique selon vos objectifs."),
                "cours": st.column_config.NumberColumn("Cours Marché (€)", format="%.2f", step=0.01),
                "ticker": "Ticker", "nom": "Actif",
                "valeur": st.column_config.NumberColumn("Valeur (€)", disabled=True, format="%.2f"),
                "plus_value": st.column_config.NumberColumn("+/- Value (€)", disabled=True, format="%.2f"),
            },
            disabled=["ticker", "nom", "quantite", "qte_cible", "alloc_actuelle", "valeur", "plus_value"],
            hide_index=True,
            use_container_width=True
        )
        
        # Enregistrement en direct si modifications manuelles de l'allocation ou des cours
        for i, row in edited_df.iterrows():
            nouveau_cours = row['cours']
            nouvelle_alloc = row['alloc']
            if st.session_state.df.at[i, 'cours'] != nouveau_cours or st.session_state.df.at[i, 'alloc'] != nouvelle_alloc:
                st.session_state.df.at[i, 'cours'] = nouveau_cours
                st.session_state.df.at[i, 'alloc'] = nouvelle_alloc
                st.rerun()

        st.divider()
        st.markdown("### 💱 Passage d'Ordres Manuels")
        
        col_actif, col_qty, col_action = st.columns([2, 1, 1])
        with col_actif:
            selected_ticker = st.selectbox("Sélectionner l'actif", df['ticker'] + " - " + df['nom'])
            ticker_pur = selected_ticker.split(" - ")[0]
            actif_idx = df.index[df['ticker'] == ticker_pur][0]
            actif = df.iloc[actif_idx]
        with col_qty:
            qty = st.number_input("Quantité", min_value=1, value=1, step=1)
        with col_action:
            st.write("")
            st.write("")
            c_achat, c_vente = st.columns(2)
            
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
        
        df_mom = df[['ticker', 'nom', 'couche', 'secteur', 'momentum']].sort_values(by='momentum', ascending=False).reset_index(drop=True)
        
        def color_momentum(val):
            try:
                if isinstance(val, (int, float)):
                    if val >= 70: return 'color: #10B981; font-weight: bold;'
                    elif val >= 55: return 'color: #F59E0B; font-weight: bold;'
                    else: return 'color: #EF4444; font-weight: bold;'
                elif isinstance(val, str):
                    if "⚡" in val or "Achat" in val: return 'color: #10B981; font-weight: bold;'
                    elif "⏸" in val or "Statu" in val: return 'color: #F59E0B; font-weight: bold;'
                    elif "⚠️" in val or "Allègement" in val: return 'color: #EF4444; font-weight: bold;'
            except Exception:
                pass
            return ''
            
        def momentum_action(val):
            if val >= 70: return "⚡ Achat / Renfort"
            elif val >= 55: return "⏸ Statu Quo"
            else: return "⚠️ Allègement"
            
        df_mom['Action'] = df_mom['momentum'].apply(momentum_action)
        
        styled_df = df_mom.style.map(color_momentum, subset=['momentum', 'Action'])
        st.dataframe(styled_df, hide_index=True, use_container_width=True)
