import bqplot as bq
from ipywidgets import widgets
import numpy as np
from time import sleep
from BNumMet import Random


class RandomVisualizer:
    def __init__(self, random_generator=Random.genrand):
        """
        Initializes the RandomVisualizer class.

        Parameters
        ----------
        randGenerator : RandomGenerator
            The random generator to use. It is a function that does not take any parameters and returns a random number between 0 and 1.
        """
        self.random_generator = random_generator
        self.generated_numbers = []
        self.current_value = 0
        self.iterations = 100
        self.current_iteration = 0
        self.inside_circle = 0

    def initialize_components(self):
        """
        Initializes the components of the visualizer.
        """
        # Figure 1: Circle inside a square of side 1 centered at the origin
        # =================================================================================================
        self.figure1 = bq.Figure(title="Montecarlo's method")

        self.x_sc = bq.LinearScale()  # x scale
        self.y_sc = bq.LinearScale()  # y scale
        ax_x = bq.Axis(scale=self.x_sc, grid_lines="solid", label="X")
        ax_y = bq.Axis(
            scale=self.y_sc,
            orientation="vertical",
            grid_lines="solid",
            label="Y",
        )
        # Set up the plot figure
        self.figure1 = bq.Figure(
            marks=[],  # marks
            axes=[ax_x, ax_y],  # axes
            title="Montecarlo's Method",  # title
        )

        # Draw the square
        self.square = bq.Lines(
            x=[0, 1, 1, 0, 0],
            y=[0, 0, 1, 1, 0],
            scales={"x": self.x_sc, "y": self.y_sc},
            colors=["black"],
        )
        self.figure1.marks = [self.square]
        # Draw the full circle centered at (0.5, 0.5) with radius 0.5
        x = np.linspace(0, 1, 1000)
        y = np.sqrt(1 / 4 - (x - 0.5) ** 2)
        y = np.concatenate((y, -y))  # y
        y += 0.5
        x = np.concatenate((x, (x[::-1])))  # x

        self.circle = bq.Lines(
            x=x,
            y=y,
            scales={"x": self.x_sc, "y": self.y_sc},
            colors=["red"],
            stroke_width=5,
        )
        self.figure1.marks = [self.square, self.circle]

        # Prepare the figure for the points
        self.points = bq.Scatter(
            x=[],
            y=[],
            scales={"x": self.x_sc, "y": self.y_sc},
            colors=["blue"],
            default_size=2,
        )
        self.figure1.marks = [self.points, self.square, self.circle]

        # Figure 2: (Current value and Pi) vs. (Number of iterations)
        # =================================================================================================
        self.figure2 = bq.Figure(title="Convergence of Pi", legend_location="top-right")
        self.x_sc2 = bq.LinearScale()  # x scale
        self.y_sc2 = bq.LinearScale()  # y scale
        ax_x2 = bq.Axis(
            scale=self.x_sc2, grid_lines="solid", label="Number of iterations"
        )
        ax_y2 = bq.Axis(
            scale=self.y_sc2,
            orientation="vertical",
            grid_lines="solid",
            label="Value",
        )

        self.x_sc2.min = 0
        self.x_sc2.max = self.iterations  # Number of iterations **

        # Set up the plot figure
        self.figure2 = bq.Figure(
            marks=[],  # marks
            axes=[ax_x2, ax_y2],  # axes
            title="Convergence of Pi",  # title
        )  # this will change as the algorithm runs

        # Draw the line of Pi
        x = np.linspace(0, self.iterations, 1000)
        y = np.full(1000, np.pi)
        self.pi_line = bq.Lines(
            x=x,
            y=y,
            scales={"x": self.x_sc2, "y": self.y_sc2},
            colors=["red"],
            labels=["Pi"],
            display_legend=True,
        )
        self.figure2.marks = [self.pi_line]

        # Prepare the figure for the current value update
        self.current_value_line = bq.Lines(
            x=[],
            y=[],
            scales={"x": self.x_sc2, "y": self.y_sc2},
            colors=["blue"],
            labels=["Current Value"],
            display_legend=True,
        )
        self.figure2.marks = [self.pi_line, self.current_value_line]

        # Widget: Number of Points to generate
        # =================================================================================================
        self.iterations_widget = widgets.BoundedIntText(
            value=self.iterations,
            min=1,
            max=10000,
            description="Iterations:",
            disabled=False,
        )

        # Widget: Button for running the algorithm
        # =================================================================================================
        self.run_button = widgets.Button(
            description="Run",
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltip="Run",
            icon="check",  # (FontAwesome names without the `fa-` prefix)
        )
        # Observer: Button for running the algorithm
        self.run_button.on_click(self.play_montecarlo)

        self.pi_value = widgets.FloatText(  # Widget: Pi value
            value=0,
            description="$\pi$:",
            disabled=True,
        )
        # Widget: Grid
        # =================================================================================================
        self.grid = widgets.GridspecLayout(4, 4)
        self.grid[0:2, 0:2] = self.figure1
        self.grid[2:4, 0:4] = self.figure2
        self.grid[0:1, 2:4] = widgets.VBox([self.iterations_widget, self.run_button])

        self.grid[1:2, 2:4] = self.pi_value

    def number_of_iterations(self):
        """
        Updates the number of iterations. This is called when the user plays the animation. It configures the x axis of the second figure. and the number of iterations of the algorithm.
        """
        self.iterations = self.iterations_widget.value
        self.x_sc2.max = self.iterations
        self.pi_line.x = np.linspace(0, self.iterations, 1000)

    def play_montecarlo(self, b):
        """
        Plays the montecarlo algorithm.
        """
        self.number_of_iterations()
        self.current_iteration = 0
        self.generated_numbers = []
        self.current_value = 0
        self.inside_circle = 0
        self.points.x = []
        self.points.y = []
        self.current_value_line.x = []
        self.current_value_line.y = []
        self.total_points = 0
        self.run_button.disabled = True

        batch_coords = []
        batch_current_value = []
        batch_current_iteration = []
        batch_size = int(self.iterations / 100) * (2 if self.iterations < 2000 else 5)

        for self.current_iteration in range(self.iterations):
            new_x = self.random_generator()
            new_y = self.random_generator()
            self.total_points += 1

            batch_coords.append([new_x, new_y])
            if ((new_x - 0.5) ** 2 + (new_y - 0.5) ** 2) <= 0.25:
                self.inside_circle += 1
            batch_current_value.append(4 * self.inside_circle / self.total_points)

            batch_current_iteration.append(self.current_iteration)

            if (
                len(batch_coords) >= batch_size
                or self.current_iteration == self.iterations - 1
            ):
                aux = self.generated_numbers + batch_coords
                with self.grid.hold_sync():
                    with self.points.hold_sync():
                        self.points.x = [x[0] for x in aux]
                        self.points.y = [x[1] for x in aux]
                    with self.current_value_line.hold_sync():
                        self.current_value_line.x = (
                            list(self.current_value_line.x) + batch_current_iteration
                        )  # [x for x in self.current_value_line.x] + batch_current_iteration
                        self.current_value_line.y = (
                            list(self.current_value_line.y) + batch_current_value
                        )  # [x for x in self.current_value_line.y] + batch_current_value
                    self.pi_value.value = batch_current_value[-1]
                    self.generated_numbers += batch_coords

                batch_coords = []
                batch_current_value = []
                batch_current_iteration = []

        self.run_button.disabled = False

    def run(self):
        """
        Runs the visualizer.
        """
        self.initialize_components()
        return self.grid
