import attr
import json


@attr.s(auto_attribs=True)
class ModifyCellInputDto:
    """ """

    description: str

    def to_dict(self):
        field_dict = {}
        field_dict["description"] = self.description
        return json.dumps(field_dict)
