from typing import Any, Callable, Optional
import nonebot

from nonebot.plugin import on_command
from nonebot.adapters.cqhttp import Bot, MessageEvent

from enum import Enum
from dataclasses import dataclass

import os
import json

from userlib.plugin import PluginInfo

export = nonebot.export()
export.info = PluginInfo(
    "Template Generator",
    "模板生成器",
    "[添加模板] 添加模板 <模板名称>（换行）<模板内容（具体模板内容格式要求请发送该指令的无参数传入）>\n"
    "[修改模板] 修改模板 <模板 ID>（换行）<模板名称>（换行）<模板内容>\n"
    "[查看模板] 查看模板 [页数]\n"
    "[应用模板] 应用模板 <模板 ID>（换行）<模板参数（不定参数量，至少为 1 个，各参数间也需换行）>\n"
)

addTemplate = on_command("添加模板")
editTemplate = on_command("修改模板")
showTemplates = on_command("查看模板")
applyTemplate = on_command("应用模板")


class State(Enum):
    DEFAULT = 0
    BRACE = 1
    TRANSFERRING = 2


class TemplateItemKind(Enum):
    CONSTANT = 0
    REPLACEMENT = 1


@dataclass
class TemplateItem:
    Kind: TemplateItemKind
    Content: str


@dataclass
class Template:
    Name: str
    Items: list[TemplateItem]


class ParsingException(Exception):
    def __init__(self, innerException: Exception, column: int):
        self.InnerException = innerException
        super(ParsingException, self).__init__(
            "An exception was raised while parsing:\n{}"
            "\nPosition: Column {}.".format(str(innerException), column))


class InvalidTransferredTokenException(Exception):
    def __init__(self, token: str):
        super(InvalidTransferredTokenException, self).__init__(
            "Invalid Transferred Token \"{}\".".format(token))


class InvalidOperationException(Exception):
    def __init__(self, message: Optional[str] = None):
        if message is None:
            super(InvalidOperationException, self).__init__(
                "Invalid Operation.")
        else:
            super(InvalidOperationException, self).__init__(
                "Invalid Operation: {}".format(message))


class TemplateJsonEncoder(json.JSONEncoder):
    def default(self, o: Any):
        if isinstance(o, Template):
            return {
                "name": o.Name,
                "items": [{
                    "kind": item.Kind.value,
                    "content": item.Content
                } for item in o.Items]}
        else:
            return o


class TemplatesJsonDecoder(json.JSONDecoder):
    def decode(self, s: str, _w: Callable[..., Any] = ...):
        dics = json.loads(s)
        return [Template(
            dic["name"], [TemplateItem(
                TemplateItemKind(item["kind"]),
                item["content"]
            ) for item in dic["items"]]
        ) for dic in dics]


_translationDic = {'\\': '\\', '{': '{', '}': '}', 'n': '\n'}


def _parse(s: str) -> list[TemplateItem]:
    lastState = State.DEFAULT
    state = State.DEFAULT
    items = list[TemplateItem]()
    currentStr = ""

    for index, c in enumerate(s):
        if state != State.TRANSFERRING and c == '\\':
            lastState = state
            state = State.TRANSFERRING
            continue

        if state == State.DEFAULT:
            if c == '{':
                state = State.BRACE
                items.append(
                    TemplateItem(TemplateItemKind.CONSTANT, currentStr))
                currentStr = ""
            elif c == '}':
                raise ParsingException(InvalidOperationException(
                    "Unexpected token \"}\" when state is DEFAULT."
                ), index + 1)
            else:
                currentStr += c

        elif state == State.BRACE:
            if c == '}':
                state = State.DEFAULT
                items.append(
                    TemplateItem(TemplateItemKind.REPLACEMENT, currentStr))
                currentStr = ""
            elif c == '{':
                raise ParsingException(
                    InvalidOperationException(
                        "Unexpected token \"{\" when state is BRACE."
                    ), index + 1)
            else:
                currentStr += c

        elif state == State.TRANSFERRING:
            if c in _translationDic.keys():
                currentStr += _translationDic[c]
                state = lastState
                lastState = State.DEFAULT
            else:
                raise ParsingException(
                    InvalidTransferredTokenException(c), index + 1)

    if state != State.DEFAULT:
        raise ParsingException(
            InvalidOperationException(
                "State is not DEFAULT after parsing the last char."), len(s))

    if currentStr != "":
        items.append(TemplateItem(TemplateItemKind.CONSTANT, currentStr))

    return items


_filepath = "templates.json"


def _readFile() -> list[Template]:
    if os.path.exists(_filepath):
        try:
            with open(_filepath) as fp:
                templates = json.load(fp, cls=TemplatesJsonDecoder)
            return templates
        except json.JSONDecodeError:
            pass
    else:
        os.mknod(_filepath)

    return list[Template]()


_templates = _readFile()


def _writeFile(templates: list[Template]):
    with open(_filepath, "w") as fp:
        json.dump(templates, fp, cls=TemplateJsonEncoder)


def _splitMessage(message: str) -> list[str]:
    return list(filter(lambda s: s, message.replace("\r\n", "\n").split("\n")))


def _getTemplateReplacements(items: list[TemplateItem]) -> list[TemplateItem]:
    return [
        item for item in items if item.Kind == TemplateItemKind.REPLACEMENT
    ]


def _templateItemsToString(items: list[TemplateItem]) -> str:
    content = ""

    for item in items:
        if item.Kind == TemplateItemKind.CONSTANT:
            content += item.Content
        elif item.Kind == TemplateItemKind.REPLACEMENT:
            content += "(" + item.Content + ")"

    return content


def _templateReplacementsToString(replacements: list[TemplateItem]) -> str:
    return "".join("<" + item.Content + ">" for item in replacements)


def _tryParseToInt(s: str) -> Optional[int]:
    try:
        return int(s)
    except:
        return None


_pageItemCount = 8


@addTemplate.handle()
async def addTemplate_escape(bot: Bot, event: MessageEvent):
    strs = _splitMessage(event.message.extract_plain_text())

    if len(strs) != 2:
        await bot.send(event,
                       """[添加模板] 需要 2 个参数：<模板名称>（换行）<模板内容>

模板内容格式：无任何限定符号字符串 - 模板固定内容
限定符号{} - 指定模板可更改部分（{}内需填写该部分的描述）
转义符号\\ - 转义字符
支持转义：
\\\\ -> \\
\\{ -> {
\\} -> }
\\n -> (空行)

示例：

命令：
添加模板 Say Hello!
你好，{姓名}先生小姐

查看模板返回信息：模板 1. [Say Hello!] 需要 1 个参数：<姓名>""")
        return

    try:
        items = _parse(strs[1])
    except ParsingException as ex:
        await bot.send(event, "解析模板时出现错误：\n" + str(ex))
        return

    replacements = _getTemplateReplacements(items)
    replacementLength = len(replacements)

    if replacementLength < 1:
        await bot.send(event, "模板参数过少，至少需要 1 个参数")
        return

    template = Template(strs[0].strip(), items)

    _templates.append(template)
    _writeFile(_templates)

    await bot.send(event, "添加模板成功！模板预览：\n\n"
                   "查看模板返回信息：模板 {}. [{}] 需要 {} 个参数：{}\n"
                   "模板内容：{}".format(
                       len(_templates) - 1, template.Name, replacementLength,
                       _templateReplacementsToString(replacements),
                       _templateItemsToString(template.Items)))


@editTemplate.handle()
async def editTemplate_escape(bot: Bot, event: MessageEvent):
    strs = _splitMessage(event.message.extract_plain_text())

    if len(strs) != 3:
        await bot.send(event, "[修改模板] 需要 3 个参数：<模板 ID>（换行）"
                       "<模板名称>（换行）<模板内容>\n"
                       "（模板内容格式请参考 [添加模板] 指令）")
        return

    index = _tryParseToInt(strs[0])

    if index is None:
        await bot.send(event, "数字格式不正确")
        return

    if len(_templates) <= index:
        await bot.send(event, "对应模板不存在")
        return

    try:
        items = _parse(strs[2])
    except ParsingException as ex:
        await bot.send(event, "解析模板时出现错误：\n" + str(ex))
        return

    replacements = _getTemplateReplacements(items)
    replacementLength = len(replacements)

    if replacementLength < 1:
        await bot.send(event, "模板参数过少，至少需要 1 个参数")
        return

    template = Template(strs[1].strip(), items)

    _templates[index] = template
    _writeFile(_templates)

    await bot.send(event, "修改模板成功！模板预览：\n\n"
                   "查看模板返回信息：模板 {}. [{}] 需要 {} 个参数：{}\n"
                   "模板内容：{}".format(
                       len(_templates) - 1, template.Name, replacementLength,
                       _templateReplacementsToString(replacements),
                       _templateItemsToString(template.Items)))


@showTemplates.handle()
async def showTemplates_escape(bot: Bot, event: MessageEvent):
    strs = _splitMessage(event.message.extract_plain_text())

    async def showTemplates(pageIndex: int):
        index = pageIndex - 1
        pageLength = (len(_templates) // _pageItemCount) + 1

        if index > pageLength:
            await bot.send(event, "页数过大，总页数为：{}".format(pageLength))
            return
        elif index < 0:
            await bot.send(event, "页数过小")
            return

        start = index * _pageItemCount

        await bot.send(event, "\n".join(
            ("模板 {}. [{}] 需要 {} 个参数：{}"
             .format(start + index, template.Name, len(replacements),
                     _templateReplacementsToString(replacements))
             for (index, template, replacements) in (
                 (index, template, _getTemplateReplacements(template.Items))
                 for (index, template) in enumerate[Template](
                     _templates[start:start + _pageItemCount])))))

    length = len(strs)

    if length > 1:
        await bot.send(
            event, "[查看模板] 传入 0 个参数 - 显示第 1 页模板内容\n"
            "[显示模板] 传入 1 个参数：<页数> - 显示指定页数模板内容")
    elif length == 0:
        await showTemplates(1)
    elif length == 1:
        pageIndex = _tryParseToInt(strs[0])

        if pageIndex is None:
            await bot.send(event, "数字格式不正确")
            return

        await showTemplates(pageIndex)


@applyTemplate.handle()
async def applyTemplate_escape(bot: Bot, event: MessageEvent):
    strs = _splitMessage(event.message.extract_plain_text())
    length = len(strs)

    if length < 2:
        await bot.send(event, "[应用模板] 需要传入：<模板 ID>（换行）"
                       "<模板参数（不定参数量，至少为 1 个，各参数间也需换行）>")
        return

    index = _tryParseToInt(strs[0])

    if index is None:
        await bot.send(event, "数字格式不正确")
        return

    if len(_templates) <= index:
        await bot.send(event, "对应模板不存在")
        return

    template = _templates[index]

    replacements = _getTemplateReplacements(template.Items)
    replacementLength = len(replacements)

    if length < replacementLength + 1:
        await bot.send(event, "模板 [{}] 需要传入 {} 个参数：{}"
                       .format(template.Name, replacementLength,
                               _templateReplacementsToString(replacements)))
        return

    result = ""
    index = 1

    for item in template.Items:
        if item.Kind == TemplateItemKind.CONSTANT:
            result += item.Content
        elif item.Kind == TemplateItemKind.REPLACEMENT:
            result += strs[index]
            index += 1

    await bot.send(event, result)
