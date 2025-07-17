# Create the complete corrected Streamlit application
complete_code = '''import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import groq
import json
from datetime import datetime
import io
import base64

# Page configuration
st.set_page_config(
    page_title="AI-Powered HR Kostenvergleich",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Groq client
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

# Industry templates
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
    }
}

def create_detailed_csv_report(results, context_data, ai_insights=None, ai_scenarios=None):
    """Generate a comprehensive CSV report"""
    report = []
    
    # Header
    report.append("HR KOSTENVERGLEICH - DETAILBERICHT (INCREMENTAL ANALYSIS)")
    report.append("=" * 60)
    report.append("")
    report.append(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    report.append(f"Branche: {context_data.get('industry', 'General')}")
    report.append("Vergleichstyp: Inkrementelle Kosten (Zusatzkosten)")
    report.append("")
    
    # Executive Summary
    if results['total_hire'] > results['total_salary_increase']:
        recommendation = f"Gehaltserhöhung ist günstiger um {results['total_hire'] - results['total_salary_increase']:,.0f} €"
    else:
        recommendation = f"Neubesetzung ist günstiger um {results['total_salary_increase'] - results['total_hire']:,.0f} €"
    
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 20)
    report.append(f"Empfehlung: {recommendation}")
    report.append(f"Neubesetzung Zusatzkosten: {results['total_hire']:,.0f} €")
    report.append(f"Gehaltserhöhung Kosten: {results['total_salary_increase']:,.0f} €")
    report.append("")
    
    # Parameters
    report.append("PARAMETER")
    report.append("-" * 20)
    report.append(f"Jahresgehalt (Neubesetzung): {context_data.get('hire_salary', 0):,.0f} €")
    report.append(f"Aktuelles Gehalt: {context_data.get('current_salary', 0):,.0f} €")
    report.append(f"Gehaltsdifferenz: {results.get('hire_vs_current_salary', 0):,.0f} €")
    report.append(f"Vakanzdauer: {context_data.get('vacancy_months', 0)} Monate")
    report.append(f"Produktivitätsverlust: {context_data.get('prod_loss_percent', 0)}%")
    report.append("")
    
    # Cost Breakdown
    report.append("KOSTENAUFSCHLÜSSELUNG NEUBESETZUNG (ZUSATZKOSTEN)")
    report.append("-" * 50)
    report.append(f"Recruiting: {results['recruiting']['sum']:,.0f} € ({results['recruiting']['sum']/results['total_hire']*100:.1f}%)")
    report.append(f"Vakanz: {results['vacancy']['sum']:,.0f} € ({results['vacancy']['sum']/results['total_hire']*100:.1f}%)")
    report.append(f"Onboarding: {results['onboarding']['sum']:,.0f} € ({results['onboarding']['sum']/results['total_hire']*100:.1f}%)")
    report.append(f"Produktivitätsverlust: {results['productivity']['sum']:,.0f} € ({results['productivity']['sum']/results['total_hire']*100:.1f}%)")
    report.append(f"Weitere Kosten: {results['other']['sum']:,.0f} € ({results['other']['sum']/results['total_hire']*100:.1f}%)")
    report.append(f"Gehaltsdifferenz: {results['salary_difference']['sum']:,.0f} € ({results['salary_difference']['sum']/results['total_hire']*100:.1f}%)")
    report.append(f"GESAMT ZUSATZKOSTEN: {results['total_hire']:,.0f} €")
    report.append("")
    
    # Detailed costs
    report.append("DETAILKOSTEN")
    report.append("-" * 20)
    report.append("Recruiting-Details:")
    for item, cost in results['recruiting']['costs'].items():
        report.append(f"  {item}: {cost:,.0f} €")
    
    report.append("Vakanz-Details:")
    for item, cost in results['vacancy']['costs'].items():
        report.append(f"  {item}: {cost:,.0f} €")
    
    report.append("Onboarding-Details:")
    for item, cost in results['onboarding']['costs'].items():
        report.append(f"  {item}: {cost:,.0f} €")
    
    report.append("Weitere Kosten-Details:")
    for item, cost in results['other']['costs'].items():
        report.append(f"  {item}: {cost:,.0f} €")
    report.append("")
    
    # AI sections
    if ai_insights:
        report.append("KI-STRATEGIEANALYSE")
        report.append("-" * 20)
        report.append(ai_insights)
        report.append("")
    
    if ai_scenarios:
        report.append("KI-SZENARIEN")
        report.append("-" * 20)
        report.append(ai_scenarios)
        report.append("")
    
    return "\\n".join(report)

def create_excel_dataframe(results, context_data):
    """Create structured data for Excel export"""
    # Summary data
    summary_data = {
        'Kostenart': [
            'Neubesetzung Zusatzkosten Gesamt',
            '- Recruiting',
            '- Vakanz', 
            '- Onboarding',
            '- Produktivitätsverlust',
            '- Weitere Kosten',
            '- Gehaltsdifferenz',
            '',
            'Gehaltserhöhung Gesamt'
        ],
        'Betrag (€)': [
            results['total_hire'],
            results['recruiting']['sum'],
            results['vacancy']['sum'],
            results['onboarding']['sum'],
            results['productivity']['sum'],
            results['other']['sum'],
            results['salary_difference']['sum'],
            0,
            results['total_salary_increase']
        ],
        'Anteil (%)': [
            100.0,
            results['recruiting']['sum']/results['total_hire']*100,
            results['vacancy']['sum']/results['total_hire']*100,
            results['onboarding']['sum']/results['total_hire']*100,
            results['productivity']['sum']/results['total_hire']*100,
            results['other']['sum']/results['total_hire']*100,
            results['salary_difference']['sum']/results['total_hire']*100,
            0,
            100.0
        ]
    }
    
    # Parameters data
    param_data = {
        'Parameter': [
            'Jahresgehalt (Neubesetzung)',
            'Aktuelles Gehalt',
            'Gehaltsdifferenz',
            'Vakanzdauer',
            'Branche',
            'Produktivitätsverlust',
            'Vergleichstyp',
            'Analyse-Datum'
        ],
        'Wert': [
            f"{context_data.get('hire_salary', 0):,.0f} €",
            f"{context_data.get('current_salary', 0):,.0f} €",
            f"{results.get('hire_vs_current_salary', 0):,.0f} €",
            f"{context_data.get('vacancy_months', 0)} Monate",
            context_data.get('industry', 'General'),
            f"{context_data.get('prod_loss_percent', 0)}%",
            "Inkrementelle Kosten",
            datetime.now().strftime('%d.%m.%Y %H:%M')
        ]
    }
    
    return pd.DataFrame(summary_data), pd.DataFrame(param_data)

def get_ai_insights(groq_client, calculation_data, context_data):
    """Get AI-powered insights using Groq"""
    if not groq_client:
        return None
    
    try:
        prompt = f"""
        Als HR-Experte analysiere bitte diese INKREMENTELLEN Kostenvergleichsdaten und gib strategische Empfehlungen:

        WICHTIG: Dies ist ein Vergleich von ZUSATZKOSTEN (inkrementelle Analyse):
        - Neubesetzung: Alle Zusatzkosten im Vergleich zum aktuellen Mitarbeiter
        - Gehaltserhöhung: Nur die zusätzlichen Kosten der Erhöhung

        KOSTENDATEN:
        - Neubesetzung Zusatzkosten: {calculation_data['total_hire']:,.0f} €
        - Gehaltserhöhung Kosten: {calculation_data['total_salary_increase']:,.0f} €
        - Neues Jahresgehalt: {context_data['hire_salary']:,.0f} €
        - Aktuelles Gehalt: {context_data.get('current_salary', 60000):,.0f} €
        - Gehaltsdifferenz: {calculation_data.get('hire_vs_current_salary', 0):,.0f} €
        - Branche: {context_data.get('industry', 'Unbekannt')}
        - Vakanzdauer: {context_data['vacancy_months']} Monate
        - Produktivitätsverlust: {context_data['prod_loss_percent']}%

        KOSTENAUFSCHLÜSSELUNG:
        - Recruiting: {calculation_data['recruiting']['sum']:,.0f} €
        - Vakanz: {calculation_data['vacancy']['sum']:,.0f} €
        - Onboarding: {calculation_data['onboarding']['sum']:,.0f} €
        - Produktivitätsverlust: {calculation_data['productivity']['sum']:,.0f} €
        - Weitere Kosten: {calculation_data['other']['sum']:,.0f} €
        - Gehaltsdifferenz: {calculation_data['salary_difference']['sum']:,.0f} €

        Bitte analysiere und gib zurück:
        1. Strategische Empfehlung (Neubesetzung vs Gehaltserhöhung)
        2. Top 3 Kostentreiber identifizieren
        3. Konkrete Optimierungsvorschläge
        4. Risikobewertung für beide Optionen
        5. Langzeit-Perspektive (3-5 Jahre)

        Berücksichtige, dass dies eine inkrementelle Kostenanalyse ist.
        Antworte auf Deutsch, präzise und geschäftsorientiert.
        """

        chat_completion = groq_client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": "Du bist ein erfahrener HR-Strategieberater mit 15+ Jahren Erfahrung in Personalkosten-Optimierung und inkrementeller Kostenanalyse."
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
    """Generate AI-powered what-if scenarios"""
    if not groq_client:
        return None
    
    try:
        prompt = f"""
        Erstelle 3 realistische What-If-Szenarien für diesen HR-Kostenvergleich (INKREMENTELLE ANALYSE):

        BASISDATEN:
        - Neubesetzung Zusatzkosten: {calculation_data['total_hire']:,.0f} €
        - Gehaltserhöhung: {calculation_data['total_salary_increase']:,.0f} €

        Erstelle Szenarien für:
        1. Best-Case (optimistische Annahmen)
        2. Worst-Case (pessimistische Annahmen)  
        3. Economic Downturn (Wirtschaftskrise)

        Für jedes Szenario gib an:
        - Kurze Beschreibung der Annahmen
        - Geschätzte Kostenveränderung in % 
        - Empfehlung für dieses Szenario

        Berücksichtige, dass dies eine inkrementelle Kostenanalyse ist.
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

def load_template(template_name):
    """Load industry template into session state"""
    template = INDUSTRY_TEMPLATES[template_name]
    for key, value in template.items():
        st.session_state[key] = value
    st.session_state['industry'] = template_name

def reset_to_defaults():
    """Reset all values to defaults"""
    defaults = {
        # Basic assumptions
        "hire_salary": 60000,
        "vacancy_months": 3,
        "social_percent": 22,
        "benefits_percent": 8,
        "prod_loss_percent": 40,
        "industry": "General",
        
        # Recruiting costs
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
        
        # Vacancy costs
        "produkt_price": 6000,
        "ueberstunden_qty": 30,
        "ueberstunden_price": 50,
        "extern_qty": 20,
        "extern_price": 400,
        "gehalt_price": 6000,
        
        # Onboarding costs
        "hr_hours": 10,
        "hr_rate": 50,
        "kollegen_hours": 15,
        "kollegen_rate": 60,
        "training_cost": 1000,
        "it_cost": 1200,
        "mentor_hours": 6,
        "mentor_rate": 60,
        
        # Other costs
        "fehler_cost": 1400,
        "knowhow_cost": 2000,
        "kunden_cost": 2500,
        "team_cost": 2000,
        
        # Salary increase
        "current_salary": 60000,
        "increase_percent": 8,
        "social_increase_percent": 22,
        "benefits_increase_percent": 8,
    }
    
    for key, value in defaults.items():
        st.session_state[key] = value

def initialize_session_state():
    """Initialize session state with default values"""
    if 'initialized' not in st.session_state:
        reset_to_defaults()
        st.session_state.initialized = True

def calculate_costs():
    """Calculate all costs and return results - FIXED for proper incremental comparison"""
    # Get values from session state
    hire_salary = st.session_state.get('hire_salary', 60000)
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
    
    # Productivity loss during ramp-up (first few months of new hire)
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
    
    # FIXED: Calculate salary difference between new hire and current employee
    current_salary = st.session_state.get('current_salary', 60000)
    
    # Salary difference (could be positive or negative)
    salary_difference = hire_salary - current_salary
    social_difference = salary_difference * (social_percent / 100)
    benefits_difference = salary_difference * (benefits_percent / 100)
    annual_salary_difference = salary_difference + social_difference + benefits_difference
    
    # FIXED: Total incremental cost for new hire (excluding baseline salary costs)
    total_hire_incremental = (recruiting_sum + vacancy_sum + onboarding_sum + 
                            productivity_sum + other_sum + annual_salary_difference)
    
    # Salary increase costs (already incremental)
    increase_percent = st.session_state.get('increase_percent', 8)
    social_increase_percent = st.session_state.get('social_increase_percent', 22)
    benefits_increase_percent = st.session_state.get('benefits_increase_percent', 8)
    
    increase_amount = current_salary * (increase_percent / 100)
    social_increase = increase_amount * (social_increase_percent / 100)
    benefits_increase = increase_amount * (benefits_increase_percent / 100)
    total_salary_increase = increase_amount + social_increase + benefits_increase
    
    # For display purposes, also calculate full employment costs
    social_hire = hire_salary * (social_percent / 100)
    benefits_hire = hire_salary * (benefits_percent / 100)
    full_employment_cost = hire_salary + social_hire + benefits_hire
    
    return {
        "recruiting": {"costs": recruiting_costs, "sum": recruiting_sum},
        "vacancy": {"costs": vacancy_costs, "sum": vacancy_sum},
        "onboarding": {"costs": onboarding_costs, "sum": onboarding_sum},
        "productivity": {"sum": productivity_sum},
        "other": {"costs": other_costs, "sum": other_sum},
        "salary_difference": {"sum": annual_salary_difference},  # NEW: Show salary difference
        "total_hire": total_hire_incremental,  # FIXED: Now truly incremental
        "total_salary_increase": total_salary_increase,
        "salary_breakdown": {
            "increase": increase_amount,
            "social": social_increase,
            "benefits": benefits_increase
        },
        # Additional info for display
        "full_employment_cost": full_employment_cost,
        "current_total_cost": current_salary * (1 + social_increase_percent/100 + benefits_increase_percent/100),
        "hire_vs_current_salary": salary_difference,
        "comparison_type": "incremental"  # Flag to show this is incremental comparison
    }

def main():
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🤖 AI-Powered HR Kostenvergleich")
    st.markdown("""
    **Intelligenter Kostenvergleich** zwischen Neubesetzung und Gehaltserhöhung mit **KI-gestützten Insights**. 
    Alle Werte sind editierbar und werden in Echtzeit mit AI-Empfehlungen aktualisiert.
    
    ⚡ **Inkrementelle Analyse**: Vergleicht nur die Zusatzkosten beider Optionen.
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
        
        # Industry template selector
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
        
        # Basic assumptions
        st.subheader("Grundparameter")
        st.number_input("Jahresgehalt (Neubesetzung) €", 
                       min_value=20000, max_value=200000, step=1000,
                       key="hire_salary")
        
        st.number_input("Aktuelles Jahresgehalt €", 
                       min_value=20000, max_value=200000, step=1000,
                       key="current_salary",
                       help="Gehalt des aktuellen Mitarbeiters für Vergleich")
        
        st.number_input("Vakanzdauer (Monate)", 
                       min_value=1, max_value=24, step=1,
                       key="vacancy_months")
        
        st.number_input("Sozialabgaben (%)", 
                       min_value=15, max_value=30, step=1,
                       key="social_percent")
        
        st.number_input("Benefits (%)", 
                       min_value=5, max_value=25, step=1,
                       key="benefits_percent")
        
        st.slider("Produktivitätsverlust (%)", 
                 min_value=0, max_value=100, step=5,
                 key="prod_loss_percent",
                 help="Wie viel Prozent der Arbeitsleistung fehlen pro Monat während der Einarbeitung?")
        
        # Show salary difference
        hire_sal = st.session_state.get('hire_salary', 60000)
        current_sal = st.session_state.get('current_salary', 60000)
        diff = hire_sal - current_sal
        if diff > 0:
            st.info(f"💰 Neuer Mitarbeiter kostet {diff:,.0f} € mehr pro Jahr")
        elif diff
