import re
import itertools
import typing as tp
from collections import deque

def parse_deleg(delegs):
    # e.g., activate@(hint[annotation])[FitzView]{SomeModel}
    alist=[]
    for deleg in delegs:
        data=deleg.split('@', 1)
        if len(data)==2:
            action=data[0]
            vimo=data[1]
            tags=parse_tag(vimo)
            for tag in tags:
                _, (mode, submode), (view, subview), (mdl, sbmdl) = tag
                alist+=[{
                    'action': action, 
                    'mode': mode,
                    'submode': submode,
                    'view': view,
                    'subview': subview,
                    'model': mdl,
                    'submodel': sbmdl,
                    }]
    return alist

def parse_tag(
    tags: tp.Union[str, tp.List[str]] = None,
) -> tp.List[tp.Tuple[str, str, str]]:
    parsed_tags = set()
    if type(tags) != list:
        tags = [tags,]
    for tag in tags:
        shortcut_key, mode_key, view_key, model_key = parse_parts(tag)
        key_part = parse_key(shortcut_key)
        mode_part = parse_vimo(mode_key)
        view_part = parse_vimo(view_key)
        model_part=parse_vimo(model_key)
        args = key_part, mode_part, view_part, model_part
        for i in itertools.product(*args):
            parsed_tags.add(i)
    return parsed_tags

def parse_parts(key: str) -> tp.Tuple[str]:
    rest_key: str = key[::-1]
    idx = getIndex(rest_key, opening="}", closing="{")
    if idx:
        model_key = rest_key[0 + 1 : idx][::-1]
        rest_key = rest_key[idx + 1 :]
    else:
        model_key = "any"
    idx = getIndex(rest_key, opening="]", closing="[")
    if idx:
        view_key = rest_key[0 + 1 : idx][::-1]
        rest_key = rest_key[idx + 1 :]
    else:
        view_key = "any"
    idx = getIndex(rest_key, opening=")", closing="(")
    if idx:
        mode_key = rest_key[0 + 1 : idx][::-1]
        rest_key = rest_key[idx + 1 :]
    else:
        mode_key = "any"
    shortcut_key=rest_key[::-1]
    return shortcut_key, mode_key, view_key, model_key

def parse_vimo(key: str) -> tp.List[tp.Tuple[str, str]]:
    klist = []
    alist = key.split("/")
    for key in alist:
        submode_key = None
        rest_key = key[::-1]
        idx = getIndex(rest_key, opening="]", closing="[")
        if idx:
            submode_key = rest_key[0 + 1 : idx][::-1]
            rest_key = rest_key[idx + 1 :]
            if submode_key=='None':
                submode_key=None
        else:
            submode_key = "any"
        sup = rest_key[::-1]
        klist += [(sup, submode_key)]
    return klist

def parse_key(key: str) -> tp.List[str]:
    if not "{" in key:
        return key.split("/")
    else:
        klist = []
        alist = key.split("}/{")
        for i in alist:
            klist += [re.sub("[{}]", "", i)]
        return klist

def getIndex(
    astring: str,
    idx: int = 0,
    opening: str = "[",
    closing: str = "]",
) -> tp.Union[int, None]:
    if astring[idx] != opening:
        return
    d = deque()
    for k in range(idx, len(astring)):
        if astring[k] == closing:
            d.popleft()
        elif astring[k] == opening:
            d.append(astring[idx])
        if not d:
            return k
