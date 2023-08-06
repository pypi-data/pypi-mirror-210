from .json_serializer import JsonSerializer
from .xml_serializer import XmlSerializer
from .serializer_interface import ISerializer


class SerializerFactory:
    serializers = {'json': JsonSerializer, 'xml': XmlSerializer}

    @classmethod
    def get_serializer(cls, serializer_type):
        return cls.serializers[serializer_type]()

    @classmethod
    def add_serializer(cls, serializer_type: str, serializer: ISerializer):
        cls.serializers[serializer_type] = serializer
