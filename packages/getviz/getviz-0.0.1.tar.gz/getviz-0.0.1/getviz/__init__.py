import math
import matplotlib.pyplot as plt
import numpy as np
import random



def create_bar_graph(num_points, x_axis_name, y_axis_name):
    x_values = []
    y_values = []

    for i in range(num_points):
        x = float(input(f"Enter x-coordinate for point {i+1}: "))
        y = float(input(f"Enter y-coordinate for point {i+1}: "))
        x_values.append(x)
        y_values.append(y)

    # Sort the coordinates based on x-axis values
    sorted_indices = np.argsort(x_values)
    x_values = np.array(x_values)[sorted_indices]
    y_values = np.array(y_values)[sorted_indices]

    # Determine the axis limits based on the minimum and maximum x-axis values
    x_min = min(x_values)
    x_max = max(x_values)
    y_max = max(y_values)

    # Determining the length of intervals
    length_x = len(str(x_max))
    determining_factor_x = math.pow(10, length_x - 1)
    length_y = len(str(y_max))
    determining_factor_y = math.pow(10, length_y - 1)

    # Set the axis limits and intervals
    plt.xlim(x_min - 1, x_max + 1)
    plt.ylim(0, y_max + 1)
    plt.xticks(np.arange(x_min, x_max + 1, determining_factor_x))
    plt.yticks(np.arange(0, y_max + 1, determining_factor_y))

    # Remove spines and ticks
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False)

    # Plotting the bar graph
    plt.bar(x_values, y_values, width=0.3, align='center')
    plt.xlabel(x_axis_name)
    plt.ylabel(y_axis_name)
    plt.title("Bar Graph")

    # Show x-axis and y-axis labels with a distance of determining_factor_x and determining_factor_y, respectively
    x_tick_labels = np.arange(x_min, x_max + 1, determining_factor_x)
    y_tick_labels = np.arange(0, y_max + 1, determining_factor_y)
    plt.xticks(x_tick_labels, [str(int(label)) for label in x_tick_labels])
    plt.yticks(y_tick_labels, [str(int(label)) for label in y_tick_labels])

    plt.show()

    
        
def plot_function():
    # Get the function expression from the user
    expression = input("Enter the function expression: ")
    try:
        # Create a lambda function from the expression
        func = lambda x: eval(expression)

        # Generate x values
        x = np.linspace(-10, 10, 100)

        # Evaluate the function for the given x values
        y = func(x)

        # Create the plot
        plt.plot(x, y)

        # Set labels and title
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title("Graph of the Function")

        # Display the plot
        plt.show()

    except:
        print("Invalid function expression!")
        
        

def create_line_graph(num_points, x_axis_name, y_axis_name):
    x_values = []
    y_values = []

    for i in range(num_points):
        x = float(input(f"Enter x-coordinate for point {i + 1}: "))
        y = float(input(f"Enter y-coordinate for point {i + 1}: "))
        x_values.append(x)
        y_values.append(y)

    # Sort the coordinates based on x-axis values
    sorted_indices = np.argsort(x_values)
    x_values = np.array(x_values)[sorted_indices]
    y_values = np.array(y_values)[sorted_indices]

    # Determine the axis limits based on the minimum and maximum x-axis values
    x_min = min(x_values)
    x_max = max(x_values)
    y_max = max(y_values)

    # Determining the length of intervals
    length_x = len(str(x_max))
    determining_factor_x = math.pow(10, length_x - 1)
    length_y = len(str(y_max))
    determining_factor_y = math.pow(10, length_y - 1)

    # Set the axis limits and intervals
    plt.xlim(x_min - 1, x_max + 1)
    plt.ylim(0, y_max + 1)
    plt.xticks(np.arange(x_min, x_max + 1, determining_factor_x))
    plt.yticks(np.arange(0, y_max + 1, determining_factor_y))

    # Remove spines and ticks
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False)

    # Plotting the line graph
    plt.plot(x_values, y_values, marker='o', linestyle='-')
    plt.xlabel(x_axis_name)
    plt.ylabel(y_axis_name)
    plt.title("Line Graph")

    plt.show()
    


def create_gantt_chart(num_points):
    tasks = []
    start_times = []
    durations = []

    # Generate random colors for each task
    colors = ['#'+ ''.join(random.choices('0123456789ABCDEF', k=6)) for _ in range(num_points)]

    for i in range(num_points):
        task = input(f"Enter the name of task {i+1}: ")
        start_time = float(input(f"Enter the start time for task {i+1}: "))
        duration = float(input(f"Enter the duration for task {i+1}: "))

        tasks.append(task)
        start_times.append(start_time)
        durations.append(duration)

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Set y-axis limits
    ax.set_ylim(0, 10)

    # Set x-axis limits
    ax.set_xlim(0, max(start_times) + max(durations))

    # Set y-axis tick labels
    ax.set_yticks([5])
    ax.set_yticklabels(['Tasks'])

    # Plot the Gantt bars with different colors
    for i in range(num_points):
        ax.broken_barh([(start_times[i], durations[i])], (4, 2), facecolors=colors[i])

        # Add task labels
        ax.text(start_times[i] + durations[i] / 2, 5.5, tasks[i], ha='center', va='center')

    # Remove spines and ticks
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(left=False, bottom=False)

    # Set labels and title
    ax.set_xlabel('Time')
    ax.set_title('Gantt Chart')

    plt.show()
    
    
    
def create_pie_chart(num_parts):
    parts = []
    labels = []
    total = 0

    for i in range(num_parts):
        part = float(input(f"Enter the portion for part {i+1}: "))
        label = input(f"Enter the name for part {i+1}: ")
        parts.append(part)
        labels.append(f"{label}: {part}")
        total += part

    # Remove spines and ticks
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False)

    # Create pie chart
    plt.pie(parts, labels=labels, autopct='%1.1f%%')

    # Add title and total portion
    plt.title("Pie Chart")
    plt.xlabel(f"Total Portion: {total}")

    plt.show()



def create_scatter_chart(num_points, x_axis_name, y_axis_name):
    x_values = []
    y_values = []

    for i in range(num_points):
        x = float(input(f"Enter x-coordinate for point {i + 1}: "))
        y = float(input(f"Enter y-coordinate for point {i + 1}: "))
        x_values.append(x)
        y_values.append(y)

    # Set the axis limits and intervals
    x_min = min(x_values)
    x_max = max(x_values)
    y_max = max(y_values)

    # Remove spines and ticks
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False)

    # Plotting the scatter chart
    plt.scatter(x_values, y_values)
    plt.xlabel(x_axis_name)
    plt.ylabel(y_axis_name)
    plt.title("Scatter Chart")

    plt.show()