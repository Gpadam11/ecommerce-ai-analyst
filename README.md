# 📊 Multi-Agent E-commerce Data Orchestrator

An intelligent, multi-agent AI system that bridges the gap between raw database storage and actionable business intelligence. Users can ask questions in plain English, and the system will autonomously write SQL, query BigQuery, draw visual charts, and generate strategic business reports.

## 🚀 The Vision
Data is useless if business development and sales teams can't easily access and understand it. This project replaces complex SQL dashboards with a conversational AI Manager. It allows anyone from SDRs to Executives to pull real-time revenue gaps, identify high-ticket items, and generate cold-outreach strategies directly from the database.

## 🧠 Architecture & Tech Stack
* **Frontend:** Streamlit (deployed via Google Cloud Run)
* **Orchestration:** Vertex AI / Gemini 2.5 Flash
* **Database:** Google BigQuery
* **Framework:** Agent-as-a-Tool (MCP-compliant function calling)

## 🤖 How the Agents Work
The system operates using a two-agent hierarchy:
1.  **The Primary Manager:** Interacts with the user, plans the analytical steps, draws UI charts, synthesizes raw data into business strategy, and logs final reports.
2.  **The Data Specialist (Sub-Agent):** Receives plain-English data requests from the Manager, translates them into standard SQL, securely queries BigQuery, and auto-corrects its own syntax errors before returning the numbers.

## ✨ Key Features
* **Text-to-SQL:** Seamlessly handles messy user inputs and case-sensitivity (e.g., dynamically using `LOWER()` functions) to extract accurate data.
* **Automated Data Visualization:** Dynamically renders interactive Streamlit bar charts when users ask for category comparisons.
* **Strategic Reporting:** Capable of performing multi-step reasoning to calculate performance gaps and automatically save executive summaries to a local report file.
* **Sales Enablement:** Turns database rows into actionable copy, such as generating VIP outreach emails based on top-selling product categories.

## 💡 Example Prompts to Try
* *“What was the total revenue for Jeans compared to Sweaters?”*
* *“Identify the top 5 most popular product categories by the total number of items sold and draw a bar chart.”*
* *“Find our highest and lowest-grossing product categories. Calculate the revenue difference and write a strategic recommendation on whether we should discount the lowest performer. Save this to the report.”*

## 🛠️ Local Installation
If you want to run this project locally:

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME
