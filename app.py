import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="HR Kostenvergleich",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        "increase_percent": 8,
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
        "increase_percent": 7,
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
        "increase_percent": 6,
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
        "increase_percent": 9,
    }
}

def load_template(template_name):
    """Load industry template into session state"""
    if template_name in INDUSTRY_TEMPLATES:
        template = INDUSTRY_TEMPLATES[template_name]
        for key, value in template.items():
            st.session_state[key] = value
        st.session_state['industry'] = template_name

def reset_to_defaults():
    """Reset all values to defaults"""
    defaults = {
        # Basic assumptions
        "hire_salary": 60000,
        "current_salary": 55000,
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
        "gehalt_price": 5000,
        
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
    """Initialize session state with default values"""
    if 'initialized' not in st.session_state:
        reset_to_defaults()
        st.session_state.initialized = True

def calculate_costs():
    """Calculate all costs with corrected comparison logic"""
    try:
        # Get values from session state with defaults
        hire_salary = st.session_state.get('hire_salary', 60000)
        current_salary = st.session_state.get('current_salary', 55000)
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
            "Gehaltsersparnis": -(vacancy_months * st.session_state.get('gehalt_price', 5000)),
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
        
        # Productivity loss during ramp-up
        prod_loss_monthly = (hire_salary / 12) * (1 + social_percent / 100) * (prod_loss_percent / 100)
        productivity_sum = prod_loss_monthly * 3  # Assume 3 months ramp-up
        
        # Other costs
        other_costs = {
            "Fehlerrate": st.session_state.get('fehler_cost', 1400),
            "Know-how-Verlust": st.session_state.get('knowhow_cost', 2000),
            "Kundenbindung/Umsatzverluste": st.session_state.get('kunden_cost', 2500),
            "Team-Moral": st.session_state.get('team_cost', 2000),
        }
        other_sum = sum(other_costs.values())
        
        # Calculate annual costs
        current_social = current_salary * (social_percent / 100)
        current_benefits = current_salary * (benefits_percent / 100)
        current_total_annual = current_salary + current_social + current_benefits
        
        hire_social = hire_salary * (social_percent / 100)
        hire_benefits = hire_salary * (benefits_percent / 100)
        hire_total_annual = hire_salary + hire_social + hire_benefits
        
        # CORRECTED: Calculate incremental salary difference
        salary_difference = hire_total_annual - current_total_annual
        
        # Total incremental cost of new hire (one-time + annual difference)
        total_hire_incremental = recruiting_sum + vacancy_sum + onboarding_sum + productivity_sum + other_sum + salary_difference
        
        # Salary increase costs (annual)
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
            "salary_difference": {"sum": salary_difference},
            
            # CORRECTED: Now comparing incremental costs properly
            "total_hire": total_hire_incremental,
            "total_salary_increase": total_salary_increase,
            
            # Additional transparency
            "current_annual_cost": current_total_annual,
            "hire_annual_cost": hire_total_annual,
            "one_time_costs": recruiting_sum + vacancy_sum + onboarding_sum + productivity_sum + other_sum,
            
            "salary_breakdown": {
                "increase": increase_amount,
                "social": social_increase,
                "benefits": benefits_increase
            }
        }
    
    except Exception as e:
        st.error(f"Fehler bei der Berechnung: {e}")
        return None

def create_detailed_report(results):
    """Generate a detailed text report"""
    if not results:
        return "Fehler bei der Berechnung."
    
    report = []
    report.append("HR KOSTENVERGLEICH - DETAILBERICHT")
    report.append("=" * 50)
    report.append("")
    report.append(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    report.append(f"Branche: {st.session_state.get('industry', 'General')}")
    report.append("")
    
    # Recommendation
    if results['total_hire'] > results['total_salary_increase']:
        recommendation = f"Gehaltserhöhung ist günstiger um {results['total_hire'] - results['total_salary_increase']:,.0f} €"
    else:
        recommendation = f"Neubesetzung ist günstiger um {results['total_salary_increase'] - results['total_hire']:,.0f} €"
    
    report.append("EMPFEHLUNG")
    report.append("-" * 20)
    report.append(recommendation)
    report.append(f"Zusatzkosten Neubesetzung: {results['total_hire']:,.0f} €")
    report.append(f"Zusatzkosten Gehaltserhöhung: {results['total_salary_increase']:,.0f} €")
    report.append("")
    
    # Parameters
    report.append("PARAMETER")
    report.append("-" * 20)
    report.append(f"Jahresgehalt (aktuell): {st.session_state.get('current_salary', 0):,.0f} €")
    report.append(f"Jahresgehalt (neu): {st.session_state.get('hire_salary', 0):,.0f} €")
    report.append(f"Vakanzdauer: {st.session_state.get('vacancy_months', 0)} Monate")
    report.append(f"Produktivitätsverlust: {st.session_state.get('prod_loss_percent', 0)}%")
    report.append("")
    
    return "\n".join(report)

def main():
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("💼 HR Kostenvergleich")
    st.markdown("""
    **Intelligenter Kostenvergleich** zwischen Neubesetzung und Gehaltserhöhung. 
    **WICHTIG**: Vergleicht die *zusätzlichen* Kosten beider Optionen fair.
    """)
    
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
        st.subheader("Gehälter")
        st.number_input("Aktuelles Jahresgehalt €", 
                       min_value=20000, max_value=200000, step=1000,
                       key="current_salary",
                       help="Gehalt des aktuellen Mitarbeiters")
        
        st.number_input("Neues Jahresgehalt €", 
                       min_value=20000, max_value=200000, step=1000,
                       key="hire_salary",
                       help="Gehalt für neue Besetzung")
        
        st.subheader("Weitere Parameter")
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
                 help="Produktivitätsverlust während Einarbeitung")
    
    # Calculate results
    results = calculate_costs()
    
    if not results:
        st.error("Fehler bei der Berechnung. Bitte überprüfen Sie die Eingaben.")
        return
    
    # Top-level metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💼 Zusatzkosten Neubesetzung", f"{results['total_hire']:,.0f} €", 
                 help="Einmalige + jährliche Mehrkosten vs. aktuellen Mitarbeiter")
    with col2:
        st.metric("💰 Zusatzkosten Gehaltserhöhung", f"{results['total_salary_increase']:,.0f} €",
                 help="Jährliche Mehrkosten durch Gehaltserhöhung")
    with col3:
        difference = abs(results['total_hire'] - results['total_salary_increase'])
        percentage = (difference / min(results['total_hire'], results['total_salary_increase'])) * 100
        st.metric("💡 Differenz", f"{difference:,.0f} €", f"{percentage:.1f}%")
    
    # Recommendation with better explanation
    st.subheader("🎯 Empfehlung")
    if results['total_hire'] > results['total_salary_increase']:
        st.success(f"**Gehaltserhöhung ist günstiger** - Ersparnis: {difference:,.0f} € ({percentage:.1f}%)")
        st.info("💡 Die Gehaltserhöhung verursacht weniger zusätzliche Kosten als eine Neubesetzung.")
    else:
        st.info(f"**Neubesetzung ist günstiger** - Ersparnis: {difference:,.0f} € ({percentage:.1f}%)")
        st.success("💡 Trotz aller Zusatzkosten ist die Neubesetzung wirtschaftlicher.")
    
    # Cost breakdown visualization
    st.subheader("📊 Kostenaufschlüsselung Neubesetzung")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create breakdown chart
        categories = ["Recruiting", "Vakanz", "Onboarding", "Produktivitätsverlust", "Weitere Kosten", "Gehaltsdifferenz"]
        values = [
            results['recruiting']['sum'],
            results['vacancy']['sum'],
            results['onboarding']['sum'],
            results['productivity']['sum'],
            results['other']['sum'],
            max(0, results['salary_difference']['sum'])  # Only show if positive
        ]
        
        # Remove zero values
        non_zero_data = [(cat, val) for cat, val in zip(categories, values) if val > 0]
        if non_zero_data:
            categories, values = zip(*non_zero_data)
            
            fig = px.pie(
                values=values,
                names=categories,
                title="Kostenverteilung Neubesetzung",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Comparison chart
        st.subheader("⚖️ Direktvergleich")
        comparison_data = {
            "Option": ["Neubesetzung\n(Zusatzkosten)", "Gehaltserhöhung\n(Zusatzkosten)"],
            "Kosten": [results['total_hire'], results['total_salary_increase']]
        }
        
        fig2 = px.bar(
            comparison_data,
            x="Option",
            y="Kosten",
            title="Zusatzkosten-Vergleich",
            color="Kosten",
            color_continuous_scale="RdYlGn_r"
        )
        fig2.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed input sections
    st.header("🔧 Detaileinstellungen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Recruiting costs
        with st.expander("🧲 Recruiting-Kosten"):
            st.number_input("Stellenanzeigen (Anzahl)", min_value=0, max_value=10, key="anzeigen_qty")
            st.number_input("Stellenanzeigen (€ pro Anzeige)", min_value=0, max_value=5000, key="anzeigen_price")
            st.number_input("Personalberater (%)", min_value=0, max_value=50, key="berater_percent")
            st.number_input("Interview-Stunden", min_value=0, max_value=100, key="interview_hours")
            st.number_input("Interview-Stundensatz (€)", min_value=0, max_value=200, key="interview_rate")
            st.number_input("Assessment Center (€)", min_value=0, max_value=10000, key="assessment_price")
        
        # Onboarding costs
        with st.expander("🎓 Onboarding-Kosten"):
            st.number_input("HR-Aufwand (Stunden)", min_value=0, max_value=100, key="hr_hours")
            st.number_input("HR-Stundensatz (€)", min_value=0, max_value=200, key="hr_rate")
            st.number_input("Einarbeitung Kollegen (Stunden)", min_value=0, max_value=200, key="kollegen_hours")
            st.number_input("Kollegen-Stundensatz (€)", min_value=0, max_value=200, key="kollegen_rate")
            st.number_input("Schulungen/Training (€)", min_value=0, max_value=20000, key="training_cost")
            st.number_input("IT-Setup & Equipment (€)", min_value=0, max_value=10000, key="it_cost")
    
    with col2:
        # Vacancy costs
        with st.expander("⏳ Vakanz-Kosten"):
            st.number_input("Entgangene Produktivität (€/Monat)", min_value=0, max_value=50000, key="produkt_price")
            st.number_input("Überstunden (Anzahl)", min_value=0, max_value=200, key="ueberstunden_qty")
            st.number_input("Überstunden (€/Std)", min_value=0, max_value=200, key="ueberstunden_price")
            st.number_input("Externe Unterstützung (Tage)", min_value=0, max_value=100, key="extern_qty")
            st.number_input("Externe Unterstützung (€/Tag)", min_value=0, max_value=2000, key="extern_price")
        
        # Other costs
        with st.expander("⚠️ Weitere Kosten"):
            st.number_input("Fehlerrate (€)", min_value=0, max_value=10000, key="fehler_cost")
            st.number_input("Know-how-Verlust (€)", min_value=0, max_value=10000, key="knowhow_cost")
            st.number_input("Kundenbindung/Umsatzverluste (€)", min_value=0, max_value=20000, key="kunden_cost")
            st.number_input("Team-Moral (€)", min_value=0, max_value=10000, key="team_cost")
    
    # Salary increase section
    st.header("💰 Gehaltserhöhung Details")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Erhöhung (%)", min_value=0, max_value=50, key="increase_percent")
        st.number_input("Sozialabgaben auf Erhöhung (%)", min_value=0, max_value=30, key="social_increase_percent")
    with col2:
        st.number_input("Benefits auf Erhöhung (%)", min_value=0, max_value=30, key="benefits_increase_percent")
    
    # Detailed breakdown
    st.header("📋 Detaillierte Aufschlüsselung")
    
    tab1, tab2, tab3 = st.tabs(["💼 Neubesetzung Details", "💰 Gehaltserhöhung Details", "📄 Export"])
    
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
            st.write(f"Gesamtverlust: {results['productivity']['sum']:,.0f} €")
            
            st.subheader("💶 Gehaltsdifferenz")
            st.write(f"Aktuell: {results['current_annual_cost']:,.0f} €/Jahr")
            st.write(f"Neu: {results['hire_annual_cost']:,.0f} €/Jahr")
            st.write(f"**Differenz: {results['salary_difference']['sum']:,.0f} €/Jahr**")
            
            st.subheader("📊 Zusammenfassung")
            st.write(f"Einmalkosten: {results['one_time_costs']:,.0f} €")
            st.write(f"Jährliche Mehrkosten: {results['salary_difference']['sum']:,.0f} €")
            st.write(f"**Gesamte Zusatzkosten: {results['total_hire']:,.0f} €**")
    
    with tab2:
        breakdown = results['salary_breakdown']
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Grunderhöhung", f"{breakdown['increase']:,.0f} €")
            st.metric("Sozialabgaben", f"{breakdown['social']:,.0f} €")
            st.metric("Benefits", f"{breakdown['benefits']:,.0f} €")
            st.metric("**Gesamte Zusatzkosten**", f"**{results['total_salary_increase']:,.0f} €**")
        with col2:
            # Visualization of salary increase breakdown
            fig_salary = px.pie(
                values=[breakdown['increase'], breakdown['social'], breakdown['benefits']],
                names=['Grunderhöhung', 'Sozialabgaben', 'Benefits'],
                title="Gehaltserhöhung Aufschlüsselung"
            )
            st.plotly_chart(fig_salary, use_container_width=True)
    
    with tab3:
        st.subheader("📄 Export")
        
        # Create export data
        export_data = create_detailed_report(results)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Detailbericht herunterladen",
                data=export_data,
                file_name=f"hr_kostenvergleich_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
        
        with col2:
            # Create CSV data
            csv_data = {
                'Kostenart': [
                    'Neubesetzung - Recruiting',
                    'Neubesetzung - Vakanz', 
                    'Neubesetzung - Onboarding',
                    'Neubesetzung - Produktivitätsverlust',
                    'Neubesetzung - Weitere Kosten',
                    'Neubesetzung - Gehaltsdifferenz',
                    'Neubesetzung - GESAMT',
                    'Gehaltserhöhung - GESAMT'
                ],
                'Betrag': [
                    results['recruiting']['sum'],
                    results['vacancy']['sum'],
                    results['onboarding']['sum'],
                    results['productivity']['sum'],
                    results['other']['sum'],
                    results['salary_difference']['sum'],
                    results['total_hire'],
                    results['total_salary_increase']
                ]
            }
            
            df = pd.DataFrame(csv_data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="📥 CSV herunterladen",
                data=csv,
                file_name=f"hr_kostenvergleich_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    # Important explanation
    st.markdown("---")
    st.info("""
    **📋 Wichtiger Hinweis zur Berechnung:**
    
    Diese Analyse vergleicht die **zusätzlichen Kosten** beider Optionen fair:
    - **Neubesetzung**: Alle Recruiting-, Vakanz- und Onboarding-Kosten + jährliche Gehaltsdifferenz
    - **Gehaltserhöhung**: Nur die zusätzlichen jährlichen Kosten durch die Erhöhung
    
    Das aktuelle Grundgehalt wird nicht doppelt gezählt, da es in beiden Szenarien anfällt.
    """)

if __name__ == "__main__":
    main()
