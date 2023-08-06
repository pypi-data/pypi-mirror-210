from IPython.display import display
from ipywidgets import widgets
from IPython.display import clear_output
import io
from multiprocessing import Process
import unittest
from pathlib import Path
import json

from .handlers import setup_handlers


HERE = Path(__file__).parent.resolve()


with (HERE / "labextension" / "package.json").open() as fid:
    data = json.load(fid)


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": data["name"]}]


def _jupyter_server_extension_points():
    return [{
        "module": "jupyterlab_training"
    }]


def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP
    requests from the frontend extension.

    Parameters
    ----------
    lab_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    setup_handlers(server_app.web_app)
    server_app.log.info(
        "Registered Jupyterlab_training extension"
    )


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


class ServiceLauncher():

    process = None

    def __init__(self, service_function, service_name, args=None):
        self.service_function = service_function
        self.service_name = service_name
        self.create_button()
        self.args = args

    def create_button(self):

        output = widgets.Output()
        exec_button = widgets.ToggleButton(
            description=f'Start {self.service_name}',
            disabled=False,
            button_style='',
            tooltip=f'Launch the service {self.service_name}',
            icon='check',
        )
        print("(Re) Run the service before executing your cell.")
        print("Always stop and restart the service before testing")

        @output.capture()
        def handle_service(obj):
            clear_output()

            if obj['new']:
                """start service"""
                if self.args:
                    self.process = Process(
                        target=self.service_function,
                        args=self.args
                    )
                else:
                    self.process = Process(target=self.service_function)
                    self.process.start()
                    print(f"{self.service_name} is started")
                exec_button.description = f"Stop {self.service_name}"
            else:
                """stop service"""
                self.process.kill()
                exec_button.description = f"Start {self.service_name}"

        exec_button.observe(handle_service, 'value')
        display(exec_button)
        display(output)
