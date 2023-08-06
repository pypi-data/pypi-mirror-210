#!/usr/bin/env python
# csv_embeddings_creator.py
import argparse
import csv
import glob
import os
import re
from concurrent.futures import ThreadPoolExecutor
from time import time

import torch
from sentence_transformers import SentenceTransformer

DEFAULT_NUM_THREADS = 4
sentence_transformer = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def find_pattern(pattern, path):
    match = re.search(pattern, path)
    return match.group(0) if match else ''


def encode_row(row, model):
    embedding_input = '"' + '","'.join(row) + '"'
    embeddings = model.encode(embedding_input)
    return row, embeddings


def create_embeddings(input_folder, output_txt_folder, output_embeddings_folder, force=False,
                      num_threads=DEFAULT_NUM_THREADS):
    os.makedirs(output_txt_folder, exist_ok=True)
    os.makedirs(output_embeddings_folder, exist_ok=True)

    csv_files = glob.glob(os.path.join(input_folder, '**/*.csv'), recursive=True)
    embedding_files = glob.glob(os.path.join(output_embeddings_folder, '**/*.pt'), recursive=True)

    dic_skip_done_doc_id = {}
    if not force:
        for path in embedding_files:
            dic_skip_done_doc_id[find_pattern('doc-id_(.*?)_sha', path)] = True

    i = 0
    for csv_file in csv_files:
        if find_pattern('doc-id_(.*?)_sha', csv_file) in dic_skip_done_doc_id:
            continue
        file_base_name = os.path.splitext(os.path.basename(csv_file))[0]
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)

            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                all_embeddings = list(executor.map(lambda row: encode_row(row, sentence_transformer), reader))

            for idx, (row, row_embeddings) in enumerate(all_embeddings):
                i += 1
                folder_txt = os.path.join(output_txt_folder, f"{file_base_name}")
                os.makedirs(folder_txt, exist_ok=True)
                txt_file = os.path.join(folder_txt, f"{file_base_name}_{idx + 1}.txt")
                with open(txt_file, 'w', encoding='utf-8') as txt_f:
                    txt_f.write('"' + '","'.join(row) + '"')

                folder_embeddings = os.path.join(output_embeddings_folder, f"{file_base_name}")
                os.makedirs(folder_embeddings, exist_ok=True)
                embeddings_file = os.path.join(folder_embeddings, f"{file_base_name}_{idx + 1}.pt")
                torch.save(row_embeddings, embeddings_file)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Create embeddings for text files using Hugging Face Transformers.')
    parser.add_argument('--input-folder', type=str, required=True,
                        help='Input folder containing CSV files')
    parser.add_argument('--output-txt-folder', type=str, required=True,
                        help='Output folder for the txt files')
    parser.add_argument('--embeddings-folder', type=str, required=True,
                        help='Output folder for the embeddings')
    parser.add_argument('--force', action='store_true',
                        help='Force to recreate embeddings even if they already exist')
    parser.add_argument('--num-threads', type=int, default=DEFAULT_NUM_THREADS,
                        help='Number of threads')
    return parser.parse_args()


def main():
    args = parse_arguments()
    create_embeddings(args.input_folder, args.output_txt_folder, args.embeddings_folder, args.force, args.num_threads)


if __name__ == '__main__':
    main()
