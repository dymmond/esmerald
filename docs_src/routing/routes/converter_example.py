from datetime import datetime

from lilya.transformers import Transformer, register_path_transformer


class DateTimeTransformer(Transformer):
    regex = "[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(.[0-9]+)?"

    def transform(self, value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")

    def normalise(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%dT%H:%M:%S")


register_path_transformer("datetime", DateTimeTransformer())
