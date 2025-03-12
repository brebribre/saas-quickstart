from controller.telegram.telegram_utils import (
    send_telegram_notification,
)
from flask import Blueprint, request, jsonify
from flasgger import swag_from

telegram_bp = Blueprint("telegram", __name__)

@telegram_bp.route("/bot/send/text", methods=["POST"])
def send_telegram_text_message():
    """
    Send a text message to Telegram
    ---
    tags:
      - Telegram
    summary: Send a text message to a Telegram chat
    description: Send a text message to a specified Telegram chat or the default chat
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - message
          properties:
            message:
              type: string
              description: The message to send
              example: "Hello, this is a test message"
            chat_id:
              type: string
              description: Optional chat ID to send the message to
              example: "123456789"
    responses:
      200:
        description: Message sent successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Message sent successfully"
      400:
        description: Bad request, missing required parameters
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Message is required"
      500:
        description: Server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to send message"
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    message = data["message"]
    chat_id = data.get("chat_id")

    try:
        send_telegram_notification(message)
        return jsonify({"success": True, "message": "Message sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
