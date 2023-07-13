from api.csv_api import CsvAPI


# This file is for test purposes. You can find the real (solidity) version to be 
# imported by the receivers here:

# this algorithm only works for a specific letter-number relationship convention

# words_helper only works for homogenous _input lists (either only numbers or only words)


def single_number_to_text(_input: int):
    number = _input
    
    alphabet = {
    '11': 'a',
    '12': 'b',
    '13': 'c',
    '14': 'd',
    '15': 'e',
    '16': 'f',
    '17': 'g',
    '18': 'h',
    '19': 'i',
    '20': 'j',
    '21': 'k',
    '22': 'l',
    '23': 'm',
    '24': 'n',
    '25': 'o',
    '26': 'p',
    '27': 'q',
    '28': 'r',
    '29': 's',
    '30': 't',
    '31': 'u',
    '32': 'v',
    '33': 'w',
    '34': 'x',
    '35': 'y',
    '36': 'z',
    #'37': 'ä',
    #'38': 'ö',
    #'39': 'ü',
    '40': '!',
    '41': '@',
    '42': '#',
    '43': '$',
    '44': '%',
    '45': '&',
    '46': '*',
    '47': '(',
    '48': ')',
    '49': '-',
    '50': '+',
    '51': '/',
    '52': '?',
    '53': ':',
    '54': ';',
    '55': '<',
    '56': '>',
    '57': '[',
    '58': ']',
    '59': '{',
    '60': '}',
    '61': '=',
    '62': '|',
    '63': '~',
    '64': '_',
    '65': '`',
    '66': ' ',
    '67': '^',
    '68': '0',
    '69': '1',
    '70': '2',
    '71': '3',
    '72': '4',
    '73': '5',
    '74': '6',
    '75': '7',
    '76': '8',
    '77': '9'
}
    # Add more keys and values as needed


    word = ""
    for i, bla in enumerate(str(number)):
        if i % 2 == 0:
            digit = str(str(number)[i]) + str(str(number)[i+1])
            letter = alphabet[digit]
            word += letter

    return word


if __name__ == '__main__':
    obj = CsvAPI()
    print()
    print("input example: '<csv_file_path>,True,2,2'")
    input_number = obj.get_data(input())[0]
    print(input_number)
    print(single_number_to_text(input_number))
    print()
    


