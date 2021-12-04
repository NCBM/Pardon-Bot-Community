from typing import Any, Optional
from ..translation import TranslatorBase, TranslatorConfigBase
from ..translation import TranslationError, TranslationResult

from hashlib import md5
from dataclasses import dataclass

import random
import httpx


@dataclass
class BaiduTranslatorConfig(TranslatorConfigBase):
    app_id: str
    app_key: str


class BaiduTranslator(TranslatorBase):
    _client = httpx.AsyncClient()
    config: BaiduTranslatorConfig

    def __init__(self, config: BaiduTranslatorConfig):
        self.config = config

    def _generate_sign(self, text: str, salt: int) -> str:
        raw = self.config.app_id + text + str(salt)\
            + self.config.app_key
        return md5(raw.encode('utf-8')).hexdigest()

    async def translate(
        self,
        text: str,
        dest_lang: str,
        src_lang: Optional[str] = None
    ) -> TranslationResult:
        salt = random.randint(32768, 65536)
        res = await BaiduTranslator._client.post(
            'https://api.fanyi.baidu.com/api/trans/vip/translate',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            params={
                'appid': self.config.app_id,
                'q': text,
                'from': 'auto' if src_lang is None else src_lang,
                'to': dest_lang,
                'salt': salt,
                'sign': self._generate_sign(text, salt)
            }
        )
        result: dict[str, Any] = res.json()

        if error_code := result.get('error_code'):
            raise BaiduTranslationError(int(error_code))

        result_text = '\n'.join(
            [item['dst'] for item in result['trans_result']]
        )

        return TranslationResult(
            result_text,
            result['from']
        )


class BaiduTranslationError(TranslationError):
    MESSAGE_FOR_CODE = {
        52000: '成功',
        52001: '请求超时',
        52002: '系统错误',
        52003: '未授权用户',
        54000: '必填参数为空',
        54001: '签名错误',
        54003: '访问频率受限',
        54004: '账户余额不足',
        54005: '长query请求频繁',
        58000: '客户端IP非法',
        58001: '译文语言方向不支持',
        58002: '服务当前已关闭',
        90107: '认证未通过或未生效'
    }

    @property
    def message(self):
        return BaiduTranslationError.MESSAGE_FOR_CODE.get(
            self.code, '未知错误: ' + str(self.code)
        )
