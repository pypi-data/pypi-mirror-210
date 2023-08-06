#!/usr/bin/env python
# knowledgebase_gsheet_gpt.py
import argparse
import os

from time import time

import csv_embeddings_creator
import google_sheet_downloader
import openai_chat_thread
import similarity_ranker

DEFAULT_BEFORE_QUESTION_PROMPT = '\n-- the user question\n'
DEFAULT_BEFORE_KNOWLEDGE_PROMPT = '\n-- reference following knowledge base content to answer the user question (answer as long as possible)\n'
DEFAULT_MODEL = "gpt-4"
DEFAULT_TOP_N = 1
DEFAULT_KEY_FILE = "./keys/google_service_account_key.json"


class ChatMemory:
    def __init__(self, max_n=3):
        self.max_n = max_n
        self.user_dict = {}

    def append_context(self, user, text):
        if user not in self.user_dict:
            self.user_dict[user] = []
        self.user_dict[user].append(text)
        if len(self.user_dict[user]) > self.max_n:
            self.user_dict[user] = self.user_dict[user][-self.max_n:]

    def get_context(self, user):
        if user in self.user_dict:
            return '--\n'.join(self.user_dict[user])
        else:
            return ''


chat_memory = ChatMemory()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Knowledgebase GSheet GPT')
    parser.add_argument('--user', type=str, required=True, help='User email')
    parser.add_argument('--prompt', type=str, required=True, help='Prompt sentence for finding similar embeddings.')
    parser.add_argument('--sheet-ids', type=str, default="", help='Comma separated Google sheet IDs to download')
    parser.add_argument('--before-question-prompt', type=str, default=DEFAULT_BEFORE_QUESTION_PROMPT,
                        help='Text before the user question in the final prompt')
    parser.add_argument('--before-knowledge-prompt', type=str,
                        default=DEFAULT_BEFORE_KNOWLEDGE_PROMPT,
                        help='Text before the knowledge base content in the final prompt')
    parser.add_argument('--top-n', type=int, default=DEFAULT_TOP_N,
                        help='Number of top similar knowledge base texts to include in the final prompt')
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL,
                        help='gpt-3.5-turbo or gpt-4')
    parser.add_argument('--key-file', type=str, default=DEFAULT_KEY_FILE,
                        help='Google service account key JSON file path')
    return parser.parse_args()


def knowledgebase_gsheet_gpt(user, prompt,
                             sheet_ids="",
                             before_question_prompt=DEFAULT_BEFORE_QUESTION_PROMPT,
                             before_knowledge_prompt=DEFAULT_BEFORE_KNOWLEDGE_PROMPT,
                             top_n=DEFAULT_TOP_N,
                             model=DEFAULT_MODEL,
                             key_file=DEFAULT_KEY_FILE):
    os.environ["TOKENIZERS_PARALLELISM"] = "true"

    user = user.lower().replace('@', '_').replace('.', '_')
    data_folder = f'./data/users/{user}'

    # t = time()

    # Google Sheet Downloader
    if sheet_ids:
        google_sheet_downloader.download_google_sheets(
            key_file,
            sheet_ids,
            os.path.join(data_folder, 'google_sheet_downloader'),
            False
        )

    # print('time 001:', time() - t)
    # t = time()

    # CSV Embeddings Creator
    csv_embeddings_creator.create_embeddings(
        os.path.join(data_folder, 'google_sheet_downloader'),
        os.path.join(data_folder, 'csv_embeddings_creator', 'txt'),
        os.path.join(data_folder, 'csv_embeddings_creator', 'embeddings'),
        False
    )

    # print('time 002:', time() - t)
    # t = time()

    # Similarity Ranker
    ranking_result = similarity_ranker.query_embeddings(
        prompt,
        os.path.join(data_folder, 'csv_embeddings_creator', 'embeddings'),
        top_n
    )

    # print('time 003:', time() - t)
    # t = time()

    ranked_result = similarity_ranker.save_ranking_to_json(
        prompt,
        ranking_result,
        os.path.join(data_folder, 'csv_embeddings_creator', 'txt'),
        os.path.join(data_folder, 'similarity_ranker', 'similarity_ranker.json')
    )

    # print('time 004:', time() - t)
    # t = time()

    # Combine prompt with most similar sheet content
    knowledge_prompt = before_knowledge_prompt
    num_ranked_results = len(ranked_result['ranking'])
    top_n = min(top_n, num_ranked_results)

    # print('time 005:', time() - t)
    # t = time()

    for i in range(top_n):
        knowledge_prompt += f"{ranked_result['ranking'][i]['content']}"
        knowledge_prompt += '\n\n'

    knowledge_prompt += before_question_prompt
    knowledge_prompt += f"{prompt}\n"

    # print('time 006:', time() - t)
    # t = time()

    # print('knowledgebase_gsheet_gpt.py, knowledge_prompt:\n', knowledge_prompt)
    # chat_memory.append_context(user, knowledge_prompt)

    # print("knowledgebase_gsheet_gpt.py chat_memory.get_context(user):\n", chat_memory.get_context(user))
    # response_queue = openai_chat_thread.openai_chat_thread_taiwan(prompt=chat_memory.get_context(user), model=model)

    print('\nknowledgebase_gsheet_gpt.py, knowledge_prompt:\n', knowledge_prompt)

    # print('time 007:', time() - t)
    # t = time()

    response_queue = openai_chat_thread.openai_chat_thread_taiwan(prompt=knowledge_prompt, model=model)

    # print('time 008:', time() - t)
    # t = time()

    return response_queue


def main():
    arg = parse_arguments()
    response_stream = knowledgebase_gsheet_gpt(arg.user,
                                               arg.prompt,
                                               arg.sheet_ids,
                                               arg.before_question_prompt,
                                               arg.before_knowledge_prompt,
                                               arg.top_n,
                                               arg.model,
                                               arg.key_file
                                               )
    while True:
        response = response_stream.get()
        if response is None:
            break
        print(response, end="", flush=True)


if __name__ == '__main__':
    main()
