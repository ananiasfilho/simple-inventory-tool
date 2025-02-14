from flask import Flask, render_template
import csv

app = Flask(__name__)

def read_csv():
    """Lê o arquivo CSV e retorna os dados em uma lista de dicionários."""
    csv_filename = "../scan_results.csv"
    data = []
    try:
        with open(csv_filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='|')
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        data.append({"ip": "Arquivo CSV não encontrado"})
    return data

@app.route('/')
def index():
    """Exibe a interface web com os dados do CSV."""
    data = read_csv()
    return render_template("index.html", data=data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
