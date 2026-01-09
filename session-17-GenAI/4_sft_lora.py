"""
Goal: training with input-output pairs
Input: "This movie was great!"  →  Output: Positive (1)
Input: "Terrible film, boring"  →  Output: Negative (0)  
"""
# PyTorch - deep learning framework for tensor operations
import torch
# Hugging Face library to load datasets (like IMDB)
from datasets import load_dataset
# Hugging Face library for pre-trained models (BERT, RoBERTa, etc.)
from transformers import (
    AutoModelForSequenceClassification,  # Load pre-trained model for classification
    AutoTokenizer,                       # Load tokenizer matching the model
    TrainingArguments,                   # Configure training hyperparameters
    Trainer                              # High-level training API
)
# Parameter-Efficient Fine-Tuning library (LoRA implementation)
from peft import (
    LoraConfig,         # Configure LoRA settings
    get_peft_model,     # Wrap base model with LoRA adapters
    TaskType            # Enum for task types (classification, causal LM, etc.)
)

# 1. Set up the model and tokenizer
model_name = "roberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
# Load a base model for sequence classification
base_model = AutoModelForSequenceClassification.from_pretrained(
    model_name, 
    num_labels=2  #Binary classification (positive/negative)
    )

# 2. Load and preprocess the dataset (using IMDB movie review sentiment classification as an example)
def tokenize_function(examples):
    return tokenizer(
        examples["text"], 
        padding="max_length",   # Pad all sequences to same length
        truncation=True         # Cut sequences that are too long
    )

dataset = load_dataset("imdb")
tokenized_datasets = dataset.map(
    tokenize_function, 
    batched=True        # Process multiple examples at once (faster)
)

# Prepare smaller training and evaluation datasets for the example
small_train_dataset = tokenized_datasets["train"].shuffle(seed=42).select(range(1000)) # Randomize order (reproducible with seed) & Take only first 1000 examples
small_eval_dataset = tokenized_datasets["test"].shuffle(seed=42).select(range(1000))

# 3. Define the LoRA Configuration (This is the most critical step)
lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS, # Task type: Sequence Classification
    r=16,                       # The rank of the LoRA matrices. This is the most important hyperparameter.
    lora_alpha=32,              # The alpha scaling factor. A common practice is to set this to 2 * r.
    lora_dropout=0.1,           # Dropout probability for the LoRA layers
    target_modules=["query", "value"] # Specify the names of the modules to apply LoRA to, typically the attention layers.
)

# 4. Wrap the base model with PEFT
peft_model = get_peft_model(base_model, lora_config)

# Print the number of trainable parameters. You'll see it's much smaller than the original model.
peft_model.print_trainable_parameters()
# Example output: trainable params: 462,850 || all params: 125,100,292 || trainable% 0.3699828...

# 5. Define training arguments and train the model
training_args = TrainingArguments(
    output_dir="./lora-roberta-imdb",   # Where to save checkpoints
    learning_rate=2e-5,                 # How fast to update weights
    per_device_train_batch_size=8,      # Examples per training step
    per_device_eval_batch_size=8,
    num_train_epochs=3,                 # Pass through data 3 times
    weight_decay=0.01,                  # L2 regularization
    eval_strategy="epoch",              # Evaluate after each epoch
    save_strategy="epoch",
    load_best_model_at_end=True,        # Keep best checkpoint
)
trainer = Trainer(
    model=peft_model,
    args=training_args,
    train_dataset=small_train_dataset,
    eval_dataset=small_eval_dataset,
)

# Start training
trainer.train()

# 6. Perform inference with the trained LoRA model
# Load the best model checkpoint
trained_model = trainer.model

# Prepare input text
text = "This movie was absolutely fantastic! The acting was superb."
inputs = tokenizer(
    text, 
    return_tensors="pt" # Return PyTorch tensors
)

# `.to(trained_model.device)`: Move inputs to the same device (CPU/GPU) as the model
inputs = {k: v.to(trained_model.device) for k, v in inputs.items()}

# Get predictions
with torch.no_grad(): # Disable gradient calculation (faster inference)
    outputs = trained_model(**inputs)
logits = outputs.logits
predicted_class_id = torch.argmax(logits, dim=-1).item()
# `torch.argmax(logits, dim=-1)`: Get index of highest score

# Print the result (assuming label 1 is positive, 0 is negative)
print(f"Predicted class ID: {predicted_class_id}")
print(f"Prediction: {'Positive' if predicted_class_id == 1 else 'Negative'}")

"""
## Complete Flow Summary
```
┌─────────────────────────────────────────────────────────┐
│                    LORA FINE-TUNING FLOW                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Load Model ──► RoBERTa (125M params)                │
│                                                         │
│  2. Load Data ──► IMDB reviews (1000 train, 1000 eval)  │
│                                                         │
│  3. Configure LoRA ──► r=16, target Q and V layers      │
│                                                         │
│  4. Wrap Model ──► Only 0.37% params trainable now      │
│                                                         │
│  5. Train ──► 3 epochs, learning_rate=2e-5              │
│                                                         │
│  6. Inference ──► "Fantastic movie!" → "Positive"       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```
"""