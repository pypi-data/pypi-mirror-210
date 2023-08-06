import bqplot as bq
import numpy as np
from ipywidgets import widgets
from BNumMet.NonLinear import zBrentDekker


class NonLinearVisualizer:
    def __init__(
        self, fun=lambda x: (x - 1) * (x - 4) * np.exp(-x), interval=(0, 3), tol=1e-3
    ):
        # Initialize basic Parameters
        self.brent_dekker = zBrentDekker(
            fun, interval, tol, iters=True, steps=True
        )  # Get the output of Brent Dekkers Alg --> (x, iters)

        # Set the input function, the interval for the function evaluation,
        # and the tolerance for the algorithm
        self.f = fun
        self.a, self.b = interval
        self.fa, self.fb = self.f(self.a), self.f(self.b)

        # Check that the function has a zero in the interval
        if self.f(self.a) * self.f(self.b) > 0:
            raise ValueError("The function has no zeros in the given interval")

        # Set the tolerance and initial values for data variables
        self.t = tol
        self.original_data = (self.a, self.b)
        self.iterations = 0

        # First Step of the Algorithm
        # ==========================================================================
        ## Section: INT
        # Set the initial values for internal variables
        self.c, self.fc, self.e = self.a, self.fa, self.b - self.a
        ## Section: EXT
        # Call the sectionEXT() function to perform the first external section of the algorithm
        self.section_ext()

        # Current Step Save Values
        # ==========================================================================
        # Save the current state of the algorithm in a tuple
        self.current_step = (self.a, self.b, self.c, self.e)

        # Revert Stack
        # ==========================================================================
        # Create an empty stack to keep track of previous states of the algorithm
        self.revert_stack = []

        # Draw mesh
        # ==========================================================================
        # Create a numpy array of 1000 evenly spaced values between the minimum and maximum
        # values of the function interval to use for plotting the function
        self.x = np.linspace(min(self.a, self.b), max(self.a, self.b), 1000)
        self.widen = False

    def checkbox_changed(self, change):
        with self.fig.hold_sync():  # Hold the figure syncronized
            self.draw_figures()  # Draw the figures

    def section_int(self):
        # Check if the function evaluates with the same sign on both sides of c
        if np.sign(self.fb) == np.sign(self.fc) != 0:
            # If the condition is met, update the values of c, fc and e
            self.c, self.fc, self.e = self.a, self.fa, self.b - self.a

    def section_ext(self):
        # Check which of the endpoints has the smaller absolute value of f
        if abs(self.fc) < abs(self.fb):
            # If the condition is met, swap the values of a, b and c with b, c and b respectively,
            # and update the values of fa, fb and fc accordingly
            self.a, self.b, self.c, self.fa, self.fb, self.fc = (
                self.b,
                self.c,
                self.b,
                self.fb,
                self.fc,
                self.fb,
            )

    def initialize_components(self):
        # Current Solution Text
        # ==========================================================================
        # Widget for displaying current solution output
        # Current Solution: (b, f(b))
        # Iterations: N
        self.current_solution_output = widgets.Output()

        # Helper Text
        # ==========================================================================
        # Widget for displaying helper output
        # Suggestion for next step: <Bisect/IQI/Secant>
        self.helper_output = widgets.Output()  # Next Possible Step: <Bisect/IQI/None>

        # Brent-Dekker Solution
        # ==========================================================================
        # Widget for displaying Brent-Dekker solution output
        # Brent-Dekker Solution: (x^, f(x^)) in N^ iterations
        self.brent_dekker_output = widgets.HTML(
            value=f"<blockquote> Brent-Dekker Solution: <b>({self.brent_dekker[0]:.4e}, {self.f(self.brent_dekker[0]):.4e})</b> in <b>{self.brent_dekker[1]}</b> iterations"
        )

        # Reset Button
        # ==========================================================================
        # Widget for reset button
        self.reset_button = widgets.Button(
            description="Reset",
            disabled=False,
            button_style="danger",
            tooltip="Reset",
            icon="undo",
        )
        self.reset_button.on_click(self.reset)

        # Revert Button
        # ==========================================================================
        # Widget for revert button
        self.revert_button = widgets.Button(
            description="Revert",
            disable=False,
            button_style="warning",
            tooltip="Revert",
            icon="arrow-left",
        )
        self.revert_button.on_click(self.revert)

        # FIGURE
        # ==========================================================================
        # Widget for plotting the function and its zeros
        # Set up axes and scales for the plot
        self.x_sc = bq.LinearScale()
        self.y_sc = bq.LinearScale()
        ax_x = bq.Axis(scale=self.x_sc, grid_lines="solid", label="X")
        ax_y = bq.Axis(
            scale=self.y_sc,
            orientation="vertical",
            tick_format="0.4e",
            grid_lines="solid",
            label="Y",
        )
        # Set up the plot figure
        self.fig = bq.Figure(
            marks=[],
            axes=[ax_x, ax_y],
            title="Zeros of a Function",
        )
        # Set up the plot figure toolbar
        self.toolbar = bq.Toolbar(figure=self.fig)
        # Add default lines to the plot figure
        self.default_lines()

        # FUNCTION BUTTONS
        # ==========================================================================
        # Widgets for buttons for selecting the next function to perform
        # Each button has a pointIndex attribute that is used to identify the point in the points array
        # 0: Bisect  1: Secant  2: IQI
        # Bisect Button
        self.bisect_button = widgets.Button(
            description="Bisect",
            disabled=False,
            tooltip="Bisect",
        )
        self.bisect_button.pointIndex = 0
        self.bisect_button.on_click(self.next_step)

        # Secant Button
        self.secant_button = widgets.Button(
            description="Secant",
            disabled=False,
            tooltip="Secant",
        )
        self.secant_button.pointIndex = 1
        self.secant_button.on_click(self.next_step)

        # IQI Button
        self.iqi_button = widgets.Button(
            description="IQI",
            disabled=False,
            tooltip="IQI",
        )
        self.iqi_button.pointIndex = 2
        self.iqi_button.on_click(self.next_step)

        # CHECKBOXES FOR FUNCTION BUTTONS
        # ==========================================================================
        self.bisect_checkbox = widgets.Checkbox(
            value=False,
            description="Bisect",
            disabled=False,
            indent=False,
        )
        # On change of checkbox, function checkBoxChanged
        self.bisect_checkbox.observe(self.checkbox_changed, names="value")

        self.secant_checkbox = widgets.Checkbox(
            value=False,
            description="Secant",
            disabled=False,
            indent=False,
        )
        self.secant_checkbox.observe(self.checkbox_changed, names="value")

        self.iqi_checkbox = widgets.Checkbox(
            value=False,
            description="IQI",
            disabled=False,
            indent=False,
        )
        self.iqi_checkbox.observe(self.checkbox_changed, names="value")

        # GRID
        # ==========================================================================
        self.grid = widgets.GridspecLayout(2, 2)
        self.grid[0, 0] = widgets.VBox([self.toolbar, self.fig])

        # Text Outputs Group
        texts_group = widgets.VBox(
            [self.current_solution_output, self.helper_output, self.brent_dekker_output]
        )
        self.grid[1, 0] = texts_group

        # Buttons Group
        text1 = widgets.HTML(value="<b>Next Step Selector</b>")  # Next Step Selector
        text2 = widgets.HTML(value="<b>Draw Step?</b>")  # Draw Step?
        selectors = widgets.VBox(  # Next Step Selectors
            [text1, self.bisect_button, self.secant_button, self.iqi_button]
        )
        checkboxes = widgets.VBox(
            [text2, self.bisect_checkbox, self.secant_checkbox, self.iqi_checkbox]
        )
        buttons_group = widgets.HBox([selectors, checkboxes])

        self.grid[0, 1] = buttons_group

        # Reset and Revert Buttons Group
        buttons_group_2 = widgets.HBox(
            [
                self.revert_button,
                self.reset_button,
            ]
        )
        self.grid[1, 1] = buttons_group_2

    def default_lines(self):
        # 0. Horizontal Line f(x)=0
        self.horizontal_line = bq.Lines(  # Horizontal Line f(x)=0
            x=self.x,
            y=[0] * len(self.x),
            scales={"x": self.x_sc, "y": self.y_sc},
            enable_move=False,
            enable_add=False,
            colors=["Black"],
        )
        # 1. Function Line f(x)
        self.function_line = bq.Lines(  # Function Line f(x)
            x=self.x,
            y=list(map(self.f, self.x)),
            scales={"x": self.x_sc, "y": self.y_sc},
            labels=["f(x)"],
            display_legend=False,
            enable_move=False,
            enable_add=False,
            colors=["Gray"],
            line_style="dashed",
        )

    def next_step(self, b):
        """
        This function is called when a button is clicked

        Parameters
        ----------
        b : Button
            The button that was clicked

        Returns
        -------
        None.
        """

        if self.hint_step is None:
            return
        self.revert_stack.append(
            [self.a, self.b, self.c, self.e, self.iterations]
        )  # Add the current state to the revert stack

        self.a = self.b  # Set a = b
        self.fa = self.fb  # Set f(a) = f(b)

        new_point_b = self.next_points_addition[b.pointIndex]  # Get the next point
        self.b = (
            new_point_b
            if abs(self.b - new_point_b) > self.tolerance
            else self.b + np.sign(0.5 * (self.c - self.b)) * self.tolerance
        )  # If the new point is too close to the current point, move it a little bit
        self.fb = self.f(self.b)  # Set f(b) = f(newB)
        if b.pointIndex != 1:
            self.e = self.errs[b.pointIndex]  # Set e = error
        self.iterations += 1  # Increment the number of iterations

        # Section: Ext
        self.section_ext()  # Update the section
        # Section: Int
        self.section_int()  # Update the section

        self.one_step()  # Update the plot

    def reset(self, b):
        """
        Reset everything to the initial state, this can be understood as reverting all the steps
        """
        if len(self.revert_stack) == 0:
            return

        self.a, self.b, self.c, self.e, self.iterations = self.revert_stack[
            0
        ]  # Get the initial state
        self.fb = self.f(self.b)  # Set f(b) = f(newB)
        self.fa = self.f(self.a)  # Set f(a) = f(b)
        self.fc = self.f(self.c)  # Set f(c) = f(newC)

        self.revert_stack = []  # Clear the revert stack
        self.one_step()  # Update the plot

    def revert(self, b):
        """
        This method reverts the last step
        """
        if len(self.revert_stack) == 0:  # If there is no step to revert
            return

        (
            self.a,
            self.b,
            self.c,
            self.e,
            self.iterations,
        ) = self.revert_stack.pop()  # Get the last state
        self.fb = self.f(self.b)  # Set f(b) = f(newB)
        self.fa = self.f(self.a)  # Set f(a) = f(b)
        self.fc = self.f(self.c)  # Set f(c) = f(newC)

        self.one_step()  # Update the plot

    def one_step(self):
        """
        This method is called when a step is made
        """
        with self.grid.hold_sync():  # Hold the grid syncronized
            self.brent_dekker_step()  # Update the Brent-Dekker step
            self.iqi_button.disabled = (
                self.next_points_addition[2] is None
            )  # Disable the IQI button if the IQI point is None
            self.iqi_checkbox.disabled = (
                self.next_points_addition[2] is None
            )  # Disable the IQI checkbox if the IQI point is None

            self.update_ouputs()  # Update the outputs
            with self.fig.hold_sync():  # Hold the figure syncronized
                self.draw_figures()  # Draw the figures
            # self.drawFigures()

    def draw_figures(self):
        """
        This method draws the figures
        1. The function
        2. Dot for the current solution
        3. The next step suggestions
        4. if checkboxes are checked, the steps are drawn
        """

        def draw_point(point, value, color, label, marker, legend=True):
            return bq.Scatter(
                x=[point],
                y=[value],
                scales={"x": self.x_sc, "y": self.y_sc},
                colors=[color],
                default_size=100,
                stroke="black",
                display_legend=legend,
                labels=[label],
                marker=marker,
            )  # Draw a point

        def secant_draw():
            # Draws a line on whole self.x range with the secant equation on the points (b, fb) and (self.nextPoints_addition[1], self.f(self.nextPoints_addition[1]))
            secant = bq.Lines(
                x=self.x,
                y=[
                    self.fb + (self.fa - self.fb) / (self.a - self.b) * (x - self.b)
                    for x in self.x
                ],
                scales={"x": self.x_sc, "y": self.y_sc},
                colors=["red"],
                display_legend=True,
                labels=["Secant Line"],
                line_style="dashed",
            )  # Draw a line
            return secant

        def bisect_draw(m, min_y, max_y):
            # m = (a + b) / 2
            # draw a vertical line at m
            bisect = bq.Lines(
                x=[m, m],
                y=[min_y, max_y],
                scales={"x": self.x_sc, "y": self.y_sc},
                colors=["green"],
                display_legend=True,
                labels=["Bisect Line"],
                line_style="dashed",
            )  # Draw a line
            return bisect

        def iqi_draw(a, b, c, min_y, max_y):
            # draw a vertical line at m
            inperpolation_y = [self.f(a), self.f(b), self.f(c)]  # [f(a), f(b), f(c)]
            interpolation_x = [a, b, c]  # [a, b, c]
            y_mesh = np.linspace(min_y, max_y, 1000)
            # Lagrange interpolation with (Y,X)
            q_y = (  # Lagrange interpolation
                lambda y: ((y - inperpolation_y[1]) * (y - inperpolation_y[2]))
                / (
                    (inperpolation_y[0] - inperpolation_y[1])
                    * (inperpolation_y[0] - inperpolation_y[2])
                )
                * interpolation_x[0]
                + ((y - inperpolation_y[0]) * (y - inperpolation_y[2]))
                / (
                    (inperpolation_y[1] - inperpolation_y[0])
                    * (inperpolation_y[1] - inperpolation_y[2])
                )
                * interpolation_x[1]
                + ((y - inperpolation_y[0]) * (y - inperpolation_y[1]))
                / (
                    (inperpolation_y[2] - inperpolation_y[0])
                    * (inperpolation_y[2] - inperpolation_y[1])
                )
                * interpolation_x[2]
            )
            x_mesh = q_y(y_mesh)  # Get the x values for the y values
            x_mesh = np.where(
                (x_mesh < self.x[0]) | (x_mesh > self.x[-1]), np.nan, x_mesh
            )  # Set the x values outside the range to nan
            iqi_line = bq.Lines(  # Draw a line
                x=x_mesh,
                y=y_mesh,
                scales={"x": self.x_sc, "y": self.y_sc},
                colors=["blue"],
                display_legend=True,
                labels=["IQI Line"],
                line_style="dashed",
            )
            return iqi_line

        points2check = [  # Points to check
            self.a,
            self.b,
            self.c,
            self.next_points_addition[0],
            self.next_points_addition[1],
        ] + (
            []
            if self.next_points_addition[2] is None
            else [
                self.next_points_addition[2]
            ]  # If the IQI point is None, add it to the list
        )

        if self.hint_step is None:  # If the hint step is None
            # set the original function
            self.x = np.linspace(min(self.original_data), max(self.original_data), 1000)
            self.default_lines()
            # Adjust the scales
            self.x_sc.min = min(self.original_data)
            self.x_sc.max = max(self.original_data)
            self.y_sc.min = min(self.function_line.y)
            self.y_sc.max = max(self.function_line.y)

            self.fig.marks = [
                self.horizontal_line,
                self.function_line,
                draw_point(  # Draw the current solution
                    self.b,
                    0,
                    "red",
                    "Current Solution",
                    "circle",
                ),
            ]  # Set the marks to the function and the horizontal line
            return

        min_max = [
            min(points2check),
            max(points2check),
        ]  # Get the min and max of the points to check

        if min_max[0] < min(self.original_data) or min_max[1] > max(
            self.original_data
        ):  # If the min or max of the points to check is outside the range of the original data
            self.x = np.linspace(  # Set the x values to the min and max of the points to check
                min(min(self.original_data), min_max[0]),
                max(max(self.original_data), min_max[1]),
                1000,
            )
            self.default_lines()  # Set the default lines
            self.widen = True  # Set widen to True
        elif self.widen:  # If widen is True
            self.x = np.linspace(
                min(self.original_data), max(self.original_data), 10000
            )  # Set the x values to the min and max of the original data
            self.default_lines()  # Set the default lines
            self.widen = False  # Set widen to False

        marks2plot = [
            self.horizontal_line,
            self.function_line,
        ]  # Set the marks to the function and the horizontal line

        # 1. The Current Points (a,b,c)
        marks2plot.append(
            draw_point(
                self.a, self.fa, "red", "a", "circle", legend=False
            )  # Draw a point
        )
        marks2plot.append(
            draw_point(
                self.b,
                self.fb,
                "Black",
                "Current Solution",
                "cross",
                legend=True,  # Draw a point
            )
        )
        marks2plot.append(
            draw_point(
                self.c, self.fc, "green", "c", "circle", legend=False
            )  # Draw a point
        )

        # 2. The next step suggestions
        marks2plot.append(  # Bisect
            draw_point(
                self.next_points_addition[0],
                0,
                "green",
                "Bisection",
                "rectangle",
            )
        )
        marks2plot.append(
            draw_point(  # Secant
                self.next_points_addition[1],
                0,
                "red",
                "Secant",
                "triangle-up",
            )
        )
        if self.next_points_addition[2] is not None:
            marks2plot.append(
                draw_point(  # IQI
                    self.next_points_addition[2],
                    0,
                    "blue",
                    "IQI",
                    "triangle-down",
                )
            )

        # FIX THE VIEW
        self.x_sc.min = min_max[
            0
        ]  # Set the x scale min to the min of the points to check
        self.x_sc.max = min_max[
            1
        ]  # Set the x scale max to the max of the points to check

        self.y_sc.min = min(
            self.f(min_max[0]), self.f(min_max[1])
        )  # Set the y scale min to the min of the function of the min and max of the points to check
        self.y_sc.max = max(
            self.f(min_max[0]), self.f(min_max[1])
        )  # Set the y scale max to the max of the function of the min and max of the points to check

        fx = list(map(self.f, self.x))  # Get the function values for the x values
        y_min_max = (min(fx), max(fx))  # Get the min and max of the function values

        # 3. The steps
        if self.secant_checkbox.value:  # If the secant checkbox is checked
            marks2plot.append(secant_draw())  # Draw the secant line

        if self.bisect_checkbox.value:  # If the bisect checkbox is checked
            marks2plot.append(  # Draw the bisect line
                bisect_draw(
                    self.next_points_addition[0], y_min_max[0], y_min_max[1]
                )  # Draw the bisect line
            )
        if (
            self.iqi_checkbox.value and self.next_points_addition[2] is not None
        ):  # If the IQI checkbox is checked and the IQI point is not None
            marks2plot.append(
                iqi_draw(self.a, self.b, self.c, y_min_max[0], y_min_max[1])
            )  # Draw the IQI line

        self.fig.marks = marks2plot  # Set the marks to the marks to plot

    def update_ouputs(self):
        """
        This method updates the outputs of the app
            > current solution
            > helper text
        The next step must be calculated before calling this method
        """
        self.current_solution_output.clear_output()  # Clear the current solution output
        self.helper_output.clear_output()  # Clear the helper output

        with self.current_solution_output:  # Print the current solution
            print(
                f"Current Solution: ({self.b:.4e}, {self.f(self.b):.4e})"
            )  # Print the current solution
            print(f"Iterations: {self.iterations}")  # Print the iterations
        with self.helper_output:  # Print the helper text
            print(  # Print the helper text
                f"Next Step suggested by Brent-Dekker: {self.hint_step if self.hint_step is not None else 'FINISHED'}"
            )

    def run(self):
        """
        This method sets up everything and runs the app

        Returns
        -------
        Widgets.GridBox
            The GridBox containing all the widgets
        """
        self.initialize_components()  # Initialize the components
        self.one_step()  # Run one step

        return self.grid

    def brent_dekker_step(self):
        """
        This method imitates the Brent-Dekker in one step, instead of giving the result point, this method returns the 3 available points for the next step as well as the next possible step

        Returns
        -------
        - next_step: str
            The next possible step
        - nextPoints_addition: list
            The 3 available quantity to add to b for the next step (midpoint, secant, IQI)
        - errs: list
            The errors of the 3 available points for the next step
        """
        self.tolerance = 2 * np.finfo(float).eps * abs(self.b) + self.t
        ## Midpoint error
        m = 0.5 * (self.c - self.b)

        if abs(m) <= self.tolerance or self.f(self.b) == 0 or self.f(self.a) == 0:
            self.hint_step = None
            self.next_points_addition = [None, None, None]
            self.errs = [None, None, None]
            self.update_ouputs()
            return

        next_step = None
        next_points_addition = [None, None, None]
        errs = [None, None, None]

        next_points_addition[0] = self.b + m  # Always exists
        errs[0] = m  # Always exists

        # See if Bisection is possible
        # CHECK abs(self.e) < self.tolerance or abs(self.fa) <= abs(self.fb) in the original code
        # Here we do nothing because it is the midpoint - only thing next_step is Bisection (which will be default if secant/iqi fails)

        s = self.fb / self.fa
        pq_pair = None
        if self.a == self.c:
            # Linear Interpolation (Secant)
            p1 = 2 * m * s
            q1 = 1 - s

        else:
            # Linear Interpolation (Secant)
            p1 = self.fb * (self.b - self.a)
            q1 = self.fb - self.fa

            # Inverse Quadratic Interpolation (IQI)
            q = self.fa / self.fc
            r = self.fb / self.fc
            p2 = s * (2 * m * q * (q - r) - (self.b - self.a) * (r - 1))
            q2 = (q - 1) * (r - 1) * (s - 1)

            # Correct signs of IQI
            if p2 > 0:
                q2 = -q2
            else:
                p2 = -p2

            pq_pair = (p2, q2)

            self.s = self.e

        if p1 > 0:
            q1 = -q1
        else:
            p1 = -p1

        # Store e-Values for next step
        errs[1] = abs(p1 / q1)  # Secant always exists
        errs[2] = (
            None if pq_pair is None else abs(pq_pair[0] / pq_pair[1])
        )  # IQI may not exist if a==c if it does, it is stored in pqPair

        # Store next points (Quantity to add) for next step
        next_points_addition[1] = self.b + p1 / q1  # Secant always exists
        next_points_addition[2] = (
            None if pq_pair is None else self.b + pq_pair[0] / pq_pair[1]
        )  # IQI may not exist if a==c if it does, it is stored in pqPair
        pq_pair = (
            (p1, q1) if pq_pair is None else pq_pair
        )  # If IQI does not exist, use Secant instead (pqPair is None if IQI does not exist), otherwise use IQI (pqPair is not None if IQI exists)

        # Choose the best interpolation
        if 2 * pq_pair[0] < 3 * m * pq_pair[1] - abs(
            self.tolerance * pq_pair[1]
        ) and pq_pair[0] < abs(0.5 * self.e * pq_pair[1]):
            next_step = "IQI" if self.a != self.c else "Secant"
        else:
            next_step = "Bisection"

        self.hint_step = next_step
        self.next_points_addition = next_points_addition
        self.errs = errs

        return next_step, next_points_addition, errs
