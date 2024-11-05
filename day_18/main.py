import turtle as t
import random

# Set up the turtle and color mode
t.colormode(255)
tim = t.Turtle()
tim.speed("fastest")
tim.penup()
tim.hideturtle()

# Color list from the image
color_list = [(202, 164, 109), (238, 240, 245), (150, 75, 49), (223, 201, 135), 
              (52, 93, 124), (172, 154, 40), (140, 30, 19), (133, 163, 185), 
              (198, 91, 71), (46, 122, 86), (72, 43, 35), (145, 178, 148), 
              (13, 99, 71), (233, 175, 164), (161, 142, 158), (105, 74, 77), 
              (55, 46, 50), (183, 205, 171), (36, 60, 74), (18, 86, 90), 
              (81, 148, 129), (148, 17, 20), (14, 70, 64), (30, 68, 100), 
              (107, 127, 153), (174, 94, 97), (176, 192, 209)]

# Position turtle to start bottom left
tim.setheading(225)
tim.forward(300)
tim.setheading(0)

# Draw dots
number_of_dots = 100

for dot_count in range(1, number_of_dots + 1):
    tim.dot(20, random.choice(color_list))
    tim.forward(50)
    
    # Move to next line after every 10 dots
    if dot_count % 10 == 0:
        tim.setheading(90)    # Turn upward
        tim.forward(50)       # Move up
        tim.setheading(180)   # Turn left
        tim.forward(500)      # Move to start of next line
        tim.setheading(0)     # Face right again

screen = t.Screen()
screen.exitonclick()