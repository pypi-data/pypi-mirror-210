# -*- coding:utf-8 -*-
import os

from zhipuai.api_resource import APIResource

api_base = os.environ.get(
    "ZHIPUAI_API_BASE", "https://open.bigmodel.cn/api/paas/v3/model-api"
)

api_key = os.environ.get("API_KEY")

api_token_ttl_seconds = 3 * 60  # default 3 minutes
