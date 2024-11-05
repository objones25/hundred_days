from turtle import Turtle, Screen
import random

def create_turtle(color, y_position):
    """Create and initialize a single turtle racer"""
    new_turtle = Turtle(shape="turtle")
    new_turtle.penup()
    new_turtle.color(color)
    new_turtle.goto(x=-230, y=y_position)
    return new_turtle

def setup_race_track(screen, width, height):
    """Setup the race track with start and finish lines"""
    track_designer = Turtle()
    track_designer.hideturtle()
    track_designer.penup()
    
    # Draw finish line
    track_designer.goto(230, 150)
    track_designer.pendown()
    track_designer.goto(230, -150)
    
    # Draw start line
    track_designer.penup()
    track_designer.goto(-230, 150)
    track_designer.pendown()
    track_designer.goto(-230, -150)

def display_race_info(screen, colors):
    """Display race information and get user bet"""
    # Create color options string
    color_options = ", ".join(colors)
    
    # Get user bet with input validation
    while True:
        bet = screen.textinput(
            title="🐢 Make your bet 🐢",
            prompt=f"Which turtle will win?\nChoose from: {color_options}"
        )
        if bet and bet.lower() in colors:
            return bet.lower()
        elif bet:  # If bet is invalid but not None
            screen.textinput(
                title="Invalid Color!",
                prompt=f"Please choose from: {color_options}"
            )

def run_race(all_turtles):
    """Execute the race logic"""
    is_race_on = True
    winner = None
    
    while is_race_on:
        for turtle in all_turtles:
            # Check if turtle has crossed finish line (230 = 250 - half turtle width)
            if turtle.xcor() > 230:
                is_race_on = False
                winner = turtle
                break
                
            # Generate random movement (weighted towards middle values)
            rand_distance = random.randint(1, 6) + random.randint(1, 6)
            turtle.forward(rand_distance)
    
    return winner

def main():
    # Initialize screen
    screen = Screen()
    screen.setup(width=500, height=400)
    screen.title("🐢 Turtle Racing Championship 🐢")
    
    # Define race parameters
    colors = ["red", "orange", "yellow", "green", "blue", "purple"]
    y_positions = [-70, -40, -10, 20, 50, 80]
    
    # Setup race track
    setup_race_track(screen, 500, 400)
    
    # Get user bet
    user_bet = display_race_info(screen, colors)
    
    # Create and store all turtles
    all_turtles = [
        create_turtle(colors[i], y_positions[i])
        for i in range(len(colors))
    ]
    
    # Start the race if bet was placed
    if user_bet:
        # Run the race
        winning_turtle = run_race(all_turtles)
        winning_color = winning_turtle.pencolor()
        
        # Display results
        result_turtle = Turtle()
        result_turtle.hideturtle()
        result_turtle.penup()
        result_turtle.goto(0, 160)
        
        if winning_color == user_bet:
            result_turtle.color("green")
            result_turtle.write(
                f"🎉 You've won! The {winning_color} turtle is the winner! 🎉",
                align="center",
                font=("Arial", 16, "bold")
            )
        else:
            result_turtle.color("red")
            result_turtle.write(
                f"💔 You've lost! The {winning_color} turtle is the winner! 💔",
                align="center",
                font=("Arial", 16, "bold")
            )
    
    screen.exitonclick()

if __name__ == "__main__":
    main()