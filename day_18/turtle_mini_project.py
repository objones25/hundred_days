import turtle
import random

# Set up the turtle
tim = turtle.Turtle()
screen = turtle.Screen()
turtle.colormode(255)

def random_color():
    """Generate random RGB color"""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)

def draw_shapes():
    """Draw different shapes from triangle to decagon"""
    for sides in range(3, 11):
        tim.pencolor(random_color())
        angle = 360 / sides
        for _ in range(sides):
            tim.forward(100)
            tim.right(angle)

def draw_random_walk():
    """Create a random walk pattern"""
    directions = [0, 90, 180, 270]
    tim.pensize(10)
    tim.speed("fastest")
    
    for _ in range(200):
        tim.color(random_color())
        tim.forward(30)
        tim.setheading(random.choice(directions))

def draw_spirograph(gap_size):
    """Draw a spirograph pattern"""
    tim.speed("fastest")
    
    for angle in range(0, 360, gap_size):
        tim.pencolor(random_color())
        tim.circle(100)
        tim.setheading(angle)

# Main execution
def main():
    # Drawing different shapes
    tim.pen(pensize=2)
    draw_shapes()
    tim.clear()
    
    # Random walk
    draw_random_walk()
    tim.clear()
    
    # Spirograph
    draw_spirograph(5)
    
    screen.exitonclick()

if __name__ == "__main__":
    main()