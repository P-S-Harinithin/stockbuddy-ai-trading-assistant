from flask import Flask, render_template, request, jsonify
from trader_ai import analyze_stock, search_stock

app = Flask(__name__)

# ================= HOME =================
@app.route("/")
def index():
    return render_template("index.html")


# ================= CHAT API =================
@app.route("/ask", methods=["POST"])
def ask():
    user_msg = request.json["message"].strip()

    if not user_msg:
        return jsonify({
            "type": "text",
            "reply": "Type a company name or stock symbol."
        })

    user_upper = user_msg.upper()

    # 🔹 CASE 1: USER CLICKED / ENTERED SYMBOL → ANALYZE
    result = analyze_stock(user_upper)
    if result:
        reply = (
            f"📊 Stock: {result['symbol']}\n"
            f"💰 Current Price: {result['current_price']}\n"
            f"📈 5Y Return: {result['total_return']}%\n"
            f"📉 CAGR: {result['cagr']}%\n"
            f"📊 RSI: {result['rsi']}\n"
            f"🤖 Recommendation: {result['recommendation']}"
        )
        return jsonify({"type": "text", "reply": reply})

    # 🔹 CASE 2: USER TYPED NAME → SEARCH
    search_results = search_stock(user_msg)

    if search_results:
        return jsonify({
            "type": "options",
            "reply": "I found these stocks. Click one:",
            "options": search_results
        })

    return jsonify({
        "type": "text",
        "reply": "I couldn’t find this company. Try another name."
    })


# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(debug=True)
