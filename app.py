def calculate_costs():
    """Calculate all costs and return results with corrected comparison logic"""
    # Get values from session state
    hire_salary = st.session_state.get('hire_salary', 60000)
    current_salary = st.session_state.get('current_salary', 60000)
    vacancy_months = st.session_state.get('vacancy_months', 3)
    social_percent = st.session_state.get('social_percent', 22)
    benefits_percent = st.session_state.get('benefits_percent', 8)
    prod_loss_percent = st.session_state.get('prod_loss_percent', 40)
    
    # Recruiting costs (same as before)
    recruiting_costs = {
        "Stellenanzeigen": st.session_state.get('anzeigen_qty', 2) * st.session_state.get('anzeigen_price', 800),
        "Personalberater": hire_salary * (st.session_state.get('berater_percent', 25) / 100),
        "Interviews": st.session_state.get('interview_hours', 12) * st.session_state.get('interview_rate', 70),
        "Assessment Center": st.session_state.get('assessment_qty', 1) * st.session_state.get('assessment_price', 1500),
        "Reisekosten": st.session_state.get('reise_qty', 2) * st.session_state.get('reise_price', 300),
        "Background Checks": st.session_state.get('background_qty', 1) * st.session_state.get('background_price', 200),
    }
    recruiting_sum = sum(recruiting_costs.values())
    
    # Vacancy costs (same as before)
    vacancy_costs = {
        "Entgangene Produktivität": vacancy_months * st.session_state.get('produkt_price', 6000),
        "Überstunden Team": st.session_state.get('ueberstunden_qty', 30) * st.session_state.get('ueberstunden_price', 50),
        "Externe Unterstützung": st.session_state.get('extern_qty', 20) * st.session_state.get('extern_price', 400),
        "Gehaltsersparnis": -(vacancy_months * st.session_state.get('gehalt_price', 6000)),
    }
    vacancy_sum = sum(vacancy_costs.values())
    
    # Onboarding costs (same as before)
    onboarding_costs = {
        "HR-Aufwand": st.session_state.get('hr_hours', 10) * st.session_state.get('hr_rate', 50),
        "Einarbeitung Kollegen": st.session_state.get('kollegen_hours', 15) * st.session_state.get('kollegen_rate', 60),
        "Schulungen/Training": st.session_state.get('training_cost', 1000),
        "IT-Setup & Equipment": st.session_state.get('it_cost', 1200),
        "Mentor/Buddy-System": st.session_state.get('mentor_hours', 6) * st.session_state.get('mentor_rate', 60),
    }
    onboarding_sum = sum(onboarding_costs.values())
    
    # Productivity loss (same as before)
    prod_loss_monthly = (hire_salary / 12) * (1 + social_percent / 100) * (prod_loss_percent / 100)
    productivity_sum = prod_loss_monthly * vacancy_months
    
    # Other costs (same as before)
    other_costs = {
        "Fehlerrate": st.session_state.get('fehler_cost', 1400),
        "Know-how-Verlust": st.session_state.get('knowhow_cost', 2000),
        "Kundenbindung/Umsatz": st.session_state.get('kunden_cost', 2500),
        "Team-Moral": st.session_state.get('team_cost', 2000),
    }
    other_sum = sum(other_costs.values())
    
    # Calculate current employee annual cost
    current_social = current_salary * (social_percent / 100)
    current_benefits = current_salary * (benefits_percent / 100)
    current_total_annual = current_salary + current_social + current_benefits
    
    # Calculate new hire annual cost
    hire_social = hire_salary * (social_percent / 100)
    hire_benefits = hire_salary * (benefits_percent / 100)
    hire_total_annual = hire_salary + hire_social + hire_benefits
    
    # FIXED: Calculate incremental salary difference
    salary_difference = hire_total_annual - current_total_annual
    
    # Total incremental cost of new hire (vs keeping current employee)
    total_hire_incremental = recruiting_sum + vacancy_sum + onboarding_sum + productivity_sum + other_sum + salary_difference
    
    # Salary increase costs
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
        "salary_difference": {"sum": salary_difference},  # New: incremental salary cost
        
        # CORRECTED: Compare incremental costs
        "total_hire": total_hire_incremental,  # Total incremental cost of hiring
        "total_salary_increase": total_salary_increase,  # Cost of salary increase
        
        # Additional info for transparency
        "current_annual_cost": current_total_annual,
        "hire_annual_cost": hire_total_annual,
        
        "salary_breakdown": {
            "increase": increase_amount,
            "social": social_increase,
            "benefits": benefits_increase
        }
    }
