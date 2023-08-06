import re

from sciform.modes import PrecMode, SignMode
from sciform.format_utils import (get_round_digit, get_top_and_bottom_digit,
                                  get_top_digit, get_mantissa_exp)
from sciform.format_spec import parse_format_spec, pattern, FormatSpec
from sciform.sfloat import format_float
from sciform.prefix import replace_prefix


def format_val_unc(val: float, unc: float, fmt: str):
    format_spec = parse_format_spec(fmt)
    match = re.match(pattern, fmt)
    if match.group('width'):
        match_widths = True
    else:
        match_widths = False

    unc = abs(unc)

    if format_spec.percent_mode:
        val *= 100
        unc *= 100

    val_mantissa, exp = get_mantissa_exp(
        val, format_mode=format_spec.format_mode, exp=format_spec.exp,
        alternate_mode=format_spec.alternate_mode)
    unc_mantissa, _ = get_mantissa_exp(
        unc, format_mode=format_spec.format_mode, exp=exp,
        alternate_mode=format_spec.alternate_mode)
    unc_top_digit, unc_bottom_digit = get_top_and_bottom_digit(unc_mantissa)
    round_digit = get_round_digit(unc_top_digit, unc_bottom_digit,
                                  format_spec.prec, format_spec.prec_mode)

    prec = -round_digit

    user_top_digit = format_spec.top_dig_place

    if match_widths:
        val_top_digit = get_top_digit(val_mantissa)
        new_top_digit = max(user_top_digit, val_top_digit, unc_top_digit)
    else:
        new_top_digit = user_top_digit

    val_format_spec = FormatSpec(
        format_spec.fill_mode,
        sign_mode=format_spec.sign_mode,
        alternate_mode=format_spec.alternate_mode,
        top_dig_place=new_top_digit,
        thousands_separator=format_spec.thousands_separator,
        decimal_separator=format_spec.decimal_separator,
        thousandths_separator=format_spec.thousandths_separator,
        prec_mode=PrecMode.PREC,
        prec=prec,
        format_mode=format_spec.format_mode,
        capital_exp_char=format_spec.capital_exp_char,
        percent_mode=False,
        exp=exp,
        prefix_mode=False)

    unc_format_spec = FormatSpec(
        format_spec.fill_mode,
        sign_mode=SignMode.NEGATIVE,
        alternate_mode=format_spec.alternate_mode,
        top_dig_place=new_top_digit,
        thousands_separator=format_spec.thousands_separator,
        decimal_separator=format_spec.decimal_separator,
        thousandths_separator=format_spec.thousandths_separator,
        prec_mode=PrecMode.PREC,
        prec=prec,
        format_mode=format_spec.format_mode,
        capital_exp_char=format_spec.capital_exp_char,
        percent_mode=False,
        exp=exp,
        prefix_mode=False)

    val_exp_pattern = re.compile(r'^(?P<val_str>.*?)(?P<exp_str>[eEbB].*?)?$')

    val_str = format_float(val, val_format_spec)
    val_match = val_exp_pattern.match(val_str)
    val_str = val_match.group('val_str')
    exp_str = val_match.group('exp_str')

    unc_str = format_float(unc, unc_format_spec)
    unc_match = val_exp_pattern.match(unc_str)
    unc_str = unc_match.group('val_str')
    val_unc_str = f'{val_str} +/- {unc_str}'

    if exp_str is not None:
        val_unc_exp_str = f'({val_unc_str}){exp_str}'
    else:
        val_unc_exp_str = val_unc_str

    if format_spec.prefix_mode:
        val_unc_exp_str = replace_prefix(val_unc_exp_str)

    if format_spec.percent_mode:
        result_str = f'({val_unc_exp_str})%'
    else:
        result_str = val_unc_exp_str

    return result_str
