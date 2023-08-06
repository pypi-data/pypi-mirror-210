import pandas as pd

class ReadExcel:
    _excel_path = ""
    dict_data = {}
    keys = []

    def __init__(self, file_path):
        # Read and create members during initialization
        self._excel_path = file_path
        self.dict_data = self.read_excel_to_dict(file_path)
        self.keys = list(self.dict_data.keys())

    def __repr__(self) -> str:
        # Get dictionary content
        dict_str = ""
        for key, value in self.dict_data.items():
            dict_str += f"\n    {key}: {value}"
        # Print representation
        return f"{self.__class__.__name__}{{\n  READ_PATH: {repr(self._excel_path)},\n  KEYS: {repr(self.keys)},\n  READ_DICT: {{{dict_str}\n  }}\n}}"

    def read_excel_to_dict(self, file_path=_excel_path):
        # Read Excel spreadsheet data
        df = pd.read_excel(file_path)
        
        # Store column names and values in a dictionary
        data_dict = {}
        for column in df.columns:
            data_dict[column] = df[column].values.tolist()
        
        return data_dict

# # Usage
# if __name__ == "__main__":
#     # Specify the path to the Excel file
#     test_edict = ReadExcel("./test.xlsx")
#     print(test_edict)
