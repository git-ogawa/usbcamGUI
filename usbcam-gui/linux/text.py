from PySide2.QtWidgets import QTableWidget, QTableWidgetItem


class MessageText():

    usage_text = (
        """
        <h1> Usage </h1>

        <h2> Read frame from the connected camera </h2>
        The center region on the window shows frame from the connected camera. The frame
        switching automatically every the set time (10 mesc by default).

        <h2> Button action </h2>
        Pressing each button on the window works as follows.
        <ul>
            <li> Quit
                <ul> Finish this program. </ul>
            </li>
            <li> Save
                <ul> Save the current frame as png. </ul>
            </li>
            <li> Stop
                <ul> Pause reading frame from usb camera. </ul>
                <ul> When pressed, stop button's text changes "Start".</ul>
                <ul> When pressed again, Resume reading frame.</ul>
            </li>
            <li> Usage
                <ul> Show the usage. </ul>
            </li>
        </ul>

        <h2> Change values of parameter </h2>
        The slidebar enable users to change values of parameter interactively.
        The string on the left of slider shows the name of parameter, the label on the right
        does its current value.

        <h2> Coordinates and pixel value </h2>
        The status bar below the window shows the coordinates and values (RGBA) of
        the pixel where the cursor is placed. These will be single value if user sets image
        format to grayscale.
        """)

    about_text = (
        """
        This is about
        """
    )

    keylist = [
            ["Ctrl + a", "About the program"],
            ["Ctrl + d", "Set parameters to default value"],
            ["Ctrl + f", "Change the file to save frame"],
            ["Ctrl + t", "Switch theme of main window"],
            ["Ctrl + r", "Start recording"],
            ["Ctrl + s", "Save the current frame"],
            ["Ctrl + q", "Exit the program"],
            ["Ctrl + p", "Stop reading frame"],
            ["Ctrl + h", "Show usage"],
            ["Ctrl + Shift + s", "Show the list of shortcut key"]
        ]