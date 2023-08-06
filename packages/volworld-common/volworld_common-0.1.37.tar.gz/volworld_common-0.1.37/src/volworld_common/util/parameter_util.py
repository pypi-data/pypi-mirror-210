from src.volworld_common.test.behave.BehaveUtil import BehaveUtil


def to_keyword_list(keywords: str) -> list:
    keywords = BehaveUtil.clear_string(keywords)
    keyword_raw_list = keywords.split(',')
    keyword_list = list()
    for k in keyword_raw_list:
        keyword_list.append(k.strip())
    # if len(keywords) == 0:
    #     keyword_list = None
    return keyword_list
