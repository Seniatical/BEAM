from flask import Flask, request, render_template
from api import scan
import base64
from io import BytesIO

app = Flask('app')

## Acts like a temporary file
class File(object):
    def __init__(self, filename: str):
        self.stream = open(filename, 'rb')
        self.name = filename

    def close(self):
        return self.stream.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        r""" This handles the images and returns the segmented images back to the user """
        
        files = request.files.getlist("files")
        data = {}

        if request.form.get('Y1'):
            files.append(File('./samples/Y1.png'))
        if request.form.get('Y2'):
            files.append(File('./samples/Y2.png'))
        if request.form.get('Y3'):
            files.append(File('./samples/Y3.png'))
        if request.form.get('Y4'):
            files.append(File('./samples/Y4.png'))
        if request.form.get('Y6'):
            files.append(File('./samples/Y6.png'))
        if request.form.get('Y7'):
            files.append(File('./samples/Y7.png'))
        if request.form.get('Y8'):
            files.append(File('./samples/Y8.png'))
        if request.form.get('Y9'):
            files.append(File('./samples/Y9.png'))

        if files:
            for file in files:
                stream = BytesIO(file.stream.read())
                scanned = scan.get_tumour(stream)

                data[file.name] = base64.b64encode(scanned.read()).decode()

                file.close()

            return render_template('index.html', results={
                'files': data
                })

        return render_template('index.html', results=None, error="No files were submitted!")

    return render_template('index.html', results=None)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
