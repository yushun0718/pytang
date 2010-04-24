"""Shapes docking implementation.


Run this module standalone for self-testing.
"""


import math
from math import sqrt, pi, cos


import lines
from lines import *


PRECISION = 1e-10

def edges(shape):
    """Shape edges generator function.
    
    Generate a tuple of 2 consequetive vertices
    from
        (vertex[N - 1], vertex[0])
        to 
        (vertex[N - 2], vertex[N - 1]),
    where N is a number of shape vertices.
    NB! the sequence start vertex m.b. changed later.
    """
    vertex0 = shape[-1]
    
    for vertex1 in shape:
        yield (vertex0, vertex1)
        vertex0 = vertex1


def _params_gen(
    static, floating,
    ang_threshold_cos,
    dist_threshold,
    manu_rotate,
    manu_move
):
    """Generator to get the most suited edge for docking.
    
    Arguments:
        static - static shapes sequence;
        floating - floating shape (NB! static
            and floating shapes are given as vertices sequences,
            all vertices are the points, just like in lines.py
            module);
        ang_threshold_cos - angular threshold cosine value, two edges
            should't be put into account if the angle between these
            two edges is greater than the angular threshold;
        
    """
    for floating_edge in edges(floating):
        floating_vector = vectorAB(floating_edge[0], floating_edge[1])
        # Filter by manual movement direction: the floating edge
        # shouldn't be put into account if the manual movement
        # direction vector applied to this edge is looking 
        # inside the shape.
        if x_product(floating_vector, manu_move) > PRECISION:
            continue
        
        floating_module = distance(*floating_edge)
        
        for shape in static:
            
            for static_edge in edges(shape):
                static_vector = vectorAB(*static_edge)
                if (
                    x_product(static_vector, floating_vector)
                    *
                    manu_rotate
                ) < -PRECISION:
                    continue
                
                static_module = vector_abs(static_vector)
                
                D = min(
                    [
                        point_to_line_distance(
                            p,
                            static_edge[0], static_vector
                        )
                        for p in floating_edge
                    ]
                )
                if D > dist_threshold:
                    continue
                
                cos_theta = -(
                    scalar_product(floating_vector, static_vector)
                    /
                    (floating_module * static_module)
                )
                if cos_theta < ang_threshold_cos:
                    continue
                
                overlapping = static_module * (
                    min(
                        scalar_product(
                            static_vector,
                            vectorAB(static_edge[0], floating_edge[0])
                        )
                        /
                        static_module ** 2
                        ,
                        1.0
                    )
                    -
                    max(
                        scalar_product(
                            static_vector,
                            vectorAB(static_edge[0], floating_edge[1])
                        )
                        /
                        static_module ** 2
                        ,
                        0.0
                    )
                )
                if overlapping < PRECISION:
                    continue
                yield(-D, cos_theta, overlapping, (static_edge, floating_edge))
    
    # NB! Is needed to provide non-empty argument for max
    # function if no appropriate edge for docking was found.
    yield ()


def gravity(
    static, floating,
    ang_threshold_cos,
    dist_threshold,
    manu_rotate,
    manu_move
):
    result = max(
        _params_gen(
            static, floating,
            ang_threshold_cos,
            dist_threshold,
            manu_rotate,
            manu_move
        ),
        key=lambda p: p[0:-1]
    )
    if result:
        return result[-1]
    else:
        return None


#----------------------------------------------------------------------
#                             Self-testing


if __name__ == '__main__':
    
    
    import unittest
    from unittest import TestCase
    import profile
    
    
    class TestBase:
        
        class Bottom:
            def __cmp__(self, other):
                return -1
        
        class Top:
            def __cmp__(self, other):
                return 1
        
        ANG_THRESHOLD_COS = Bottom()
        DIST_THRESHOLD = 0.0
        MANU_ROTATE = 0.0
        MANU_MOVE = (0.0, 0.0)
        
        STATIC = None
        FLOATING = None
        STATIC_EDGE = None
        DOCKING_EDGE = None
        
        def shortDescription(self):
            """Override inherited method"""
            if not self.__doc__:
                return TestCase.shortDescription(self)
            else:
                return self.__doc__.split('\n')[0]
        
        def assertGravity(self, found, expected):
            """Compare edge coords"""
            self.failUnlessEqual(found, expected)
        
        def testMain(self):
            RUT_result = gravity(
                self.STATIC, self.FLOATING,
                self.ANG_THRESHOLD_COS,
                self.DIST_THRESHOLD,
                self.MANU_ROTATE,
                self.MANU_MOVE
            )
            if self.DOCKING_EDGE is not None:                
                self.failUnlessEqual(
                    RUT_result,
                    (
                        self.STATIC_EDGE,
                        self.DOCKING_EDGE
                    )
                )
            else:
                self.failIf(RUT_result)
    
    
    class TwoDocked(TestBase):
        STATIC = (
            ((2, 1), (5, 2), (3, 4)),
        )
        STATIC_EDGE = ((5, 2), (3, 4))
        FLOATING = ((3, 4), (5, 2), (4, 6))
        DOCKING_EDGE = ((3, 4), (5, 2))
    
    
    class AlreadyDocked2(TwoDocked, TestCase):
        """Two shapes, already docked"""
        pass
    
    
    class Near2(TwoDocked, TestCase):
        """Two near shapes"""
        DIST_THRESHOLD = 1.0
        FLOATING = ((3.1, 4), (5, 2.4), (4, 6))
        DOCKING_EDGE = ((3.1, 4), (5, 2.4))
    
    
    class Far2(TwoDocked, TestCase):
        """Two far shapes"""
        DIST_THRESHOLD = TestBase.Bottom()
        DOCKING_EDGE = None
    
    
    class Biased2(TwoDocked, TestCase):
        """Two near shapes with too big angular distance.
        
        Some trick is to use the Top() as a threshold cos value.
        """
        ANG_THRESHOLD_COS = TestBase.Top()
        DOCKING_EDGE = None
    
    
    class NoOverlapping2(TwoDocked, TestCase):
        """Two not overlapping shapes"""
        FLOATING = ((1, 6), (3, 4), (2, 8))
        DIST_THRESHOLD = 1.0
        DOCKING_EDGE = None
    
    
    class ManuMove2(TwoDocked):
        ANG_THRESHOLD_COS = 0.9
        MANU_MOVE = (2, 1)
    
    
    class AntiMove2(ManuMove2, TestCase):
        """Two near shapes, man. move direction is oppos. to docking"""
        DOCKING_EDGE = None
    
    
    class CoMove2(ManuMove2, TestCase):
        """Two near shapes, man. move direction is co-dir. to docking"""
        MANU_MOVE = (-2, -1)
    
    
    class ManuRotate2(TwoDocked):
        FLOATING = ((3, 4), (5, 3), (4, 6))
        DOCKING_EDGE = ((3, 4), (5, 3))
        STATIC_EDGE = ((5, 2), (3, 4))
    
    
    class AntiRotate2(ManuRotate2, TestCase):
        """Two near shapes, man. rotate direction is oppos. to docking"""
        MANU_ROTATE = +1.0
        DOCKING_EDGE = None
    
    
    class CoRotate2(ManuRotate2, TestCase):
        MANU_ROTATE = -1.0
    
    
    class ZeroRotate2(ManuRotate2, TestCase):
        MANU_ROTATE = 0.0
    
    
    unittest.main()


#~ def test_benchmark(self):
    #~ profiler = profile.Profile()
    #~ profiler.runcall(
        #~ gravity,
        #~ (
            #~ ((2, 1), (5, 2), (3, 4)),
            #~ ((2, 1), (5, 2), (3, 4)),
            #~ ((2, 1), (5, 2), (3, 4)),
            #~ ((2, 1), (5, 2), (3, 4)),
            #~ ((2, 1), (5, 2), (3, 4)),
            #~ ((2, 1), (5, 2), (3, 4)),
            #~ ((2, 1), (5, 2), (3, 4)),
        #~ ),
        #~ ((3, 4), (5, 2), (4, 6)),
        #~ self.ANG_THRESHOLD_COS,
        #~ self.DIST_THRESHOLD,
        #~ self.MANU_ROTATE,
        #~ self.MANU_MOVE
    #~ )
    #~ profiler.print_stats()
