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

        for match in matches:
            struct_name, struct_content = match
            struct_dict[struct_name] = {}

            # Extract struct elements and their values
            element_pattern = r'\.(\w+)\s*=\s*({.*?}|[^,]+)(?=,|\s*\})'
            element_matches = re.findall(element_pattern, struct_content)

            for element_match in element_matches:
                element_name, element_value = element_match

                # Exclude curly brackets from addr value
                if element_name == 'addr' and element_value.startswith('{'):
                    element_value = element_value[1:]
                if element_name == 'addr' and element_value.endswith('}'):
                    element_value = element_value[:-1]

                struct_dict[struct_name][element_name] = element_value.strip()

    return struct_dict

# Usage example
file_path = 'mu_1sf_driver.c'
result = parse_c_file(file_path)
pprint(result)

with open('mu_1sf_driver_registers_data.pkl', 'wb') as f:
    pickle.dump(result, f)



