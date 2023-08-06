from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from datasets import load_dataset
from evaluate import load
import torch

from hfrunner.loaders import load_model_and_tokenizer, load_ds, rouge_metrics_scorer
from hfrunner.process import tokenize


def train(model, train_tok, val_tok, rouge_fn, tokenizer, config):
    train_args = Seq2SeqTrainingArguments(
        output_dir=config['project_name'],
        evaluation_strategy="steps",
        save_strategy="steps",
        logging_strategy="steps",
        logging_steps=config['logging']['steps'],
        save_total_limit=config['save_limit'],
        # optimization args, the trainer uses the Adam optimizer
        # and has a linear warmup for the learning rate
        per_device_train_batch_size=config['training']['batch_size'],
        per_device_eval_batch_size=config['evaluation']['batch_size'],
        gradient_accumulation_steps=1,
        learning_rate=config['training']['lr'],
        num_train_epochs=config['training']['num_train_epochs'],
        warmup_steps=config['training']["warmup_steps"],
        # misc args
        report_to=config['logging']['report_to'],
        seed=config['seed'],
        disable_tqdm=False,
        load_best_model_at_end=True,
        metric_for_best_model=config['metric_for_best_model'],
        # generation
        predict_with_generate=True,
        generation_max_length=config['generation']['max_length'],
        include_inputs_for_metrics=True
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=train_args,
        train_dataset=train_tok,
        eval_dataset=val_tok,
        tokenizer=tokenizer,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer),
        compute_metrics=rouge_fn
    )
    trainer.train()

def run(config):
    model, tokenizer = load_model_and_tokenizer(config)
    train_df, val_df = load_ds(config)
    train_tok = tokenize(train_df, tokenizer, config)
    val_tok = tokenize(val_df, tokenizer, config)
    rouge_fn = rouge_metrics_scorer(tokenizer)
    train(
        model,
        train_tok,
        val_tok,
        rouge_fn,
        tokenizer,
        config
    )
