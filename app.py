from flask import Flask, request
import pandas as pd
import glob
import os

app = Flask(__name__)

# 리스트 초기화
data1, data2, prices1, prices2, weeks = [], [], [], [], []

# 주차별로 정렬된 파일 목록을 가져오기 위해 data1 기준 파일명을 정렬
data1_files = sorted(glob.glob("data/*_data1.csv"))

for path in data1_files:
    # 예: 'data/1주차_data1.csv' → '1주차'
    filename = os.path.basename(path)
    week = filename.split("_")[0]
    weeks.append(week)

    # 같은 주차의 다른 파일 경로
    data2_path = f"data/{week}_data2.csv"
    prices1_path = f"data/{week}_prices1.csv"
    prices2_path = f"data/{week}_prices2.csv"

    # CSV 불러오기
    data1.append(pd.read_csv(path))
    data2.append(pd.read_csv(data2_path))
    prices1.append(pd.read_csv(prices1_path))
    prices2.append(pd.read_csv(prices2_path))

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
                            '품목(or 치아 번호)': item,
                            '수량': int(quantity),
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
                * {{
                    box-sizing: border-box;
                }}
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
                h2 {{
                    color: #2c3e50;
                    text-align: center;
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
                input[type="submit"]:hover {{
                    background-color: #2980b9;
                }}
                .account-info {{
                    text-align: center;
                    font-size: 1rem;
                    margin-bottom: 1.5rem;
                    color: #555;
                }}
                .table-wrapper {{
                    overflow-x: auto;
                    margin-top: 1.5rem;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    background-color: white;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    min-width: 600px;
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
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <h1>3-1Q 1~7주차 개인 재료 정산</h1>
            <form method="post">
                <input type="text" name="name" placeholder="예: 오민정" required>
                <input type="submit" value="조회">
            </form>
            <div class="account-info">입금 계좌: 3333-08-7060602 카카오뱅크 오민정</div>
            <div class="table-wrapper">
                {result_html if result_html else '<div class="message">이름을 입력하고 조회 버튼을 눌러주세요 😊</div>'}
            </div>
        </body>
        </html>
    '''

