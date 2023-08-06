import React from "react";
import { DocumentRegistry } from "@jupyterlab/docregistry";
import { INotebookModel, NotebookPanel } from "@jupyterlab/notebook";
import { DisposableDelegate, IDisposable } from "@lumino/disposable";
import { ServerConnection } from "@jupyterlab/services";
import { ISignal, Signal } from "@lumino/signaling";
import { Widget } from "@lumino/widgets";
import { ReactWidget } from "@jupyterlab/apputils";

import i18next from "./i18n";
import { request } from "./utils";

class SucceedExerciseToolBarButton extends ReactWidget {
  constructor(handleChange: (e: React.FormEvent<HTMLButtonElement>) => void) {
    super();
    this._handleChange = handleChange;
  }

  update_color(state: boolean) {
    state ? (this._color = "green") : (this._color = "black");
    this.update();
  }

  updateSucceedState = (e: React.FormEvent<HTMLButtonElement>) => {
    this._handleChange(e);
    this._color === "green" ? (this._color = "black") : (this._color = "green");
    this.update();
  };

  render(): JSX.Element {
    return (
      <button
        type="button"
        className="bp3-button bp3-minimal jp-ToolbarButtonComponent minimal jp-Button progress-button"
        id="succeed-button"
        onClick={this.updateSucceedState}
        value="done"
        title={i18next.t("Mark this exercise as done")}
      >
        <i className={`fa fa-thumbs-o-up ${this._color}`}></i>
      </button>
    );
  }

  private _handleChange: (e: React.FormEvent<HTMLButtonElement>) => void;
  private _color = "black";
}

class NeedHelpToolBarButton extends ReactWidget {
  constructor(handleChange: (e: React.FormEvent<HTMLButtonElement>) => void) {
    super();
    this._handleChange = handleChange;
  }

  update_color(state: boolean) {
    state ? (this._color = "red") : (this._color = "black");
    this.update();
  }

  updateNeedHelpState = (e: React.FormEvent<HTMLButtonElement>) => {
    this._handleChange(e);
    this._color === "red" ? (this._color = "black") : (this._color = "red");
    this.update();
  };

  render(): JSX.Element {
    return (
      <button
        type="button"
        className="bp3-button bp3-minimal jp-ToolbarButtonComponent minimal jp-Button progress-button"
        id="need-help-button"
        onClick={this.updateNeedHelpState}
        value="needHelp"
        title={i18next.t("Ask the trainer for help")}
      >
        <i className={`fa fa-hand-stop-o ${this._color}`}></i>
      </button>
    );
  }

  private _handleChange: (e: React.FormEvent<HTMLButtonElement>) => void;
  private _color = "black";
}

export class ProgressButtons
  extends Widget
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel>
{
  public createNew(panel: NotebookPanel): IDisposable {
    const succeed_button = new SucceedExerciseToolBarButton((e) =>
      this.handleChange(e, panel),
    );
    panel.toolbar.insertAfter("spacer", "succeed", succeed_button);
    const need_help_button = new NeedHelpToolBarButton((e) =>
      this.handleChange(e, panel),
    );
    panel.toolbar.insertAfter("spacer", "needHelp", need_help_button);
    // update buttons color
    this.getExerciseState(panel.context.path).then(([succeed, needHelp]) => {
      succeed_button.update_color(Boolean(succeed));
      need_help_button.update_color(Boolean(needHelp));
    });
    return new DisposableDelegate(() => {
      need_help_button.dispose();
      succeed_button.dispose();
    });
  }

  getExerciseState = async (exo_path: string): Promise<boolean[]> => {
    const data = await request(
      `state/${exo_path.split("/").slice(-2, -1).pop()}`,
      "GET",
      {},
      ServerConnection.makeSettings(),
    )
      .then((data) => {
        return data;
      })
      .catch(() => {
        console.error("Something went wrong :(");
      });
    return [data.done, data.needHelp];
  };

  handleChange = (
    e: React.FormEvent<HTMLButtonElement>,
    panel: NotebookPanel,
  ) => {
    request(
      "progress",
      "POST",
      JSON.stringify({
        state: e.currentTarget.value,
        path: panel.context.path,
        url: panel.node.baseURI,
      }),
      ServerConnection.makeSettings(),
    );
    this._stateChanged.emit("update-progress");
  };

  public get stateChanged(): ISignal<ProgressButtons, string> {
    return this._stateChanged;
  }

  private _stateChanged = new Signal<ProgressButtons, string>(this);
}
