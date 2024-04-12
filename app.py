from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use Agg backend which does not require a GUI
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import plotly.graph_objs as go
from plotly.offline import plot
from sklearn.linear_model import LinearRegression
import numpy as np
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

def debug(test):
    """
    Debugging function to print information about the data being processed.

    Parameters:
    - test: The data to be printed for debugging.
    """
    print(f'\n\n\n*************THIS SECTION IS WORKING*************\n')
    print(f'TEST: {test}, LEN:{len(test)}, TYPE:{type(test)}\n\n\n')

def unfiltered():
    """
    Retrieve unfiltered data from a SQLite database table

    Parameters:
    - start: The start year for filtering.
    - end: The end year for filtering.

    Returns:
    A pandas DataFrame containing the unfiltered data.
    """
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('Inflation-data.db')
    cursor = conn.cursor()
    # Read data from the 'Inflation_data' table into a pandas DataFrame
    df = pd.read_sql('SELECT * FROM Inflation_data', conn)
    df = df.drop(columns='Unnamed: 58')
    # Close the database connection
    conn.close()
    return df

def filtered(start, end):
    """
    Retrieve filtered data from a SQLite database table based on the specified start and end years.

    Parameters:
    - start: The start year for filtering.
    - end: The end year for filtering.

    Returns:
    A pandas DataFrame containing the filtered data.
    """
    # Establish a connection to the SQLite database
    conn = sqlite3.connect('Inflation-data.db')
    cursor = conn.cursor()
    # Read data from the 'Inflation_data' table into a pandas DataFrame
    df = pd.read_sql('SELECT * FROM Inflation_data', conn)
    df = df.drop(columns='Unnamed: 58')
    # Close the database connection
    conn.close()

    # Select years within the specified range
    years = list(range(int(start), int(end) + 1))
    filtered_df = df.loc[:, ['Country Code', 'Country'] + list(map(str, years))].dropna().reset_index()
    return filtered_df

def process_data(countries, filtered_df, start, end):
    """
    Process the filtered data to calculate average and total inflation percentages for each selected country.

    Parameters:
    - countries: A list of selected countries.
    - filtered_df: The filtered DataFrame containing the data.
    - start: The start year for filtering.
    - end: The end year for filtering.

    Returns:
    A tuple containing a list of inflation data for each country and a DataFrame containing country codes, names, average inflation, and total inflation.
    """
    avgs = []
    all_vals = []

    # Process data for each selected country
    for country in countries:
        current_vals = filtered_df.query("Country == @country").loc[:, str(start):str(end)].sum().to_list()
        avg = round(sum(current_vals) / len(current_vals), 2)
        avgs.append(avg)
        all_vals.append(current_vals)

    # Create DataFrame containing country codes, names, average inflation, and total inflation
    data = pd.DataFrame({'Country': countries,
                        'Average Inflation': avgs,
                        'Inflation Values': all_vals}).dropna()

    return all_vals, data

@app.route('/')
def index():
    """
    Render the index.html template.

    Returns:
    The rendered HTML template.
    """
    return render_template('index.html')

@app.route('/submit_years', methods=['POST'])
def submit_years():
    """
    Handle the submission of start and end years from the form.

    Returns:
    The rendered HTML template with a list of countries based on the filtered years.
    """
    start = request.form.get('start')
    end = request.form.get('end')
    filtered_df = filtered(start, end)
    countries = filtered_df['Country'].to_list()
    return render_template('countries.html', countries=countries, start=start, end=end)

# @app.route('/add', methods=['POST'])
# def selected():
#     """
#     Handle the submission of selected countries from the form.

#     Returns:
#     The rendered HTML template with a plot of inflation data for selected countries.
#     """
#     countries = request.form.getlist('countries')
#     start = request.form.get('start')
#     end = request.form.get('end')
#     years = list(range(int(start), int(end) + 1))
#     filtered_df = filtered(start, end)
#     all_vals, data = process_data(countries, filtered_df, start, end)
#     debug(filtered_df)

#     # Plot inflation data using Seaborn
#     plt.figure(figsize=(13.5, 6))
#     sns.set(style="whitegrid")  # Set the style to whitegrid
#     for vals in all_vals:
#         sns.lineplot(x=years, y=vals)

#     # Customize tick marks on the x-axis
#     ax = plt.gca()
#     tick_locs = list(range(int(start), int(end) + 1, 3))
#     if int(end) not in tick_locs:
#         del tick_locs[-1]
#         tick_locs.append(int(end))
#     ax.xaxis.set_major_locator(ticker.FixedLocator(tick_locs))

#     # Add legend with country names and average inflation
#     legend_labels = [f'{c}: {avg}%' for c, avg in zip(data['Country'], data['Average Inflation'])]
#     plt.legend(legend_labels, 
#                title='Countries Average Inflation', 
#                loc='upper right', 
#                bbox_to_anchor=(1.25, 1.0))

#     # Set titles and labels
#     plt.title('Inflation Data by Year')
#     plt.xlabel('Year')
#     plt.ylabel('Inflation Percentage')

#     # Set x-axis limits to start and end years
#     plt.xlim(min(years), max(years))

#     # Save the plot to a temporary file
#     plot_path = 'static/figs/plot.png'
#     plt.tight_layout()
#     plt.savefig(plot_path)

#     # Render the add.html template with the plot
#     return render_template('add.html', plot_path=plot_path)

@app.route('/add', methods=['POST'])
def selected():
    """
    Handle the submission of selected countries from the form.

    Returns:
    The rendered HTML template with a plot of inflation data for selected countries.
    """
    countries = request.form.getlist('countries')
    start = int(request.form.get('start'))
    end = int(request.form.get('end'))
    years = list(range(start, end + 1))
    filtered_df = filtered(start, end)
    all_vals, data = process_data(countries, filtered_df, start, end)
    debug(filtered_df)

    # Create traces for each country
    traces = []
    for vals, country in zip(all_vals, countries):
        trace = go.Scatter(x=years, y=vals, mode='lines', name=country)
        traces.append(trace)

    # Create layout
    layout = go.Layout(
        title='Inflation Data by Year',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Inflation Percentage'),
        legend=dict(title='Countries Average Inflation', x=1, y=1),
        height=750
    )

    # Create figure
    fig = go.Figure(data=traces, layout=layout)

    # Plot the graph and get the HTML
    graph_html = plot(fig, output_type='div', include_plotlyjs=False)

    # Render the template with the Plotly graph HTML
    return render_template('add.html', graph_html=graph_html)

@app.route('/world_avgs')
def world_avgs():
    years = list(range(1970, 2023))
    df = unfiltered()
    means = [df[str(y)].mean() for y in years]

    # Define the color scale from green to red based on mean values
    colorscale = [
        [0, 'green'],
        [1, 'red']
    ]

    # Create a bar trace with color scale
    bar_trace = go.Bar(
        x=years,
        y=means,
        name='World Averages',
        marker=dict(
            color=means,
            colorscale=colorscale,
            # colorbar=dict(
            #     title='Mean Value',
            #     tickvals=means,
            #     ticktext=[f'{mean:.2f}' for mean in means]
            # )
        )
    )

    # Calculate linear regression
    X = np.array(years).reshape(-1, 1)
    y = np.array(means)
    regressor = LinearRegression()
    regressor.fit(X, y)
    y_pred = regressor.predict(X)

    # Create a line trace for the regression line with blue color
    line_trace = go.Scatter(
        x=years,
        y=y_pred,
        mode='lines',
        name='Line of Best Fit',
        line=dict(color='blue')
    )

    # Create layout
    layout = go.Layout(
        title='World Average Food Inflation by Year from 1970 to 2022',
        xaxis=dict(title='Year'),
        yaxis=dict(title='World Average Inflation Value'),
        height=800
    )

    # Create figure
    fig = go.Figure(data=[bar_trace, line_trace], layout=layout)

    # Plot the graph and get the HTML
    graph_html = plot(fig, output_type='div', include_plotlyjs=False)

    # Render the template with the Plotly graph HTML
    return render_template('world_avgs.html', graph_html=graph_html)

if __name__ == '__main__':
    # Create the directory for saving plot images if it doesn't exist
    directory_path = 'static/figs'
    create_directory_if_not_exists(directory_path)
    # Run the Flask app
    app.run(debug=True)
