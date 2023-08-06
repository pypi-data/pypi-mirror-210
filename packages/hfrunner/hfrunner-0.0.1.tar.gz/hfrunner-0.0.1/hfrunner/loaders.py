from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from datasets import load_dataset
from evaluate import load
import numpy as np

def load_model_and_tokenizer(config):
    BASE_MODEL = config['model']

    model = AutoModelForSeq2SeqLM.from_pretrained(
        BASE_MODEL,
        load_in_8bit=config['load_in_8bit'],
        device_map="auto",
    )

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    return model, tokenizer

def load_ds(config):
    dataset = load_dataset(*(config['dataset']['name']))
    train_df = dataset['train'].remove_columns(config['dataset']['drop_columns'])
    val_df = dataset['validation'].remove_columns(config['dataset']['drop_columns'])
    return train_df, val_df

def rouge_metrics_scorer(tokenizer):
    rouge_scorer = load('rouge')

    def rouge_metric_builder(tokenizer):
        def compute_rouge_metrics(pred):
            """Utility to compute ROUGE during training."""
            labels_ids = np.array(pred.label_ids)
            pred_ids = np.array(pred.predictions)
            # All special tokens are removed.
            pred_ids[pred_ids == -100] = tokenizer.pad_token_id
            pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
            labels_ids[labels_ids == -100] = tokenizer.pad_token_id
            label_str = tokenizer.batch_decode(labels_ids, skip_special_tokens=True)
            # Compute the metric.
            rouge_results = rouge_scorer.compute(
                predictions=pred_str,
                references=label_str,
                rouge_types=["rouge2", "rougeL"],
                use_stemmer=False,
            )
            return {
                "rouge2": round(rouge_results['rouge2'], 4),
                "rougeL": round(rouge_results['rougeL'], 4),
            }
        return compute_rouge_metrics
    rouge_metric_fn = rouge_metric_builder(tokenizer)
    return rouge_metric_fn