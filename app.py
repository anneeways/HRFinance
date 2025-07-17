# Create the corrected version with proper incremental cost comparison
with open('hr_app_incremental_fixed.py', 'w', encoding='utf-8') as f:
    f.write("""import streamlit as st
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
        "current_salary": 75000,
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
        "current_salary": 58000,
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
        "current_salary": 32000,
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
        "current_salary": 68000,
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

def load_template(template_name):
    template = INDUSTRY_TEMPLATES[template_name]
    for key, value in template.items():
        st.session_state[key] = value
    st.session_state['industry'] = template_name

def reset_to_defaults():
    defaults = {
        # Basic assumptions
        "hire_salary": 60000,
        "current_salary": 55000,  # Added current salary
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

def calculate_costs():
    \"\"\"Calculate all costs with PROPER INCREMENTAL COMPARISON\"\"\"
    # Get values from session state
    hire_salary = st.session_state.get('hire_salary', 60000)
    current_salary = st.session_state.get('current_salary', 55000)
    vacancy_months = st.session_state.get('vacancy_months', 3)
    social_percent = st.session_state.get('social_percent', 22)
    benefits_percent = st.session_state.get('benefits_percent', 8)
    prod_loss_percent = st.session_state.get('prod_loss_percent', 40)
    
    # Recruiting costs (one-time costs for hiring)
    recruiting_costs = {
        "Stellenanzeigen": st.session_state.get('anzeigen_qty', 2) * st.session_state.get('anzeigen_price', 800),
        "Personalberater": hire_salary * (st.session_state.get('berater_percent', 25) / 100),
        "Interviews": st.session_state.get('interview_hours', 12) * st.session_state.get('interview_rate', 70),
        "Assessment Center": st.session_state.get('assessment_qty', 1) * st.session_state.get('assessment_price', 1500),
        "Reisekosten": st.session_state.get('reise_qty', 2) * st.session_state.get('reise_price', 300),
        "Background Checks": st.session_state.get('background_qty', 1) * st.session_state.get('background_price', 200),
    }
    recruiting_sum = sum(recruiting_costs.values())
    
    # Vacancy costs (costs during vacancy period)
    vacancy_costs = {
        "Entgangene Produktivität": vacancy_months * st.session_state.get('produkt_price', 6000),
        "Überstunden Team": st.session_state.get('ueberstunden_qty', 30) * st.session_state.get('ueberstunden_price', 50),
        "Externe Unterstützung": st.session_state.get('extern_qty', 20) * st.session_state.get('extern_price', 400),
        "Gehaltsersparnis": -(vacancy_months * st.session_state.get('gehalt_price', 6000)),
    }
    vacancy_sum = sum(vacancy_costs.values())
    
    # Onboarding costs (one-time costs for new hire)
    onboarding_costs = {
        "HR-Aufwand": st.session_state.get('hr_hours', 10) * st.session_state.get('hr_rate', 50),
        "Einarbeitung Kollegen": st.session_state.get('kollegen_hours', 15) * st.session_state.get('kollegen_rate', 60),
        "Schulungen/Training": st.session_state.get('training_cost', 1000),
        "IT-Setup & Equipment": st.session_state.get('it_cost', 1200),
        "Mentor/Buddy-System": st.session_state.get('mentor_hours', 6) * st.session_state.get('mentor_rate', 60),
    }
    onboarding_sum = sum(onboarding_costs.values())
    
    # Productivity loss during ramp-up
    prod_loss_monthly = (hire_salary / 12) * (1 + social_percent / 100) * (prod_loss_percent / 100)
    productivity_sum = prod_loss_monthly * vacancy_months
    
    # Other costs (one-time or transition costs)
    other_costs = {
        "Fehlerrate": st.session_state.get('fehler_cost', 1400),
        "Know-how-Verlust": st.session_state.get('knowhow_cost', 2000),
        "Kundenbindung/Umsatz": st.session_state.get('kunden_cost', 2500),
        "Team-Moral": st.session_state.get('team_cost', 2000),
    }
    other_sum = sum(other_costs.values())
    
    # FIXED: Calculate salary difference (incremental cost)
    salary_difference = hire_salary - current_salary
    social_difference = salary_difference * (social_percent / 100)
    benefits_difference = salary_difference * (benefits_percent / 100)
    annual_salary_difference = salary_difference + social_difference + benefits_difference
    
    # FIXED: Total INCREMENTAL cost for new hire
    # This includes all one-time costs PLUS the annual salary difference
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
    
    # For display: also calculate full employment costs
    social_hire = hire_salary * (social_percent / 100)
    benefits_hire = hire_salary * (benefits_percent / 100)
    full_employment_cost = hire_salary + social_hire + benefits_hire
    
    current_social = current_salary * (social_percent / 100)
    current_benefits = current_salary * (benefits_percent / 100)
    current_employment_cost = current_salary + current_social + current_benefits
    
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
        "current_employment_cost": current_employment_cost,
        "hire_vs_current_salary": salary_difference,
        "comparison_type": "incremental"  # Flag to show this is incremental comparison
    }

def main():
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🤖 AI-Powered HR Kostenvergleich")
    st.markdown('''
    **Intelligenter Kostenvergleich** zwischen Neubesetzung und Gehaltserhöhung mit **KI-gestützten Insights**. 
    
    ⚡ **INKREMENTELLER VERGLEICH**: Zeigt nur die **Zusatzkosten** beider Optionen - jetzt korrekt!
    ''')
    
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
        salary_diff = st.session_state.get('hire_salary', 60000) - st.session_state.get('current_salary', 55000)
        if salary_diff > 0:
            st.success(f"💰 Neuer MA kostet {salary_diff:,.0f} € mehr/Jahr")
        elif salary_diff < 0:
            st.info(f"💰 Neuer MA kostet {abs(salary_diff):,.0f} € weniger/Jahr")
        else:
            st.info("💰 Gleiches Gehaltsniveau")
    
    # Main content area
    results = calculate_costs()
    
    # Top-level metrics with improved labeling
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💼 Neubesetzung (Zusatzkosten)", f"{results['total_hire']:,.0f} €", 
                 delta=f"{results['total_hire'] - results['total_salary_increase']:+,.0f} €")
    with col2:
        st.metric("💰 Gehaltserhöhung", f"{results['total_salary_increase']:,.0f} €")
    with col3:
        difference = abs(results['total_hire'] - results['total_salary_increase'])
        percentage = (difference / min(results['total_hire'], results['total_salary_increase'])) * 100
        st.metric("💡 Ersparnis", f"{difference:,.0f} €", f"{percentage:.1f}%")
    
    # Enhanced recommendation with salary context
    salary_diff = results.get('hire_vs_current_salary', 0)
    if results['total_hire'] > results['total_salary_increase']:
        st.success("🎯 **Empfehlung: Gehaltserhöhung ist günstiger**")
        st.info(f"💰 Sie sparen {difference:,.0f} € ({percentage:.1f}%) mit einer Gehaltserhöhung")
        if salary_diff > 0:
            st.warning(f"⚠️ Hinweis: Neuer Mitarbeiter würde {salary_diff:,.0f} € mehr kosten")
    else:
        st.info("🎯 **Empfehlung: Neubesetzung ist günstiger**")
        st.success(f"💰 Sie sparen {difference:,.0f} € ({percentage:.1f}%) mit einer Neubesetzung")
        if salary_diff < 0:
            st.info(f"💡 Bonus: Neuer Mitarbeiter kostet {abs(salary_diff):,.0f} € weniger")
    
    # Detailed input sections
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Detailed cost inputs
        st.header("🏢 Neubesetzung - Detailkosten")
        
        # Recruiting costs
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
        
        # Salary increase section
        st.header("💰 Alternative: Gehaltserhöhung")
        with st.expander("💶 Gehaltserhöhung Details", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.number_input("Erhöhung (%)", min_value=0, max_value=50, key="increase_percent")
            with col_b:
                st.number_input("Sozialabgaben auf Erhöhung (%)", min_value=0, key="social_increase_percent")
                st.number_input("Benefits auf Erhöhung (%)", min_value=0, key="benefits_increase_percent")
    
    with col2:
        # Cost breakdown chart - UPDATED for incremental costs
        st.subheader("📊 Zusatzkosten-Verteilung")
        
        categories = ["Recruiting", "Vakanz", "Onboarding", "Produktivität", "Weitere", "Gehaltsdifferenz"]
        values = [
            results['recruiting']['sum'],
            results['vacancy']['sum'],
            results['onboarding']['sum'],
            results['productivity']['sum'],
            results['other']['sum'],
            results['salary_difference']['sum']
        ]
        
        # Filter out zero or negative values for better visualization
        filtered_data = [(cat, val) for cat, val in zip(categories, values) if val > 0]
        if filtered_data:
            filtered_categories, filtered_values = zip(*filtered_data)
            
            fig = px.pie(
                values=filtered_values,
                names=filtered_categories,
                title="Neubesetzung - Zusatzkosten-Verteilung",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Comparison chart
        st.subheader("⚖️ Direktvergleich (Inkrementell)")
        comparison_data = {
            "Option": ["Neubesetzung\\n(Zusatzkosten)", "Gehaltserhöhung"],
            "Kosten": [results['total_hire'], results['total_salary_increase']]
        }
        
        fig2 = px.bar(
            comparison_data,
            x="Option",
            y="Kosten",
            title="Inkrementeller Kostenvergleich",
            color="Kosten",
            color_continuous_scale="RdYlGn_r"
        )
        fig2.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Salary comparison info box
        st.info(f'''
        **💰 Gehaltsvergleich:**
        - Aktuell: {st.session_state.get('current_salary', 55000):,.0f} €
        - Neu: {st.session_state.get('hire_salary', 60000):,.0f} €
        - Differenz: {results.get('hire_vs_current_salary', 0):+,.0f} €
        ''')
    
    # Detailed breakdown
    st.header("📋 Detaillierte Kostenaufschlüsselung")
    
    tab1, tab2 = st.tabs(["💼 Neubesetzung Details", "💰 Gehaltserhöhung Details"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🧲 Recruiting")
            for item, cost in results['recruiting']['costs'].items():
                st.write(f"{item}: {cost:,.0f} €")
            st.write(f"**Summe: {results['recruiting']['sum']:,.0f} €**")
            
            st.subheader("🎓 Onboarding")
            for item, cost in results['onboarding']['costs'].items():
                st.write(f"{item}: {cost:,.0f} €")
            st.write(f"**Summe: {results['onboarding']['sum']:,.0f} €**")
        
        with col2:
            st.subheader("⏳ Vakanz")
            for item, cost in results['vacancy']['costs'].items():
                st.write(f"{item}: {cost:,.0f} €")
            st.write(f"**Summe: {results['vacancy']['sum']:,.0f} €**")
            
            st.subheader("⚠️ Weitere Kosten")
            for item, cost in results['other']['costs'].items():
                st.write(f"{item}: {cost:,.0f} €")
            st.write(f"**Summe: {results['other']['sum']:,.0f} €**")
        
        with col3:
            st.subheader("📉 Produktivitätsverlust")
            st.write(f"Monatlicher Verlust: {results['productivity']['sum']/st.session_state.vacancy_months:,.0f} €")
            st.write(f"**Gesamtverlust: {results['productivity']['sum']:,.0f} €**")
            
            st.subheader("💶 Gehaltsdifferenz")
            salary_diff = results.get('hire_vs_current_salary', 0)
            st.write(f"Neues Gehalt: {st.session_state.hire_salary:,.0f} €")
            st.write(f"Aktuelles Gehalt: {st.session_state.current_salary:,.0f} €")
            st.write(f"Differenz: {salary_diff:+,.0f} €")
            st.write(f"**Jährliche Mehrkosten: {results['salary_difference']['sum']:,.0f} €**")
    
    with tab2:
        breakdown = results['salary_breakdown']
        st.subheader("💰 Gehaltserhöhung Aufschlüsselung")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Grunderhöhung", f"{breakdown['increase']:,.0f} €")
            st.metric("Sozialabgaben", f"{breakdown['social']:,.0f} €")
            st.metric("Benefits", f"{breakdown['benefits']:,.0f} €")
        with col2:
            st.metric("**Gesamtkosten**", f"**{results['total_salary_increase']:,.0f} €**")
            
            # Visualization of salary increase breakdown
            fig_salary = px.pie(
                values=[breakdown['increase'], breakdown['social'], breakdown['benefits']],
                names=['Grunderhöhung', 'Sozialabgaben', 'Benefits'],
                title="Gehaltserhöhung Aufschlüsselung"
            )
            st.plotly_chart(fig_salary, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown('''
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🤖 Powered by <strong>Künstliche Intelligenz</strong>  💼 HR Intelligence Platform</p>
        <p><small>⚡ **INKREMENTELLER KOSTENVERGLEICH** - Zeigt nur Zusatzkosten beider Optionen</small></p>
        <p><small>✅ **FIXED**: Jetzt korrekte Äpfel-mit-Äpfeln Vergleich!</small></p>
        <p><small>Alle Berechnungen sind Schätzungen. Konsultieren Sie einen HR-Experten für finale Entscheidungen.</small></p>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
""")

print("✅ Fixed incremental cost comparison app created!")
print("📁 File: hr_app_incremental_fixed.py")
print("🔧 Key fixes:")
print("   - Added current_salary input")
print("   - Fixed calculation to compare incremental costs only")
print("   - Salary difference now properly calculated")
print("   - Updated UI labels for clarity")
print("   - Added industry templates with current salary")
