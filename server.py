from flask import Flask, request

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    # You can save the file or perform other actions here
    # For example, save the file to the server
    file.save('assets/' + file.filename)

    return 'File successfully uploaded'

if __name__ == '__main__':
    app.run(debug=True)
