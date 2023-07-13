from api.randomorg_api import RandomOrgAPI
from api.csv_api import CsvAPI
from words_helper import single_number_to_text


# This file is for test purposes. You can find the real (solidity) version to be 
# imported by the receivers here: Contract/MainContract/contracts/multiple_number_helper.sol.


def split_up_number(_input):
    result = []

    # This whole process removes the metadata digits added onto our concatenated large integer added by the individual apis (that offer multiple datapoints).
    # It then splits the remaining concatenation back up into the originally ordered numbers.
    print("_input: ", _input)
    len_of_counter = _input % 10
    print("len_of_counter: ", len_of_counter)
    _input = _input // 10
    print("_input: ", _input)

    counter = _input % (10 ** len_of_counter)
    print("counter: ", counter)
    _input = _input // (10 ** len_of_counter)
    print("_input: ", _input)

    helper_digits = _input % (10 ** counter)
    print("helper_digits: ", helper_digits)
    _input = _input // (10 ** counter)
    print("_input: ", _input)


    for i in range (1, (counter + 1)):
        #print("i: ", i)
        helper_digit = helper_digits % 10
        #print("helper_digit: ", helper_digit)
        helper_digits = helper_digits // 10
        #print("helper_digits: ", helper_digits)

        number = _input % (10 ** helper_digit)
        _input = _input // (10 ** helper_digit)

        result.append(number)
        
    result.reverse()
    return result


def split_up_csv(_input):
    result = []

    # This whole process removes the metadata digits added onto our concatenated large integer added by the individual apis (that offer multiple datapoints).
    # It then splits the remaining concatenation back up into the originally ordered numbers.
    print("_input: ", _input)
    len_of_len_of_counter2 = _input % 10
    print("len_of_len_of_counter2: ", len_of_len_of_counter2)
    _input = _input // 10
    print("_input: ", _input)

    how_many_numbers_total = _input % (10 ** len_of_len_of_counter2)
    print("how_many_numbers_total: ", how_many_numbers_total)
    _input = _input // (10 ** len_of_len_of_counter2)
    print("_input: ", _input)

    alpha = _input % (10 ** how_many_numbers_total)
    print("alpha: ", alpha)
    _input = _input // (10 ** how_many_numbers_total)
    print("_input: ", _input)

    helper_digits2 = _input % (10 ** how_many_numbers_total)
    print("helper_digits2: ", helper_digits2)
    _input = _input // (10 ** how_many_numbers_total)
    print("_input: ", _input)

    len_of_helper_digits = 0
    for digit in str(helper_digits2):
        len_of_helper_digits += int(digit)
        print("digit: ", digit)
        print("len_of_helper_digits: ", len_of_helper_digits)

    helper_digits = _input % (10 ** len_of_helper_digits)
    print("helper_digits: ", helper_digits)
    _input = _input // (10 ** len_of_helper_digits)
    print("_input: ", _input)


    for i in range (1, (how_many_numbers_total + 1)):
        helper_digit2 = helper_digits2 % 10
        helper_digits2 = helper_digits2 // 10

        is_alpha = alpha % 10
        alpha = alpha // 10

        helper_digit = helper_digits % (10 ** helper_digit2)
        helper_digits = helper_digits // (10 ** helper_digit2)

        number = _input % (10 ** helper_digit)
        print("number: ", number)
        if is_alpha == 1:
            number = single_number_to_text(number)
        _input = _input // (10 ** helper_digit)
        print("_input: ", _input)

        result.append(str(number))
    
    result.reverse()
    return result


if __name__ == '__main__':
    #obj = RandomOrgAPI()
    #print()
    #print(split_up_number(obj.get_data("4,1,10000")[0]))
    #print()

    obj = CsvAPI()
    print()
    print("input example: '<csv_file_path>,True,3'")
    print(split_up_csv(obj.get_data(input())[0]))
    print()
