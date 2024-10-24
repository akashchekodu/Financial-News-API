from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
PORT = int(os.getenv("PORT", 5000))  # Use the PORT environment variable, default to 5000

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)  # This will enable CORS for all routes and origins

# Database connection
def get_db_connection():
    connection = psycopg2.connect(DB_CONNECTION_STRING)
    return connection

@app.route('/api/news', methods=['GET'])
def get_news():
    # Get the search query parameter
    search_query = request.args.get('search', default='', type=str)
    
    # Get the source filter parameter
    source_filter = request.args.get('source', default='', type=str)
    
    # Get pagination parameters
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)

    # Calculate the offset for pagination
    offset = (page - 1) * limit

    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Use a SQL query to filter results based on the search query and source
    sql_query = """
        SELECT title, link, date, description, source 
        FROM news 
        WHERE TRUE
    """
    
    query_conditions = []
    params = []

    # Add conditions based on the search query
    if search_query:
        query_conditions.append("title ~* %s")
        params.append(f'\\y{search_query}\\y')  # \\y denotes word boundaries

    # Add conditions based on the source filter
    if source_filter:
        query_conditions.append("source = %s")
        params.append(source_filter)

    # Combine conditions into the final SQL query
    if query_conditions:
        sql_query += " AND " + " AND ".join(query_conditions)

    sql_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s;"
    params.extend([limit, offset])  # Add limit and offset to parameters

    cursor.execute(sql_query, params)
    news_items = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    # Format data into JSON
    news_list = []
    for item in news_items:
        news_list.append({
            'title': item[0],
            'link': item[1],
            'date': item[2].isoformat() if item[2] is not None else None,  # Check if date is NULL
            'description': item[3],
            'source': item[4]
        })

    # Return the results along with pagination information
    return jsonify({
        'page': page,
        'limit': limit,
        'news': news_list
    })

if __name__ == '__main__':
    # Bind to the PORT environment variable
    app.run(host='0.0.0.0', port=PORT, debug=True)
