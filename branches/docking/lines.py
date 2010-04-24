"""Points and lines operating routines.

Provides means for vectors, lines and points manipulations.

Point is defined as (X, Y) tuple.

Vector is defined as (X, Y) tuple, where (X, Y) is vector end point
(vector start point is assumed to be (0, 0) point).

Line can be defined by two different points laying on it,
or by two vectors: base vector and direction vector.
Given base vector B and direction vector D, any point P of the line
can be defined as:
    
    P = B + p * D
    
    ,where p is a real number.


Run this module standalone for self-testing.
"""


__all__ = [
    'vectorAB', 'vector_abs','distance', 'inclination', 'intersection',
    'point_to_line_distance',
    'scalar_product', 'x_product','transposed'
]


import math
from math import sin, cos, sqrt, atan2
from math import pi as PI

def vectorAB(A, B):
    """Make a vector given by start and end points.
    
    Arguments:
        A - vector start point;
        B - vector end point;
    
    Result:
        vector AB, where: A + AB = B
    """
    return tuple([B[coord] - A[coord] for coord in (0, 1)])


def vector_abs(A):
    """Evaluate vector length"""
    return sqrt(A[0] **2 + A[1] **2)
    
    
def distance(A, B):
    """Evaluate euqlidian distance between two points"""
    result = 0.0
    for coord in (0, 1):
        result += (A[coord] - B[coord])** 2
    return sqrt(result)


def scalar_product(A, B):
    """Evaluate two vectors scalar product"""
    return A[0] * B[0] + A[1] * B[1]


def x_product(A, B):
    """Evaluate two vectors cross-product"""
    return A[0] * B[1] - B[0] * A[1]

def transposed(A):
    """Return transposed vector, i.e. rotated PI/2 counterclockwise"""
    return (-A[1], A[0])


def inclination(A, B):
    """Evaluate inclination of the line given by two points.
    
    Result is in radians.
    """
    AB = vectorAB(A, B)
    return atan2(*[AB[coord] for coord in (1, 0)])


def intersection(baseA, directionA, baseB, directionB):
    """Find two lines intersection point.
    
    Arguments:
        baseA, directionA - 1-st line base vector and direction vector;
        baseB, directionB - 2-nd line base vector and direction vector.
    """
    directionB_t = transposed(directionB)
    p = (
            float(scalar_product(directionB_t, vectorAB(baseA, baseB)))
            /
            scalar_product(directionB_t, directionA)
    )
    return tuple([baseA[coord] + p * directionA[coord] for coord in (0, 1)])


def point_to_line_distance(A, base, direction):
    """Evaluate the distance between point and line.
    
    Arguments:
        A - point;
        base, direction - line base and direction vectors.
    """
    #---- Deprecated implementation
    
    #~ # Find the intersection point of the given line
    #~ # and the orthogonal line including the point A.
    #~ I = intersection(base, direction, A, transposed(direction))
    #~ # Return the distance between the point A
    #~ # and the intersection point I.
    #~ return distance(A, I)
    
    #---- New implementation
    
    return (
        abs(x_product(vectorAB(A, base), direction))
        /
        vector_abs(direction)
    )


#----------------------------------------------------------------------
#                             Self-testing


if __name__ == '__main__':
    
    
    import unittest
    from unittest import TestCase
    
    
    class TestInclination(TestCase):
        """inclination routine tests"""
        
        def test_0(self):
            """Horizontal line case"""
            self.failUnlessAlmostEqual(inclination((1, 2), (3, 2)), 0.0)
        
        def test_pi(self):
            """Horizontal line case, inclination is PI"""
            self.failUnlessAlmostEqual(inclination((3, 2), (1, 2)), PI)
        
        def test_pi_d_2(self):
            """Vertical line case"""
            self.failUnlessAlmostEqual(
                inclination((1, 2), (1, 10)), PI / 2
            )
        
        def test_pi_d_4(self):
            """Inclination is PI / 4"""
            self.failUnlessAlmostEqual(
                inclination((1, 10), (3, 12)), PI / 4
            )
        
        def test_pi_d_4_2(self):
            """Inclination is PI / 4, case 2"""
            self.failUnlessAlmostEqual(
                inclination((-5, 10), (-3, 12)), PI / 4
            )
        
        def testSamePoint(self):
            """Line is given by two equal points"""
            self.failUnlessAlmostEqual(inclination((3, 2), (3, 2)), 0.0)
    
    
    class TestDistance(TestCase):
        """distance routine tests"""
        
        def testSamePoint(self):
            """Same point distance"""
            self.failUnlessAlmostEqual(distance((1, 2), (1, 2)), 0.0)
        
        def testDifferentPoints(self):
            """Different points distance"""
            self.failUnlessAlmostEqual(distance((2, -1), (5, 3)), 5.0)
    
    
    class TestIntersection(TestCase):
        """intersection routine tests"""
        
        TEST_LINE = ((2.0, -1.0), (2.0, 3.0))
        
        def testSame(self):
            """The same line case"""
            self.failUnlessRaises(
                ZeroDivisionError,
                intersection,
                self.TEST_LINE[0],
                self.TEST_LINE[1],
                *self.TEST_LINE
            )
        
        def testParallel(self):
            """Parallel lines case"""
            self.failUnlessRaises(
                ZeroDivisionError,
                intersection,
                (5.0, 5.0), (3.0, 4.5),
                *self.TEST_LINE
            )
        
        def testOrthogonal(self):
            """Orthogonal lines case"""
            self.failUnlessAlmostEqual(
                distance(
                    intersection(
                        (7.0, 0.0), (1.5, -1.0),
                        *self.TEST_LINE
                    ),
                    (4.0, 2.0)
                ),
                0.0
            )
        
        def testArbitrary(self):
            """Arbitrary lines case"""
            self.failUnlessAlmostEqual(
                distance(
                    intersection(
                        (7.0, -2.5), (4.0, -3.0),
                        *self.TEST_LINE
                    ),
                    (3.0, 0.5)
                ),
                0.0
            )
        
        def testInt(self):
            """Integer data case"""
            self.failUnlessAlmostEqual(
                distance(
                    intersection(
                        (7, 6), (4, 3),
                        (2, 6), (2, 3)
                    ),
                    (-3.0, -1.5)
                ),
                0.0
            )
        
        def testVertical(self):
            """Vertical line case"""
            self.failUnlessAlmostEqual(
                distance(
                    intersection(
                        (3.0, 1.5), (0.0, 1.0),
                        *self.TEST_LINE
                    ),
                    (3.0, 0.5)
                ),
                0.0
            )
        
        def testHorizontal(self):
            """Horizontal line case"""
            self.failUnlessAlmostEqual(
                distance(
                    intersection(
                        (3.0, 3.5), (1.0, 0.0),
                        *self.TEST_LINE
                    ),
                    (5.0, 3.5)
                ),
                0.0
            )
    
    
    class TestPointToLineDistance(TestCase):
        """point_to_line_distance routine tests"""
        
        def testLineIncludesPoint(self):
            """Point is laying on the line"""
            self.failUnlessAlmostEqual(
                point_to_line_distance((1, 2), (0, 4), (1, -2)),
                0.0
            )
        
        def testSameAsBase(self):
            """Point is the same as line base vector end point"""
            self.failUnlessAlmostEqual(
                point_to_line_distance((1, 2), (1, 2), (1, -2)),
                0.0
            )
        
        def testVerticalLine(self):
            """Vertical line case"""
            self.failUnlessAlmostEqual(
                point_to_line_distance((6, 8), (-1, 2), (0, 3)),
                7.0
            )
        
        def testHorizontalLine(self):
            """Horizontal line case"""
            self.failUnlessAlmostEqual(
                point_to_line_distance((6, 8), (4, 5), (2, 0)),
                3.0
            )
        
        def testFinitDistance(self):
            """Arbitrary line inclination, finit nonzero distance"""
            self.failUnlessAlmostEqual(
                point_to_line_distance((6, 8), (-1, -1), (3, 2)),
                sqrt(13.0)
            )
    
    
    unittest.main()
