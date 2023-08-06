from typing import Optional
from dataclasses import dataclass
import re
from math import isfinite
import logging

from sciform.modes import FormatMode, PrecMode, SignMode, GroupingMode
from sciform.format_utils import (get_mantissa_exp, get_exp_str,
                                  get_top_and_bottom_digit,
                                  get_round_digit,
                                  format_float_by_top_bottom_dig)
from sciform.grouping import add_group_chars_float
from sciform.prefix import replace_prefix


logger = logging.getLogger(__name__)


@dataclass
class FormatSpec:
    fill_char: str = ''
    sign_mode: SignMode = SignMode.NEGATIVE
    force_zero_positive: bool = True
    alternate_mode: bool = False
    width: int = 0
    grouping_option_1: GroupingMode = GroupingMode.NO_GROUPING
    grouping_option_2: GroupingMode = GroupingMode.NO_GROUPING
    prec_mode: PrecMode = PrecMode.SIG_FIG
    precision: Optional[int] = None
    format_mode: FormatMode = FormatMode.FIXEDPOINT
    capital_exp_char: bool = False
    percent_mode: bool = False
    exp: Optional[int] = None
    prefix_mode: bool = False


pattern = re.compile(r'''^
                         (?:(?P<fill>[ 0])=)?
                         (?P<sign>[+\- ])?
                         (?P<pos_zero>z)?  
                         (?P<alternate>\#)?                         
                         (?P<width>\d+)?
                         (?P<grouping_option_1>[_,v])?                     
                         (?P<grouping_option_2>[_,v])?                     
                         (?:(?P<prec_mode>[.!])(?P<prec>-?\d+))?
                         (?P<format_mode>[fF%eErRbB])?
                         (?P<exp>[+-]\d+)?
                         (?P<prefix_mode>p)?
                         $''', re.VERBOSE)


def parse_format_spec(fmt: str) -> FormatSpec:
    # TODO: Catch more formatting errors as early as possible
    match = pattern.match(fmt)
    if match is None:
        raise ValueError(f'Invalid format specifier: \'{fmt}\'')

    fill = match.group('fill') or ' '

    sign_flag = match.group('sign') or '-'
    sign_mode = SignMode.from_flag(sign_flag)

    force_pos_zero = match.group('pos_zero') is not None

    alternate_mode = match.group('alternate') is not None

    width = match.group('width') or 0
    width = int(width)

    grouping_option_flag_1 = match.group('grouping_option_1') or ''
    grouping_option_1 = GroupingMode.from_flag(grouping_option_flag_1)

    grouping_option_flag_2 = match.group('grouping_option_2') or ''
    grouping_option_2 = GroupingMode.from_flag(grouping_option_flag_2)

    prec_mode_flag = match.group('prec_mode') or '.'
    prec_mode = PrecMode.from_flag(prec_mode_flag)

    prec = match.group('prec')
    if prec:
        prec = int(prec)
        if prec < 0 and prec_mode is PrecMode.SIG_FIG:
            raise ValueError(f'Invalid format specifier: \'{fmt}\'. Cannot '
                             f'specify negative number of significant '
                             f'figures.')

    format_mode_flag = match.group('format_mode') or 'f'
    format_mode = FormatMode.from_flag(format_mode_flag)
    capital_exp_char = format_mode_flag.isupper()
    percent_mode = format_mode_flag == '%'

    exp = match.group('exp')
    if exp is not None:
        exp = int(exp)

    prefix_mode = match.group('prefix_mode') is not None

    format_spec = FormatSpec(fill_char=fill,
                             sign_mode=sign_mode,
                             force_zero_positive=force_pos_zero,
                             alternate_mode=alternate_mode,
                             width=width,
                             grouping_option_1=grouping_option_1,
                             grouping_option_2=grouping_option_2,
                             prec_mode=prec_mode,
                             precision=prec,
                             format_mode=format_mode,
                             capital_exp_char=capital_exp_char,
                             percent_mode=percent_mode,
                             exp=exp,
                             prefix_mode=prefix_mode)

    return format_spec


def format_float(num: float, format_spec: FormatSpec) -> str:
    format_mode = format_spec.format_mode
    alternate_mode = format_spec.alternate_mode
    prec_mode = format_spec.prec_mode
    prec = format_spec.precision
    top_padded_digit = format_spec.width
    sign_mode = format_spec.sign_mode
    capital_exp_char = format_spec.capital_exp_char
    fill_char = format_spec.fill_char

    if not isfinite(num):
        if capital_exp_char:
            return str(num).upper()
        else:
            return str(num).lower()

    if format_spec.percent_mode:
        if format_spec.format_mode is not FormatMode.FIXEDPOINT:
            raise ValueError('Invalid format specifier')  # TODO better message
        num *= 100

    exp = format_spec.exp
    mantissa, exp = get_mantissa_exp(num, format_mode, exp, alternate_mode)
    exp_str = get_exp_str(exp, format_mode, capital_exp_char)

    if format_spec.force_zero_positive:
        if mantissa == -0.0:
            mantissa = abs(mantissa)

    top_digit, bottom_digit = get_top_and_bottom_digit(mantissa)
    round_digit = get_round_digit(top_digit, bottom_digit,
                                  prec, prec_mode)
    mantissa_str = format_float_by_top_bottom_dig(mantissa, top_padded_digit,
                                                  round_digit, sign_mode,
                                                  fill_char)
    grouping_char_1 = GroupingMode.to_char(format_spec.grouping_option_1)
    grouping_char_2 = GroupingMode.to_char(format_spec.grouping_option_2)
    mantissa_str = add_group_chars_float(mantissa_str, grouping_char_1,
                                         grouping_char_2,
                                         group_size=3)

    full_str = f'{mantissa_str}{exp_str}'

    if format_spec.prefix_mode:
        full_str = replace_prefix(full_str)

    if format_spec.percent_mode:
        full_str = full_str + '%'

    return full_str
