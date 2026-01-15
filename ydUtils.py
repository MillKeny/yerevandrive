def check_suffix(text, suffix):
    return text.lower().endswith(suffix)

def check_suffix_list(text, list):
    for i in list:
        if text.lower().endswith(i): return True
    return False