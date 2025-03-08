from flask import Blueprint, jsonify, request
from controller.telegram.telegram_utils import (
    send_telegram_notification,
)

telegram_bp = Blueprint("telegram", __name__)

@telegram_bp.route("/api/bot/send/text", methods=["POST"])
def send_telegram_text_message():
    """
    Send a text message to Telegram
    ---
    tags:
      - Telegram
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Hello, this is a test message"
    responses:
      200:
        description: The message was sent successfully
        schema:
          type: object
          properties:
            status_code:
              type: integer
              example: 200
    """
    data = request.json
    message = data.get("message")

    send_telegram_notification(message)

    return jsonify(
        {
            "status_code": 200,
        }
    )
