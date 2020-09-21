

def smart_downer(string: str) -> str:
    """
    Sanitizes input to match the format used in
    csv files found in data/weather directory
    """
    list_  = list(string.lower())

    for i in range(len(list_)):
        if list_[i] == " ":
            list_[i] = "_" 
    
    return "".join(list_)

if __name__ == "__main__":
    print(smart_downer("china town"))
    print(len(smart_downer("china town")))