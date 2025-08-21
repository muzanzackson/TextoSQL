# 🧠 TextoSQL – Natural Language to SQL using Gemini + Flask + Azure SQL

An **AI-powered Text-to-SQL system** that enables users to query databases using plain English.  
Built with **Google Gemini API**, **Flask**, and **Azure SQL** for seamless conversion of natural language instructions into executable SQL queries.

---

## ✨ Features
- 🔹 **English → SQL Conversion** – Generate syntactically correct SQL queries from plain text using Gemini AI.  
- 🔹 **Secure Database Integration** – Connects to Azure SQL with credentials managed via `.env`.  
- 🔹 **Query Execution Engine** – Safely executes SQL queries and returns structured results in JSON format.  
- 🔹 **RESTful APIs** – Endpoints for generating SQL, executing queries, and testing database connectivity.  
- 🔹 **Safety Layer** – Restricts destructive operations (e.g., `DROP`, `DELETE`, `TRUNCATE`) by default.  

---

## 🛠 Tech Stack
- **Backend:** Python, Flask  
- **AI Model:** Google Gemini `gemini-2.5-flash`  
- **Database:** Azure SQL + PyODBC  
- **Environment Management:** Python-dotenv  
- **API Style:** REST (JSON responses)  

---

## 🚀 Getting Started

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/TextoSQL.git
cd TextoSQL
````

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # on macOS/Linux
venv\Scripts\activate      # on Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up environment variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_google_gemini_api_key
AZURE_SQL_PASSWORD=your_azure_sql_password
```

### 5️⃣ Run the Flask app

```bash
python TextSQL.py
```

App runs at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📡 API Endpoints

### 🔹 Generate SQL

`POST /generate`

```json
{
  "input": "Show me the top 5 customers by revenue"
}
```

Response:

```json
{
  "sql_query": "SELECT TOP 5 customer_id, SUM(revenue) AS total_revenue FROM Sales GROUP BY customer_id ORDER BY total_revenue DESC"
}
```

---

### 🔹 Execute SQL

`POST /execute`

```json
{
  "sql_query": "SELECT TOP 5 * FROM Customers"
}
```

Response:

```json
{
  "success": true,
  "columns": ["CustomerID", "Name", "City"],
  "data": [
    {"CustomerID": 1, "Name": "Alice", "City": "London"},
    {"CustomerID": 2, "Name": "Bob", "City": "Paris"}
  ],
  "row_count": 2
}
```

---

### 🔹 Test DB Connection

`GET /test-connection`
Response:

```json
{
  "success": true,
  "message": "Database connection successful"
}
```

---

## 🔒 Safety Notes

* Only **SELECT queries** are allowed by default.
* Destructive SQL operations (`DROP`, `DELETE`, `TRUNCATE`, etc.) are blocked for safety.
* Use caution before enabling modifications in production.

---

## 📂 Project Structure

```
TextoSQL/
│── templates/
│   └── index.html        # Basic frontend template
│── TextSQL.py            # Flask app entry point
│── .env                  # Environment variables (ignored by git)
│── requirements.txt      # Python dependencies
│── README.md             # Project documentation
```

---

## 📌 Future Enhancements

* [ ] Add user authentication & role-based query permissions
* [ ] Support for non-SELECT queries with audit logging
* [ ] Extend to multiple database backends (PostgreSQL, MySQL)
* [ ] Build a React/Next.js frontend dashboard

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork this repo and submit a pull request.

---

