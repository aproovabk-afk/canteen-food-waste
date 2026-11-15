from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

def get_db():
    db = sqlite3.connect("canteen.db")
    db.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, date TEXT, cooked INTEGER, sold INTEGER)")
    return db

PAGE = """
<style>
body {
    font-family: Arial, sans-serif;
    background: #f1f8f4;
    margin: 0;
    padding: 30px;
    color: #26332b;
}

h1 {
    text-align: center;
    color: #218838;
}

form {
    background: white;
    padding: 25px;
    border-radius: 12px;
    max-width: 500px;
    margin: 20px auto;
    box-shadow: 0 3px 12px #0001;
}

input {
    padding: 10px;
    margin: 10px 0;
    border: 1px solid #ccc;
    border-radius: 6px;
}

button {
    background: #218838;
    color: white;
    padding: 12px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

button:hover {
    background: #176b2c;
}

table {
    width: 100%;
    background: white;
    border-collapse: collapse;
    margin-top: 20px;
}

th, td {
    padding: 12px;
    border: 1px solid #ddd;
    text-align: center;
}

th {
    background: #218838;
    color: white;
}

h2 {
    text-align: center;
    color: #218838;
}
.dashboard {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    max-width: 700px;
    margin: 25px auto;
}

.card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 3px 10px #0001;
}

.card h2 {
    color: #218838;
}
</style>
<h1>Canteen Food Waste App</h1>
<div class="dashboard">
    <div class="card">
        <h3>Total Cooked</h3>
        <h2>{{ total_cooked }}</h2>
    </div>

    <div class="card">
        <h3>Total Sold</h3>
        <h2>{{ total_sold }}</h2>
    </div>

    <div class="card">
        <h3>Total Wasted</h3>
        <h2>{{ total_wasted }}</h2>
    </div>

    <div class="card">
        <h3>Waste Percentage</h3>
        <h2>{{ waste_percent }}%</h2>
    </div>
</div>
<form method="post">
  Date: <input type="date" name="date" required><br><br>
  Meals cooked: <input type="number" name="cooked" required><br><br>
  Meals sold: <input type="number" name="sold" required><br><br>
  <button type="submit">Save</button>
</form>
{% if suggestion %}
<h2>Suggested quantity for tomorrow: {{ suggestion }} meals</h2>
{% endif %}
<form method="post" action="/donate">
  <button type="submit">Donate Leftovers to NGOs</button>
</form>
<h3>Last 7 records</h3>
<table border="1" cellpadding="6">
<tr><th>Date</th><th>Cooked</th><th>Sold</th><th>Wasted</th></tr>
{% for r in rows %}
<tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td><td>{{ r[1] - r[2] }}</td></tr>
{% endfor %}
</table>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    db = get_db()

    # Your existing database code

    rows = db.execute(
        "SELECT date, cooked, sold FROM records ORDER BY date DESC LIMIT 7"
    ).fetchall()

    total_cooked = sum(r[1] for r in rows) if rows else 0
    total_sold = sum(r[2] for r in rows) if rows else 0
    total_wasted = total_cooked - total_sold

    waste_percent = round(
        (total_wasted / total_cooked) * 100, 1
    ) if total_cooked > 0 else 0

    suggestion = None

    if rows:
        avg_sold = sum(r[2] for r in rows) / len(rows)
        suggestion = round(avg_sold * 1.05)

    return render_template_string(
        PAGE,
        rows=rows,
        suggestion=suggestion,
        total_cooked=total_cooked,
        total_sold=total_sold,
        total_wasted=total_wasted,
        waste_percent=waste_percent
    )



@app.route('/donate', methods=['POST'])
def donate():
    db = get_db()
    row = db.execute("SELECT date, cooked, sold FROM records ORDER BY date DESC LIMIT 1").fetchone()
    if not row:
        return "No data yet. <a href='/'>Go back</a>"
    leftover = row[1] - row[2]
    return f"Alert sent to NGOs: {leftover} leftover meals available from {row[0]}. <a href='/'>Go back</a>"
if __name__ == "__main__":
    app.run(debug=True)
    