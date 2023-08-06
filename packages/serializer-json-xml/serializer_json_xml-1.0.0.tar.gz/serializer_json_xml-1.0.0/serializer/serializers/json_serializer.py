from serializer.utils.converter import Converter
from .serializer_interface import ISerializer


class JsonSerializer(ISerializer):
    _data_converter = Converter()

    def dump(self, obj, file):
        file.write(self.dumps(obj))

    def dumps(self, obj):
        converted_data = self._data_converter.convert(obj)
        if isinstance(converted_data, (list, tuple)):
            return self._dump_list_and_tuple(converted_data)

        if isinstance(converted_data, dict):
            return self._dump_dict(converted_data)

        return self._dump_primitive(obj)

    def load(self, file):
        data = file.read()
        return self.loads(data)

    def loads(self, string):
        result, ind = self._loads_json(string, 0)
        return self._data_converter.deconvert(result)

    def _dump_primitive(self, obj):
        if isinstance(obj, str):
            obj = f"'{obj}'"
        return f'"{str(obj)}"'

    def _dump_dict(self, dictionary):
        if not dictionary:
            return '{}'

        result = '{'

        for key, value in dictionary.items():
            if isinstance(value, dict):
                result += f'"{key}": {self._dump_dict(value)},'
            elif isinstance(value, (list, tuple)):
                result += f'"{key}": {self._dump_list_and_tuple(value)},'
            else:
                result += f'"{key}": {self._dump_primitive(value)},'

        return result[:-1] + '}'  # exclude last comma

    def _dump_list_and_tuple(self, collection):
        if not collection:
            return '[]'

        result = '['

        for item in collection:
            if isinstance(item, dict):
                result += f'{self._dump_dict(item)},'
            elif isinstance(item, (list, tuple)):
                result += f'{self._dump_list_and_tuple(item)},'
            else:
                result += f'{self._dump_primitive(item)},'

        return result[:-1] + ']'  # exclude last comma

    def _loads_json(self, string, index):
        match string[index]:
            case '"':
                if string[index + 1] == "'":
                    return self._load_string(string, index + 2)
                else:
                    return self._load_primitive(string, index + 1)
            case '[':
                return self._load_list(string, index)
            case '{':
                return self._load_dict(string, index)

    def _load_dict(self, string, index):
        end_index = index
        bracket_count = 1

        while bracket_count > 0 and end_index + 1 < len(string):
            end_index += 1
            if string[end_index] == '{':
                bracket_count += 1
            if string[end_index] == '}':
                bracket_count -= 1
        index += 1

        result = {}
        while index < end_index:
            if string[index] in (',', ' '):
                index += 1
                continue
            key, index = self._loads_json(string, index)
            while string[index] in (':', ' '):
                index += 1
            value, index = self._loads_json(string, index)
            result[key] = value

        return result, end_index + 1

    def _load_list(self, string, index):
        # index is : [1,2,3]
        end_index = index + 1
        brackets = 1

        while brackets > 0 and end_index < len(string):
            if string[end_index] == '[':
                brackets += 1
            elif string[end_index] == ']':
                brackets -= 1
            end_index += 1

        index += 1
        # index is first element
        result = []
        while index < end_index:
            if string[index] in (',', ' '):
                index += 1
                continue
            if end_index - index < 2:  # if last element was reached
                break
            element, index = self._loads_json(string, index)
            result.append(element)

        return result, end_index + 1

    def _load_string(self, string, index):
        # index is first 'symbol' of string
        end_index = index

        # get str value
        while string[end_index] != "'" and end_index < len(string):
            end_index += 1
        data = string[index:end_index]

        return data, end_index + 3

    def _string_catcher(self, string, index):
        # check incorrect value
        end_index = index

        # related element
        while string[end_index] != '"' and end_index < len(string):
            end_index += 1
        data_slice = string[index:end_index]

        return data_slice, end_index + 3

    def _load_number(self, string, index):

        end_index = index
        while string[end_index] != '"' and end_index < len(string):
            end_index += 1
        number_str = string[index:end_index]

        try:
            if '.' in number_str:
                return float(number_str), end_index + 1
            else:
                return int(number_str), end_index + 1
        except:
            return self._string_catcher(string, index)

    def _load_primitive(self, string, index):
        # index is start of primitive
        # [none, boolean, numbers]
        if string[index] == 'N':
            return None, index + 5
        elif string[index] == 'T':
            return True, index + 5
        elif string[index] == 'F':
            return False, index + 6
        else:
            return self._load_number(string, index)
