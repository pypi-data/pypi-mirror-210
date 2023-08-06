import numpy as np
from ..Interpolation import polinomial, piecewise_linear, pchip, splines
from bqplot import pyplot as plt
import ipywidgets as widgets
import bqplot as bq


class InterpolVisualizer:
    def __init__(
        self,
        x_initial=list(np.arange(1, 7, 1).astype(float)),
        y_initial=[16, 18, 21, 17, 15, 12],
        u_initial=list(np.arange(1, 6.1, 0.1)),
    ) -> None:
        """
        Initializes the Class

        Parameters:
            - xInitial: Initial x coordinates
            - yInitial: Initial y coordinates
            - uInitial: Initial mesh
        """
        if len(x_initial) != len(y_initial):
            raise ValueError("The length of the X and Y coordinates must be the same")

        self.x = np.array(x_initial).astype(float)
        self.y = np.array(y_initial).astype(float)
        self.u = np.array(u_initial).astype(float)

        self.originals = [self.x, self.y, self.u]

        self.methods = {
            "InterPoly": [polinomial, "blue"],
            "Piecewise Linear": [piecewise_linear, "green"],
            "Pchip": [pchip, "orange"],
            "Splines": [splines, "purple"],
        }

    def initialize_components(self):
        """
        Initializes the components of the GUI
        Components:
            - Checkboxes
                Checkboxes for each interpolation method
            - Slider
                Slider for the mesh size
            - Reset Button
                Button to reset the points
        """

        """
        Checkboxes
        ======================
        One checkbox for every possible interpolation method
        Every checkbox will be associated with a method called update_checkboxes that will update the plot according to the updated checkboxes. 
        Additionally, the checkbox will have the same color as the color of associated interpolation method
        """
        self.checkboxes = []
        for key, val in self.methods.items():
            checkbox = widgets.Checkbox(
                description=key, value=True, style={"background-color": val[1]}
            )
            checkbox.background_color = val[1]
            checkbox.observe(self.update_checkboxes, "value")

            self.methods[key].append(checkbox)
            self.checkboxes.append(checkbox)

        """
        Reset button
        ======================
        Button to reset the points to the original ones, linked to the method reset
        """
        self.reset_button = widgets.Button(
            description="Reset", button_style="danger", tooltip="Reset", icon="undo"
        )
        self.reset_button.on_click(self.reset)

        """
        block adding points checkbox
        ======================
        Checkbox to block adding points, linked to anything - it is just a boolean value that will be used in update_X and update_Y
        """
        self.block_adding = widgets.Checkbox(
            description="Block adding points", value=False
        )

        """
        Effects of Extrapolation checkbox
        ======================
        Checkbox to show the effects of extrapolation, linked to the method update_extrapolation
        """
        self.extrapolation = widgets.Checkbox(
            description="Show effects of extrapolation", value=False
        )
        self.extrapolation.observe(self.update_extrapolation, "value")

        """
        Auto Zoom button
        ======================
        Button to auto zoom the plot, linked to the method auto_zoom
        """
        self.auto_zoom_button = widgets.Button(
            description="Auto Zoom",
            button_style="info",
            tooltip="Auto Zoom",
            icon="search-plus",
        )
        self.auto_zoom_button.on_click(self.auto_zoom)

    def update_extrapolation(self, change):
        """
        Updates the plot according to the effects of extrapolation checkbox
        """
        min_max = [min(self.x), max(self.x)]
        half = (min_max[1] - min_max[0]) / 4
        if change["new"]:
            self.u = np.linspace(
                min_max[0] - half, min_max[1] + half, 100, endpoint=True
            )
        else:
            self.u = np.linspace(min_max[0], min_max[1], 100, endpoint=True)

        self.update_x(None)
        self.update_y(None)

    def auto_zoom(self, change):
        """
        Auto zooms the plot
        """

        self.x_sc.min = min(self.u)
        self.x_sc.max = max(self.u)
        y_values = [j for line in self.interpolation_lines for j in line.y]
        if len(y_values) != 0:
            self.y_sc.min = min(y_values)
            self.y_sc.max = max(y_values)

    def scatter_dots(self):
        """
        Updates ScatteredDots - the scatter plot of the data - according to the new points
        It observers the changes in the x and y coordinates of the scatter plot and links them to the update_X and update_Y methods
        It also lets adding new points
        """
        self.scattered_dots = bq.Scatter(
            x=self.x,
            y=self.y,
            scales={"x": self.x_sc, "y": self.y_sc},
            colors=["red"],
            name="Points",
            enable_move=True,
            enable_add=False,
            display_legend=False,
            labels=["Points"],
        )

        # observe change XY
        self.scattered_dots.observe(self.update_x, "x")
        self.scattered_dots.observe(self.update_y, "y")
        self.scattered_dots.interactions = {"click": "add"}

    def interpol_lines(self):
        """
        Updates the interpolation lines according to the new points
        It creates an array of Lines for every interpolation method that is checked in the checkboxes
        """
        self.interpolation_lines = [
            bq.Lines(
                x=self.u,
                y=val[0](self.x, self.y, self.u),
                scales={"x": self.x_sc, "y": self.y_sc},
                colors=[val[1]],
                name=key,
                display_legend=False,
                labels=[key],
                enable_move=False,
                enable_add=False,
            )
            for key, val in self.methods.items()
            if val[2].value
        ]

    def update_x(self, change):
        """
        Updates the x coordinates and the plot according to the new x coordinates if the change is not None and does not contain Repetitions (Definition of a function)
        It also updates the slider according to the new x coordinates

        This method will always be called when the x coordinates are changed and before the y coordinates are changed.
        """
        if (
            change is not None
            and change["name"] == "x"
            and len(list(change["new"])) == len(set(change["new"]))
        ):  # There are changes and there are no repetitions in the x coordinates
            if (
                len(list(change["new"])) > len(self.x) and not self.block_adding.value
            ):  # There are more points than before and the block adding points checkbox is not checked
                self.x = change["new"]
            elif len(list(change["new"])) <= len(
                self.x
            ):  # There are the same number of points as before - the points are moved
                self.x = change["new"]
            else:  # There are more points than before and the block adding points checkbox is checked
                return  # Nothing to re-plot

    def update_y(self, change):
        """
        Updates the y coordinates and the plot according to the new y coordinates if the change is not None and contains the same number of points as X
        It makes new scattering and inteprolation lines and updates the plot.
        Also, it updates Scales and Axes according to the new points

        This method will always be called when the y coordinates are changed and after the x coordinates are changed.
        """

        with self.widgetsgrid.hold_sync():
            if (
                change is not None
                and change["name"] == "y"
                and len(list(change["new"])) == len(self.x)
            ):
                if (
                    len(list(change["new"])) > len(self.y)
                    and not self.block_adding.value
                ):
                    self.y = change["new"]
                elif len(list(change["new"])) <= len(self.y):
                    self.y = change["new"]
                else:
                    return  # Nothing to re-plot

            self.scatter_dots()
            self.interpol_lines()

            to_update = [*self.interpolation_lines, self.scattered_dots]

            self.fig.marks = to_update

    def update_checkboxes(self, change):
        """
        Updates the plot according to the new checkboxes
        """
        self.update_x(None)
        self.update_y(None)

    def reset(self, b):
        """
        Resets everything to what it was at the beginning of the program
        """
        self.x = self.originals[0]
        self.y = self.originals[1]
        self.u = self.originals[2]

        # Reset checkboxes
        for key, val in self.methods.items():
            val[2].value = True

        self.extrapolation.value = False
        self.block_adding.value = False

        values = [min(self.x), max(self.x)]
        self.u = np.linspace(values[0], values[1], 100, endpoint=True)

        self.update_x(None)
        self.update_y(None)

        # Reset Y scale
        self.y_sc.min = min(self.y)
        self.y_sc.max = max(self.y)

        # Reset X scale
        self.x_sc.min = min(self.x)
        self.x_sc.max = max(self.x)

    def run(self):
        """
        Runner method : Creates all the widgets and displays the plot with a given layout
        """
        self.x_sc = bq.LinearScale(stabilize=True)
        self.y_sc = bq.LinearScale(stabilize=True)
        ax_x = bq.Axis(scale=self.x_sc, grid_lines="solid", label="X")
        ax_y = bq.Axis(
            scale=self.y_sc,
            orientation="vertical",
            tick_format="0.2f",
            grid_lines="solid",
            label="Y",
        )

        self.initialize_components()
        self.interpol_lines()
        self.scatter_dots()

        # Reset Y scale
        self.y_sc.min = min(self.y)
        self.y_sc.max = max(self.y)

        # Reset X scale
        self.x_sc.min = min(self.x)
        self.x_sc.max = max(self.x)

        self.fig = bq.Figure(
            marks=[*self.interpolation_lines, self.scattered_dots],
            axes=[ax_x, ax_y],
            title="Interpolation Visualizer",
            legend_location="top-right",
            animation_duration=1000,
        )

        self.toolbar = bq.Toolbar(figure=self.fig)

        self.checkboxes_vbox = widgets.VBox(
            [
                widgets.HBox(
                    [
                        widgets.Button(
                            description="",
                            style={"button_color": i.background_color},
                            disabled=True,
                            layout=widgets.Layout(width="20px"),
                        ),
                        i,
                    ]
                )
                for i in self.checkboxes
            ]  # BUTTON + CHECKBOX PAIR -- Fake Legend
        )
        tools = widgets.VBox(
            [
                self.checkboxes_vbox,
                self.block_adding,
                self.extrapolation,
                widgets.HBox([self.reset_button, self.auto_zoom_button]),
            ]
        )

        self.widgetsgrid = widgets.GridspecLayout(11, 7)

        self.widgetsgrid[0, :] = self.toolbar
        self.widgetsgrid[1:, :4] = self.fig
        self.widgetsgrid[1:, 4:] = tools

        return self.widgetsgrid
