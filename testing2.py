import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

def functor(x):
    # Convert input to numpy array to handle scalar and array inputs uniformly
    x = np.array(x)
    
    # Apply the function element-wise using numpy's vectorized operations
    result = np.where(x > 0, 1/x, np.nan)
    
    return result

def functor2(x):
    # Convert input to numpy array to handle scalar and array inputs uniformly
    
    return np.sin(x)

def functor3(x):
    # Convert input to numpy array to handle scalar and array inputs uniformly
    
    return x**2

TITLE = "f(x) = " + fr"$1/x$"
XSP = np.linspace(0, 4, 1000)
YLIM = [0,12]
fn = functor
n = 20
pace = 2
# Define the Cauchy sequence as a list of tuples
SEQUENCE = [(x, x - 1/(pace*(i+1))) for i, x in enumerate(list(reversed(np.linspace(0,1,n))))]

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        self.setParent(parent)

        self.function = fn  # Example function (sin(x))
        self.xsp = XSP

        self.plot_function()

    def plot_function(self):
        self.ax.clear()

        # Generate points for plotting the function curve
        x = self.xsp
        y = self.function(x)

        # Plot the function curve
        self.ax.plot(x, y,color='blue')

        # Set plot labels and title
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('f(x)')
        self.ax.set_title(TITLE)
        self.ax.legend()
        self.ax.set_ylim(YLIM)
        # self.ax.set_yscale('log')

               # Store default axis limits
        self.default_xlim = self.ax.get_xlim()
        self.default_ylim = self.ax.get_ylim()
        # Draw the plot
        self.draw()

    def draw_lines(self, lines):
        self.ax.clear()  # Clear previous lines and function plot

        # Plot the function curve
        x = self.xsp
        y = self.function(x)
        self.ax.plot(x, y, color='blue')

        # Draw the lines from the provided list of lists of tuples
        for line in lines:
            if line[0] == 'h':
                y = line[1]
                x1, x2 = line[2], line[3]
                color = line[4]
                self.ax.hlines(y, x1, x2, color=color)
            elif line[0] == 'v':
                x = line[1]
                y1, y2 = line[2], line[3]
                color = line[4]
                self.ax.vlines(x, y1, y2, color=color)

        # Set plot labels and title
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('f(x)')
        self.ax.set_title('Function Graph')
        self.ax.legend()
        self.ax.set_xlim(self.default_xlim)
        self.ax.set_ylim(self.default_ylim)
        # Redraw the plot
        self.draw()

def get_line_sets(cauchy_sequence, func):
    line_sets = []
    for (x1, x2) in cauchy_sequence:
        lines = []
        y1 = func(x1)
        y2 = func(x2)
        lines.append(('v', x1, 0, y1, 'green'))
        lines.append(('v', x2, 0, y2, 'green'))
        lines.append(('h', y1, 0, x1, 'green'))
        lines.append(('h', y2, 0, x2, 'green'))
        line_sets.append(lines)
    return line_sets


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        n = 30
        distances = [1/i for i in range(1,n)]
        # Define the Cauchy sequence as a list of tuples
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.canvas = PlotCanvas(self.central_widget, width=5, height=4, dpi=100)
        layout.addWidget(self.canvas)
        n = 20
        pace = 10
        # Define the Cauchy sequence as a list of tuples
        cauchy_sequence = SEQUENCE
        self.button_draw_lines = QPushButton('Draw Lines')
        self.button_draw_lines.clicked.connect(self.draw_next_lines)
        layout.addWidget(self.button_draw_lines)

        self.line_sets = get_line_sets(cauchy_sequence=cauchy_sequence, func=self.canvas.function)

        self.current_line_set = 0

    def draw_next_lines(self):
        # Increment current_line_set and wrap around if necessary
        self.current_line_set = (self.current_line_set + 1) % len(self.line_sets)

        # Get the current set of lines to draw
        lines_to_draw = self.line_sets[self.current_line_set]

        # Draw lines on the canvas
        self.canvas.draw_lines(lines_to_draw)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.setGeometry(100, 100, 800, 600)
    main_win.show()
    sys.exit(app.exec_())
