from flask import Flask, render_template, request, jsonify
from chat_core import chat

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    if not data or "messages" not in data:
        return jsonify({"error": "messages required"}), 400

    try:
        answer = chat(data["messages"])
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)