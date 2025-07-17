import streamlit as st
import pandas as pd
import plotly.express as px
import groq
from datetime import datetime
import io

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI-Powered HR Kostenvergleich",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INDUSTRY TEMPLATES ---
INDUSTRY_TEMPLATES = {
    "Tech": {
        "hire_salary": 85000,
        "vacancy_months": 4,
        "social_percent": 22,
        "benefits_percent": 12,
        "prod_loss_percent": 50,
        "berater_percent": 30,
        "interview_hours": 15,
        "interview_rate": 80,
        "training_cost": 2000,
        "current_salary": 75000
    },
    "Healthcare": {
        "hire_salary": 65000,
        "vacancy_months": 3,
        "social_percent": 24,
        "benefits_percent": 15,
        "prod_loss_percent": 40,
        "berater_percent": 20,
        "interview_hours": 10,
        "interview_rate": 70,
        "training_cost": 1500,
        "current_salary": 55000
    },
    "Retail": {
        "hire_salary": 35000,
        "vacancy_months": 2,
        "social_percent": 20,
        "benefits_percent": 8,
        "prod_loss_percent": 30,
        "berater_percent": 15,
        "interview_hours": 8,
        "interview_rate": 50,
        "training_cost": 500,
        "current_salary": 30000
    },
    "Finance": {
        "hire_salary": 75000,
        "vacancy_months": 5,
        "social_percent": 23,
        "benefits_percent": 18,
        "prod_loss_percent": 45,
        "berater_percent": 25,
        "interview_hours": 12,
        "interview_rate": 90,
        "training_cost": 2500,
        "current_salary": 65000
    }
}

# --- SESSION STATE INIT ---
def reset_to_defaults():
    defaults = {
        "hire_salary": 60000,
        "vacancy_months": 3,
        "social_percent": 22,
        "benefits_percent": 8,
        "prod_loss_percent": 40,
        "industry": "General",
        "anzeigen_qty": 2,
        "anzeigen_price": 800,
        "berater_percent": 25,
        "interview_hours": 12,
        "interview_rate": 70,
        "assessment_qty": 1,
        "assessment_price": 1500,
        "reise_qty": 2,
        "reise_price": 300,
        "background_qty": 1,
        "background_price": 200,
        "produkt_price": 6000,
        "ueberstunden_qty": 30,
        "ueberstunden_price": 50,
        "extern_qty": 20,
        "extern_price": 400,
        "gehalt_price": 6000,
        "hr_hours": 10,
        "hr_rate": 50,
        "kollegen_hours": 15,
        "kollegen_rate": 60,
        "training_cost": 1000,
        "it_cost": 1200,
        "mentor_hours": 6,
        "mentor_rate": 60,
        "fehler_cost": 1400,
        "knowhow_cost": 2000,
        "kunden_cost": 2500,
        "team_cost": 2000,
        "current_salary": 60000,
        "increase_percent": 8,
        "social_increase_percent": 22,
        "benefits_increase_percent": 8,
    }
    for key, value in defaults.items():
        st.session_state[key] = value

def initialize_session_state():
    if 'initialized' not in st.session_state:
        reset_to_defaults()
        st.session_state.initialized = True

def load_template(template_name):
    template = INDUSTRY_TEMPLATES[template_name]
    for key, value in template.items():
        st.session_state[key] = value
    st.session_state['industry'] = template_name

# --- AI INIT ---
@st.cache_resource
def init_groq():
    try:
        api_key = st.secrets.get("GROQ_API_KEY") or st.session_state.get("groq_api_key")
        if not api_key:
            return None
        return groq.Groq(api_key=api_key)
    except Exception as e:
        st.error(f"KI-Initialisierung Fehler: {e}")
        return None

# --- COST CALCULATION (INCREMENTAL) ---
def calculate_costs():
    hire_salary = st.session_state.get('hire_salary', 60000)
    current_salary = st.session_state.get('current_salary', 60000)
    vacancy_months = st.session_state.get('vacancy_months', 3)
    social_percent = st.session_state.get('social_percent', 22)
    benefits_percent = st.session_state.get('benefits_percent', 8)
    prod_loss_percent = st.session_state.get('prod_loss_percent', 40)

    # Recruiting costs
    recruiting_costs = {
        "Stellenanzeigen": st.session_state.get('anzeigen_qty', 2) * st.session_state.get('anzeigen_price', 800),
        "Personalberater": hire_salary * (st.session_state.get('berater_percent', 25) / 100),
        "Interviews": st.session_state.get('interview_hours', 12) * st.session_state.get('interview_rate', 70),
        "Assessment Center": st.session_state.get('assessment_qty', 1) * st.session_state.get('assessment_price', 1500),
        "Reisekosten": st.session_state.get('reise_qty', 2) * st.session_state.get('reise_price', 300),
        "Background Checks": st.session_state.get('background_qty', 1) * st.session_state.get('background_price', 200),
    }
    recruiting_sum = sum(recruiting_costs.values())

    # Vacancy costs
    vacancy_costs = {
        "Entgangene Produktivität": vacancy_months * st.session_state.get('produkt_price', 6000),
        "Überstunden Team": st.session_state.get('ueberstunden_qty', 30) * st.session_state.get('ueberstunden_price', 50),
        "Externe Unterstützung": st.session_state.get('extern_qty', 20) * st.session_state.get('extern_price', 400),
        "Gehaltsersparnis": -(vacancy_months * st.session_state.get('gehalt_price', 6000)),
    }
    vacancy_sum = sum(vacancy_costs.values())

    # Onboarding costs
    onboarding_costs = {
        "HR-Aufwand": st.session_state.get('hr_hours', 10) * st.session_state.get('hr_rate', 50),
        "Einarbeitung Kollegen": st.session_state.get('kollegen_hours', 15) * st.session_state.get('kollegen_rate', 60),
        "Schulungen/Training": st.session_state.get('training_cost', 1000),
        "IT-Setup & Equipment": st.session_state.get('it_cost', 1200),
        "Mentor/Buddy-System": st.session_state.get('mentor_hours', 6) * st.session_state.get('mentor_rate', 60),
    }
    onboarding_sum = sum(onboarding_costs.values())

    # Productivity loss
    prod_loss_monthly = (hire_salary / 12) * (1 + social_percent / 100) * (prod_loss_percent / 100)
    productivity_sum = prod_loss_monthly * vacancy_months

    # Other costs
    other_costs = {
        "Fehlerrate": st.session_state.get('fehler_cost', 1400),
        "Know-how-Verlust": st.session_state.get('knowhow_cost', 2000),
        "Kundenbindung/Umsatz": st.session_state.get('kunden_cost', 2500),
        "Team-Moral": st.session_state.get('team_cost', 2000),
    }
    other_sum = sum(other_costs.values())

    # --- INCREMENTAL SALARY COSTS FOR NEW HIRE ---
    salary_difference = max(hire_salary - current_salary, 0)
    social_difference = salary_difference * (social_percent / 100)
    benefits_difference = salary_difference * (benefits_percent / 100)
    annual_salary_difference = salary_difference + social_difference + benefits_difference

    # Total incremental cost for new hire
    total_hire_incremental = (
        recruiting_sum + vacancy_sum + onboarding_sum +
        productivity_sum + other_sum + annual_salary_difference
    )

    # Salary increase costs (as before)
    increase_percent = st.session_state.get('increase_percent', 8)
    social_increase_percent = st.session_state.get('social_increase_percent', 22)
    benefits_increase_percent = st.session_state.get('benefits_increase_percent', 8)

    increase_amount = current_salary * (increase_percent / 100)
    social_increase = increase_amount * (social_increase_percent / 100)
    benefits_increase = increase_amount * (benefits_increase_percent / 100)
    total_salary_increase = increase_amount + social_increase + benefits_increase

    return {
        "recruiting": {"costs": recruiting_costs, "sum": recruiting_sum},
        "vacancy": {"costs": vacancy_costs, "sum": vacancy_sum},
        "onboarding": {"costs": onboarding_costs, "sum": onboarding_sum},
        "productivity": {"sum": productivity_sum},
        "other": {"costs": other_costs, "sum": other_sum},
        "fixed": {"sum": annual_salary_difference},
        "total_hire": total_hire_incremental,
        "total_salary_increase": total_salary_increase,
        "salary_breakdown": {
            "increase": increase_amount,
            "social": social_increase,
            "benefits": benefits_increase
        }
    }

# --- AI INSIGHTS ---
def get_ai_insights(groq_client, calculation_data, context_data):
    if not groq_client:
        return None
    try:
        prompt = f"""
        Als HR-Experte analysiere bitte diese Kostenvergleichsdaten und gib strategische Empfehlungen:

        KOSTENDATEN:
        - Neubesetzung Gesamtkosten: {calculation_data['total_hire']:,.0f} €
        - Gehaltserhöhung Gesamtkosten: {calculation_data['total_salary_increase']:,.0f} €
        - Jahresgehalt: {context_data['hire_salary']:,.0f} €
        - Branche: {context_data.get('industry', 'Unbekannt')}
        - Vakanzdauer: {context_data['vacancy_months']} Monate
        - Produktivitätsverlust: {context_data['prod_loss_percent']}%

        KOSTENAUFSCHLÜSSELUNG:
        - Recruiting: {calculation_data['recruiting']['sum']:,.0f} €
        - Vakanz: {calculation_data['vacancy']['sum']:,.0f} €
        - Onboarding: {calculation_data['onboarding']['sum']:,.0f} €
        - Produktivitätsverlust: {calculation_data['productivity']['sum']:,.0f} €
        - Weitere Kosten: {calculation_data['other']['sum']:,.0f} €

        Bitte analysiere und gib zurück:
        1. Strategische Empfehlung (Neubesetzung vs Gehaltserhöhung)
        2. Top 3 Kostentreiber identifizieren
        3. Konkrete Optimierungsvorschläge
        4. Risikobewertung für beide Optionen
        5. Langzeit-Perspektive (3-5 Jahre)

        Antworte auf Deutsch, präzise und geschäftsorientiert.
        """
        chat_completion = groq_client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": "Du bist ein erfahrener HR-Strategieberater mit 15+ Jahren Erfahrung in Personalkosten-Optimierung."
            }, {
                "role": "user", 
                "content": prompt
            }],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=1000
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"KI-Analyse Fehler: {e}")
        return None

def get_ai_scenarios(groq_client, calculation_data):
    if not groq_client:
        return None
    try:
        prompt = f"""
        Erstelle 3 realistische What-If-Szenarien für diesen HR-Kostenvergleich:

        BASISDATEN:
        - Neubesetzung: {calculation_data['total_hire']:,.0f} €
        - Gehaltserhöhung: {calculation_data['total_salary_increase']:,.0f} €

        Erstelle Szenarien für:
        1. Best-Case (optimistische Annahmen)
        2. Worst-Case (pessimistische Annahmen)  
        3. Economic Downturn (Wirtschaftskrise)

        Für jedes Szenario gib an:
        - Kurze Beschreibung der Annahmen
        - Geschätzte Kostenveränderung in % 
        - Empfehlung für dieses Szenario

        Format als strukturierten Text, nicht als JSON.
        """
        chat_completion = groq_client.chat.completions.create(
            messages=[{
                "role": "user", 
                "content": prompt
            }],
            model="llama-3.1-8b-instant",
            temperature=0.5,
            max_tokens=800
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Szenario-Generierung Fehler: {e}")
        return None

# --- MAIN APP ---
def main():
    initialize_session_state()
    st.title("🤖 AI-Powered HR Kostenvergleich")
    st.markdown("""
    **Intelligenter Kostenvergleich** zwischen Neubesetzung und Gehaltserhöhung mit **KI-gestützten Insights**.
    """)

    # AI API Key input (if not in secrets)
    groq_client = init_groq()
    if not groq_client:
        with st.expander("🔑 AI Setup", expanded=True):
            st.info("Für AI-Features benötigen Sie einen API Key.")
            api_key = st.text_input("AI API Key", type="password", help="API Key für KI-Funktionen")
            if api_key:
                st.session_state.groq_api_key = api_key
                groq_client = init_groq()
                if groq_client:
                    st.success("✅ AI erfolgreich verbunden!")
                    st.rerun()

    # Sidebar for main assumptions
    with st.sidebar:
        st.header("⚙️ Grundannahmen")
        col1, col2 = st.columns(2)
        with col1:
            template = st.selectbox("🏭 Branche", [""] + list(INDUSTRY_TEMPLATES.keys()))
            if template and st.button("Vorlage laden"):
                load_template(template)
                st.rerun()
        with col2:
            if st.button("🔄 Reset"):
                reset_to_defaults()
                st.rerun()
        st.divider()
        st.subheader("Grundparameter")
        st.number_input("Jahresgehalt (Neubesetzung) €", min_value=20000, max_value=200000, step=1000, key="hire_salary")
        st.number_input("Aktuelles Jahresgehalt (€)", min_value=20000, max_value=200000, step=1000, key="current_salary")
        st.number_input("Vakanzdauer (Monate)", min_value=1, max_value=24, step=1, key="vacancy_months")
        st.number_input("Sozialabgaben (%)", min_value=15, max_value=30, step=1, key="social_percent")
        st.number_input("Benefits (%)", min_value=5, max_value=25, step=1, key="benefits_percent")
        st.slider("Produktivitätsverlust (%)", min_value=0, max_value=100, step=5, key="prod_loss_percent")
        st.divider()
        st.subheader("🤖 AI Features")
        use_ai_insights = st.checkbox("AI-Insights aktivieren", value=bool(groq_client))
        use_ai_scenarios = st.checkbox("AI-Szenarien generieren", value=bool(groq_client))

    results = calculate_costs()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💼 Neubesetzung (Zusatzkosten)", f"{results['total_hire']:,.0f} €",
                 delta=f"{results['total_hire'] - results['total_salary_increase']:+,.0f} €")
    with col2:
        st.metric("💰 Gehaltserhöhung (Zusatzkosten)", f"{results['total_salary_increase']:,.0f} €")
    with col3:
        difference = abs(results['total_hire'] - results['total_salary_increase'])
        percentage = (difference / min(results['total_hire'], results['total_salary_increase'])) * 100 if min(results['total_hire'], results['total_salary_increase']) > 0 else 0
        st.metric("💡 Ersparnis", f"{difference:,.0f} €", f"{percentage:.1f}%")

    if results['total_hire'] > results['total_salary_increase']:
        st.success("🎯 Empfehlung: Gehaltserhöhung ist günstiger")
        st.info(f"💰 Sie sparen {difference:,.0f} € ({percentage:.1f}%) mit einer Gehaltserhöhung")
    else:
        st.info("🎯 Empfehlung: Neubesetzung ist günstiger")
        st.success(f"💰 Sie sparen {difference:,.0f} € ({percentage:.1f}%) mit einer Neubesetzung")

    # --- AI INSIGHTS ---
    if groq_client and use_ai_insights:
        with st.container():
            st.header("🧠 KI-gestützte Strategieanalyse")
            if st.button("🚀 AI-Analyse generieren", type="primary"):
                with st.spinner("🤖 KI analysiert Ihre Daten..."):
                    context_data = {
                        'hire_salary': st.session_state.get('hire_salary', 60000),
                        'vacancy_months': st.session_state.get('vacancy_months', 3),
                        'prod_loss_percent': st.session_state.get('prod_loss_percent', 40),
                        'industry': st.session_state.get('industry', 'General')
                    }
                    insights = get_ai_insights(groq_client, results, context_data)
                    if insights:
                        st.success("✅ AI-Analyse abgeschlossen!")
                        st.markdown("### 🎯 Strategische Empfehlungen")
                        st.markdown(insights)
                        st.session_state.ai_insights = insights
                        st.session_state.insights_timestamp = datetime.now()
            if hasattr(st.session_state, 'ai_insights'):
                st.markdown("### 📋 Letzte AI-Analyse")
                st.info(f"Erstellt: {st.session_state.insights_timestamp.strftime('%d.%m.%Y %H:%M')}")
                st.markdown(st.session_state.ai_insights)

    # --- AI SCENARIOS ---
    if groq_client and use_ai_scenarios:
        st.header("🔮 KI-generierte What-If-Szenarien")
        if st.button("🎲 AI-Szenarien generieren"):
            with st.spinner("🤖 KI erstellt Szenarien..."):
                scenarios = get_ai_scenarios(groq_client, results)
                if scenarios:
                    st.success("✅ Szenarien generiert!")
                    st.markdown("### 📈 What-If-Szenarien")
                    st.markdown(scenarios)
                    st.session_state.ai_scenarios = scenarios
                    st.session_state.scenarios_timestamp = datetime.now()
        if hasattr(st.session_state, 'ai_scenarios'):
            st.markdown("### 📋 Letzte AI-Szenarien")
            st.info(f"Erstellt: {st.session_state.scenarios_timestamp.strftime('%d.%m.%Y %H:%M')}")
            st.markdown(st.session_state.ai_scenarios)

    # --- DETAILED INPUTS ---
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header("🏢 Neubesetzung - Detailkosten")
        with st.expander("🧲 Recruiting-Kosten", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.number_input("Stellenanzeigen (Anzahl)", min_value=0, key="anzeigen_qty")
                st.number_input("Stellenanzeigen (€ pro Anzeige)", min_value=0, key="anzeigen_price")
                st.number_input("Personalberater (%)", min_value=0, max_value=50, key="berater_percent")
            with col_b:
                st.number_input("Interview-Stunden", min_value=0, key="interview_hours")
                st.number_input("Interview-Stundensatz (€)", min_value=0, key="interview_rate")
                st.number_input("Assessment Center (€)", min_value=0, key="assessment_price")
        with st.expander("⏳ Vakanz-Kosten", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.number_input("Entgangene Produktivität (€/Monat)", min_value=0, key="produkt_price")
                st.number_input("Überstunden (Anzahl)", min_value=0, key="ueberstunden_qty")
                st.number_input("Überstunden (€/Std)", min_value=0, key="ueberstunden_price")
            with col_b:
                st.number_input("Externe Unterstützung (Tage)", min_value=0, key="extern_qty")
                st.number_input("Externe Unterstützung (€/Tag)", min_value=0, key="extern_price")
                st.number_input("Monatliches Gehalt (€)", min_value=0, key="gehalt_price")
        with st.expander("🎓 Onboarding-Kosten", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.number_input("HR-Aufwand (Stunden)", min_value=0, key="hr_hours")
                st.number_input("HR-Stundensatz (€)", min_value=0, key="hr_rate")
                st.number_input("Einarbeitung Kollegen (Stunden)", min_value=0, key="kollegen_hours")
                st.number_input("Kollegen-Stundensatz (€)", min_value=0, key="kollegen_rate")
            with col_b:
                st.number_input("Schulungen/Training (€)", min_value=0, key="training_cost")
                st.number_input("IT-Setup & Equipment (€)", min_value=0, key="it_cost")
                st.number_input("Mentor-Stunden", min_value=0, key="mentor_hours")
                st.number_input("Mentor-Stundensatz (€)", min_value=0, key="mentor_rate")
        with st.expander("⚠️ Weitere Kosten", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                st.number_input("Fehlerrate (€)", min_value=0, key="fehler_cost")
                st.number_input("Know-how-Verlust (€)", min_value=0, key="knowhow_cost")
            with col_b:
                st.number_input("Kundenbindung/Umsatzverluste (€)", min_value=0, key="kunden_cost")
                st.number_input("Team-Moral (€)", min_value=0, key="team_cost")
        st.header("💰 Alternative: Gehaltserhöhung")
        with st.expander("💶 Gehaltserhöhung Details", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.number_input("Erhöhung (%)", min_value=0, max_value=50, key="increase_percent")
            with col_b:
                st.number_input("Sozialabgaben auf Erhöhung (%)", min_value=0, key="social_increase_percent")
                st.number_input("Benefits auf Erhöhung (%)", min_value=0, key="benefits_increase_percent")

    with col2:
        st.subheader("📊 Kostenverteilung")
        categories = ["Recruiting", "Vakanz", "Onboarding", "Produktivität", "Weitere", "Gehaltsdifferenz"]
        values = [
            results['recruiting']['sum'],
            results['vacancy']['sum'],
            results['onboarding']['sum'],
            results['productivity']['sum'],
            results['other']['sum'],
            results['fixed']['sum']
        ]
        fig = px.pie(
            values=values,
            names=categories,
            title="Neubesetzung - Kostenverteilung",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("⚖️ Direktvergleich")
        comparison_data = {
            "Option": ["Neubesetzung", "Gehaltserhöhung"],
            "Kosten": [results['total_hire'], results['total_salary_increase']]
        }
        fig2 = px.bar(
            comparison_data,
            x="Option",
            y="Kosten",
            title="Kostenvergleich",
            color="Kosten",
            color_continuous_scale="RdYlGn_r"
        )
        fig2.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🤖 Powered by <strong>Künstliche Intelligenz</strong>  💼 HR Intelligence Platform</p>
        <p><small>Alle Berechnungen sind Schätzungen. Konsultieren Sie einen HR-Experten für finale Entscheidungen.</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
