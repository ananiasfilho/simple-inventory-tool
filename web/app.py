from flask import Flask, render_template, request
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
    """Exibe a interface web com os dados do CSV, permitindo paginação, ordenação e filtragem."""
    data = read_csv()
    
    # Filtragem por status
    filter_status = request.args.get("filter_status", default="both")
    if filter_status == "online":
        data = [row for row in data if row.get("status", "").lower() == "online"]
    elif filter_status == "offline":
        data = [row for row in data if row.get("status", "").lower() == "offline"]
    
    # Configurações de paginação
    per_page = request.args.get("per_page", default=10, type=int)
    page = request.args.get("page", default=1, type=int)
    total_items = len(data)
    
    if per_page == 0:
        total_pages = 1
        paginated_data = data
    else:
        total_pages = (total_items // per_page) + (1 if total_items % per_page > 0 else 0)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_data = data[start_idx:end_idx]
    
    # Ordenação por coluna
    sort_by = request.args.get("sort_by", default="ip")
    sort_order = request.args.get("sort_order", default="asc")
    paginated_data = sorted(paginated_data, key=lambda x: x.get(sort_by, ""), reverse=(sort_order == "desc"))
    
    return render_template("index.html", data=paginated_data, per_page=per_page, page=page, total_pages=total_pages, sort_by=sort_by, sort_order=sort_order, filter_status=filter_status)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
