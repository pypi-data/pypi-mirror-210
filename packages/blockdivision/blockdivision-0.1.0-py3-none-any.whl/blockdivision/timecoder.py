from sentence_transformers import SentenceTransformer
from gpt_shortening import summarization
import pandas as pd
import json
from sentence_similarity import similarity
from parse_subs import sub_parse


with open('../data/dataset/tmp/subs.json', 'r') as file:
    data = json.load(file)

example_len = 12 # кол-во предложений для проверки работы пайплайна
df = sub_parse(data, sub_len=6)
df_shortened = df.iloc[:example_len, :]
print(df_shortened)

first_summarization = False # если True, то сначала суммаризуем потом считаем similarity score. В обратном случае - наоборот

if first_summarization:
    summarized_df = summarization(df_shortened, embeddings=True)

    sentences_smrzd = []
    time_start = df.iloc[:example_len, 0].to_list()
    sentences = summarized_df.iloc[:example_len, 1].to_list()

    model = SentenceTransformer('symanto/sn-xlm-roberta-base-snli-mnli-anli-xnli')

    similarities, timecodes = similarity(sentences, model, time_start, 0.18)

    print(similarities)
    print()
    print(timecodes)
    
else:
    time_start = df_shortened.iloc[:, 0].to_list()
    sentences = df_shortened.iloc[:, 1].to_list()
    model = SentenceTransformer('symanto/sn-xlm-roberta-base-snli-mnli-anli-xnli')

    similarities, timecodes = similarity(sentences, model, time_start, 0.18)
    print(similarities)
    print(timecodes)
    blocks = []
    i = 0
    for t in timecodes:
        text = ''
        while df_shortened.iloc[i, 0] < t:
            text += df.iloc[i, 1] + ' '
            i += 1
        blocks.append({'text': text})
    
    new_df = pd.DataFrame(blocks)
    summarized_df = summarization(new_df)
    print(summarized_df)
