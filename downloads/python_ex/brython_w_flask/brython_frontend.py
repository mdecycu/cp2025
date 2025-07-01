from browser import document, html, window
import json

# === UI 產生 ===
div = html.DIV()
div <= html.LABEL("維度 D: ") + html.INPUT(id="D", value="2") + html.BR()
div <= html.LABEL("NP: ") + html.INPUT(id="NP", value="200") + html.BR()
div <= html.LABEL("F: ") + html.INPUT(id="F", value="1.2") + html.BR()
div <= html.LABEL("CR: ") + html.INPUT(id="CR", value="0.9") + html.BR()
div <= html.LABEL("genmax: ") + html.INPUT(id="genmax", value="1000") + html.BR()
div <= html.LABEL("strategy: ") + html.INPUT(id="strategy", value="3") + html.BR()
div <= html.BUTTON("開始最佳化", id="go_btn") + html.BR() + html.BR()
div <= html.PRE("結果將顯示於此", id="result")
document["brython_div1"] <= div

# === 建立 WebSocket 客戶端 ===
ws = window.WebSocket.new("ws://localhost:8765")

def on_message(evt):
    data = window.JSON.parse(evt.data)
    output = document["result"]
    if "error" in data:
        output.text = "❌ 錯誤：" + data["error"]
    else:
        output.text = (
            f"✅ 最佳值: {data['best_cost']:.6f}\n"
            f"✅ 最佳參數: {data['best_vector']}"
        )

ws.bind("message", on_message)

def send_to_server(ev):
    params = {
        "D": int(document["D"].value),
        "NP": int(document["NP"].value),
        "F": float(document["F"].value),
        "CR": float(document["CR"].value),
        "genmax": int(document["genmax"].value),
        "strategy": int(document["strategy"].value)
    }
    msg = json.dumps(params)
    ws.send(msg)
    document["result"].text = "⏳ 計算中..."

document["go_btn"].bind("click", send_to_server)