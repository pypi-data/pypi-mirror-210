from IPython.display import clear_output, display
from ipywidgets import widgets
import io
import unittest


# utils for unittests in notebooks
def display_test_results(results, output_msg):
    """Display tests results nicely."""
    success = results.wasSuccessful()
    status_layout = widgets.Layout(display='flex')
    nb_errors = len(results.errors) + len(results.failures)
    msg = u'Congratulations!'
    if nb_errors:
        msg = '{n} test{s} failed'.format(
            n=nb_errors,
            s='' if results.testsRun == 1 else 's'
        )
    testnumber_wdg = widgets.Label(value=msg)
    valid_wdg = widgets.Valid(value=success)
    status_wdg = widgets.HBox(children=[testnumber_wdg, valid_wdg],
                              layout=status_layout)
    display(status_wdg)
    if not success:
        print(output_msg.getvalue())


class FormUnitTests():

    def __init__(self, test_class):
        self.test_class = test_class
        self.create_button()

    def create_button(self):

        output = widgets.Output()

        @output.capture()
        def on_button_clicked(b):
            clear_output()
            suite = unittest.TestSuite()
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromTestCase(self.test_class)
            output_msg = io.StringIO()
            results = unittest.TextTestRunner(stream=output_msg).run(suite)
            display_test_results(results, output_msg)

        exec_button = widgets.Button(
            description='Execute tests',
            disabled=False,
            button_style='',
            tooltip='Execute the unitary tests',
            icon='check')
        print("\x1b[31m Run the cell containing your function before"
              " launching unit tests \x1b[0m")
        display(exec_button)
        exec_button.on_click(on_button_clicked)
        display(output)
