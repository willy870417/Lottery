from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import random
import os

app = Flask(__name__)
DATA_FILE = 'progress.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"prizes": [], "drawn": []}


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/save_settings', methods=['POST'])
def save_settings():
    prize_names = request.form.getlist('prize_name')  # 從表單獲取獎品名稱
    prize_counts = request.form.getlist('prize_count')  # 從表單獲取獎品數量

    # 後端檢查空白欄位
    if any(name.strip() == "" or count.strip() == "" for name, count in zip(prize_names, prize_counts)):
        return "不能有空白欄位", 400

    # 處理獎品設定保存邏輯
    prize_pool = []
    for name, count in zip(prize_names, prize_counts):
        try:
            count = int(count)  # 確保獎品數量是整數
            prize_pool.extend([name] * count)  # 根據數量將該獎品加入獎池
        except ValueError:
            return "獎品數量必須是數字", 400

    # 隨機打亂獎品池順序
    random.shuffle(prize_pool)

    # 保存到進度檔案
    data = load_data()  # 讀取現有數據
    data['prizes'] = prize_pool  # 更新獎品池
    data['drawn'] = []  # 重置已抽中的獎品
    save_data(data)  # 保存更新後的數據

    return redirect(url_for('index'))  # 重定向回首頁


@app.route('/')
def index():
    data = load_data()
    remaining_counts = {item: data['prizes'].count(item) for item in set(data['prizes'])}
    return render_template('index.html', prizes=data['prizes'], drawn=data['drawn'], remaining=remaining_counts)


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        # 從表單獲取獎品資料
        prizes = request.form.getlist('prize')
        counts = request.form.getlist('count')
        prize_pool = []
        
        # 建立獎品池
        for prize, count in zip(prizes, counts):
            prize_pool.extend([prize] * int(count))
        
        # 添加未中獎籤
        no_prize_count = int(request.form['no_prize_count'])
        prize_pool.extend(["未中獎"] * no_prize_count)
        
        # 洗牌
        random.shuffle(prize_pool)

        # 保存設置並重置進度
        data = {"prizes": prize_pool, "drawn": []}
        save_data(data)

        
        return redirect(url_for('index'))

    default_prizes = {
    "重低音藍芽喇叭": 1,
    "星巴克耶誕紅隨行杯": 1,
    "側背小帥包": 1,
    "帽子": 20,
    "硅藻土杯墊": 20,
    "摺疊碗": 30,
    "保溫杯400ml": 100,
    "飲料提袋": 150
    }   
    prizes = request.args.get('prizes', default_prizes)
    return render_template('setup.html', prizes=prizes)
    # return render_template('setup.html')


@app.route('/draw', methods=['POST'])
def draw():
    data = load_data()
    if not data['prizes']:
        return jsonify({"error": "所有籤已經被抽完"})

    # 抽一張籤
    prize = data['prizes'].pop(0)
    data['drawn'].append(prize)
    save_data(data)
    
    # 返回獎品結果及剩餘統計
    remaining_counts = {item: data['prizes'].count(item) for item in set(data['prizes'])}
    return jsonify({"prize": prize, "remaining": remaining_counts})

@app.route('/remaining', methods=['GET'])
def remaining():
    data = load_data()
    remaining_counts = {item: data['prizes'].count(item) for item in set(data['prizes'])}
    return jsonify(remaining_counts)
    

@app.route('/undo_draw', methods=['POST'])
def undo_draw():
    # 載入進度數據
    data = load_data()

    # 確保有抽獎記錄可以回朔
    if not data['drawn']:
        return jsonify({"error": "沒有可以回朔的抽獎記錄"}), 400

    # 取出最後一次的抽獎
    last_draw = data['drawn'].pop()

    # 將該獎品放回剩餘獎品池的最後
    data['prizes'].append(last_draw)

    # 保存更新後的數據
    save_data(data)

    # 返回更新後的剩餘獎品統計
    remaining_counts = {item: data['prizes'].count(item) for item in set(data['prizes'])}
    return jsonify({"message": "回朔成功", "remaining": remaining_counts})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
