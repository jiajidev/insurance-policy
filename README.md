This project aims to calculate cash flows and PVs of an insurance policy.

Brief descriptions of the files:
- "policy.py": You could run this file directly to get results contained in a file called "output.xlsx".
- "output.xlsx": This is the results I got when I ran the "policy.py" file.

I have defined five methods for Policy objects:
- The "__init__" method instantiates a Policy object.
- The "generate_fund2_return" method generates a stochastic path for fund2_return.
- The "manually_input_fund2_return" method lets you use a predefined fund2_return path. This method could be used if you want to compare the output of this model against another model using the same fund2_return path.
- The "calculate" method calculates the cash flows and the PVs once fund2_return has been defined.
- The "output_to_excel" method outputs the results to an excel file called "output.xlsx" which contains two sheets with one sheet containing the cash flow data and the other sheet containing the PV data.
