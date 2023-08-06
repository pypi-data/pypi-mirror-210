from datavision_beeyard_sdk.api.overlay import add_shapes, read_shape
from datavision_beeyard_sdk.exceptions import ShapeError
import json


class Shape:
    def __init__(self, strokeColor, strokeWidth, name, properties=[], id=None):
        self.strokeColor = strokeColor
        self.strokeWidth = strokeWidth
        self.name = name
        self.properties = properties
        if id is not None:
            self.id = id

    def create(self):
        return self.__dict__

    def upload(self, cell_id, overlay_name, layer_name, client):
        resp = add_shapes.add(
            id=cell_id,
            overlay_name=overlay_name,
            layer_name=layer_name,
            client=client,
            shape_list=[self.__dict__],
        )
        return resp

    @classmethod
    def read_from_beeyard(cls, cell_id, overlay_name, sh_id, client):
        shape = json.loads(
            read_shape.read(
                cell_id, overlay_name=overlay_name, shape_id=sh_id, client=client
            )
        )
        if "location" in shape.keys():
            shape["location"] = Point.read_from_shape(shape["location"])
        if "vertices" in shape.keys():
            vertex_list = []
            for v in shape["vertices"]:
                vertex_list.append(Point.read_from_shape(v))
            shape["vertices"] = vertex_list
        del shape["typeName"]
        return cls(**shape)


class Cross(Shape):
    def __init__(
        self,
        strokeColor,
        strokeWidth,
        name,
        location,
        rotationDeg,
        size,
        zoomInvariant,
        properties=[],
        id=None,
    ):
        self.typeName = "cross"
        super().__init__(strokeColor, strokeWidth, name, properties, id)
        if isinstance(location, Point):
            self.location = location.create()
        else:
            raise ShapeError("single_point")
        self.rotationDeg = rotationDeg
        self.size = size
        self.zoomInvariant = zoomInvariant


class Rectangle(Shape):
    def __init__(
        self,
        strokeColor,
        strokeWidth,
        name,
        location,
        width,
        height,
        fillColor,
        properties=[],
        id=None,
    ):
        self.typeName = "rectangle"
        super().__init__(strokeColor, strokeWidth, name, properties, id)
        if isinstance(location, Point):
            self.location = location.create()
        else:
            raise ShapeError("single_point")
        self.width = width
        self.height = height
        self.fillColor = fillColor
        self.rotationDeg = 0.0


class OrientedRectangle(Rectangle):
    def __init__(
        self,
        strokeColor,
        strokeWidth,
        name,
        location,
        width,
        height,
        fillColor,
        rotationDeg,
        properties=[],
        id=None,
    ):
        self.typeName = "oriented_rectangle"
        super().__init__(
            strokeColor,
            strokeWidth,
            name,
            properties,
            location,
            width,
            height,
            fillColor,
            id,
        )
        self.rotationDeg = rotationDeg


class Polygon(Shape):
    def __init__(
        self,
        strokeColor,
        strokeWidth,
        name,
        vertices,
        fillColor,
        properties=[],
        id=None,
    ):
        self.typeName = "polygon"
        super().__init__(strokeColor, strokeWidth, name, properties, id)
        self.vertices = []
        for i in vertices:
            if isinstance(i, Point):
                self.vertices.append(i.create())
            else:
                raise ShapeError("polygon")
        self.fillColor = fillColor


class Ellipse(Shape):
    def __init__(
        self,
        strokeColor,
        strokeWidth,
        name,
        location,
        radiusRow,
        radiusCol,
        rotationDeg,
        fillColor,
        properties=[],
        id=None,
    ):
        self.typeName = "ellipse"
        super().__init__(strokeColor, strokeWidth, name, properties, id)
        if isinstance(location, Point):
            self.location = location.create()
        else:
            raise ShapeError("single_point")
        self.radiusRow = radiusRow
        self.radiusCol = radiusCol
        self.fillColor = fillColor
        self.rotationDeg = rotationDeg


class Circle(Shape):
    def __init__(
        self,
        strokeColor,
        strokeWidth,
        name,
        location,
        radius,
        fillColor,
        properties=[],
        id=None,
    ):
        self.typeName = "circle"
        super().__init__(strokeColor, strokeWidth, name, properties, id)
        if isinstance(location, Point):
            self.location = location.create()
        else:
            raise ShapeError("single_point")
        self.radius = radius
        self.fillColor = fillColor


class Point:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def create(self):
        return self.__dict__

    @classmethod
    def read_from_shape(cls, dictionary):
        return cls(dictionary["row"], dictionary["col"])
