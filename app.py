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
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Use a SQL query to filter results based on the search query
    if search_query:
        cursor.execute("""
            SELECT title, link, date, description, source 
            FROM news 
            WHERE title ~* %s
            ORDER BY created_at DESC;
        """, (f'\\y{search_query}\\y',))  # \\y denotes word boundaries
    else:
        cursor.execute("SELECT title, link, date, description, source FROM news ORDER BY created_at DESC;")
        
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

    return jsonify(news_list)

if __name__ == '__main__':
    # Bind to the PORT environment variable
    app.run(host='0.0.0.0', port=PORT, debug=True)
