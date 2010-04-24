"""Shapes operations.

Provides 2 shape classes:

Triangle;
Parallelogram.

Each shape class instance has the following properties,
accessible via appropriate routines:
    a tuple of shape vertices;
    reference point - a point, which is used as a shape
        rotation axle etc.;
    inner radius - radius of the inner circle with center in
        reference point;

Shape also supports [] clause to access separate vertices, as
well as for ... in ... clause to iterate over shape vertices.

Point is defined as in lines.py module, i.e. as (X, Y) tuple.

Run this module standalone for self-testing.
"""


__all__ = ['Triangle', 'Parallelogram']


import math
from math import cos, sin, sqrt
from math import pi as PI


import lines
from lines import *


def in_triangle(point, A, B, C):
    """Check if the given point is located inside the triangle.
    
    The triangle is given by 3 vertices: A, B, C.
    NB! It is assumed, that vertices are not laying on the same line.
    """
    
    # The line connecting each two vertices divides
    # a plane on two halfs.
    # If the point is located inside the triangle, the
    # point and the third vertex are located in the same half-plane,
    # and this is true for every pair of vertices.
    
    vertices = (A, B, C)
    
    for n in range(0, 3):
        
        vertex0 = vertices[n]
        vertex1 = vertices[(n + 1) % 3]
        vertex2 = vertices[(n + 2) % 3]
        
        side = [
                (
                    (vertex2[0] - vertex1[0]) * (p[1] - vertex1[1]) -
                    (vertex2[1] - vertex1[1]) * (p[0] - vertex1[0])
                )
            for p in (point, vertex0)
        ]
        
        # point and vertex0 are located in the same half-plane
        # iff side[0] and side[1] have the same sign.
        # If side[0] is 0, the point is laying on line between
        # vertex1 and vertex2.
        
        assert side[1] != 0.0, \
            "Points %s, %s, %s are laying on the same line" % \
            (A, B, C)
        
        # HACK! We check, if side[0] and side[1]
        # have a same sign or side[0] is 0 in such a manner:
        if side[0] * side[1] < 0:
            return False
    
    return True


class Shape:
    """Generic shape class"""
    
    def __init__(self, vertices, ref_point, r_inner):
        """Constructor.
        
        Arguments:
            vertices - sequence (list, tuple, etc.) of shape vertices;
            ref_point - shape reference point;
            r_inner - shape inner radius.
        """
        self.__vertices = tuple(vertices)
        self.__ref_point = ref_point
        self.__r_inner = r_inner
    
    def __getitem__(self, *args, **kwargs):
        return self.__vertices.__getitem__(*args, **kwargs)
    
    def get_vertices(self):
        """Shape vertices getter"""
        return self.__vertices
    
    def get_ref_point(self):
        """Shape reference point getter"""
        return self.__ref_point
    
    def get_r_inner(self):
        """Shape inner radius getter"""
        return self.__r_inner
    
    def rotate(self, angle):
        """Rotate a shape by an angle specified in radians.
        
        Shape reference point is used as a rotation axle.
        """
        self.__vertices = tuple(
            self.__moved_by(
                [
                    (
                        point[0] * cos(angle) - point[1] * sin(angle),
                        point[0] * sin(angle) + point[1] * cos(angle)
                    )
                    for point in
                        self.__moved_by(self.__vertices, self.__ref_point, -1)
                ],
                self.__ref_point,
                +1
            )
        )
    
    def move_to(self, point):
        """Move shape to the given location.
        
        Shape is moved to bring the reference point
        to the given location.
        """
        self.__vertices = tuple(
            self.__moved_by(
                self.__vertices,
                self.__moved_by((self.__ref_point,), point, -1)[0],
                -1
            )
        )
        self.__ref_point = point
    
    def move_by(self, offset):
        """Move shape relatively"""
        self.__ref_point, = \
            self.__moved_by((self.__ref_point, ), offset, 1)
        self.__vertices = \
            tuple(self.__moved_by(self.__vertices, offset, 1))
    
    @staticmethod
    def __moved_by(points, offset, sign):
        """Move points sequence by the given bias.
        
        Arguments:
            points - points sequence;
            offset - movement amount as a tuple (delta x, delta y);
            sign - movement sign (whether the offset s.b. added or
                substracted from the point coord) - negative or
                positive value;
        
        Result:
            input sequence copy, moved by the given offset.
        """
        
        sign = (sign >= 0) - (sign < 0)
        
        return [
            tuple(
                [
                    point[coord] + sign * offset[coord]
                    for coord in (0, 1)
                ]
            )
            for point in points
        ]


class Triangle(Shape):
    """Triangle shape class"""
    
    def __init__(self, A, B, C):
        """Constructor.
        
        Arguments are triangle vertices.
        """
        
        # Triangle inner circle center evaluation.
        # Point is evaluated as an intersection of triangle
        # bissectrisses.
        
        # Find triangle edges inclination
        BAX = inclination(B, A)
        CAX = inclination(C, A)
        BCX = inclination(B, C)
        
        # Find bissectrisses inclination
        IAX = (BAX + CAX) / 2
        ICX = (BCX + (CAX + PI)) / 2
        
        # Find bissectrisses intersection
        I = intersection(
            A, (cos(IAX), sin(IAX)),
            C, (cos(ICX), sin(ICX))
        )
        
        # Triangle inner circle radius evaluation. Radius is
        # evaluated as a distance between point I and one of
        # the triangle edges
        r_inner = point_to_line_distance(
            I,
            A, (cos(CAX), sin(CAX))
        )
        
        # Call the base class constructor
        Shape.__init__(
            self, (A, B, C), I, r_inner
        )
    
    def include(self, point):
        """Check if the given point is located inside the triangle"""
        return in_triangle(point, *self.get_vertices())


class Parallelogram(Shape):
    """Parallelogram shape class"""
    
    def __init__(self, A, B, C):
        """Constructor.
        
        Arguments are any three sequential vertices.
        """
        
        # Find the 4-th vertex
        D = tuple([A[coord] + C[coord] - B[coord] for coord in (0, 1)])
        
        # Find reference point as parallelogram diagonales
        # intersection point
        I = intersection(A, vectorAB(A, C), B, vectorAB(D, B))
        
        # Find inner circle radius as min distance between
        # I point and parallelogram edges
        r = min(
            point_to_line_distance(I, A, vectorAB(A, B)),
            point_to_line_distance(I, A, vectorAB(A, D))
        )
        
        # Call the base class constructor
        Shape.__init__(self, (A, B, C, D), I, r)
    
    def include(self, point):
        """Check if the point is located inside the parallelogram"""
        A, B, C, D = self.get_vertices()
        return \
            in_triangle(point, A, B, C) or in_triangle(point, C, D, A)


#----------------------------------------------------------------------
#                             Self-testing


if __name__ == '__main__':
    
    
    import unittest
    from unittest import TestCase
    
    
    def points_eq(A, B, tolerance=1e-6):
        """Compare two points.
        
        Comparison is made with the given tolerance.
        """
        
        for point in (A, B):
            if len(point) != 2 :
                raise ValueError("Value %s is not a valid point" % (point,))
        
        return distance(A, B) < tolerance
    
    
    def shapes_eq(A, B, tolerance=1e-6):
        """Compare two points sequencies.
        
        Points order in the sequencies s.b. the same, e.g.:
            shapes_eq([(1, 2), (3, 4)], [(3, 4), (1, 2)])
        return False.
        
        Comparison is made with the given tolerance.
        """
        
        if len(A) != len(B) :
            return False
        
        for i in range(len(A)):
            if not points_eq(A[i], B[i], tolerance):
                return False
        
        return True
    
    
    class TestInTriangle(TestCase):
        """in_triangle() routine tests"""
        
        TEST_TRI_1 = (0, 1), (1, -1), (-1, -1)
        TEST_TRI_2 = (0, 3), (4, -1), (-2, -1)
        
        def testNotInTriangle(self):
            """Point of interest is not in triangle"""
            assert not in_triangle((1, 1), *self.TEST_TRI_1)
        
        def test1(self):
            assert in_triangle((0, 0), *self.TEST_TRI_1)
        
        def test2(self):
            assert in_triangle((0, 0), *self.TEST_TRI_2)
        
        def testVertex(self):
            """Point of interest is the triangle vertex"""
            assert in_triangle(self.TEST_TRI_2[1], *self.TEST_TRI_2)
        
        def testOnEdge(self):
            """Point of interest is laying on the triangle edge"""
            point = (5, 2.5)
            A, B, C = (3, 1), (6, 1), (7, 4)
            self.failUnlessAlmostEqual(
                point_to_line_distance(point, A, vectorAB(A, C)), 0.0
            )
            assert in_triangle(point, A, B, C)
    
    
    class TestShape(TestCase):
        """Shape class tests.
        
        Most tests are performed on triangle shape case.
        """
        
        def ttmplCreateFromTuple(self, vertices, refpoint, r_inner):
            """Test template: create a shape from the Python tuple.
            
            Arguments:
                vertices - shape vertices tuple;
                refpoint - shape reference point;
                r_inner - shape inner radius.
            """
            s = Shape(vertices, refpoint, r_inner)
            assert s.get_ref_point() == refpoint
            assert s.get_r_inner() == r_inner
            
            assert isinstance(s.get_vertices(), tuple)
            assert shapes_eq(s.get_vertices(), vertices)
            assert s.get_vertices() is vertices
            # NB! Python tuples are immutable!
            assert not hasattr(s.get_vertices(), '__setslice__')
        
        #---- Shape creation tests
        
        def testCreateTriangleFromList(self):
            """Create a triangle shape from the Python list"""
            vertices = [(0, 0), (1, 1), (-2, -2)]
            s = Shape(vertices, (0, 0), 2)
            
            assert isinstance(s.get_vertices(), tuple)
            assert shapes_eq(vertices, s.get_vertices())
            assert s.get_vertices() is not vertices
        
        def testCreateTriangle(self):
            """Create a triangle shape from the Python tuple"""
            self.ttmplCreateFromTuple(
                refpoint=(10, 1), r_inner=0.5,
                vertices=((0, 0), (1, 1), (2, -2))
            )
        
        def testCreateTetrangle(self):
            """Create a tetrangle shape from the Python tuple"""
            self.ttmplCreateFromTuple(
                refpoint=(3, 1), r_inner=1.0,
                vertices=((0, 0), (0, 1), (2, 2), (3, 0))
            )
        
        #---- rotate() method tests
        
        def testRotate360(self):
            """Rotate a shape on 360 degrees"""
            vertices = ((0, 0), (0, 3), (1, 0))
            s = Shape(vertices, (0, 0), 1.0)
            s.rotate(2 * PI)
            assert shapes_eq(s.get_vertices(), vertices)
            assert isinstance(s.get_vertices(), tuple)
        
        def testRotate180(self):
            """Rotate a shape on 180 degrees"""
            s = Shape([(0, 0), (0, 3), (1, 0)], (0, 0), 1.0)
            s.rotate(PI)
            assert shapes_eq(
                s.get_vertices(), [(0, 0), (0, -3), (-1, 0)]
            )
        
        def testRotate90(self):
            """Rotate a shape on 90 degrees"""
            s = Shape([(0, 0), (0, 3), (1, 0)], (0, 0), 1.0)
            s.rotate(PI / 2)
            assert shapes_eq(
                s.get_vertices(), [(0, 0), (-3, 0), (0, 1)]
            )
        
        def testRotate90nzeroRefpoint(self):
            """Rotate a shape on 90 degrees, ref. point isn't 0-0"""
            s = Shape([(1, -2), (4, 5), (6, -2)], (4, 5), 1.0)
            s.rotate(PI / 2)
            assert shapes_eq(
                s.get_vertices(), [(11, 2), (4, 5), (11, 7)]
            )
        
        #---- move() method tests
        
        def testMoveTo(self):
            """Move a shape to absolute position"""
            s = Shape([(0, 0), (0, 3), (2, 0)], (4, 6), 1.0)
            s.move_to((1, 2))
            assert s.get_ref_point() == (1, 2)
            assert shapes_eq(
                s.get_vertices(),
                [(-3, -4), (-3, -1), (-1, -4)]
            )
            assert isinstance(s.get_vertices(), tuple)
        
        def testMoveBy(self):
            """Move a shape relatively"""
            s = Shape([(0, 0), (0, 3), (2, 0)], (4, 6), 1.0)
            s.move_by((1, 2))
            assert s.get_ref_point() == (5, 8)
            assert shapes_eq(
                s.get_vertices(),
                [(1, 2), (1, 5), (3, 2)]
            )
            assert isinstance(s.get_vertices(), tuple)
        
        #---- special attributes tests
        
        def test__getitem__(self):
            """Item access method test"""
            vertices = [(0, 0), (0, 1), (1, 2)]
            s = Shape(vertices, (0.5, 0.5), 1.0)
            for i in range(len(vertices)):
                assert points_eq(s[i], vertices[i])
        
        def test__iter__(self):
            """Iterations over shape test"""
            vertices = [(0, 0), (0, 1), (1, 2)]
            s = Shape(vertices, (0.1, 0.1), 2.5)
            vertices2 = [v for v in s]
            assert vertices2 is not vertices
            assert shapes_eq(vertices, vertices2)
    
    
    class TestTriangle(TestCase):
        """Triangle class tests"""
        
        VERTICES0 = (-1, 0), (0, 1), (1, 0)
        
        def ttmplCreate(self, offset):
            """Triangle creation test template.
            
            Create the triangle of the known size
            in the given location, check it's parameters.
            
            Arguments:
                offset - triangle location relatively to (0, 0) point.
                    Each point of the triangle should be moved by this
                    offset.
            
            Result:
                Triangle object created in this test.
            """
            vertices = [
                    [
                        point[coord] + offset[coord]
                        for coord in (0, 1)
                    ]
                for point in (-22, -7), (11, 23), (12, -12)
            ]
            
            triangle = Triangle(*vertices)
            assert shapes_eq(triangle.get_vertices(), vertices)
            
            assert points_eq(
                triangle.get_ref_point(),
                (1.2 + offset[0], 0.1 + offset[1]), 0.1
            )
            
            self.failUnlessAlmostEqual(triangle.get_r_inner(), 10.4, 2)
            
            return triangle
        
        def ttmplRotate(self, angle):
            """Triangle rotation test template.
            
            Create a triangle by self.ttmplCreate call,
            rotate it by the given angle and check rotated
            shape parameters.
            """
            A = self.ttmplCreate((0, 0)) # Reference object
            B = Triangle(*A.get_vertices()) # Work object
            
            assert shapes_eq(
                A.get_vertices(), B.get_vertices()
            )
            
            B.rotate(angle)
            # Copy rotated work object, because some of Triangle
            # parameters are evaluated in constructor, and
            # ARE NOT ALTERED by rotation operation
            C = Triangle(*B.get_vertices())
            
            assert not shapes_eq(
                A.get_vertices(), C.get_vertices()
            )
            assert points_eq(A.get_ref_point(), C.get_ref_point())
            self.failUnlessAlmostEqual(A.get_r_inner(), C.get_r_inner())
        
        #---- Creation tests
        
        def testCreate_0_0(self):
            self.ttmplCreate((0, 0))
        
        def testCreate_3_0(self):
            self.ttmplCreate((3, 0))
        
        def testCreate_0_5(self):
            self.ttmplCreate((0, 5))
        
        def testCreate_m10_7(self):
            self.ttmplCreate((-10, 7))
        
        #---- rotate() method tests
        
        def testRotate30(self):
            self.ttmplRotate(PI / 3)
        
        def testRotate90(self):
            self.ttmplRotate(PI / 2)
        
        def testRotate180(self):
            self.ttmplRotate(PI)
        
        #---- include() method tests
        
        def testInclude1(self):
            assert Triangle(*self.VERTICES0).include((0, 0))
        
        def testInclude2(self):
            assert not Triangle(*self.VERTICES0).include((10, 10))
        
        def testIncludeRefPoint(self):
            triangle = Triangle(*self.VERTICES0)
            assert triangle.include(triangle.get_ref_point())
        
        #---- Miscellaneous tests
        
        def testEqEdges(self):
            """Equal edges triangle test"""
            triangle = Triangle(
                (0, 4), (2 * sqrt(3), -2), (-2 * sqrt(3), -2)
            )
            assert points_eq(triangle.get_ref_point(), (0, 0))
            self.failUnlessAlmostEqual(triangle.get_r_inner(), 2)
    
    
    class TestParallelogram(TestCase):
        """Parallelogram class tests"""
        
        VERTICES0 = ((2, 1), (7, 1), (8, 4))
        
        def testCreate(self):
            """Creation test"""
            
            vertices = self.VERTICES0
            parallelogram = Parallelogram(*vertices)
            
            assert shapes_eq(
                parallelogram.get_vertices(),
                vertices + ((3, 4),)
            )
            
            assert points_eq(
                parallelogram.get_ref_point(),
                (5, 2.5)
            )
            
            self.failUnlessEqual(parallelogram.get_r_inner(), 1.5)
        
        #---- include() method tests
        
        def testInclude1(self):
            assert Parallelogram(*self.VERTICES0).include((4, 3))
        
        def testInclude2(self):
            assert Parallelogram(*self.VERTICES0).include((6, 2))
        
        def testIncludeRefPoint(self):
            parallelogram = Parallelogram(*self.VERTICES0)
            assert parallelogram.include(parallelogram.get_ref_point())
    
    
    unittest.main()
