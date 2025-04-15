from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'uploads'
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/process', methods=['POST'])
# def process():
#     text_input = request.form.get('text_input')
#     uploaded_file = request.files.get('file_input')

#     file_info = None
#     if uploaded_file and uploaded_file.filename != '':
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
#         uploaded_file.save(filepath)
#         file_info = {
#             'filename': uploaded_file.filename,
#             'size_kb': round(os.path.getsize(filepath) / 1024, 2)
#         }

#     return render_template('result.html', text_input=text_input, file_info=file_info)

if __name__ == '__main__':
    app.run(debug=True)
