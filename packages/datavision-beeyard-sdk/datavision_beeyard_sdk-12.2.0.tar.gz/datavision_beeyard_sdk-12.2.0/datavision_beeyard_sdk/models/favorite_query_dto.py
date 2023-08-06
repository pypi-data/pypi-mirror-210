from ..types import favorite_query_checker


class FavoriteQueryDto:
    """ """

    name: str
    filter_: str
    sorting_field: str
    sorting_direction: str

    @favorite_query_checker
    def __init__(self, name, filter_, sorting_field, sorting_direction):
        self.name = name
        self.filter_ = filter_
        self.sorting_field = sorting_field
        self.sorting_direction = sorting_direction

    def to_dict(self):
        field_dict = {}
        field_dict.update({})
        if self.name != "":
            field_dict["name"] = self.name
        field_dict["filter"] = self.filter_
        field_dict["sortingField"] = self.sorting_field
        field_dict["sortingDirection"] = self.sorting_direction
        return field_dict
