from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import pyodbc
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Azure SQL connection string
def get_db_connection():
    """
    Create connection to Azure SQL Database
    """
    try:
        # Azure SQL connection string
        conn_str = (
            "Driver={ODBC Driver 18 for SQL Server};"
            "Server=tcp:textosql.database.windows.net,1433;"
            "Database=db;"  # replace with your actual database name
            "Uid=texttosql@textosql;"
            f"Pwd={os.getenv('AZURE_SQL_PASSWORD')};"  # get password from environment
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )
        connection = pyodbc.connect(conn_str)
        return connection
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None

def generate_sql_query(user_input):
    """
    Generate SQL query using Gemini API
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create a prompt that specifically asks for SQL query only
        prompt = f"""
        Convert the following natural language request into a SQL query for Microsoft SQL Server. 
        Return ONLY the SQL query without any explanations, comments, or additional text.
        Do not include markdown formatting or code blocks.
        Make sure the query is compatible with Microsoft SQL Server syntax.
        
        Request: {user_input}
        
        SQL Query:
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Extract and clean the SQL query
        sql_query = response.text.strip()
        
        # Remove any potential markdown formatting
        if sql_query.startswith('```'):
            lines = sql_query.split('\n')
            sql_query = '\n'.join([line for line in lines if not line.strip().startswith('```')])
        
        return sql_query.strip()
        
    except Exception as e:
        return f"Error generating SQL query: {str(e)}"

def execute_sql_query(sql_query):
    """
    Execute SQL query on Azure SQL Database
    """
    try:
        connection = get_db_connection()
        if not connection:
            return {"error": "Failed to connect to database"}
        
        cursor = connection.cursor()
        
        # Execute the query
        cursor.execute(sql_query)
        
        # Check if it's a SELECT query (returns results)
        if sql_query.strip().upper().startswith('SELECT'):
            # Fetch results
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            # Convert rows to list of dictionaries
            results = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    # Handle different data types
                    if value is None:
                        row_dict[columns[i]] = None
                    elif isinstance(value, (int, float, str, bool)):
                        row_dict[columns[i]] = value
                    else:
                        # Convert other types to string
                        row_dict[columns[i]] = str(value)
                results.append(row_dict)
            
            cursor.close()
            connection.close()
            
            return {
                "success": True,
                "columns": columns,
                "data": results,
                "row_count": len(results)
            }
        else:
            # For non-SELECT queries (INSERT, UPDATE, DELETE, etc.)
            connection.commit()
            affected_rows = cursor.rowcount
            
            cursor.close()
            connection.close()
            
            return {
                "success": True,
                "message": f"Query executed successfully. {affected_rows} row(s) affected.",
                "affected_rows": affected_rows
            }
            
    except Exception as e:
        if 'connection' in locals() and connection:
            connection.close()
        return {"error": f"Database error: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    user_input = request.json.get('input', '')
    
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    sql_query = generate_sql_query(user_input)
    
    return jsonify({'sql_query': sql_query})

@app.route('/execute', methods=['POST'])
def execute():
    sql_query = request.json.get('sql_query', '')
    
    if not sql_query:
        return jsonify({'error': 'No SQL query provided'}), 400
    
    # Basic validation to prevent potentially harmful queries
    dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
    query_upper = sql_query.upper().strip()
    
    # Allow only SELECT queries by default (you can modify this based on your needs)
    if not query_upper.startswith('SELECT'):
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return jsonify({
                    'error': f'Potentially dangerous operation detected: {keyword}. Only SELECT queries are allowed for safety.'
                }), 400
    
    result = execute_sql_query(sql_query)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route('/test-connection')
def test_connection():
    """
    Test database connection endpoint
    """
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return jsonify({'success': True, 'message': 'Database connection successful'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
        return jsonify({'success': False, 'error': 'Failed to establish database connection'})

if __name__ == '__main__':
    # Check environment variables
    required_vars = ['GEMINI_API_KEY', 'AZURE_SQL_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with all required variables")
    
    app.run(debug=True)