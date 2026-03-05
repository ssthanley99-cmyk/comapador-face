import os
import base64
import requests
from flask import Flask, render_template, request, jsonify

FACEPP_COMPARE_URL = "https://api-us.faceplusplus.com/facepp/v3/compare"

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

# Rota só pra confirmar se o servidor está enxergando as variáveis
@app.get("/api/env-check")
def env_check():
    k = os.getenv("AbXQcHc-66dcHwg9wYh-jaVrUSdx7_HW") or ""
    s = os.getenv("seYJHVvcm8rTq-BGXORvuSC6UIMOOpPg") or ""
    return jsonify({
        "has_key": bool(k),
        "has_secret": bool(s),
        "key_last4": k[-4:] if k else None,
        "secret_last4": s[-4:] if s else None
    })

@app.post("/api/compare")
def compare():

    api_key = os.getenv("FACEPP_API_KEY")
    api_secret = os.getenv("FACEPP_API_SECRET")

    img1 = request.files["img1"].read()
    img2 = request.files["img2"].read()

    b64_1 = base64.b64encode(img1).decode("utf-8")
    b64_2 = base64.b64encode(img2).decode("utf-8")

    data = {
        "api_key": api_key,
        "api_secret": api_secret,
        "image_base64_1": b64_1,
        "image_base64_2": b64_2
    }

    try:
        r = requests.post(FACEPP_COMPARE_URL, data=data, timeout=60)
        payload = r.json()

        if r.status_code != 200:
            return jsonify({
                "error": payload.get("error_message", f"Erro Face++ (HTTP {r.status_code})")
            }), 400

        if "confidence" not in payload:
            return jsonify(payload)

        confidence = payload["confidence"]

        return jsonify({
            "confidence": confidence,
            "thresholds": payload.get("thresholds", {})
        })

    except requests.RequestException:
        return jsonify({"error": "Falha de rede ao chamar o Face++."}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)