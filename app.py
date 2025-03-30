from flask import Flask, request
import pandas as pd
import glob
import os

app = Flask(__name__)

data1, data2, prices1, prices2, weeks = [], [], [], [], []

for path in sorted(glob.glob("data/*_data1.csv")):
    week = os.path.basename(path).split('_')[0]
    weeks.append(week)
    data1.append(pd.read_csv(path))

for path in sorted(glob.glob("data/*_data2.csv")):
    data2.append(pd.read_csv(path))
for path in sorted(glob.glob("data/*_prices1.csv")):
    prices1.append(pd.read_csv(path))
for path in sorted(glob.glob("data/*_prices2.csv")):
    prices2.append(pd.read_csv(path))

def get_person_orders(name):
    result_rows = []
    for i in range(len(weeks)):
        for df, price_row in [(data1[i], prices1[i].iloc[0]), (data2[i], prices2[i].iloc[0])]:
            match = df[df['이름'] == name]
            if not match.empty:
                row = match.iloc[0]
                for item in df.columns[1:]:
                    quantity = row[item]
                    if quantity > 0:
                        price = price_row[item]
                        total = quantity * price
                        result_rows.append({
                            '주차': weeks[i],
                            '품목': item,
                            '수량': quantity,
                            '단가': price,
                            '금액': total
                        })
    result_df = pd.DataFrame(result_rows)
    if not result_df.empty:
        total = result_df['금액'].sum()
        result_df.loc[len(result_df)] = ['합계', '', '', '', total]
    return result_df

@app.route('/', methods=['GET', 'POST'])
def index():
    result_html = ''
    if request.method == 'POST':
        name = request.form['name']
        result_df = get_person_orders(name)
        if not result_df.empty:
            result_html = result_df.to_html(index=False)
        else:
            result_html = "<p>해당 이름의 주문 내역이 없습니다.</p>"
    return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>주문 조회</title>
            <style>
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    background-color: #f9f9f9;
                    color: #333;
                    padding: 2rem;
                    max-width: 800px;
                    margin: auto;
                }}
                h2 {{
                    color: #2c3e50;
                }}
                form {{
                    margin-bottom: 2rem;
                }}
                input[type="text"] {{
                    padding: 0.5rem;
                    font-size: 1rem;
                    width: 200px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }}
                input[type="submit"] {{
                    padding: 0.5rem 1rem;
                    font-size: 1rem;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                input[type="submit"]:hover {{
                    background-color: #2980b9;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    background-color: white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: center;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:last-child {{
                    font-weight: bold;
                    background-color: #fafafa;
                }}
                .message {{
                    margin-top: 1rem;
                    font-size: 1.1rem;
                    color: #e74c3c;
                }}
            </style>
        </head>
        <body>
            <h2>이름을 입력하세요</h2>
            <form method="post">
                <input type="text" name="name" placeholder="예: 허성광" required>
                <input type="submit" value="조회">
            </form>
            {result_html if result_html else '<div class="message">이름을 입력하고 조회 버튼을 눌러주세요 😊</div>'}
        </body>
        </html>
    '''

