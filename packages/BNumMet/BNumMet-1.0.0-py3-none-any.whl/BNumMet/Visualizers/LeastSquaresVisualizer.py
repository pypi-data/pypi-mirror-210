import numpy as np
from bqplot import pyplot as plt
import ipywidgets as widgets
import bqplot as bq
from ..LinearSystems import qr_solve


class LSPVisualizer:
    """
    Visualizer for the least squares method with the examples of
        * Exponential function
        * Polynomial function
        * Sine and Cosine functions
    """

    def __init__(
        self, x_data_lsp=np.array([0, 1, 2, 3]), y_data_lsp=np.array([4.5, 2.4, 1.5, 1])
    ):
        if len(x_data_lsp) != len(y_data_lsp):  # check if the data is valid
            raise ValueError("x_data_lsp and y_data_lsp must have the same length")
        if len(x_data_lsp) < 2:  # check if the data is valid
            raise ValueError(
                "x_data_lsp and y_data_lsp must have at least 2 points... Too boring otherwise"
            )
        self.x_data_lsp = np.array(
            x_data_lsp, dtype=np.float64
        )  # convert the data to float64 (float64 is the default type for numpy)
        self.y_data_lsp = np.array(
            y_data_lsp, dtype=np.float64
        )  # convert the data to float64 (float64 is the default type for numpy)

        min_max_xdata = np.min(self.x_data_lsp), np.max(
            self.x_data_lsp
        )  # min and max of x_data_lsp
        self.x = np.linspace(  # x values for plotting the fitted curve
            np.min(x_data_lsp) - 0.2 * (min_max_xdata[1] - min_max_xdata[0]),  # min x
            np.max(x_data_lsp) + 0.2 * (min_max_xdata[1] - min_max_xdata[0]),  # max x
            1000,  # number of points
        )  # for plotting the fitted curve

    def initialize_components(self):
        """
        Initialize the components of the visualizer
        """

        # 1. Dropdown for selecting the function type
        self.function_type = widgets.Dropdown(  #
            options=[
                "Only data",
                "Polynomial",
                "Exponential",
                "Sines & Cosines",
            ],  # options
            value="Only data",  # default value
            description="Function:",  # description
            disabled=False,  # disable the dropdown
        )
        self.function_type.observe(
            self.selector_function, names="value"
        )  # observe the change of the dropdown
        # 2. Int text for selecting the polynomial degree
        self.polynomial_degree = widgets.BoundedIntText(  # int text for selecting the polynomial degree
            value=1,  # default value
            description="Degree:",  # description
            disabled=False,
            # make smaller width
            layout=widgets.Layout(width="75%"),
            min=0,  # minimum value
        )
        self.polynomial_degree.observe(
            self.degree_change_poly, names="value"
        )  # observe the change of the int text
        # 3. Int text for selecting the number of sines and cosines
        self.sine_cosine_degree = widgets.BoundedIntText(  # int text for selecting the number of sines and cosines
            value=1,  # default value
            description="",  # description
            disabled=False,
            min=0,
            layout=widgets.Layout(width="50%")
            # Make smaller width
        )

        self.sine_cosine_degree.observe(
            self.degree_change_sine_cosine, names="value"
        )  # observe the change of the int text

        self.sine_cosine_degree_box = widgets.HBox(
            [widgets.Label("Basis\n Elements:"), self.sine_cosine_degree]
        )

        # 4. Checkbox for Error Bound Visualization
        self.error_bound = widgets.Checkbox(  # checkbox for error bound visualization
            value=False,  # default value
            description="Error Bound",  # description
            disabled=False,  # disable the checkbox
        )

        # 5. Remarks about LSP output Math
        self.remarks = widgets.HTMLMath(  # remarks about LSP output
            value="",  # default value
            placeholder="LSP Remarks",  # placeholder
            description="Remarks:",  # description
        )

        # 6. Figure
        self.x_sc = bq.LinearScale()  # x scale
        self.y_sc = bq.LinearScale()  # y scale
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
            marks=[],  # marks
            axes=[ax_x, ax_y],  # axes
            title="Least Squares Method",  # title
        )

        self.grid = widgets.GridspecLayout(4, 4)  # grid for the components
        self.grid[:, 0:2] = self.fig  # add the figure to the grid
        self.grid[0:2, 2:] = widgets.VBox(
            [self.function_type]
        )  # add the function type dropdown to the grid
        # self.grid[1, 3] --> self.errorBound
        self.grid[2:, 2:] = self.remarks  # add the remarks to the grid

        # Plot the data (Since it will be the same for all the functions)
        points = bq.Scatter(  # data points
            x=self.x_data_lsp,  # x values
            y=self.y_data_lsp,  # y values
            scales={"x": self.x_sc, "y": self.y_sc},  # scales
        )
        self.fig.marks = [points]  # add the data points to the figure

    def degree_change_poly(self, change):
        """
        This function is called when the polynomial degree is changed
        """
        curve, c, err = self.polynomial_lsp(change["new"])  # calculate the curve
        self.fig.marks = [self.fig.marks[0], curve]  # update the figure
        self.polynomial_remarks(c, err)  # update the remarks

    def degree_change_sine_cosine(self, change):
        """
        This function is called when the sine and cosine degree is changed
        """
        curve, c, err = self.sine_cosine_lsp(change["new"])  # calculate the curve
        self.fig.marks = [self.fig.marks[0], curve]  # update the figure
        self.sine_cosine_remarks(c, err)  # update the remarks

    def selector_function(self, change):
        """
        This function is called when the function type is changed
        """
        to_draw = [self.fig.marks[0]]  # the data points are always drawn
        to_grid = [self.function_type]  # the function type dropdown
        if (
            change["new"] == "Only data"
        ):  # if the function type is "Only data"  then we don't need to draw anything else
            self.remarks.value = ""  # clear the remarks
        elif (
            change["new"] == "Polynomial"
        ):  # if the function type is "Polynomial" then we need to
            to_grid.append(
                self.polynomial_degree
            )  # add the polynomial degree dropdown to the grid
            self.polynomial_degree.max = (  # set the max degree to the number of data points - 1
                len(self.x_data_lsp) - 1
            )  # max degree is number of data points - 1
            curve, c, err = self.polynomial_lsp(
                self.polynomial_degree.value
            )  # calculate the polynomial LSP
            to_draw.append(curve)  # add the polynomial to the list of marks to draw
            self.polynomial_remarks(c, err)  # add the remarks to the remarks widget

        elif (
            change["new"] == "Exponential"
        ):  # if the function type is "Exponential" then we need to
            curve, c, err = self.exponential_lsp()  # calculate the exponential LSP
            to_draw.append(curve)  # add the exponential to the list of marks to draw
            self.exponential_remarks(c, err)  # add the remarks to the remarks widget

        elif (
            change["new"] == "Sines & Cosines"
        ):  # if the function type is "Sines & Cosines" then we need to
            to_grid.append(
                self.sine_cosine_degree_box
            )  # add the sine and cosine degree dropdown to the grid
            self.sine_cosine_degree.max = (
                (  # set the max degree to half the number of data points - 1
                    len(self.x_data_lsp) - 1
                )
                // 2
            )  # max degree is half the number of data points - 1
            curve, c, err = self.sine_cosine_lsp(
                self.sine_cosine_degree.value
            )  # calculate the sine and cosine LSP
            to_draw.append(
                curve
            )  # add the sine and cosine to the list of marks to draw
            self.sine_cosine_remarks(c, err)  # add the remarks to the remarks widget

        with self.fig.hold_sync():  # update the figure
            self.fig.marks = to_draw  # update the marks
            self.grid[0:2, 2:] = widgets.VBox(
                to_grid,
                layout=widgets.Layout(  # set the layout of the grid
                    width="auto",
                    height="auto",
                ),
            )  # update the grid (the dropdowns and degree selectors)

    def exponential_lsp(self):
        """
        This function returns the exponential function that best fits the data Using LSP

        Returns
        -------
        curve : bqplot.Lines
            The curve that best fits the data
        a : float
            The coefficient of the exponential function
        b : float
            The coefficient of the exponential function
        """
        # Create the A matrix
        A = np.ones((len(self.x_data_lsp), 2))  # 2 columns for the 2 coefficients
        A[:, 1] = self.x_data_lsp  # The second column is the x data
        # Solve the system
        c = qr_solve(
            A, np.log(self.y_data_lsp)
        )  # Solve the system using QR decomposition

        # Revert the log on c[0]
        c[0] = np.exp(c[0])  # We have made the log of c[0] to solve the system

        # Plot the curve
        # Evaluate the exponential function
        y = c[0] * np.exp(c[1] * self.x)  # Evaluate the exponential function
        # Plot the curve
        curve = bq.Lines(
            x=self.x,
            y=y,
            scales={"x": self.x_sc, "y": self.y_sc},
            colors=["red"],
        )  # Create the curve object

        err = np.linalg.norm(
            np.log(self.y_data_lsp) - A @ np.array([np.log(c[0]), c[1]]), 2
        )  # Calculate the error

        return curve, c, err

    def exponential_remarks(self, c, err):
        """
        This function updates the remarks section of the widget

        Remark: The exponential function that best fits the data is:
            <br>$y = a e^{bx}$ <br><br>
        The coefficients of the exponential function are:
            <br>$a = $ <br>$b = $ <br><br>
        The error is:
            $err$

        Parameters
        ----------
        c : np.array
            The coefficients of the exponential function in the form of c[0]*x^c[1]
        """
        self.remarks.value = f"The exponential function that best fits the data is: <br>$y = {c[0]:.4f}e^{{{c[1]:.4f}x}}$ <br><br> The coefficients of the exponential function are: <br>$c_0 = {c[0]:.4f}$ <br>$c_1 = {c[1]:.4f}$ <br><br> The error is: ${err:.4f}$ $\left(\sqrt{{\sum_i (y_i - f(x_i))^2}}\\right)$"

    def polynomial_lsp(self, degree):
        """
        This function returns the polynomial function of the given degree that best fits the data Using LSP

        Parameters
        ----------
        degree : int
            The degree of the polynomial function

        Returns
        -------
        curve : bqplot.Lines
            The curve that best fits the data
        c : np.array
            The coefficients of the polynomial function in the form of c[0] + c[1]*x + c[2]*x^2 + ... + c[degree]*x^degree
        """
        # Create the A matrix
        A = np.zeros((len(self.x_data_lsp), degree + 1))  # +1 because of the 0th degree
        for i in range(degree + 1):  # +1 because of the 0th degree
            A[:, i] = (
                self.x_data_lsp**i
            )  # x^0 = 1 so no need to do anything special for the 0th degree case but everything else is x^i
        # Solve the system
        c = qr_solve(A, self.y_data_lsp)
        # Plot the curve
        # Evaluate the polynomial function
        y = np.array(
            [np.sum([c[i] * x**i for i in range(degree + 1)]) for x in self.x]
        )  # sum_{i=0}^n c_i x^i = c_0 + c_1 x + c_2 x^2 + ... + c_n x^n =Evaluate the polynomial function
        # Plot the curve
        curve = bq.Lines(
            x=self.x,
            y=y,
            scales={"x": self.x_sc, "y": self.y_sc},
            colors=["red"],
        )  # Create the curve object

        err = np.linalg.norm(self.y_data_lsp - A @ c)  # Calculate the error

        return curve, c, err  # Return the curve, coefficients and error

    def polynomial_remarks(self, c, err):
        """
        This function returns the remarks for the polynomial function

        The polynomial function is: <br> $y = c_0 + c_1x + c_2x^2 + ... + c_nx^n$ <br><br>
        The coefficients of the polynomial function are: <br> $c_0 = ...$ <br> $c_1 = ...$ <br> $c_2 = ...$ <br> ... <br> $c_n = ...$ <br><br>
        The error is: ...$"

        Parameters
        ----------
        c : np.array
            The coefficients of the polynomial function in the form of c[0] + c[1]*x + c[2]*x^2 + ... + c[degree]*x^degree

        Returns
        -------
        remarks : str
            The remarks for the polynomial function
        """

        # Create the remarks
        remarks = "The polynomial function is:<br> $"  # First line of the remarks

        for i in range(len(c)):  # Add the coefficients of the polynomial function
            if i == 0:
                remarks += f"{c[i]:.2f}"  # If the coefficient is 0, don't add x^{i}
            elif i == 1:
                remarks += ("+" if np.sign(c[i]) >= 0 else "") + f"{c[i]:.2f}x"
                # If the coefficient is 1, don't add power
            else:
                remarks += ("+" if np.sign(c[i]) >= 0 else "") + f"{c[i]:.2f}x^{i}"
                # If the coefficient is 1, add power

        remarks += "$ <br><br> The coefficients of the polynomial function are: <br> "  # Second line of the remarks

        for i in range(len(c)):  # Add the coefficients of the polynomial function
            remarks += f"$c_{i} = {c[i]:.2f}$<br> "  # Add the coefficient

        remarks += f"<br> The error is ${err:.4f}$ $\left(\sqrt{{\sum_i (y_i - f(x_i))^2}}\\right)$ <br><br>"  # Third line of the remarks

        self.remarks.value = remarks  # Update the remarks

    def sine_cosine_lsp(self, degree):
        """
        This function returns the sine and cosine function of the given degree that best fits the data Using LSP

        Parameters
        ----------
        degree : int
            The degree of the sine and cosine function

        Returns
        -------
        curve : bqplot.Lines
            The curve that best fits the data
        c : np.array
            The coefficients of the sine and cosine function in the form of c[0] + c[1]*sin(x) + c[2]*cos(x) + ... + c[degree]*sin(degree*x) + c[degree+1]*cos(degree*x)
        """
        # Create the A matrix
        A = np.ones(
            (len(self.x_data_lsp), 2 * degree + 1)
        )  # 2*degree+1 because we have degree sin and degree cos
        for i in range(
            1, degree + 1
        ):  # We start from 1 because we already have the first column of ones
            A[:, 2 * i - 1] = np.sin(i * self.x_data_lsp)  # 2*i-1 for the sin
            A[:, 2 * i] = np.cos(i * self.x_data_lsp)  # 2*i for the cos
        # Solve the system
        c = qr_solve(A, self.y_data_lsp)
        # Plot the curve
        # Evaluate the sine and cosine function
        y = np.array(
            [
                np.sum(
                    [
                        c[i] * np.sin(i * x) + c[i + 1] * np.cos(i * x)
                        for i in range(1, degree + 1)
                    ]
                )  # Find the sum of the sin and cos terms sum_{i=1}^{degree} c[2*i-1]*sin(i*x) + c[2*i]*cos(i*x)
                + c[0]  # The first coefficient is the constant
                for x in self.x  # For each x in our mesh
            ]
        )
        # Plot the curve
        curve = bq.Lines(
            x=self.x,
            y=y,
            scales={"x": self.x_sc, "y": self.y_sc},
            colors=["red"],
        )  # Make the curve object

        err = np.linalg.norm(
            self.y_data_lsp
            - [
                np.sum(
                    [
                        c[i] * np.sin(i * x) + c[i + 1] * np.cos(i * x)
                        for i in range(1, degree + 1)
                    ]
                )
                + c[0]
                for x in self.x_data_lsp
            ]
        )  # Calculate the error

        return curve, c, err

    def sine_cosine_remarks(self, c, err):
        """
        This function returns the remarks for the sine and cosine function

        Parameters
        ----------
        c : np.array
            The coefficients of the sine and cosine function in the form of c[0] + c[1]*sin(x) + c[2]*cos(x) + ... + c[degree]*sin(degree*x) + c[degree+1]*cos(degree*x)

        Returns
        -------
        remarks : str
            The remarks for the sine and cosine function
        """

        # Create the remarks
        remarks = "The sine and cosine function is:<br> $"
        # first coefficient
        remarks += f"{c[0]:.2f}"

        for i in range(1, len(c) // 2 + 1):
            remarks += (
                "+" if np.sign(c[2 * i - 1]) >= 0 else ""
            )  # sign of the coefficient of the sine function
            remarks += (
                f"{c[2*i - 1]:.2f}\sin({i}\cdot x)"  # coefficient of the sine function
            )
            remarks += (
                "+" if np.sign(c[2 * i]) >= 0 else ""
            )  # sign of the coefficient of the cosine function
            remarks += (
                f"{c[2*i]:.2f}\cos({i}\cdot x)"  # coefficient of the cosine function
            )

        remarks += "$ <br><br> The coefficients of the sine and cosine function are: <br> "  # Second part of the remarks (coefficients)

        for i in range(len(c)):  # Iterate through coefficients
            remarks += f"$c_{i} = {c[i]:.2f}$ <br>"  # coefficient

        remarks += f"<br> The error is: ${err:.4f}$ $\left(\sqrt{{\sum_i (y_i - f(x_i))^2}}\\right)$ <br><br>"  # Third part of the remarks (error)

        self.remarks.value = remarks  # Set the remarks

    def run(self):
        self.initialize_components()

        return self.grid
