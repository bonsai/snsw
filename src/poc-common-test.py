import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

# ダミーのベースモデルとして非常に軽量なモデルを使用（動作確認用）
model_name = "sshleifer/tiny-gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
base_model = AutoModelForCausalLM.from_pretrained(model_name)

# LoRA設定
config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM",
)

# LoRAモデルの作成
model = get_peft_model(base_model, config)
model.print_trainable_parameters()

print("LoRA model initialized successfully!")

# ダミーデータでの推論テスト
inputs = tokenizer("Hello, I am testing LoRA.", return_tensors="pt")
outputs = model(**inputs)
print(f"Output shape: {outputs.logits.shape}")
