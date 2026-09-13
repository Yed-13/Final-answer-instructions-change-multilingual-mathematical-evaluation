"""Frozen numerical extraction for the prospective MGSM study, version 1.

Unlike the exploratory archive parser, this never searches for a last number.
"""
import re
import unicodedata
from decimal import Decimal, InvalidOperation


def final_number(text):
    if not isinstance(text,str):
        return None
    chars = []
    for c in unicodedata.normalize('NFKC',text):
        try:
            chars.append(str(unicodedata.decimal(c)))
        except (ValueError,TypeError):
            chars.append(c)
    text = ''.join(chars).strip().replace('\u066c',',').replace('\u066b','.')
    if '####' in text:
        text = text.rsplit('####',1)[1].strip()
    # An explicit final declaration or a bare number must cover the entire tail.
    if not re.fullmatch(r'[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?',text):
        return None
    try:
        return Decimal(text.replace(',',''))
    except InvalidOperation:
        return None


def score_record(call, response):
    if response is None:
        return {'status':'not_generated','prediction':None,'correct':None}
    if response.get('status') != 'success':
        return {'status':'generation_failed','prediction':None,'correct':None}
    if response.get('finish_reason') != 'eos':
        return {'status':'generation_truncated','prediction':None,'correct':None}
    number = final_number(response.get('response_text'))
    reference = final_number(call['reference'])
    if reference is None:
        raise ValueError('Invalid reference for '+call['call_id'])
    return {'status':'ok' if number is not None else 'answer_unparseable',
            'prediction':str(number) if number is not None else None,
            'correct':number == reference if number is not None else None}
