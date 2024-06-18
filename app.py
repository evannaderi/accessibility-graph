import os
import json
import requests
from flask import Flask, request, redirect, url_for, render_template
import pandas as pd
from config import DATAWRAPPER_API_KEY

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        file = request.files['file']
        chart_type = request.form.get('chart_type')
        chart_title = request.form.get('chart_title')
        
        if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Read file into DataFrame
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
                
            csv_text = df.to_csv(index=False)
            
            # Create Datawrapper chart
            chart_id = create_datawrapper_chart(csv_text, chart_type, chart_title)
            
            if chart_id:
                return render_template('upload.html', chart_id=chart_id)
            else:
                return render_template('upload.html', chart_id=None, error='Failed to create chart')
        else:
            return render_template('upload.html', chart_id=None, error='Invalid file format')

def create_datawrapper_chart(csv_text, chart_type, chart_title):
    headers = {
        'Authorization': f'Bearer {DATAWRAPPER_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Step 1: Create a new chart
    chart_data = {
        'title': chart_title,
        'type': chart_type,
    }

    try:
        response = requests.post('https://api.datawrapper.de/v3/charts', headers=headers, json=chart_data)
        response.raise_for_status()
        chart_id = response.json().get('id')
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during chart creation: {e}")
        return None
    
    data_headers = {
        'Authorization': f'Bearer {DATAWRAPPER_API_KEY}',
        'Content-Type': 'text/csv'
    }
    
    # Step 2: Upload data to the chart
    upload_url = f'https://api.datawrapper.de/v3/charts/{chart_id}/data'
    try:
        data_response = requests.put(upload_url, headers=data_headers, data=csv_text)
        data_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during data upload: {e}")
        return None
    
    # Step 3: Publish the chart
    publish_url = f'https://api.datawrapper.de/v3/charts/{chart_id}/publish'
    try:
        publish_response = requests.post(publish_url, headers=headers)
        publish_response.raise_for_status()
        return chart_id
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during chart publication: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)
