"""
This script is used to extract all the register address, bank and other
details mentioned in `src/mu_1sf_driver.c`. To re-generate the data
copy this file to `src/` and run `python3 c_parser.py`. The data is saved
as a pickle object in `src/` as `mu_1sf_driver_registers_data.pkl`. Copy
this pickle file to `gui/` and re-start the GUI application.
"""

from pprint import pprint
import re
import pickle

def parse_c_file(file_path):
    struct_dict = {}

    with open(file_path, 'r') as file:
        file_content = file.read()

        # Regular expression pattern to match struct declarations and initializations
        pattern = r'const struct mu_param\s+(\w+)\s*=\s*{\s*(.*?)\s*};'

        matches = re.findall(pattern, file_content, re.DOTALL)
        #pprint(matches)

        pattern = r'\.(\w+)\s*=\s*({[^}]+}|\d+|0x[\da-fA-F]+)'

        for register_name, register_details in matches:
            # Convert to dictionary
            result = {}
            matches = re.findall(pattern, register_details)
            #pprint(matches)
            for key, value in matches:
                if key == 'addr':
                    value = [x.strip() for x in value.strip('{}').split(',')]
                result[key] = value
            struct_dict[register_name] = result

    return struct_dict


# # Usage example
file_path = 'mu_1sf_driver.c'
result = parse_c_file(file_path)
pprint(result)

with open('mu_1sf_driver_registers_data.pkl', 'wb') as f:
    pickle.dump(result, f)



