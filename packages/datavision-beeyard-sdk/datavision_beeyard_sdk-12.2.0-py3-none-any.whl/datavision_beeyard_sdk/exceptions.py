class ShapeError(Exception):
    def __init__(self, *args, **kwargs):
        if args[0] == "single_point":
            super().__init__(
                "Location must be of Type Point ('row': xxx, 'col': xxx).", **kwargs
            )
        elif args[0] == "polygon":
            super().__init__(
                "Vertices must be a list of elements of Type Point ('row': xxx, 'col': xxx).",
                **kwargs
            )
        else:
            super().__init__(*args, **kwargs)
