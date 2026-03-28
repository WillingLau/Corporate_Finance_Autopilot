import streamlit as st
import plotly.graph_objects as go
import os
import sys
import time
from langchain_core.messages import HumanMessage

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from app.services.scraper.yfinance_client import YFinanceClient
from app.services.finance.engine import FinancialEngine
from app.models.forecast import ScenarioAssumptions
from app.services.agent.graph import finance_agent_graph

st.set_page_config(page_title="Corporate Finance Autopilot", page_icon="🚀", layout="wide")
st.title("📊 Corporate Finance Autopilot")
st.markdown("Generate financial forecasts and structural assessments.")

if not os.environ.get("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY is not set.")
    st.stop()

with st.sidebar:
    st.header("⚙️ Parameters")
    target_ticker = st.text_input("Ticker", value="MSFT").upper()
    target_margin = st.slider("Target Net Margin", min_value=0.10, max_value=0.50, value=0.35, step=0.01)
    
    st.markdown("---")
    st.markdown("### Assumptions")
    upside_mod = st.number_input("Upside Modification (+%)", value=5.0) / 100
    downside_mod = st.number_input("Downside Modification (-%)", value=-5.0) / 100
    
    run_btn = st.button("🚀 Run Engine", type="primary", width='stretch')

def plot_financial_scenarios(engine_output):
    fig = go.Figure()
    base_years = [y.year for y in engine_output.base_case.forecast_data]
    
    fig.add_trace(go.Scatter(
        x=base_years, y=[y.total_revenue for y in engine_output.base_case.forecast_data],
        mode='lines+markers', name='Base Case', line=dict(color='#1f77b4', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=base_years, y=[y.total_revenue for y in engine_output.upside_case.forecast_data],
        mode='lines+markers', name='Upside Case', line=dict(color='#2ca02c', dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=base_years, y=[y.total_revenue for y in engine_output.downside_case.forecast_data],
        mode='lines+markers', name='Downside Case', line=dict(color='#d62728', dash='dot')
    ))

    fig.update_layout(
        title=f"3-Year Revenue Forecast (CAGR: {engine_output.historical_cagr:.2%})",
        xaxis_title="Year", yaxis_title="Revenue (USD)",
        template="plotly_white", hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

if run_btn:
    if not target_ticker:
        st.warning("Enter a ticker.")
        st.stop()

    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📈 Quantitative Analysis")
        with st.spinner("Fetching data and running projection models..."):
            try:
                scraper = YFinanceClient(ticker=target_ticker)
                company_profile = scraper.fetch_company_data()
                
                assumptions = ScenarioAssumptions(
                    target_net_margin=target_margin,
                    upside_modifier=upside_mod,
                    downside_modifier=downside_mod
                )
                engine = FinancialEngine()
                forecast_output = engine.run_forecast(company_profile, assumptions)
                
                st.plotly_chart(plot_financial_scenarios(forecast_output), use_container_width=True)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Base Growth", f"{forecast_output.base_case.assumed_growth_rate:.2%}")
                m2.metric("Upside Growth", f"{forecast_output.upside_case.assumed_growth_rate:.2%}")
                m3.metric("Downside Growth", f"{forecast_output.downside_case.assumed_growth_rate:.2%}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.stop()

    with col2:
        st.subheader("🧠 Agentic Advisory")
        
        with st.status("🔧 Agent is thinking...", expanded=True) as status:
            log_container = st.empty()
            logs = ""
            
            user_prompt = f"Evaluate {target_ticker} using recent market news. Summarize the findings into an advisory memo."
            inputs = {"messages": [HumanMessage(content=user_prompt)]}
            
            final_report = ""
            
            for event in finance_agent_graph.stream(inputs, stream_mode="values"):
                msg = event["messages"][-1]
                
                if msg.type == "human":
                    continue
                    
                if msg.type == "ai":
                    if msg.tool_calls:
                        for tool in msg.tool_calls:
                            logs += f"**Tool Call:** 🔧 `{tool['name']}`\n\n"
                            log_container.markdown(logs)
                            time.sleep(0.3)
                    else:
                        final_report = msg.content
                        status.update(label="✅ Workflow complete.", state="complete", expanded=False)
                        
                elif msg.type == "tool":
                    logs += f"**Tool Return:** Data acquired from ✅ `{msg.name}`\n\n"
                    log_container.markdown(logs)

        if final_report:
            st.markdown(final_report)