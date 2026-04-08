import streamlit as st
import pandas as pd
import time
import os
from main import orchestrator, ask_data_specialist, save_to_report
from vertexai.generative_models import Part

st.set_page_config(page_title="GenAI Data Orchestrator", layout="wide")

# --- SIDEBAR FOR REPORTS ---
with st.sidebar:
    st.header("📄 Saved Insights Report")
    st.write("Business insights logged by the Manager will appear here.")
    if st.button("Refresh Report"):
        if os.path.exists("agent_report.txt"):
            with open("agent_report.txt", "r") as f:
                st.markdown(f.read())
        else:
            st.info("No insights logged yet. Ask the AI to save an analysis!")

st.title("📊 Multi-Agent E-commerce Orchestrator")
st.markdown("Ask the Manager to analyze data, find insights, or draw charts!")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = orchestrator.start_chat()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("e.g., Draw a chart of the top 3 product categories by revenue."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_box = st.empty()
        status_box.info("🤖 Manager is coordinating the analysis...")
        
        response = st.session_state.chat_session.send_message(prompt)
        
        # The Orchestration Loop
        for _ in range(6):
            candidate = response.candidates[0]
            func_call = next((p.function_call for p in candidate.content.parts if hasattr(p, 'function_call') and p.function_call), None)
            
            if func_call:
                if func_call.name == "ask_data_specialist":
                    status_box.warning(f"🔄 Specialist querying database for: '{func_call.args['question']}'")
                    result = ask_data_specialist(func_call.args["question"])
                    
                elif func_call.name == "save_to_report":
                    status_box.success(f"💾 Saving Insight: '{func_call.args['task_name']}'")
                    result = save_to_report(func_call.args["task_name"], func_call.args["insight"])
                    
                elif func_call.name == "create_bar_chart":
                    title = func_call.args.get("chart_title", "Data Chart")
                    categories = list(func_call.args["categories"])
                    values = list(func_call.args["values"])
                    
                    st.subheader(title)
                    chart_df = pd.DataFrame({"Category": categories, "Value": values}).set_index("Category")
                    st.bar_chart(chart_df)
                    
                    status_box.success(f"📊 Chart generated successfully!")
                    result = "Chart was drawn for the user."
                else:
                    result = "Unknown function."
                
                time.sleep(2)
                response = st.session_state.chat_session.send_message(
                    Part.from_function_response(name=func_call.name, response={"content": str(result)})
                )
            else:
                texts = [p.text for p in candidate.content.parts if hasattr(p, 'text') and p.text]
                final_text = "".join(texts)
                status_box.empty() 
                st.markdown(final_text)
                st.session_state.messages.append({"role": "assistant", "content": final_text})
                break