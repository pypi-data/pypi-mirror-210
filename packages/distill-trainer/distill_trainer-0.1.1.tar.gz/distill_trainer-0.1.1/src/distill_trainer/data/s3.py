from pathlib import Path

import boto3
from transformers import (
    TrainingArguments,
    TrainerCallback,
    TrainerControl,
    TrainerState
)


class S3UploadCallback(TrainerCallback):
    def __init__(self, bucket_name, model_prefix):
        self.bucket_name = bucket_name
        self.model_prefix = model_prefix
        self.s3 = boto3.client("s3")

    def on_save(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs
    ):
        if state.is_world_process_zero:
            model_dir = Path(args.output_dir)
            for file_path in model_dir.glob('*'):
                s3_key = f"{self.model_prefix}/{file_path.name}"
                self.s3.upload_file(str(file_path), self.bucket_name, s3_key)
