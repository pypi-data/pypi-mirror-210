import pprint
import re
from typing import Callable

import zhipuai


def punctuation_converse_auto(msg):
    punkts = [
        [",", "，"],
        ["!", "！"],
        [":", "："],
        [";", "；"],
        ["\?", "？"],
    ]
    for item in punkts:
        msg = re.sub(r"([\u4e00-\u9fff])%s" % item[0], r"\1%s" % item[1], msg)
        msg = re.sub(r"%s([\u4e00-\u9fff])" % item[0], r"%s\1" % item[1], msg)
    return msg


def prepare_print_diff(nextStr: Callable[[any], str], printError: Callable[[], None]):
    previous = ""

    def print_diff(input):
        nonlocal previous
        str = nextStr(input)
        if not str.startswith(previous):
            last_line_index = str.rfind("\n") + 1
            if previous.startswith(str[0:last_line_index]):
                print("\r%s" % str[last_line_index:], end="", flush=True)
            else:
                print()
                print(1, "[[previous][%s]]" % previous)
                printError(input)
        else:
            print(str[len(previous):], end="", flush=True)
        previous = str

    return print_diff


if __name__ == "__main__":
    zhipuai.api_key = "98ecb12669e4427983de959c0a22061a.77f995116150f600"
    zhipuai.api_base = "https://test-maas.aminer.cn/stage-api/paas/v3/model-api"
    '''
    response = zhipuai.APIResource.query_async_invoke_result("1014907516268634316357633")
    print(response)
   
    response = zhipuai.APIResource.invoke(
        model="title-creation",
        prompt="新闻 炸裂",
        topP=1,
        topK=3,
        temperature=1,
        presencePenalty=1,
        frequencyPenalty=1,
        generatedLength=128,
    )

    print(response)


    '''

client = zhipuai.APIResource.invoke(
    model="example-model",
    prompt="人工智能"
)
print(client)
