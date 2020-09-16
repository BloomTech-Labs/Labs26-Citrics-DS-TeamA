import sys

# Function to sanitize input string (cityname param)
def smart_upper(x):
    """"
    Upper case the first letter of a string, as well as
    any letters directly following a space.

    Input: x: lowercase str (e.g. 'new york')

    Returns: new_string: str (e.g. 'New York')
    """
    
    x = x.lower()
    
    # Can start by splitting the string
    split_str = x.split()

    if len(split_str) == 1:
        
        first_letter = split_str[0][0]

        # If no space was in string, simply uppercase the first letter
        first_letter = first_letter.upper()
        new_string = first_letter + x[1:]

        return new_string

    # Empty array for "word basket"
    wb = []

    # Iterate through words in `split_str`
    for v in split_str:
        # Recursive `smart_upper` call for each word
        v = smart_upper(v)
        wb.append(v)

    # Join smart-uppercased words in word basket
    return " ".join(wb)

if __name__ == "__main__":
    
    def test_smart_upper():

        input_string = input("Please enter a city name ('quit' to exit): ")

        if input_string.lower()[0:4] == "quit":
            sys.exit()

        print(smart_upper(input_string))

        return test_smart_upper()

    test_smart_upper()