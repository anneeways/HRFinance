import streamlit as st
import pandas as pd
import plotly.express as px
import groq
from datetime import datetime
import io

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI-Powered HR Cost Comparison",
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
        "consultant_percent": 30,
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
        "consultant_percent": 20,
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
        "consultant_percent": 15,
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
        "consultant_percent": 25,
        "interview_hours": 12,
        "interview_rate": 90,
        "training_cost": 2500,
        "current_salary": 65000
    }
}

# --- AI AGENT TEMPLATES ---
AI_AGENT_TEMPLATES = {
    "HR Chatbot": {
        "setup_cost": 15000,
        "monthly_cost": 2000,
        "time_saved_hours": 20,
        "hourly_rate": 50,
        "accuracy_improvement": 15,
        "candidate_experience_score": 8.5,
        "implementation_months": 2
    },
    "Resume Screening AI": {
        "setup_cost": 25000,
        "monthly_cost": 3500,
        "time_saved_hours": 40,
        "hourly_rate": 60,
        "accuracy_improvement": 25,
        "candidate_experience_score": 7.0,
        "implementation_months": 3
    },
    "Interview Scheduling Bot": {
        "setup_cost": 8000,
        "monthly_cost": 1200,
        "time_saved_hours": 15,
        "hourly_rate": 45,
        "accuracy_improvement": 30,
        "candidate_experience_score": 9.0,
        "implementation_months": 1
    },
    "Onboarding Assistant": {
        "setup_cost": 20000,
        "monthly_cost": 2500,
        "time_saved_hours": 25,
        "hourly_rate": 55,
        "accuracy_improvement": 20,
        "candidate_experience_score": 8.0,
        "implementation_months": 2
    },
    "Performance Analytics AI": {
        "setup_cost": 35000,
        "monthly_cost": 4000,
        "time_saved_hours": 30,
        "hourly_rate": 70,
        "accuracy_improvement": 35,
        "candidate_experience_score": 7.5,
        "implementation_months": 4
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
        "job_ads_qty": 2,
        "job_ads_price": 800,
        "consultant_percent": 25,
        "interview_hours": 12,
        "interview_rate": 70,
        "assessment_qty": 1,
        "assessment_price": 1500,
        "travel_qty": 2,
        "travel_price": 300,
        "background_qty": 1,
        "background_price": 200,
        "productivity_price": 6000,
        "overtime_qty": 30,
        "overtime_price": 50,
        "external_qty": 20,
        "external_price": 400,
        "salary_price": 6000,
        "hr_hours": 10,
        "hr_rate": 50,
        "colleague_hours": 15,
        "colleague_rate": 60,
        "training_cost": 1000,
        "it_cost": 1200,
        "mentor_hours": 6,
        "mentor_rate": 60,
        "error_cost": 1400,
        "knowhow_cost": 2000,
        "customer_cost": 2500,
        "team_cost": 2000,
        "current_salary": 60000,
        "increase_percent": 8,
        "social_increase_percent": 22,
        "benefits_increase_percent": 8,
        # AI Agent defaults
        "ai_agent_type": "HR Chatbot",
        "ai_setup_cost": 15000,
        "ai_monthly_cost": 2000,
        "ai_time_saved": 20,
        "ai_hourly_rate": 50,
        "ai_accuracy_improvement": 15,
        "ai_candidate_experience": 8.5,
        "ai_implementation_months": 2,
        "ai_roi_years": 3,
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

def load_ai_template(template_name):
    template = AI_AGENT_TEMPLATES[template_name]
    mapping = {
        "setup_cost": "ai_setup_cost",
        "monthly_cost": "ai_monthly_cost",
        "time_saved_hours": "ai_time_saved",
        "hourly_rate": "ai_hourly_rate",
        "accuracy_improvement": "ai_accuracy_improvement",
        "candidate_experience_score": "ai_candidate_experience",
        "implementation_months": "ai_implementation_months"
    }
    for template_key, session_key in mapping.items():
        st.session_state[session_key] = template[template_key]
    st.session_state['ai_agent_type'] = template_name

# --- AI INIT ---
@st.cache_resource
def init_groq():
    try:
        api_key = st.secrets.get("GROQ_API_KEY") or st.session_state.get("groq_api_key")
        if not api_key:
            return None
        return groq.Groq(api_key=api_key)
    except Exception as e:
        st.error(f"AI Initialization Error: {e}")
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
        "Job Advertisements": st.session_state.get('job_ads_qty', 2) * st.session_state.get('job_ads_price', 800),
        "Recruitment Consultant": hire_salary * (st.session_state.get('consultant_percent', 25) / 100),
        "Interviews": st.session_state.get('interview_hours', 12) * st.session_state.get('interview_rate', 70),
        "Assessment Center": st.session_state.get('assessment_qty', 1) * st.session_state.get('assessment_price', 1500),
        "Travel Expenses": st.session_state.get('travel_qty', 2) * st.session_state.get('travel_price', 300),
        "Background Checks": st.session_state.get('background_qty', 1) * st.session_state.get('background_price', 200),
    }
    recruiting_sum = sum(recruiting_costs.values())

    # Vacancy costs
    vacancy_costs = {
        "Lost Productivity": vacancy_months * st.session_state.get('productivity_price', 6000),
        "Team Overtime": st.session_state.get('overtime_qty', 30) * st.session_state.get('overtime_price', 50),
        "External Support": st.session_state.get('external_qty', 20) * st.session_state.get('external_price', 400),
        "Salary Savings": -(vacancy_months * st.session_state.get('salary_price', 6000)),
    }
    vacancy_sum = sum(vacancy_costs.values())

    # Onboarding costs
    onboarding_costs = {
        "HR Effort": st.session_state.get('hr_hours', 10) * st.session_state.get('hr_rate', 50),
        "Colleague Training": st.session_state.get('colleague_hours', 15) * st.session_state.get('colleague_rate', 60),
        "Training/Courses": st.session_state.get('training_cost', 1000),
        "IT Setup & Equipment": st.session_state.get('it_cost', 1200),
        "Mentor/Buddy System": st.session_state.get('mentor_hours', 6) * st.session_state.get('mentor_rate', 60),
    }
    onboarding_sum = sum(onboarding_costs.values())

    # Productivity loss
    prod_loss_monthly = (hire_salary / 12) * (1 + social_percent / 100) * (prod_loss_percent / 100)
    productivity_sum = prod_loss_monthly * vacancy_months

    # Other costs
    other_costs = {
        "Error Rate": st.session_state.get('error_cost', 1400),
        "Knowledge Loss": st.session_state.get('knowhow_cost', 2000),
        "Customer Retention/Revenue": st.session_state.get('customer_cost', 2500),
        "Team Morale": st.session_state.get('team_cost', 2000),
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
        "fixed": {"sum": annual_salary_difference},
        "total_hire": total_hire_incremental,
        "total_salary_increase": total_salary_increase,
        "salary_breakdown": {
            "increase": increase_amount,
            "social": social_increase,
            "benefits": benefits_increase
        }
    }

# --- AI AGENT COST CALCULATION ---
def calculate_ai_costs():
    setup_cost = st.session_state.get('ai_setup_cost', 15000)
    monthly_cost = st.session_state.get('ai_monthly_cost', 2000)
    time_saved = st.session_state.get('ai_time_saved', 20)
    hourly_rate = st.session_state.get('ai_hourly_rate', 50)
    implementation_months = st.session_state.get('ai_implementation_months', 2)
    roi_years = st.session_state.get('ai_roi_years', 3)
    
    # Monthly savings from time saved
    monthly_savings = time_saved * hourly_rate * 4  # 4 weeks per month
    
    # Total costs over ROI period
    total_setup = setup_cost
    total_monthly = monthly_cost * 12 * roi_years
    total_cost = total_setup + total_monthly
    
    # Total savings over ROI period
    total_savings = monthly_savings * 12 * roi_years
    
    # Net benefit
    net_benefit = total_savings - total_cost
    
    # ROI calculation
    roi_percentage = (net_benefit / total_cost) * 100 if total_cost > 0 else 0
    
    # Payback period in months
    if monthly_savings > monthly_cost:
        payback_months = setup_cost / (monthly_savings - monthly_cost)
    else:
        payback_months = float('inf')
    
    return {
        "setup_cost": setup_cost,
        "monthly_cost": monthly_cost,
        "monthly_savings": monthly_savings,
        "total_cost": total_cost,
        "total_savings": total_savings,
        "net_benefit": net_benefit,
        "roi_percentage": roi_percentage,
        "payback_months": payback_months,
        "implementation_months": implementation_months
    }

# --- AI INSIGHTS ---
def get_ai_insights(groq_client, calculation_data, context_data):
    if not groq_client:
        return None
    try:
        prompt = f"""
        As an HR expert, please analyze this cost comparison data and provide strategic recommendations:

        COST DATA:
        - New Hire Total Cost: ${calculation_data['total_hire']:,.0f}
        - Salary Increase Total Cost: ${calculation_data['total_salary_increase']:,.0f}
        - Annual Salary: ${context_data['hire_salary']:,.0f}
        - Industry: {context_data.get('industry', 'Unknown')}
        - Vacancy Duration: {context_data['vacancy_months']} months
        - Productivity Loss: {context_data['prod_loss_percent']}%

        COST BREAKDOWN:
        - Recruiting: ${calculation_data['recruiting']['sum']:,.0f}
        - Vacancy: ${calculation_data['vacancy']['sum']:,.0f}
        - Onboarding: ${calculation_data['onboarding']['sum']:,.0f}
        - Productivity Loss: ${calculation_data['productivity']['sum']:,.0f}
        - Other Costs: ${calculation_data['other']['sum']:,.0f}

        Please analyze and provide:
        1. Strategic recommendation (New hire vs Salary increase)
        2. Identify top 3 cost drivers
        3. Concrete optimization suggestions
        4. Risk assessment for both options
        5. Long-term perspective (3-5 years)

        Respond in English, precisely and business-oriented.
        """
        chat_completion = groq_client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": "You are an experienced HR strategy consultant with 15+ years of experience in personnel cost optimization."
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
        st.error(f"AI Analysis Error: {e}")
        return None

def get_ai_scenarios(groq_client, calculation_data):
    if not groq_client:
        return None
    try:
        prompt = f"""
        Create 3 realistic What-If scenarios for this HR cost comparison:

        BASE DATA:
        - New Hire: ${calculation_data['total_hire']:,.0f}
        - Salary Increase: ${calculation_data['total_salary_increase']:,.0f}

        Create scenarios for:
        1. Best-Case (optimistic assumptions)
        2. Worst-Case (pessimistic assumptions)  
        3. Economic Downturn (economic crisis)

        For each scenario provide:
        - Brief description of assumptions
        - Estimated cost change in % 
        - Recommendation for this scenario

        Format as structured text, not JSON.
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
        st.error(f"Scenario Generation Error: {e}")
        return None

def get_ai_implementation_insights(groq_client, ai_calculation_data, context_data):
    if not groq_client:
        return None
    try:
        prompt = f"""
        As an AI implementation expert, analyze this AI agent cost-benefit data:

        AI IMPLEMENTATION DATA:
        - Agent Type: {context_data.get('ai_agent_type', 'Unknown')}
        - Setup Cost: ${ai_calculation_data['setup_cost']:,.0f}
        - Monthly Cost: ${ai_calculation_data['monthly_cost']:,.0f}
        - Monthly Savings: ${ai_calculation_data['monthly_savings']:,.0f}
        - Net Benefit (3 years): ${ai_calculation_data['net_benefit']:,.0f}
        - ROI: {ai_calculation_data['roi_percentage']:.1f}%
        - Payback Period: {ai_calculation_data['payback_months']:.1f} months

        Please provide:
        1. Implementation recommendation (Go/No-Go decision)
        2. Key success factors for this AI agent type
        3. Potential risks and mitigation strategies
        4. Change management considerations
        5. Scalability opportunities

        Respond with actionable business insights.
        """
        chat_completion = groq_client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": "You are an AI implementation specialist with expertise in HR technology adoption and change management."
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
        st.error(f"AI Implementation Analysis Error: {e}")
        return None

# --- MAIN APP ---
def main():
    initialize_session_state()
    st.title("🤖 AI-Powered HR Cost Comparison")
    st.markdown("""
    **Intelligent Cost Comparison** between new hire and salary increase with **AI-powered insights** + **AI Agent Implementation Analysis**.
    """)

    # AI API Key input (if not in secrets)
    groq_client = init_groq()
    if not groq_client:
        with st.expander("🔑 AI Setup", expanded=True):
            st.info("AI features require an API Key.")
            api_key = st.text_input("AI API Key", type="password", help="API Key for AI features")
            if api_key:
                st.session_state.groq_api_key = api_key
                groq_client = init_groq()
                if groq_client:
                    st.success("✅ AI successfully connected!")
                    st.rerun()

    # Main navigation tabs
    tab1, tab2, tab3 = st.tabs(["👥 Hire vs Raise", "🤖 AI Agent Implementation", "📊 Combined Analysis"])
    
    with tab1:
        # Sidebar for main assumptions
        with st.sidebar:
            st.header("⚙️ Basic Assumptions")
            col1, col2 = st.columns(2)
            with col1:
                template = st.selectbox("🏭 Industry", [""] + list(INDUSTRY_TEMPLATES.keys()))
                if template and st.button("Load Template"):
                    load_template(template)
                    st.rerun()
            with col2:
                if st.button("🔄 Reset"):
                    reset_to_defaults()
                    st.rerun()
            st.divider()
            st.subheader("Core Parameters")
            st.number_input("Annual Salary (New Hire) $", min_value=20000, max_value=200000, step=1000, key="hire_salary")
            st.number_input("Current Annual Salary ($)", min_value=20000, max_value=200000, step=1000, key="current_salary")
            st.number_input("Vacancy Duration (Months)", min_value=1, max_value=24, step=1, key="vacancy_months")
            st.number_input("Social Security (%)", min_value=15, max_value=30, step=1, key="social_percent")
            st.number_input("Benefits (%)", min_value=5, max_value=25, step=1, key="benefits_percent")
            st.slider("Productivity Loss (%)", min_value=0, max_value=100, step=5, key="prod_loss_percent")
            st.divider()
            st.subheader("🤖 AI Features")
            use_ai_insights = st.checkbox("Enable AI Insights", value=bool(groq_client))
            use_ai_scenarios = st.checkbox("Generate AI Scenarios", value=bool(groq_client))

        results = calculate_costs()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💼 New Hire (Additional Costs)", f"${results['total_hire']:,.0f}",
                     delta=f"{results['total_hire'] - results['total_salary_increase']:+,.0f}")
        with col2:
            st.metric("💰 Salary Increase (Additional Costs)", f"${results['total_salary_increase']:,.0f}")
        with col3:
            difference = abs(results['total_hire'] - results['total_salary_increase'])
            percentage = (difference / min(results['total_hire'], results['total_salary_increase'])) * 100 if min(results['total_hire'], results['total_salary_increase']) > 0 else 0
            st.metric("💡 Savings", f"${difference:,.0f}", f"{percentage:.1f}%")

        if results['total_hire'] > results['total_salary_increase']:
            st.success("🎯 Recommendation: Salary increase is cheaper")
            st.info(f"💰 You save ${difference:,.0f} ({percentage:.1f}%) with a salary increase")
        else:
            st.info("🎯 Recommendation: New hire is cheaper")
            st.success(f"💰 You save ${difference:,.0f} ({percentage:.1f}%) with a new hire")

        # --- AI INSIGHTS ---
        if groq_client and use_ai_insights:
            with st.container():
                st.header("🧠 AI-Powered Strategic Analysis")
                if st.button("🚀 Generate AI Analysis", type="primary"):
                    with st.spinner("🤖 AI analyzing your data..."):
                        context_data = {
                            'hire_salary': st.session_state.get('hire_salary', 60000),
                            'vacancy_months': st.session_state.get('vacancy_months', 3),
                            'prod_loss_percent': st.session_state.get('prod_loss_percent', 40),
                            'industry': st.session_state.get('industry', 'General')
                        }
                        insights = get_ai_insights(groq_client, results, context_data)
                        if insights:
                            st.success("✅ AI Analysis complete!")
                            st.markdown("### 🎯 Strategic Recommendations")
                            st.markdown(insights)
                            st.session_state.ai_insights = insights
                            st.session_state.insights_timestamp = datetime.now()
                if hasattr(st.session_state, 'ai_insights'):
                    st.markdown("### 📋 Latest AI Analysis")
                    st.info(f"Created: {st.session_state.insights_timestamp.strftime('%m/%d/%Y %H:%M')}")
                    st.markdown(st.session_state.ai_insights)

        # --- AI SCENARIOS ---
        if groq_client and use_ai_scenarios:
            st.header("🔮 AI-Generated What-If Scenarios")
            if st.button("🎲 Generate AI Scenarios"):
                with st.spinner("🤖 AI creating scenarios..."):
                    scenarios = get_ai_scenarios(groq_client, results)
                    if scenarios:
                        st.success("✅ Scenarios generated!")
                        st.markdown("### 📈 What-If Scenarios")
                        st.markdown(scenarios)
                        st.session_state.ai_scenarios = scenarios
                        st.session_state.scenarios_timestamp = datetime.now()
            if hasattr(st.session_state, 'ai_scenarios'):
                st.markdown("### 📋 Latest AI Scenarios")
                st.info(f"Created: {st.session_state.scenarios_timestamp.strftime('%m/%d/%Y %H:%M')}")
                st.markdown(st.session_state.ai_scenarios)

        # --- DETAILED INPUTS ---
        col1, col2 = st.columns([2, 1])
        with col1:
            st.header("🏢 New Hire - Detailed Costs")
            with st.expander("🧲 Recruiting Costs", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.number_input("Job Ads (Quantity)", min_value=0, key="job_ads_qty")
                    st.number_input("Job Ads ($ per ad)", min_value=0, key="job_ads_price")
                    st.number_input("Recruitment Consultant (%)", min_value=0, max_value=50, key="consultant_percent")
                with col_b:
                    st.number_input("Interview Hours", min_value=0, key="interview_hours")
                    st.number_input("Interview Hourly Rate ($)", min_value=0, key="interview_rate")
                    st.number_input("Assessment Center ($)", min_value=0, key="assessment_price")
            with st.expander("⏳ Vacancy Costs", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.number_input("Lost Productivity ($/Month)", min_value=0, key="productivity_price")
                    st.number_input("Overtime Hours", min_value=0, key="overtime_qty")
                    st.number_input("Overtime Rate ($/Hour)", min_value=0, key="overtime_price")
                with col_b:
                    st.number_input("External Support (Days)", min_value=0, key="external_qty")
                    st.number_input("External Support ($/Day)", min_value=0, key="external_price")
                    st.number_input("Monthly Salary ($)", min_value=0, key="salary_price")
            with st.expander("🎓 Onboarding Costs", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.number_input("HR Effort (Hours)", min_value=0, key="hr_hours")
                    st.number_input("HR Hourly Rate ($)", min_value=0, key="hr_rate")
                    st.number_input("Colleague Training (Hours)", min_value=0, key="colleague_hours")
                    st.number_input("Colleague Hourly Rate ($)", min_value=0, key="colleague_rate")
                with col_b:
                    st.number_input("Training/Courses ($)", min_value=0, key="training_cost")
                    st.number_input("IT Setup & Equipment ($)", min_value=0, key="it_cost")
                    st.number_input("Mentor Hours", min_value=0, key="mentor_hours")
                    st.number_input("Mentor Hourly Rate ($)", min_value=0, key="mentor_rate")
            with st.expander("⚠️ Other Costs", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.number_input("Error Rate ($)", min_value=0, key="error_cost")
                    st.number_input("Knowledge Loss ($)", min_value=0, key="knowhow_cost")
                with col_b:
                    st.number_input("Customer Retention/Revenue Loss ($)", min_value=0, key="customer_cost")
                    st.number_input("Team Morale ($)", min_value=0, key="team_cost")
            st.header("💰 Alternative: Salary Increase")
            with st.expander("💶 Salary Increase Details", expanded=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.number_input("Increase (%)", min_value=0, max_value=50, key="increase_percent")
                with col_b:
                    st.number_input("Social Security on Increase (%)", min_value=0, key="social_increase_percent")
                    st.number_input("Benefits on Increase (%)", min_value=0, key="benefits_increase_percent")

        with col2:
            st.subheader("📊 Cost Distribution")
            categories = ["Recruiting", "Vacancy", "Onboarding", "Productivity", "Other", "Salary Difference"]
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
                title="New Hire - Cost Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("⚖️ Direct Comparison")
            comparison_data = {
                "Option": ["New Hire", "Salary Increase"],
                "Cost": [results['total_hire'], results['total_salary_increase']]
            }
            fig2 = px.bar(
                comparison_data,
                x="Option",
                y="Cost",
                title="Cost Comparison",
                color="Cost",
                color_continuous_scale="RdYlGn_r"
            )
            fig2.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.header("🤖 AI Agent Implementation Analysis")
        st.markdown("""
        Analyze the cost-benefit of implementing AI agents in your HR processes. 
        Compare setup costs, ongoing expenses, and potential savings from automation.
        """)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("🎯 AI Agent Configuration")
            
            # AI Agent Template Selection
            ai_template = st.selectbox("🤖 AI Agent Type", [""] + list(AI_AGENT_TEMPLATES.keys()), key="ai_template_select")
            if ai_template and st.button("Load AI Template"):
                load_ai_template(ai_template)
                st.rerun()
            
            st.markdown("---")
            
            # Cost inputs
            st.number_input("Setup Cost ($)", min_value=0, step=1000, key="ai_setup_cost", 
                          help="One-time implementation and setup costs")
            st.number_input("Monthly Operating Cost ($)", min_value=0, step=100, key="ai_monthly_cost",
                          help="Ongoing monthly costs (licensing, maintenance, support)")
            
            st.markdown("**Efficiency Gains**")
            st.number_input("Time Saved per Month (Hours)", min_value=0, step=5, key="ai_time_saved",
                          help="Hours saved per month through automation")
            st.number_input("Hourly Rate of Saved Time ($)", min_value=0, step=5, key="ai_hourly_rate",
                          help="Average hourly cost of staff whose time is saved")
            
            st.markdown("**Implementation Details**")
            st.number_input("Implementation Period (Months)", min_value=1, max_value=12, key="ai_implementation_months",
                          help="Time needed to fully implement the AI agent")
            st.number_input("ROI Analysis Period (Years)", min_value=1, max_value=10, key="ai_roi_years",
                          help="Time period for ROI calculation")
            
            # Quality improvements
            st.slider("Accuracy Improvement (%)", min_value=0, max_value=50, key="ai_accuracy_improvement",
                     help="Expected improvement in process accuracy")
            st.slider("Candidate Experience Score", min_value=1.0, max_value=10.0, step=0.5, key="ai_candidate_experience",
                     help="Expected candidate experience rating (1-10)")

        with col2:
            ai_results = calculate_ai_costs()
            
            st.subheader("📈 ROI Analysis")
            
            # Key metrics
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("💰 Total Investment", f"${ai_results['total_cost']:,.0f}")
                st.metric("📅 Payback Period", 
                         f"{ai_results['payback_months']:.1f} months" if ai_results['payback_months'] != float('inf') else "Never")
            with col_b:
                st.metric("💸 Total Savings", f"${ai_results['total_savings']:,.0f}")
                st.metric("📊 ROI", f"{ai_results['roi_percentage']:.1f}%")
            
            # Net benefit
            if ai_results['net_benefit'] > 0:
                st.success(f"🎯 **Net Benefit: ${ai_results['net_benefit']:,.0f}**")
                st.info("✅ **Recommendation: Proceed with AI implementation**")
            else:
                st.error(f"🎯 **Net Loss: ${abs(ai_results['net_benefit']):,.0f}**")
                st.warning("❌ **Recommendation: Reconsider implementation or adjust parameters**")
            
            # Visual representation
            st.subheader("📊 Cost vs Savings Breakdown")
            
            # Monthly comparison chart
            months = list(range(1, 37))  # 3 years
            cumulative_costs = [ai_results['setup_cost'] + (ai_results['monthly_cost'] * month) for month in months]
            cumulative_savings = [ai_results['monthly_savings'] * month for month in months]
            cumulative_net = [savings - cost for savings, cost in zip(cumulative_savings, cumulative_costs)]
            
            chart_data = pd.DataFrame({
                'Month': months,
                'Cumulative Costs': cumulative_costs,
                'Cumulative Savings': cumulative_savings,
                'Net Benefit': cumulative_net
            })
            
            fig = px.line(chart_data, x='Month', y=['Cumulative Costs', 'Cumulative Savings', 'Net Benefit'],
                         title="AI Implementation: Costs vs Savings Over Time",
                         labels={'value': 'Amount ($)', 'variable': 'Category'})
            fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even")
            st.plotly_chart(fig, use_container_width=True)

        # AI Implementation Insights
        if groq_client:
            st.header("🧠 AI Implementation Strategy")
            if st.button("🚀 Generate AI Implementation Analysis", type="primary"):
                with st.spinner("🤖 Analyzing AI implementation strategy..."):
                    context_data = {
                        'ai_agent_type': st.session_state.get('ai_agent_type', 'Unknown'),
                        'roi_percentage': ai_results['roi_percentage'],
                        'payback_months': ai_results['payback_months']
                    }
                    ai_insights = get_ai_implementation_insights(groq_client, ai_results, context_data)
                    if ai_insights:
                        st.success("✅ AI Implementation Analysis complete!")
                        st.markdown("### 🎯 Implementation Strategy")
                        st.markdown(ai_insights)
                        st.session_state.ai_implementation_insights = ai_insights
                        st.session_state.ai_insights_timestamp = datetime.now()
            
            if hasattr(st.session_state, 'ai_implementation_insights'):
                st.markdown("### 📋 Latest AI Implementation Analysis")
                st.info(f"Created: {st.session_state.ai_insights_timestamp.strftime('%m/%d/%Y %H:%M')}")
                st.markdown(st.session_state.ai_implementation_insights)

    with tab3:
        st.header("📊 Combined Strategic Analysis")
        st.markdown("""
        Compare all three options: **New Hire**, **Salary Increase**, and **AI Agent Implementation**.
        This analysis helps you make the most strategic decision for your organization.
        """)
        
        # Calculate all costs
        hr_results = calculate_costs()
        ai_results = calculate_ai_costs()
        
        # Combined comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("💼 New Hire")
            st.metric("Total Cost", f"${hr_results['total_hire']:,.0f}")
            st.metric("Time to Value", f"{st.session_state.get('vacancy_months', 3)} months")
            st.metric("Risk Level", "Medium-High")
            
        with col2:
            st.subheader("💰 Salary Increase")
            st.metric("Total Cost", f"${hr_results['total_salary_increase']:,.0f}")
            st.metric("Time to Value", "Immediate")
            st.metric("Risk Level", "Low")
            
        with col3:
            st.subheader("🤖 AI Agent")
            st.metric("Net Benefit (3yr)", f"${ai_results['net_benefit']:,.0f}")
            st.metric("Time to Value", f"{ai_results['implementation_months']} months")
            if ai_results['roi_percentage'] > 100:
                st.metric("Risk Level", "Low-Medium")
            else:
                st.metric("Risk Level", "High")
        
        # Strategic recommendation
        st.header("🎯 Strategic Recommendation Matrix")
        
        # Create comparison dataframe
        comparison_data = {
            'Option': ['New Hire', 'Salary Increase', 'AI Agent (3yr benefit)'],
            'Cost/Benefit': [
                -hr_results['total_hire'],  # Cost (negative)
                -hr_results['total_salary_increase'],  # Cost (negative) 
                ai_results['net_benefit']  # Benefit (positive)
            ],
            'Implementation Time': [
                st.session_state.get('vacancy_months', 3),
                0,
                ai_results['implementation_months']
            ]
        }
        
        df = pd.DataFrame(comparison_data)
        
        # Visualization
        fig = px.scatter(df, x='Implementation Time', y='Cost/Benefit', 
                        text='Option', size=[abs(x) for x in df['Cost/Benefit']], 
                        color='Cost/Benefit',
                        title="Strategic Options Comparison",
                        labels={
                            'Implementation Time': 'Time to Implement (Months)',
                            'Cost/Benefit': 'Net Financial Impact ($)'
                        },
                        color_continuous_scale="RdYlGn")
        fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Break-even Line")
        fig.update_traces(textposition="top center")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Decision framework
        st.subheader("🧭 Decision Framework")
        
        best_financial = df.loc[df['Cost/Benefit'].idxmax(), 'Option']
        fastest_implement = df.loc[df['Implementation Time'].idxmin(), 'Option']
        
        st.success(f"**Best Financial Outcome:** {best_financial}")
        st.info(f"**Fastest Implementation:** {fastest_implement}")
        
        # Scenario-based recommendations
        st.markdown("### 📋 Scenario-Based Recommendations")
        
        scenarios = {
            "🚨 **Urgent Need (< 1 month)**": "Consider **Salary Increase** for immediate results, then plan AI implementation for long-term efficiency.",
            "⚖️ **Balanced Approach (1-6 months)**": "Evaluate between **New Hire** and **AI Agent** based on your strategic priorities and risk tolerance.",
            "🔮 **Long-term Strategy (> 6 months)**": "**AI Agent** likely provides best ROI if implementation is successful. Consider hybrid approach.",
            "💰 **Budget Constrained**": f"**{df.loc[df['Cost/Benefit'].idxmax(), 'Option']}** offers the best financial outcome.",
            "🎯 **Growth Phase**": "**New Hire** for immediate capacity, **AI Agent** for scalable long-term growth."
        }
        
        for scenario, recommendation in scenarios.items():
            st.markdown(f"**{scenario}**: {recommendation}")

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🤖 Powered by <strong>Artificial Intelligence</strong>  💼 HR Intelligence Platform</p>
        <p><small>All calculations are estimates. Consult an HR expert for final decisions.</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
