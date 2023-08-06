import pandas as pd

class ConsoleFormatter:
    def __init__(self, data):
        if isinstance(data, dict):
            if not data:
                raise ValueError("Invalid input data type. Supported types are dictionary and pandas DataFrame.")
            self.data = data
        elif isinstance(data, pd.DataFrame):
            self.data = data.to_dict('list')
            if data.empty:
                raise ValueError("Invalid input data type. Supported types are dictionary and pandas DataFrame.")
        else:
            raise ValueError("Invalid input data type. Supported types are dictionary and pandas DataFrame.")

    def to_table(self):
        col_names = list(self.data.keys())
        rows = [list(map(str, self.data[key])) for key in col_names]
        formatted_data = [col_names] + rows

        # Column width calculation
        col_widths = [0 for col in formatted_data[0]]

        # header size calculation
        for i in range(len(col_names)):
            size = len(col_names[i]) + 2
            if size > col_widths[i]:
                col_widths[i] = size

        items = len(rows[0]) - 1
        #print(items)

        # Data size calculation
        for i in range(items):
            for j in range(len(rows)):
                # print(formatted_data[j][i+1])
                size = len(formatted_data[j][i+1]) + 2
                if (size > col_widths[i]):
                    col_widths[i] = size

        # Add extra width for table borders and separators
        # print(formatted_data[0])

        table_formatted = "\n"

        header = "| "
        for i in range(len(formatted_data[0])):
            size = col_widths[i] - len(formatted_data[0][i])
            filler = " " * size
            header += formatted_data[0][i] + filler + " | "

        table_formatted += header + "\n"

        line = "| "
        for i in range(len(formatted_data[0])):
            size = col_widths[i]
            filler = "-" * size
            line += filler + " | "

        table_formatted += line + "\n"

        items = len(rows[0])

        print(col_widths)

        ta = ""
        for i in range(items):
            
            data = "| "
            for j in range(len(rows)):
                print(formatted_data[j][i+1])
                size = col_widths[j] - len(formatted_data[j][i+1])
                filler = " " * size
                data += formatted_data[j][i+1] + filler + " | "
            ta += data + "\n"
            
        table_formatted += ta  + "\n"
        return table_formatted

    
def markdown(data):
    return ConsoleFormatter(data).to_table()