def deunderscore(string: str):
    list_ = list(string)
    for i in range(len(list_)):
        if list_[i] == "_":
            list_[i] = " "

    new_string = ""
    for char in list_:
        new_string += char
    
    return new_string

if __name__ == "__main__":
    print(deunderscore("Salt_Lake_City"))