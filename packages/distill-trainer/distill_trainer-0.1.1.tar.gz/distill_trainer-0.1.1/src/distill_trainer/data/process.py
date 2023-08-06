def tokenize_and_process_dataset(dataset, teacher_tokenizer):
    def process(examples):
        tokenized_inputs = teacher_tokenizer(
            examples["sentence"], truncation=True, max_length=512
        )
        return tokenized_inputs

    tokenized_datasets = dataset.map(process, batched=True)
    tokenized_datasets = tokenized_datasets.rename_column("label", "labels")

    labels = tokenized_datasets["train"].features["labels"].names
    num_labels = len(labels)
    label2id, id2label = dict(), dict()

    for id, label in enumerate(labels):
        label2id[label] = str(id)
        id2label[str(id)] = label

    return tokenized_datasets, num_labels, label2id, id2label
