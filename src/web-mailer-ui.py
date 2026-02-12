import gradio as gr
import os
import json
import time
from datetime import datetime

# Path setup
MAILBOX_DIR = "data/mailbox"
INBOX_DIR = os.path.join(MAILBOX_DIR, "inbox")
SENT_DIR = os.path.join(MAILBOX_DIR, "sent")

os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(SENT_DIR, exist_ok=True)

def get_mail_list():
    """SENTディレクトリから納品済みメールのリストを取得"""
    mails = []
    if not os.path.exists(SENT_DIR):
        return []
    for f in sorted(os.listdir(SENT_DIR), reverse=True):
        if f.endswith(".json"):
            with open(os.path.join(SENT_DIR, f), "r", encoding="utf-8") as file:
                mails.append(json.load(file))
    return mails

def send_order(subject, body):
    """新しい発注（メール）を作成"""
    if not subject or not body:
        return "Subject and Body are required."
    
    order_id = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    order_data = {
        "id": order_id,
        "timestamp": datetime.now().isoformat(),
        "subject": subject,
        "from": "user@example.com",
        "to": "agent@snsw.ai",
        "body": body,
        "status": "pending"
    }
    
    file_path = os.path.join(INBOX_DIR, f"{order_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(order_data, f, indent=4, ensure_ascii=False)
    
    return f"Order Sent! ID: {order_id}. Please wait for delivery."

def refresh_view():
    """UIの表示を更新"""
    mails = get_mail_list()
    if not mails:
        return "No deliveries yet."
    
    html = "<div style='display: flex; flex-direction: column; gap: 10px;'>"
    for m in mails:
        html += f"""
        <div style='border: 1px solid #444; padding: 10px; border-radius: 5px; background: #222;'>
            <div style='color: #888; font-size: 0.8em;'>{m['delivered_at']}</div>
            <div style='font-weight: bold; color: #00ffff;'>RE: {m['subject']}</div>
            <div style='margin-top: 5px;'>{m['body']}</div>
            <div style='margin-top: 10px; color: #00ff00;'>[Deliverables]</div>
            <div style='font-size: 0.9em;'>Image: {m['artifacts']['image']}</div>
            <div style='font-size: 0.9em;'>Audio: {m['artifacts']['audio']}</div>
        </div>
        """
    html += "</div>"
    return html

# UI Design
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📧 SNSW-AI Mailer Agent (絵ジェント発注システム)")
    
    with gr.Tab("New Order (発注)"):
        with gr.Row():
            with gr.Column():
                subject_input = gr.Textbox(label="Subject (件名)", placeholder="【発注】風景画の作成依頼")
                body_input = gr.TextArea(label="Body (プロンプト内容)", placeholder="プロンプト: 富士山と桜\nTTS: '春の訪れを感じます'", lines=5)
                send_btn = gr.Button("Send Order (発注送信)", variant="primary")
                status_output = gr.Markdown()
        
        send_btn.click(send_order, inputs=[subject_input, body_input], outputs=status_output)

    with gr.Tab("Inbox / Deliveries (納品箱)"):
        refresh_btn = gr.Button("Refresh (更新)")
        delivery_view = gr.HTML(refresh_view())
        
        refresh_btn.click(refresh_view, outputs=delivery_view)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
