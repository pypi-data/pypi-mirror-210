import pandas as pd
from transformers import pipeline
from transformers import MBartTokenizer, MBartForConditionalGeneration


# model_checkpoint = "Helsinki-NLP/opus-mt-ru-en"
# translator = pipeline("translation", model=model_checkpoint)
# translated = translator('Иногда для достижения успеха людям надо прикладывать много усилий в различных сферах деятельности, но не надо пренебрегать и удачей, которая безусловно, необходима для достижения целей')
# print(translated)

# classifier = pipeline('summarization', model='apatidar0/t5-small-finetuned-amazon-en')

# res = classifier('summarize: ' + translated[0]['translation_text'])
# # outputs = classifier.generate(translated, max_new_tokens=100, do_sample=False)

# print(res)

def summarization(df, translation=False, embeddings=False):
    if translation:
        model_checkpoint = "Helsinki-NLP/opus-mt-ru-en"
        translator = pipeline("translation", model=model_checkpoint)
        classifier = pipeline('summarization', model='HUPD/hupd-t5-small')

        rows = []
        for text in df['text']:
            translated = translator(text)
            res = classifier(translated[0]['translation_text'])
            prefix = 'translation_text'
            rows.append({
                'raw sentence': text, 
                'translated sentence': {translated[0][prefix]}, 
                'summarized': res[0]['summary_text']
                })
        df = pd.DataFrame(rows)
    else:
        model_name = "IlyaGusev/mbart_ru_sum_gazeta"
        tokenizer = MBartTokenizer.from_pretrained(model_name)
        model = MBartForConditionalGeneration.from_pretrained(model_name)
        rows = []
        for text in df['text']: 
            input_ids = tokenizer(
                [text],
                max_length=600,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )["input_ids"]

            output_ids = model.generate(
                input_ids=input_ids,
                max_new_tokens=len(text)//2,
                # max_length=36,
                no_repeat_ngram_size=4,
                num_beams=5,
                top_k=0
            )[0]
            
            headline = tokenizer.decode(output_ids, skip_special_tokens=True)
            rows.append({
                'raw sentence': text, 
                'summarized': headline
                })
        df = pd.DataFrame(rows)
    return df
