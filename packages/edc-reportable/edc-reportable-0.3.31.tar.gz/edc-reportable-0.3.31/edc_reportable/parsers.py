import re
from collections import OrderedDict
from typing import Optional, Tuple

from edc_constants.constants import FEMALE, MALE

from .adult_age_options import adult_age_options
from .constants import LLN, ULN


class ParserError(Exception):
    pass


def unparse(**kwargs) -> str:
    lower = kwargs.get("lower") or ""
    upper = kwargs.get("upper") or ""
    lower_op = "" if not lower else "<=" if kwargs.get("lower_inclusive") else "<"
    upper_op = "" if not upper else "<=" if kwargs.get("upper_inclusive") else "<"
    gender = kwargs.get("gender", "")
    age_lower = kwargs.get("age_lower", "")
    age_upper = kwargs.get("age_upper", "")
    age_lower_op = "" if not age_lower else "<=" if kwargs.get("age_lower_inclusive") else "<"
    age_upper_op = "" if not age_upper else "<=" if kwargs.get("age_upper_inclusive") else "<"
    age = (
        ""
        if not age_lower and not age_upper
        else f"{age_lower}{age_lower_op}AGE{age_upper_op}{age_upper}"
    )
    try:
        fasting = kwargs.pop("fasting")
    except KeyError:
        fasting_str = ""
    else:
        fasting_str = "Fasting " if fasting else ""
    return f"{lower}{lower_op}x{upper_op}{upper} {fasting_str}{gender} {age}".rstrip()


def parse(phrase: Optional[str] = None, *, fasting=None, uln=None, lln=None, **kwargs) -> dict:
    pattern = r"(([\d+\.\d+]|[\.\d+])?(<|<=)?)+x((<|<=)?([\d+\.\d+]|[\.\d+])+)?"
    lln = f"*{LLN}"
    uln = f"*{ULN}"

    def _parse(string: str) -> Tuple[str, Optional[bool]]:
        inclusive = True if "=" in string else None
        try:
            value = float(
                string.replace("<", "").replace("=", "").replace(lln, "").replace(uln, "")
            )
        except ValueError:
            value = None
        if lln in string:
            value = f"{value}{lln}"
        elif uln in string:
            value = f"{value}{uln}"
        return value, inclusive

    phrase = phrase.replace(" ", "")
    match = re.match(pattern, phrase.replace(lln, "").replace(uln, ""))
    if not match or match.group() != phrase.replace(lln, "").replace(uln, ""):
        raise ParserError(
            f"Invalid. Got {phrase}. Expected, e.g, 11<x<22, "
            "11<=x<22, 11<x<=22, 11<x, 11<=x, x<22, x<=22, etc."
        )
    left, right = phrase.replace(" ", "").split("x")
    lower, lower_inclusive = _parse(left)
    upper, upper_inclusive = _parse(right)
    fasting = True if fasting else False
    ret_as_dict = OrderedDict(
        lower=lower,
        lower_inclusive=lower_inclusive,
        upper=upper,
        upper_inclusive=upper_inclusive,
        fasting=fasting,
        **kwargs,
    )
    for k, v in ret_as_dict.items():
        setattr(ret_as_dict, k, v)
    return ret_as_dict


def parse_boundary(value: str) -> Tuple[Optional[float], Optional[float]]:
    uln = lln = None
    value = value.upper()
    pattern = r"(\d+\.\d+)\*[LLN|ULN]"
    if not re.match(pattern, value):
        raise ParserError(f"Invalid value. Got {value}")
    else:
        value, limit_normal = value.split("*")
        if limit_normal == LLN:
            lln = float(value)
        elif limit_normal == ULN:
            uln = float(value)
    return lln, uln


def dummy_parse(phrase: Optional[str] = None, units: Optional[str] = None) -> dict:
    return parse(
        phrase or "0<=x",
        units=units,
        gender=[MALE, FEMALE],
        **adult_age_options,
    )
