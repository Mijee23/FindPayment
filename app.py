from flask import Flask, request
from threading import Thread

app = Flask(__name__)
import pandas as pd
import glob
import os

app = Flask(__name__)

# 리스트 초기화
data1, data2, prices1, prices2, weeks = [], [], [], [], []

# 주차별로 정렬된 파일 목록을 가져오기 위해 data1 기준 파일명을 정렬
data1_files = sorted(glob.glob("data/*_data1.csv"))

for path in data1_files:
    filename = os.path.basename(path)
    week = filename.split("_")[0]
    weeks.append(week)

    data2_path = f"data/{week}_data2.csv"
    prices1_path = f"data/{week}_prices1.csv"
    prices2_path = f"data/{week}_prices2.csv"

    data1.append(pd.read_csv(path))
    data2.append(pd.read_csv(data2_path))
    prices1.append(pd.read_csv(prices1_path))
    prices2.append(pd.read_csv(prices2_path))

# 공동 재료비
shared_costs = [
    
    {"항목": "1주차", "금액": 368300},
    {"항목": "2주차", "금액": 288300},
    {"항목": "3주차", "금액": 40000},
    {"항목": "4주차", "금액": 38300},
    {"항목": "5주차", "금액": 31000},
    {"항목": "6주차", "금액": 69300},
    {"항목": "7주차", "금액": 176000},
    {"항목": "8주차", "금액": 97000},
    {"항목": "9주차", "금액": 300000},
    {"항목": "10주차", "금액": 58300},
]

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
                            'Week': weeks[i],
                            'Item': item,
                            'Qty': quantity,
                            'Unit Price': price,
                            'Amount': total
                        })
    result_df = pd.DataFrame(result_rows)
    person_total = result_df['Amount'].sum() if not result_df.empty else 0
    if not result_df.empty:
        result_df.loc[len(result_df)] = ['합계', '', '', '', person_total]
    return result_df, person_total

def get_shared_table():
    df = pd.DataFrame(shared_costs)
    shared_total = df['금액'].sum()
    shared_per_person = round(shared_total / 91)
    df.loc[len(df)] = ['합계', shared_total]
    df.loc[len(df)] = ['공동비 / 91인', shared_per_person]
    return df, shared_total, shared_per_person

@app.route('/', methods=['GET', 'POST'])
def index():
    result_html = ''
    if request.method == 'POST':
        name = request.form['name']
        person_df, person_total = get_person_orders(name)
        shared_df, shared_total, shared_per_person = get_shared_table()
        final_total = person_total + shared_per_person

        person_table = person_df.to_html(index=False) if not person_df.empty else '<p>개인 구매 내역 없음</p>'
        shared_table = shared_df.to_html(index=False)

        result_html = f'''
        <p class="final-total"><strong>✅ 최종 납부 금액 (개인 + 공동): {final_total:,}원</strong></p>
        <div class="columns">
            <div class="column">
                <h3>📦 개인 구매 내역</h3>
                {person_table}
            </div>
            <div class="column">
                <h3>🤝 공동 재료비</h3>
                {shared_table}
            </div>
        </div>
        '''
        
    return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>주문 조회</title>
            <style>
                * {{ box-sizing: border-box; }}
                body {{
                    font-family: 'Segoe UI', sans-serif;
                    background-color: #f9f9f9;
                    color: #333;
                    padding: 2rem;
                    max-width: 100%;
                    margin: auto;
                }}
                h1 {{
                    text-align: center;
                    font-size: 1.8rem;
                    margin-bottom: 1.5rem;
                    color: #34495e;
                }}
                form {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-bottom: 1rem;
                    gap: 0.5rem;
                    flex-wrap: wrap;
                }}
                input[type="text"] {{
                    padding: 0.8rem;
                    font-size: 1rem;
                    width: 90%;
                    max-width: 300px;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                }}
                input[type="submit"] {{
                    padding: 0.7rem 1.2rem;
                    font-size: 1rem;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                }}
                .account-info {{
                    text-align: center;
                    font-size: 1rem;
                    margin-bottom: 1rem;
                    color: #555;
                }}
                .final-total {{
                    text-align: center;
                    font-size: 1.4rem;
                    font-weight: bold;
                    color: #2c3e50;
                    margin: 1.5rem auto;
                    background-color: #ecf0f1;
                    padding: 1rem;
                    border-radius: 10px;
                    max-width: 90%;
                }}
                .columns {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 2rem;
                    margin-top: 2rem;
                }}
                .column {{
                    flex: 1;
                    min-width: 300px;
                    width: 100%;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    background-color: white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    min-width: 400px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: center;
                }}
                th {{ background-color: #f2f2f2; }}
                tr:last-child {{
                    font-weight: bold;
                    background-color: #fafafa;
                }}
                .message {{
                    margin-top: 1rem;
                    font-size: 1.1rem;
                    color: #e74c3c;
                    text-align: center;
                }}
                @media screen and (max-width: 768px) {{
                    body {{
                        padding: 1rem;
                    }}
                    input[type="text"] {{
                        width: 100%;
                        max-width: 100%;
                    }}
                    .final-total {{
                        font-size: 1.2rem;
                    }}
                    table {{
                        min-width: unset;
                        font-size: 0.9rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <h1>3-1Q 공동 및 개인 재료 정산</h1>
            <form method="post">
                <input type="text" name="name" placeholder="예: 오민정" required>
                <input type="submit" value="조회">
            </form>
            <div class="account-info">입금 계좌: 3333-08-7060602 카카오뱅크 오민정</div>
            {result_html if result_html else '<div class="message">이름을 입력하고 조회 버튼을 눌러주세요 😊</div>'}
        </body>
        </html>
    '''
