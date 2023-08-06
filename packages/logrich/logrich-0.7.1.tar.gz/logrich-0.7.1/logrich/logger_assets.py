from __future__ import annotations

import datetime
from typing import Any

import loguru

from rich.highlighter import ReprHighlighter, _combine_regex as combine_regex
from rich.theme import Theme
from rich.table import Table
from rich.console import Console
from logrich.config import config


console = Console()


class MyReprHighlighter(ReprHighlighter):
    """подсветка вывода на основе регул. выражений"""

    # https://regex101.com/r/zR2hP5/1
    base_style = "repr."
    highlights = [
        r"'(?P<str>[\S\s]*)'",
        r":\s\'(?P<value>.+)\'",
        r"['](?P<string_list_tuple>\w+)[']",
        r"(?P<digit2>\d*)[\"\s,[,(](?P<digit>\d*\.?\s?-?\d*-?\.?\d+)",
        combine_regex(
            r"(?P<brace>[][{}()])",
            r"\'(?P<key>[\w-]+)\'(?P<colon>:)",
            r"(?P<comma>,)\s",
        ),
        r"(?P<quotes>\')",
        r"(?P<equal>=)",
        r"(?P<class_name>[A-Z].*)\(",
        r'(?P<attrib_name>[\w_]{1,50})=(?P<attrib_value>"?[\w_]+"?)?',
        r"\b(?P<bool_true>True)\b|\b(?P<bool_false>False)\b|\b(?P<none>None)\b",
    ]


color_of_digit = "bold magenta"

theme = Theme(
    # https://www.w3schools.com/colors/colors_picker.asp
    # https://htmlcolorcodes.com/color-names/
    # https://colorscheme.ru/
    {
        "repr.brace": "bold black",
        "repr.str": "green",
        "repr.attrib_name": "#0099ff",
        "repr.equal": "red dim",
        "repr.digit": color_of_digit,
        "repr.digit2": color_of_digit,
        "repr.colon": "#D2691E",
        "repr.quotes": "#778899",
        "repr.comma": "#778899",
        "repr.key": "#08e8de",
        "repr.bool_true": "bold blue",
        "repr.none": "blue",
        "repr.bool_false": "yellow",
        "repr.class_name": "magenta bold",
        "repr.string_list_tuple": "green",
        "trace_msg": "#05a7f7",
        "debug_msg": "#e64d00",
        "info_msg": "#33ccff",
        "success_msg": "green",
        "warning_msg": "yellow",
        "error_msg": "#ff5050",
        "critical_msg": "#de0b2e",
    }
)

theme_fmt = {
    "trace": "reverse #0b66de",
    "debug": "#182D0B on #9F2844",
    "info": "reverse blue",
    "success": "reverse green",
    "warning": "reverse yellow",
    "foobar": "reverse yellow",
    "error": "red bold reverse",
    "critical": "reverse #de0b2e",
}

# инстанс консоли rich
console_dict = Console(
    highlighter=MyReprHighlighter(),
    theme=theme,
    markup=True,
    log_time=False,
    log_path=False,
    safe_box=True,
)


def print_message_for_table(message: Any) -> str:
    # инстанс консоли rich
    console2 = Console(
        no_color=True,
        markup=False,
        safe_box=True,
        highlight=False,
    )

    with console2.capture() as capture:
        console2.print(
            message,
            markup=False,
            width=80,
        )
    return capture.get()


def print_tbl(
    level: loguru.RecordLevel,
    message: str,
    file: loguru.RecordFile,
    line: int,
    style: str,
) -> str:
    """Форматирует вывод логгера в табличном виде"""
    table = Table(
        highlight=True,
        show_header=False,
        padding=0,
        collapse_padding=True,
        show_edge=False,
        show_lines=False,
        show_footer=False,
        expand=True,
        box=None,
    )
    # LEVEL
    table.add_column(
        justify="left",
        min_width=config.MIN_WIDTH_COMPUTED,
        max_width=config.MAX_WIDTH,
    )
    # MESSAGE
    table.add_column(ratio=config.RATIO_MAIN, overflow="fold", style=f"{level.name.lower()}_msg")
    # FILE
    table.add_column(justify="right", ratio=config.RATIO_FROM, overflow="fold")
    # LINE
    table.add_column(ratio=2, overflow="crop")  # для паддинга справа
    record_time = ""
    if config.LOGURU_DATETIME_SHOW:
        time_ = datetime.datetime.now()
        record_time = f"\n[#00FA9A r not b] {time_.strftime(config.LOGURU_DATETIME_FORMAT)} [/]"
    table.add_row(
        f"[{theme_fmt.get(style)}] {level:<9}[/]{record_time}",
        f"{message}",
        f"[#858585]{file}...[/][#eb4034]{line}[/]",
    )
    with console.capture() as capture:
        console_dict.print(table, markup=True)
    return capture.get()


def format_extra_obj(message: Any) -> str:
    """форматирует вывод исключений в цвете и в заданной ширине, исп-ся rich"""
    table = Table(
        padding=(0, 2),
        highlight=True,
        show_footer=False,
        box=None,
    )

    table.add_column()

    # MESSAGE
    table.add_row(print_message_for_table(message=message))

    with console.capture() as capture2:
        console_dict.print(table, markup=True)
    return capture2.get()
