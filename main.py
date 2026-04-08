import os
from dotenv import load_dotenv
import time
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration, Part

# ==========================================
# 1. ENVIRONMENT SETUP
# ==========================================
load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID", "genai-data-pipeline")
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# ==========================================
# 🛠️ CORE FUNCTIONS (The "Hands")
# ==========================================

def query_bigquery(sql_query: str):
    """Data Specialist Tool: Executes SQL against BigQuery."""
    client = bigquery.Client(project=PROJECT_ID)
    try:
        # Auto-correct table names to prevent 'Not Found' errors
        clean_sql = sql_query.replace("`", "")
        if "ecommerce_analytics" not in clean_sql:
             clean_sql = clean_sql.replace("orders", f"{PROJECT_ID}.ecommerce_analytics.orders")
             clean_sql = clean_sql.replace("order_items", f"{PROJECT_ID}.ecommerce_analytics.order_items")
             clean_sql = clean_sql.replace("products", f"{PROJECT_ID}.ecommerce_analytics.products")
        
        print(f"  [DATA SPECIALIST] Running SQL -> {clean_sql[:80]}...")
        query_job = client.query(clean_sql)
        return [dict(row) for row in query_job.result()]
    except Exception as e:
        return f"SQL Error: {str(e)}"

def save_to_report(task_name: str, insight: str):
    """Manager Tool: Logs insights to a file."""
    with open("agent_report.txt", "a") as f:
        f.write(f"Task: {task_name}\nInsight: {insight}\n{'-'*30}\n")
    print(f"  [SYSTEM] ✅ Insight safely logged to agent_report.txt")
    return "Report saved successfully."

# ==========================================
# 🤖 AGENT-AS-A-TOOL LOGIC
# ==========================================

def ask_data_specialist(question: str):
    """Manager Tool: Delegates tasks to the Data Agent."""
    print(f"  [MANAGER] Delegating to Specialist -> '{question}'")
    chat = data_specialist.start_chat()
    response = chat.send_message(question)
    
    # Sub-agent loop (Allows Specialist to fix its own SQL errors)
    for _ in range(3):
        candidate = response.candidates[0]
        func_call = next((p.function_call for p in candidate.content.parts if hasattr(p, 'function_call') and p.function_call), None)
        
        if func_call and func_call.name == "query_bigquery":
            data = query_bigquery(func_call.args["sql_query"])
            response = chat.send_message(Part.from_function_response(name="query_bigquery", response={"content": str(data)}))
        else:
            texts = [p.text for p in candidate.content.parts if hasattr(p, 'text') and p.text]
            return "".join(texts) if texts else "Specialist finished but returned no text."
            
    return "Data Specialist timed out."

# ==========================================
# 📋 MCP TOOL DECLARATIONS
# ==========================================

data_tools = Tool(function_declarations=[
    FunctionDeclaration(
        name="query_bigquery",
        description="Run SQL on BigQuery. Tables: orders(order_id, created_at), order_items(order_id, product_id, sale_price, created_at), products(id, category, name).",
        parameters={"type": "object", "properties": {"sql_query": {"type": "string"}}, "required": ["sql_query"]}
    )
])

manager_tools = Tool(function_declarations=[
    FunctionDeclaration(
        name="ask_data_specialist",
        description="Use this to ask the SQL expert for any data from the database.",
        parameters={"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]}
    ),
    FunctionDeclaration(
        name="save_to_report",
        description="Use this to log final business insights and executive summaries.",
        parameters={"type": "object", "properties": {"task_name": {"type": "string"}, "insight": {"type": "string"}}, "required": ["task_name", "insight"]}
    ),
    FunctionDeclaration(
        name="create_bar_chart",
        description="Creates a visual bar chart on the UI. Use this when the user asks for a visual comparison, chart, or graph of multiple data points.",
        parameters={
            "type": "object", 
            "properties": {
                "chart_title": {"type": "string"}, 
                "categories": {"type": "array", "items": {"type": "string"}}, 
                "values": {"type": "array", "items": {"type": "number"}}
            }, 
            "required": ["chart_title", "categories", "values"]
        }
    )
])

# ==========================================
# 🧠 AGENT INITIALIZATION
# ==========================================

data_specialist = GenerativeModel(
    "gemini-2.5-flash",
    tools=[data_tools],
    system_instruction="You are the Data Specialist. Write standard SQL. For revenue, use SUM(sale_price). Join order_items to products on product_id = id. CRITICAL RULES: 1. ALWAYS make string filters case-insensitive using LOWER(), e.g., LOWER(category) = LOWER('jeans'). 2. Keep queries simple to avoid BQ errors."
)

orchestrator = GenerativeModel(
    "gemini-2.5-flash",
    tools=[manager_tools],
    system_instruction="You are the Primary Manager. Coordinate tasks. 1. Use 'ask_data_specialist' to get data. 2. If the user asks for a chart, use 'create_bar_chart'. 3. Use 'save_to_report' for final business insights. 4. Reply to the user concisely."
)

if __name__ == "__main__":
    print("Run the dashboard via Streamlit: streamlit run dashboard.py")