from flask import Flask, render_template, request, redirect, url_for  
# flask for application, render html templates, request incoming data, redirects to diff routes, url for specific pat00h
import sqlite3
# to interact with SQLite databases
app = Flask(__name__) # initialize flask application

def init_db(): # function to initialize database
    conn = sqlite3.connect('expenses.db') # connects to exepnse.db file
    cursor = conn.cursor() # Creates cursor obj to execute SQL
    cursor.execute('''      
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL,
            description TEXT
        )
    ''')# execute SQL commands to create expensees

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT
        )
    ''') # execute SQL commands to create users name
    conn.commit() # saves changes in database
    conn.close() # closes connection with daatabase

@app.route('/') # decorator binds fun index() to root URL ('/')
def index(): # defines the index fun for root route
    conn = sqlite3.connect('expenses.db') 
    cursor = conn.cursor()
    cursor.execute('SELECT first_name, last_name FROM users WHERE id = 1') # take first and last name from users table for user with id = 1.
    user = cursor.fetchone() # gets result as single row
    conn.close() # close connection after fetching data

    full_name = f"{user[0]} {user[1]}" if user else "User Name" # formats user's full name
    # take all expenses from expenses table, ordered by date, stores in expenses
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses ORDER BY date') 
    expenses = cursor.fetchall()
    conn.close()
    # creating dictionaries to store summed values
    monthly_totals = {}
    category_totals = {}
    # iterates through each expense
    for expense in expenses:
        date = expense[1]
        month = date[:7] # Extracts YYYY-MM part of date
        amount = expense[3]
        category = expense[2]
        # updates based on extracted month
        if month in monthly_totals:
            monthly_totals[month] += amount
        else:
            monthly_totals[month] = amount
        # updates based on extracted category
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount
    
    monthly_labels = sorted(monthly_totals.keys()) # sorted list of months
    monthly_data = [monthly_totals[month] for month in monthly_labels] # list of total amounts for each month
    category_labels = list(category_totals.keys()) # label for expense category
    category_data = list(category_totals.values()) # data for expense category
    # renders index.html passes data as variables
    return render_template(
        'index.html',
        full_name=full_name,
        expenses=expenses,
        monthly_labels=monthly_labels,
        monthly_data=monthly_data,
        category_labels=category_labels,
        category_data=category_data
    )

@app.route('/profile', methods=['GET', 'POST']) # handle both get and post request for the /profile route
def profile():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    # updates or inserts user data
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        cursor.execute('SELECT * FROM users WHERE id = 1')
        user = cursor.fetchone()

        if user:
            cursor.execute('UPDATE users SET first_name = ?, last_name = ? WHERE id = 1', (first_name, last_name))
        else:
            cursor.execute('INSERT INTO users (id, first_name, last_name) VALUES (1, ?, ?)', (first_name, last_name))

        conn.commit()
        conn.close()
        return redirect(url_for('profile')) # redirects to /profile route after saving changes
    # fetches user data to display in profile
    cursor.execute('SELECT first_name, last_name FROM users WHERE id = 1')
    user = cursor.fetchone()
    conn.close()

    full_name = f"{user[0]} {user[1]}" if user else "User Name"
    return render_template('profile.html', full_name=full_name, user=user) # renders profile.html with user data
# display form to add expense and handles submissions.
@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = float(request.form['amount'])
        description = request.form['description']
        # inserts expense in database
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)',
                       (date, category, amount, description))
        conn.commit()
        conn.close()

        return redirect(url_for('index')) # redirects to root route after insertion
    return render_template('add_expense.html')
# displays all expenses for review
@app.route('/manage_expenses')
def manage_expenses():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()
    conn.close()
    return render_template('manage_expenses.html', expenses=expenses)
# deletes expense from database based on its id
@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index')) # redirects to root route after deleting
# renders contact.html for Contact Us page
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__': #
    init_db() # initialize database in statring
    app.run(debug=True) # start Flask app in debug mode and give detailed error message for correciton