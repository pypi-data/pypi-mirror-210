import numpy as np
import ipywidgets as widgets
from IPython.display import display
from ..LinearSystems import interactive_lu


class LUVisualizer:
    def __init__(self, matrix=np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float)):
        """
        Parameters
        ----------
        matrix : numpy.ndarray
            Matrix to be decomposed (must be square)

        Returns
        -------
        None

        Exceptions
        ----------
        ValueError
            If the matrix is not square
        """
        self.A = np.array(matrix, dtype=float)
        if self.A.shape[0] != self.A.shape[1]:
            raise ValueError("Matrix must be square")
        self.step = 0
        self.L = np.eye(self.A.shape[0])
        self.U = self.A.copy()
        self.P = np.eye(self.A.shape[0])
        self.rank = 0

        # Stack for previous steps
        self.previous_steps = []

    def initialize_components(self):
        """
        Initialize the components of the visualizer (Output, Buttons, Grid)

        Returns
        -------
        None
        """
        # OUTPUTS
        # ==========================================================================
        ## Output for the matrix P
        self.out_p = widgets.HTMLMath(
            value=pretty_print_matrix(
                self.P, simple=True, type="pMatrix", step=self.step
            ),
            placeholder="$P$",
            description="$P:$",
        )

        ## Output for the matrix L
        self.out_l = widgets.HTMLMath(
            value=pretty_print_matrix(
                self.L, simple=True, type="lMatrix", step=self.step
            ),
            placeholder="$L$",
            description="$\\tilde{L}:$",
        )

        ## Output for the matrix U
        self.out_u = widgets.HTMLMath(
            value=pretty_print_matrix(
                self.U, simple=True, type="uMatrix", step=self.step
            ),
            placeholder="$U$",
            description="$\\tilde{U}:$",
        )

        ## Output for the checker(PA=LU)
        self.out_checker = widgets.HTMLMath(
            value=str(np.allclose(self.L @ self.U, self.P @ self.A)),
            placeholder="$PA=?LU$",
            description="$PA=?LU$",
        )
        ## Output for the message of step skipped normal text
        self.out_message = widgets.Output(
            value="",
            placeholder="Message:",
            description="Message:",
        )
        self.rank_result = widgets.HTMLMath(
            value=f"{self.rank}",
            placeholder="Rank",
            description="Rank:",
        )

        # BUTTONS
        # ==========================================================================
        ## Previous step button
        self.previous_button = widgets.Button(
            description="Previous Step",
            disabled=False,
            button_style="info",
            tooltip="Previous Step",
            icon="arrow-left",
        )
        self.previous_button.on_click(self.previous_step)

        ## Reset button
        self.reset_button = widgets.Button(
            description="Reset",
            disabled=False,
            button_style="danger",
            tooltip="Reset",
            icon="undo",
        )
        self.reset_button.on_click(self.reset)  # Observer for the button

        # MATRIX
        # ==========================================================================
        self.buttons_matrix = []  # List of lists of buttons
        for i in range(self.A.shape[0]):  # For each row
            row = []  # List of buttons
            for j in range(self.A.shape[1]):  # For each column
                row.append(
                    widgets.Button(description=f"{self.A[i,j]:.3f}", disabled=True)
                )  # Create a button with the value of the matrix
                row[-1].index = (i, j)
                # Observer for the button
                row[-1].on_click(self.matrix_pivot_button)

            self.buttons_matrix.append(row)  # Add the row to the list of rows

        self.update_buttons()  # Update the buttons

        # GRID
        # ==========================================================================
        self.grid = widgets.GridspecLayout(6, 5)
        # Add components to grid
        self.grid[0:3, 0:3] = widgets.VBox(  # Add the matrix to the grid
            list(map(lambda x: widgets.HBox(x), self.buttons_matrix))
        )
        self.grid[0, 3] = self.previous_button
        self.grid[1, 3] = self.reset_button
        self.grid[3, 3] = self.rank_result

        self.grid[3, 0] = self.out_p
        self.grid[3, 1] = self.out_l
        self.grid[3, 2] = self.out_u
        self.grid[4, :] = self.out_message

    def matrix_pivot_button(self, b):
        """
        Observer for the buttons in the matrix, when a button is clicked, the pivot is performed and the step is updated

        b.index contains the index of the pivot row
        Call luInteractive with PLU, step and index of pivot row
        Update the output

        Parameters
        ----------
        b : Button
            Button that was clicked

        Returns
        -------
        None
        """
        if b.disabled:
            return  # do nothing if the button is disabled
        self.previous_steps.append(
            (self.P.copy(), self.L.copy(), self.U.copy(), self.step, self.rank)
        )
        with self.grid.hold_sync():  # Hold the sync of the grid
            self.one_step(b.index[0])
            # Update the buttons
            self.update_buttons()

    def one_step(self, pivot):
        # Apply the LU decomposition to the matrix
        self.P, self.L, self.U, self.step, self.rank, msg = interactive_lu(
            self.P, self.L, self.U, self.step, self.rank, pivot
        )
        # Update the output
        self.update_output(msg)
        self.update_buttons()

    def update_buttons(self):
        """
        Update the buttons in the matrix, when a step is performed, blocks the buttons that are not available anymore

        Returns
        -------
        None
        """

        # Update the buttons
        for i in range(len(self.buttons_matrix)):  # For each row
            for j in range(  # For each column
                len(self.buttons_matrix[i])
            ):  # (i,j) is the index of the button
                # Disable the button
                self.buttons_matrix[i][j].disabled = True
                if self.step == -1:  # The end
                    self.buttons_matrix[i][j].style.button_color = "white"
                # Color Green and enable if the button is on the col self.step, the row is greater or eq than the rank and it is not 0
                elif (
                    j == self.step
                    and i >= self.rank
                    and not np.isclose(self.U[i, j], 0)
                ):
                    self.buttons_matrix[i][j].disabled = False
                    self.buttons_matrix[i][j].style.button_color = "LightGreen"
                # Color Red and disable if the button is on the col self.step, the row is greater or eq than the rank and it is 0
                elif j == self.step and i >= self.rank and np.isclose(self.U[i, j], 0):
                    self.buttons_matrix[i][j].style.button_color = "LightCoral"
                # Color white and disable if the button is on the col smaller than the step and the row is smaller than the rank
                elif j < self.step or i < self.rank:
                    self.buttons_matrix[i][j].style.button_color = "LightGray"
                else:  # Color white and disable if the button is on the col greater than the step and the row is greater than the rank
                    self.buttons_matrix[i][j].style.button_color = "white"

                self.buttons_matrix[i][
                    j
                ].style.font_weight = "normal"  # Remove bold from the buttons

                self.buttons_matrix[i][
                    j
                ].description = (
                    f"{self.U[i,j]:.3f}"  # Update the description of the button
                )

    def update_output(self, msg):
        """
        Update the output widgets

        Returns
        -------
        None
        """
        # Update the outputs
        self.out_p.value = pretty_print_matrix(  # Update the output of P
            self.P, simple=True, type="pMatrix", step=self.step
        )
        self.out_l.value = pretty_print_matrix(  # Update the output of L
            self.L, simple=True, type="lMatrix", step=self.step
        )
        self.out_u.value = pretty_print_matrix(  # Update the output of U
            self.U, simple=True, type="uMatrix", step=self.step
        )
        self.rank_result.value = (  # Update the output of the rank
            f"${self.rank}$ "
            if self.step != -1
            else f"$\\underline{{\\textbf{{{self.rank}}}}}$"
        )

        self.out_message.clear_output()  # Clear the output of the messages
        with self.out_message:  # Print the messages
            if msg != "":
                print(
                    "Messages from system: " + msg
                )  # Print the message if it is not empty
            else:
                print("")  # Print an empty line if the message is empty

    def previous_step(self, b):
        """
        Observer for the previous step button, when clicked, it returns the state to the previous step

        Parameters
        ----------
        b : Button
            Button that was clicked (Not used)

        Returns
        -------
        None
        """
        # If there are previous steps, then go back to the previous step
        if len(self.previous_steps) > 0:  # If there are previous steps in the stack
            (
                self.P,
                self.L,
                self.U,
                self.step,
                self.rank,
            ) = self.previous_steps.pop()  # Pop the previous step from the stack
            with self.grid.hold_sync():  # Hold the sync of the grid
                self.update_output("")  # Update the output
                # Update the buttons
                self.update_buttons()  # Update the buttons

    def reset(self, b):
        """
        Observer for the reset button, when clicked, it returns the state to the initial state

        Parameters
        ----------
        b : Button
            Button that was clicked (Not used)

        Returns
        -------
        None
        """

        # Reset the LU decomposition Visualizer to the initial state
        self.step = 0  # Set the step to 0
        self.rank = 0  # Set the rank to 0
        self.L = np.eye(self.A.shape[0])  # Set L to the identity matrix
        self.U = self.A.copy()  # Set U to the matrix A
        self.P = np.eye(self.A.shape[0])  # Set P to the identity matrix

        # Stack for previous steps
        self.previous_steps = []  # Clear the stack of previous steps
        with self.grid.hold_sync():  # Hold the sync of the grid
            # Update the output
            self.update_output("")  # Update the output
            # Update the buttons
            self.update_buttons()  # Update the buttons

    def run(self):
        """
        Run the LU decomposition Visualizer

        Returns
        -------
        None
        """
        # Run the visualizer
        self.initialize_components()
        # if the first column is all 0, then automatically perform the first step
        if np.all(self.U[:, 0] == 0):
            # print("First column is all 0, automatically performing the first step")
            with self.grid.hold_sync():
                self.one_step(0)

        return self.grid


def pretty_print_matrix(matrix, simple=False, type="normal", step=0):
    res = "  \\begin{pmatrix} \n"

    if type in ["normal", "pMatrix"]:
        for (
            row
        ) in matrix:  # Corresponds to any matrix or the P matrix (Permutation matrix)
            res += " & ".join([str(round(x, 3)) for x in row]) + "\\\\ \n"
    elif type == "lMatrix":  # Corresponds to the L matrix (Lower triangular matrix)
        # Write * everywhere except for the diagonal and the colums before the step
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if (i <= j or j < step) or step == -1:
                    res += str(round(matrix[i][j], 3)) + " & "
                else:
                    res += "* & "
            res = res[:-2] + "\\\\ \n"
    elif type == "uMatrix":  # Corresponds to the U matrix (Upper triangular matrix)
        # Write * on the submatrix [row:, step:]
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                if i < step or j < step or step == -1:
                    res += str(round(matrix[i][j], 3)) + " & "
                else:
                    res += "* & "
            res = res[:-2] + "\\\\ \n"

    res += "\\end{pmatrix} "

    return display.Math(res) if not simple else res
