"""Tangram game main module.

Run this module to play the game.
NB! Pygame package is needed!

Tangram puzzle game was invented in the ancient China.
Game task is to dock together polygonal shapes
to form some funny picture (a tree, a fox, a dog etc.).

The game has minimalistic user interface. Push mouse button down
near the shape center to start shape drag-and-drop operation,
or in shape area near the shape vertex to start shape rotate operation.

Run this module such as:

    python pytang.py option

where option (may be omitted) is one of the following:

    -h - print this help message and exit;
    -d - draw shapes in a draft mode;
    -p - print shapes location after game over before exit.

TODO:
    1. Shapes s.b. dockable, i.e. have a 'sticky edges';
    2. Library of standard images and means to display
        tham on a background are needed;
    3. One of the shapes (a parallelogram shape) is
        not isomorphical, so 'shape mirror' operation is
        needed in UI;
    4. Shapes in non-draft mode m.b. more pretty ;-)

"""


__all__ = []

import sys

import math
from math import pi as PI

import getopt

import pygame
from pygame import display, event, mouse, image, draw
from pygame import QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
pygame.init()

import lines
from lines import distance, inclination, vectorAB

import shapes
from shapes import Triangle, Parallelogram


#---- Global constants

# UI mode
DRAFT_MODE = False
PRINT_OUT = False

# Game display title
TITLE = "pyTang"

# Game field background color
BACKGROUND_COLOR = (0xFF, 0xFF, 0xFF)

# Shape edge color
SHAPE_COLOR = (0x00, 0x00, 0x00)


def _draw_shape_filled(surface, shape):
    """Draw the shape on the given surface.
    
    Arguments:
        surface - drawing surface (an instance of pygame.Surface class);
        shape - shape to draw (an instance of one of the shape classes
            defined in shapes module);
    Result:
        bounding box, defined during the drawing;
    """
    return draw.polygon(surface, SHAPE_COLOR, shape.get_vertices())

def _draw_shape_draft(surface, shape):
    """Draw the shape on the given surface.
    
    Arguments:
        surface - drawing surface (an instance of pygame.Surface class);
        shape - shape to draw (an instance of one of the shape classes
            defined in shapes module);
    Result:
        bounding box, defined during the drawing;
    """
    
    # Get some of the shape attributes
    ref_point = shape.get_ref_point()
    r_inner = shape.get_r_inner()
    
    # Draw the shape edges
    shape_bounds = draw.aalines(
        surface, SHAPE_COLOR, True, shape.get_vertices()
    )
    
    # Draw the shape inner circle
    draw.circle(
        surface, SHAPE_COLOR,
        # NB! draw.circle() expects integer arguments
        map(int, ref_point), int(r_inner),
        1 # circle edge width
    )
    
    # Draw the cross in the inner circle center
    for (a, b) in (
        ((-1, 0), (+1, 0)),
        ((0, +1), (0, -1))
        
    ):
        draw.aaline(
            surface, SHAPE_COLOR,
            *[
                [
                    ref_point[coord] + r_inner / 3 * p[coord]
                    for coord in (0, 1)
                ]
                for p in (a, b)
            ]
        )
    
    return shape_bounds


#----------------------------------------------------------------------
#                        Application main routine
#----------------------------------------------------------------------

def main():
    
    #---- Prepare
    
    # Game field size
    SCREEN_W, SCREEN_H = (640, 420)
    
    # Shape drag machine states
    (ST_MOVE, ST_ROTATE, ST_NONE) = range(3)
    state = ST_NONE
    
    # Setup game window
    display.set_caption(TITLE)
    display.set_icon(image.load('pytang.bmp'))
    
    # Create and setup game field
    screen = display.set_mode((SCREEN_W, SCREEN_H))
    screen.fill(BACKGROUND_COLOR)
    
    # Create a game field copy for internal purposes
    background = screen.copy()
    
    # Game objects - different shapes
    shapes = [
        Triangle((0, 0), (60, 60), (0, 120)),
        Triangle((0, 0), (60, 0), (30, 30)),
        Triangle((60, 0), (120, 0), (120, 60)),
        Triangle((0, 120), (60, 60), (120, 120)),
        Triangle((60, 60), (90, 30), (90, 90)),
        Parallelogram((60, 0), (90, 30), (60, 60)),
        Parallelogram((90, 30), (120, 60), (120, 120))
    ]
    
    # Game object bounding rectangles as a dictionary,
    # where key is the game object instance, and
    # the appropriate value is it's bounding rectangle
    frames = {}
    
    # Each shape is located in a separate cell of the game field
    # at first time. The game field is divided by 3 rows and
    # 3 columns, ergo, 3 x 3 = 9 cells.
    
    # One cell size
    CELL_SIZE = (SCREEN_W / 3, SCREEN_H / 3)
    
    # Shapes initial locations as (column, row) tuples.
    locations = (
        (0, 0), (1, 0), (2, 1),
        (2, 2), (0, 1), (0, 2),
        (2, 0)
    )
    
    if DRAFT_MODE:
        draw_shape = _draw_shape_draft
    else:
        draw_shape = _draw_shape_filled
    
    # Move shapes to the initial locations
    for i in range(len(shapes)):
        shapes[i].move_to(
            [
                (locations[i][coord] + 0.5) * CELL_SIZE[coord]
                for coord in (0, 1)
            ]
        )
        frames[shapes[i]] = draw_shape(screen, shapes[i])
    
    #---- Event loop
    
    do_exit = False
    
    # Shape object which is moving or rotating now
    active_shape = None
    # Mouse previous position, is valid when some shape
    # is rotating or moving
    prev_pos = None
    
    while not do_exit:
        
        display.flip()
        
        for ev in event.get():
            
            # Game is over - user close main window
            if ev.type == QUIT :
                do_exit = True
                break
            
            # Mouse button is push down:
            # user wants to move or rotate one of the shapes
            
            elif (ev.type == MOUSEBUTTONDOWN) and (state == ST_NONE):
                
                touchpoint = mouse.get_pos()
                
                # Search for the first shape including
                # the mouse button down point.
                
                for shape in shapes:
                    
                    if shape.include(touchpoint):
                        
                        active_shape = shape
                        prev_pos = touchpoint
                        
                        # If the touchpoint is laying inside the
                        # inner circle, the shape s.b. moved;
                        # the shape s.b. rotated otherwise
                        if (
                            distance(touchpoint, shape.get_ref_point())
                            <=
                            shape.get_r_inner()
                        ):
                            state = ST_MOVE
                        else:
                            state = ST_ROTATE
                        
                        
                        # Take the active shape from the shapes
                        # common list,
                        # draw other shapes on the background surface.
                        
                        shapes.remove(active_shape)
                        background.fill(BACKGROUND_COLOR)
                        for shape in shapes:
                            draw_shape(background, shape)
                        
                        break
            
            # Mouse button is up: shape moving/rotating is done
            
            elif (ev.type == MOUSEBUTTONUP) and (state != ST_NONE) :
                shapes.append(active_shape)
                active_shape = None
                state = ST_NONE
            
            # Mouse is moving. If the mouse button is down
            # (i.e. if we are in ST_MOVE or ST_ROTATE state),
            # the active shape s.b. moved or rotated.
            
            elif (ev.type == MOUSEMOTION) and (state != ST_NONE) :
                
                screen.blit(
                    background,
                    frames[active_shape].topleft, frames[active_shape]
                )
                
                curr_pos = mouse.get_pos()
                
                if state == ST_MOVE :
                    active_shape.move_by(vectorAB(prev_pos, curr_pos))
                else:
                    active_shape.rotate(
                        inclination(
                            active_shape.get_ref_point(), curr_pos
                        )
                        -
                        inclination(
                            active_shape.get_ref_point(), prev_pos
                        )
                    )
                
                prev_pos = curr_pos
                frames[active_shape] = draw_shape(screen, active_shape)
    
    # Game is over, print shapes location if needed
    if PRINT_OUT:
        for i in range(len(shapes)):
            print "Shape %u vertices:" % (i,)
            for vertex in shapes[i].get_vertices():
                print "\t (%.2f, %.2f)" % vertex


#----------------------------------------------------------------------
#                        Application entry point
#----------------------------------------------------------------------


if __name__ == '__main__':
    
    (opts, args) = getopt.getopt(sys.argv[1 : ], 'dhp')
    for option, value in opts:
        
        if option == '-h':
            print __doc__
            exit()
        
        if option == '-d':
            DRAFT_MODE = True
        
        if option == '-p':
            PRINT_OUT = True
    
    main()
