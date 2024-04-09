# from flask import Flask, render_template, request
# import sqlite3
# import pandas as pd
# import matplotlib.pyplot as plt


# app = Flask(__name__)

# # # Function to create a new database and table if they don't exist
# # def create_table():
# #     conn = sqlite3.connect('names.db')
# #     cursor = conn.cursor()
# #     cursor.execute('''CREATE TABLE IF NOT EXISTS names
# #                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                        name TEXT NOT NULL)''')
# #     conn.commit()
# #     conn.close()

# # def read_data():
    
# #     return filtered_df

# def setup():
#     # Establish a connection to the SQLite database
#     conn = sqlite3.connect('Inflation-data.db')
#     cursor = conn.cursor()
#     # Read data from the 'Inflation_data' table into a pandas DataFrame
#     df = pd.read_sql('SELECT * FROM Inflation_data', conn)
#     df = df.drop(columns='Unnamed: 58')
#     usa = cursor.execute('Select * from Inflation_data where "Country Code" == "USA"').fetchall()
#     # Close the database connection
#     conn.close()

#     # Filter columns based on column names, including "Country Code"
#     start = 2018
#     end = 2023
#     years = range(start, end)
#     filtered_df = df.loc[:, ['Country Code'] + ['Country'] + list(map(str, years))].dropna().reset_index()
#     return filtered_df

# def get_data(countries):
#     filtered_df = setup()

#     avgs = []
#     sums = []
#     curs = []

#     # Extract country for names list
#     # countries = filtered_df['Country'].tolist()

#     # # Extract country codes for names list
#     # codes = filtered_df['Country Code'].tolist()

#     for country in countries:
#         cur = filtered_df.query("Country == @country").loc[:, str(start):str(end-1)].sum().to_list()
#         avg = round(sum(cur)/len(cur), 2)
#         sums.append(round(sum(cur),2))
#         avgs.append(avg)
#         curs.append(cur)

#     test = pd.DataFrame({'Country Codes': codes,
#                         'Country': countries,
#                         'Average Inflation': avgs,
#                         'Sum Inflation': sums}).dropna()

#     plt.figure(figsize=(15, 6))
#     for cur in curs:
#         plt.plot(years, cur)
        
#     plt.legend([f'{c}: {avg}%' for c,avg in zip(test['Country'] , test['Average Inflation'])], 
#                 loc='upper right',
#                 bbox_to_anchor=(1.25, 1))
#     plt.tight_layout()
#     # plt.show()
#     test
    
#     return test

# # @app.route('/add', methods=['POST'])
# # def add_task():
# #     title = request.form['name']
# #     conn = sqlite3.connect('names.db')
# #     cursor = conn.cursor()
# #     cursor.execute('INSERT INTO tasks (title, description) VALUES (?, ?)', (title, description))
# #     conn.commit()
# #     conn.close()
# #     return redirect(url_for('home'))

# ## Old keep for now
# # @app.route('/add', methods=['POST'])
# # def selected():
# #     selected_names = request.form.getlist('names')
# #     #Use selected_names and filtered_df to get all data from the columns 
# #     return render_template('add.html', selected_names=selected_names)

# @app.route('/')
# def index():
#     return render_template('index.html', countries=countries, filtered_df=filtered_df)


# @app.route('/add', methods=['POST'])
# def selected():
#     countries = request.form.getlist('countries')
#     filtered_data = get_data(countries)
    
#     return render_template('add.html', filtered_data=filtered_data)


# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use Agg backend which does not require a GUI
import matplotlib.pyplot as plt
import json
import os

app = Flask(__name__, static_url_path='/static')

def create_directory_if_not_exists(directory):
    """
    Create a directory if it doesn't exist.

    Parameters:
    - directory: The path of the directory to create.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        # print(f"Directory '{directory}' created successfully.")
    else:
        print(f"Directory '{directory}' already exists.")

def debug(test):
    print(f'\n\n\n*************THIS SECTION IS WORKING*************\n')
    print(f'TEST: {test}, LEN:{len(test)}, TYPE:{type(test)}\n\n\n')

def get_country_names():
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('Inflation-data.db')
    cursor = conn.cursor()
    # Read data from the 'Inflation_data' table into a pandas DataFrame
    df = pd.read_sql('SELECT DISTINCT Country FROM Inflation_data', conn)
    # Close the database connection
    conn.close()

    # Extract country names from the DataFrame
    country_names = df['Country'].tolist()
    
    return country_names

def filtered(start, end):
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('Inflation-data.db')
    cursor = conn.cursor()
    # Read data from the 'Inflation_data' table into a pandas DataFrame
    df = pd.read_sql('SELECT * FROM Inflation_data', conn)
    df = df.drop(columns='Unnamed: 58')
    # Close the database connection
    conn.close()

    years = list(range(int(start), int(end) + 1))
    filtered_df = df.loc[:, ['Country Code'] + ['Country'] + list(map(str, years))].dropna().reset_index()
    return filtered_df

def get_data(countries, filtered_df, start, end):
    avgs = []
    sums = []
    curs = []
    codes = []

    for country in countries:
        cur = filtered_df.query("Country == @country")
        code = cur['Country Code']
        vals = cur.loc[:, start:end].sum().to_list()
        avg = round(sum(vals)/len(vals), 2)
        sums.append(round(sum(vals),2))
        avgs.append(avg)
        codes.append(code)
        curs.append(vals)

    test = pd.DataFrame({'Country Codes': codes,
                        'Country': countries,
                        'Average Inflation': avgs,
                        'Sum Inflation': sums}).dropna()

    
    return curs, test

@app.route('/')
def index():
    countries = get_country_names()
    return render_template('index.html', countries=countries)

@app.route('/add', methods=['POST'])
def selected():
    countries = request.form.getlist('countries')
    start = request.form.get('start')
    end = request.form.get('end')
    years = list(range(int(start), int(end) + 1))
    filtered_df = filtered(start, end)
    curs, test = get_data(countries, filtered_df, start, end)
    debug(filtered_df)
    plt.figure(figsize=(12, 6))
    plt.title('Inflation Data by Year')
    plt.xlabel('Year')
    plt.ylabel('Inflation')
    for cur in curs:
        plt.plot(years, cur)
        
    plt.legend([f'{c}: {avg}%' for c,avg in zip(test['Country'] , test['Average Inflation'])], 
                loc='upper right',
                bbox_to_anchor=(1.25, 1.0))
    plt.tight_layout()

    # Save the plot to a temporary file
    plot_path = 'static/plot.png'
    fig = plt.savefig(plot_path)
    return render_template('add.html', plot_path=plot_path)

if __name__ == '__main__':
    directory_path = 'static'
    create_directory_if_not_exists(directory_path)
    app.run(debug=True)
