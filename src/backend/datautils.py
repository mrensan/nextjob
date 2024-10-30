def flatten_dict(d, parent_key=''):
    """Flatten a dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key).items())
        elif isinstance(v, list):
            for index, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{index}]").items())
                else:
                    items.append((f"{new_key}[{index}]", str(item)))
        else:
            items.append((new_key, str(v)))
    return dict(items)
