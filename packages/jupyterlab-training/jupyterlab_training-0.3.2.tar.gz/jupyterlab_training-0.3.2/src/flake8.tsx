import { DocumentRegistry } from "@jupyterlab/docregistry";
import { INotebookModel, NotebookPanel } from "@jupyterlab/notebook";
import { DisposableDelegate, IDisposable } from "@lumino/disposable";
import { ToolbarButton } from "@jupyterlab/apputils";
import { ServerConnection } from "@jupyterlab/services";
import { CodeCell } from "@jupyterlab/cells";

import { request } from "./utils";

export class Flake8Button
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel>
{
  public createNew(panel: NotebookPanel): IDisposable {
    const callback = () => {
      this.flake8(panel);
    };
    const button = new ToolbarButton({
      className: "myButton",
      label: "Flake8",
      onClick: callback,
      tooltip: "Run flake8 on current cell",
    });

    panel.toolbar.insertItem(0, "flake8", button);
    return new DisposableDelegate(() => {
      button.dispose();
    });
  }

  // launch flake8 on current cell
  protected flake8 = (panel: NotebookPanel): string => {
    if (panel.content.activeCell instanceof CodeCell) {
      request(
        "flake8",
        "POST",
        JSON.stringify({
          code: panel.content.activeCell.model.value.text,
        }),
        ServerConnection.makeSettings(),
      )
        .then((data) => {
          panel.content.activeCell.model.value.text = data.flake8;
        })
        .catch(() => {
          console.error("Something went wrong :(");
        });
    }
    return null;
  };
}
