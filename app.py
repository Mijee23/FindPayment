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
    return f"""
        <h2>이름을 입력하세요:</h2>
        <form method="post">
            <input type='text' name='name' required>
            <input type='submit' value='조회'>
        </form>
        <br>{result_html}
    """
