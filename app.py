import streamlit as st
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

def calculate_costs():
    """Calculate all costs and return results (incremental comparison)"""
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
        "fixed": {"sum": annual_salary_difference},  # Only the incremental part!
        "total_hire": total_hire_incremental,
        "total_salary_increase": total_salary_increase,
        "salary_breakdown": {
            "increase": increase_amount,
            "social": social_increase,
            "benefits": benefits_increase
        }
    }

# --- All your other functions (AI, export, etc.) remain unchanged ---

# ... (Paste all your other functions here, unchanged) ...

def main():
    # Initialize session state
    initialize_session_state()
    # ... (rest of your main() code, unchanged) ...

if __name__ == "__main__":
    main()
