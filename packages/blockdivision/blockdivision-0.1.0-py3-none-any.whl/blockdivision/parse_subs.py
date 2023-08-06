import pandas as pd


def sub_parse(data, sub_len):
    '''
    Args: 
    - data: json-файл с субтитрами
    - sub_len: кол-во объединений субтитров перед подачей в суммаризатор
    '''
    rows = []
    buffer = []
    for dct in data['events']:
        if 'segs' in dct:
            text = dct['segs'][0]['utf8']
            for i in range(1, len(dct['segs'])):
                text += dct['segs'][i]['utf8']
            start_time = dct['tStartMs']
            buffer.append({'start_time, ms': start_time, 'text': text})
            if len(buffer) == sub_len:
                txt = ''
                for i in range(len(buffer)):
                    txt += buffer[i]['text'] + ' '
                rows.append({'start_time, ms': buffer[0]['start_time, ms'], 'text': txt.replace('\n', '').strip()})
                buffer = []
        else:
            continue
    if len(buffer) <= sub_len:
        txt = ''
        for i in range(len(buffer)):
            txt += buffer[i]['text'] + ' '
        rows.append({'start_time, ms': buffer[0]['start_time, ms'], 'text': txt.replace('\n', '').strip()})

    df = pd.DataFrame(rows)

    return df
