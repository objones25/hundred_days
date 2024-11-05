from turtle import Turtle, Screen

# Initialize turtle and screen
tim = Turtle()
screen = Screen()

# Movement functions
def move_forwards():
    tim.forward(10)

def move_backwards():
    tim.backward(10)

def turn_left():
    new_heading = tim.heading() + 10
    tim.setheading(new_heading)

def turn_right():
    new_heading = tim.heading() - 10
    tim.setheading(new_heading)

def clear():
    tim.clear()
    tim.penup()
    tim.home()
    tim.pendown()

def toggle_pen():
    if tim.isdown():
        tim.penup()
    else:
        tim.pendown()

# Initial turtle settings
tim.speed("fastest")
tim.pensize(2)

# Set up screen
screen.title("Etch-A-Sketch")
screen.setup(width=600, height=600)

# Display instructions
tim.penup()
tim.goto(-280, 260)
tim.write("Arrow Keys = Move, Space = Toggle Pen, C = Clear", 
          font=("Arial", 12, "normal"))
tim.goto(0, 0)
tim.pendown()

# Set up key bindings
screen.listen()
screen.onkey(move_forwards, "Up")
screen.onkey(move_backwards, "Down")
screen.onkey(turn_left, "Left")
screen.onkey(turn_right, "Right")
screen.onkey(clear, "c")
screen.onkey(toggle_pen, "space")

# Keep the window open
screen.exitonclick()