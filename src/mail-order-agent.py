#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mail Order Agent
Simulates a mail-based ordering process for images and audio.
"""
import os
import json
import time
from datetime import datetime

MAILBOX_DIR = "data/mailbox"
ORDERS_DIR = os.path.join(MAILBOX_DIR, "inbox")
DELIVERY_DIR = os.path.join(MAILBOX_DIR, "sent")

def setup_mailbox():
    os.makedirs(ORDERS_DIR, exist_ok=True)
    os.makedirs(DELIVERY_DIR, exist_ok=True)

def create_sample_order():
    """疑似メール（発注書）を作成する"""
    order_id = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    order_data = {
        "id": order_id,
        "timestamp": datetime.now().isoformat(),
        "subject": f"【発注】新規生成依頼 {order_id}",
        "from": "user@example.com",
        "to": "agent@snsw.ai",
        "body": "プロンプト: 黄金の夕日に照らされたサイバーパンクな都市。デジタルアート。 \nTTS: '未来の都市へようこそ' ",
        "status": "pending"
    }
    
    file_path = os.path.join(ORDERS_DIR, f"{order_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(order_data, f, indent=4, ensure_ascii=False)
    
    print(f"New order created: {file_path}")
    return file_path

def process_orders():
    """未処理の発注（メール）をチェックして処理する"""
    orders = [f for f in os.listdir(ORDERS_DIR) if f.endswith(".json")]
    
    if not orders:
        print("No pending orders.")
        return

    for order_file in orders:
        path = os.path.join(ORDERS_DIR, order_file)
        with open(path, "r", encoding="utf-8") as f:
            order = json.load(f)
            
        print(f"\nProcessing Order: {order['id']}")
        print(f"Subject: {order['subject']}")
        
        # 擬似的な生成プロセス
        time.sleep(1)
        print(">>> Generating Assets...")
        
        # 納品データの作成
        order["status"] = "delivered"
        order["delivered_at"] = datetime.now().isoformat()
        order["artifacts"] = {
            "image": f"image_outputs/mock_{order['id']}.png",
            "audio": f"tts_outputs/mock_{order['id']}.wav"
        }
        
        # 納品（移動）
        delivery_path = os.path.join(DELIVERY_DIR, order_file)
        with open(delivery_path, "w", encoding="utf-8") as f:
            json.dump(order, f, indent=4, ensure_ascii=False)
            
        os.remove(path)
        print(f"Order {order['id']} delivered successfully.")

if __name__ == "__main__":
    setup_mailbox()
    # コマンドライン引数があればサンプル作成
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        create_sample_order()
    
    process_orders()
