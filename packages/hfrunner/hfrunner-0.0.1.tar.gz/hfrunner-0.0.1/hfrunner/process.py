from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from datasets import load_dataset
from evaluate import load

def generate(text, model, tokenizer, config):
  tokens = tokenizer.encode(text, return_tensors='pt').to(config['device'])
  respose = model.generate(tokens, max_length=20)
  return tokenizer.decode(respose[0], skip_special_tokens=True)



def batch_tokenize(batch, tokenizer, config):
    """Construct the batch (source, target) and run them through a tokenizer."""
    source = batch[config['dataset']['input_column']]
    target = batch[config['dataset']['target_column']]
    src_tokenized = tokenizer(source, truncation=True)
    with tokenizer.as_target_tokenizer():
        trg_tokenized = tokenizer(target, truncation=True)
    res = {
        "input_ids": src_tokenized["input_ids"],
        "attention_mask": src_tokenized["attention_mask"],
        "labels": trg_tokenized["input_ids"],
    }
    return res

def tokenize(dataset, tokenizer, config):
    return dataset.map(
        lambda batch: batch_tokenize(batch, tokenizer, config),
        batched=True
    )
