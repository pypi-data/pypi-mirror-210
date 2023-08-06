from serializer.utils.converter import Converter
from .serializer_interface import ISerializer


class XmlSerializer(ISerializer):
    _data_converter = Converter()

    def dump(self, obj, file):
        file.write(self.dumps(obj))

    def dumps(self, obj):
        converted_data = self._data_converter.convert(obj)
        if isinstance(converted_data, (list, tuple)):
            return self._dump_list_and_tuple(converted_data)
        if isinstance(converted_data, dict):
            return self._dump_dict(converted_data)
        if isinstance(converted_data, str):
            converted_data = f'"{converted_data}"'
        return self._dump_primitive(converted_data)

    def load(self, file):
        data = file.read()
        return self.loads(data)

    def loads(self, string):
        result, ind = self._loads_xml(string, 0)
        return self._data_converter.deconvert(result)

    def _dump_list_and_tuple(self, collection):
        return f'<{collection.__class__.__name__}>{"".join([self.dumps(item) for item in collection])}</{collection.__class__.__name__}>'

    def _dump_dict(self, dictionary):
        return f'<{dictionary.__class__.__name__}>{"".join([self._dump_dict_element(key, value) for key, value in dictionary.items()])}</{dictionary.__class__.__name__}>'

    def _dump_dict_element(self, key, value):
        return f'<item><key>{self.dumps(key)}</key><value>{self.dumps(value)}</value></item>'

    def _dump_primitive(self, obj):
        return f'<{obj.__class__.__name__}>{obj}</{obj.__class__.__name__}>'

    def _loads_xml(self, string, index):
        # index is '<'

        index += 1
        end_index = index
        while string[end_index] != '>':
            end_index += 1

        tag = string[index:end_index]

        match tag:
            case 'int' | 'float':
                return self._load_number(string, end_index + 1)
            case 'bool':
                return self._load_bool(string, end_index + 1)
            case 'NoneType':
                return None, index + 24
            case 'str':
                return self._load_str(string, end_index + 1)
            case 'list':
                return self._load_list(string, end_index + 1)
            case 'dict':
                return self._load_dict(string, end_index + 1)

    def _load_number(self, string, index):
        end_index = index

        while string[end_index] != '<':
            end_index += 1

        number = string[index:end_index]
        if '.' in number:
            return float(number), end_index + 8
        return int(number), end_index + 6

    def _load_bool(self, string, index):
        if string[index] == 'T':
            return True, index + 11
        else:
            return False, index + 12

    def _load_str(self, string, index):
        end_index = index
        while string[end_index:end_index + 6] != '</str>':
            end_index += 1

        str = string[index + 1:end_index - 1]
        return f'{str}', end_index + 6

    def _load_list(self, string, index):
        end_index = index
        result = []

        tags_count = 1
        while tags_count > 0:
            if string[end_index:end_index + 6] == '<list>':
                tags_count += 1
            elif string[end_index:end_index + 7] == '</list>':
                tags_count -= 1
            end_index += 1
        end_index -= 1
        while index < end_index:
            item, index = self._loads_xml(string, index)
            result.append(item)
        return result, end_index + 7

    def _load_dict(self, string, index):
        end_index = index

        result = {}
        bracket_count = 1
        while bracket_count > 0:
            if string[end_index:end_index + 6] == '<dict>':
                bracket_count += 1
            elif string[end_index:end_index + 7] == '</dict>':
                bracket_count -= 1
            end_index += 1
        end_index -= 1

        while index < end_index:
            item, index = self._load_dict_item(string, index)
            result[item[0]] = item[1]

        return result, end_index + 7

    def _load_dict_item(self, string, index):
        end_index = index + 11  # <item><key> <...
        key, end_index = self._loads_xml(string, end_index)
        end_index += 13  # </key><value> <...
        value, end_index = self._loads_xml(string, end_index)
        return (key, value), end_index + 15  # </value></item><...
