from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('error.html', message="No file part in the request."), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('error.html', message="No file selected. Please upload a file."), 400
        
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_extension = filename.rsplit('.', 1)[1].lower()
            return render_template('dashboard.html', filename=filename, extension=file_extension)
    
    return render_template('dashboard.html')

@app.route('/search', methods=['POST'])
def search_email():
    email = request.form.get('email')
    filename = request.form.get('filename')
    extension = request.form.get('extension')
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        if extension == 'csv':
            df = pd.read_csv(file_path)
        elif extension == 'xlsx':
            df = pd.read_excel(file_path)
        else:
            return render_template('error.html', message="Invalid file format."), 400

        filtered_df = df[df['owner_email'] == email][['owner_name', 'path', 'owner_email']]
        
        if filtered_df.empty:
            return render_template('error.html', message="No records found for the entered email."), 404
        
        # Save the filtered data to a new Excel file
        output_filename = f"filtered_data_{email}.xlsx"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        filtered_df.to_excel(output_path, index=False)
        
        return send_file(output_path, as_attachment=True, download_name=output_filename)
    except Exception as e:
        return render_template('error.html', message="An error occurred while processing your request."), 500

if __name__ == '__main__':
    app.run(debug=True)

