from typing import List, Optional


def enforce_type(aname: str, item: any, tp: type | List[type]):
    if isinstance(tp, list):
        illegal = 0
        for typ in tp:
            if not isinstance(item, typ):
                illegal += 1
        
        if illegal == len(tp):
            raise TypeError(f"attribute '{aname}' accepts only from types {tp}")
    else:
        if not isinstance(item, tp):
            raise TypeError(f"attribute '{aname}' accepts only from type {tp}")
    
    return item