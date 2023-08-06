import * as React from "react";
import { ILabShell, JupyterFrontEnd } from "@jupyterlab/application";
import { IDocumentManager } from "@jupyterlab/docmanager";
import { INotebookTracker } from "@jupyterlab/notebook";

import i18next from "./i18n";

export const addTour = async (
  app: JupyterFrontEnd,
  labShell: ILabShell,
  notebookTracker: INotebookTracker,
  docmanager: IDocumentManager,
  formPanelId: string,
) => {
  const { commands } = app;
  if (!commands.hasCommand("jupyterlab-tour:add")) {
    return;
  }
  let fileBrowserTarget = "#filebrowser";
  if (document.querySelector("#jupyterlab-unfold")) {
    fileBrowserTarget = "#jupyterlab-unfold";
  }
  const tourCleaning = (notebookTracker: INotebookTracker) => {
    const current = notebookTracker.currentWidget;
    if (current) {
      current.context.save().then(() => {
        docmanager.closeFile(current.context.path);
      });
    }
    const advancedOptionsElement = document.getElementsByClassName(
      "fieldsetContainer",
    )[0] as HTMLElement;
    if (advancedOptionsElement.offsetHeight !== 0) {
      document.getElementById("toggle-options").click();
    }
  };

  const tour = await commands.execute("jupyterlab-tour:add", {
    tour: createTrainingTour(fileBrowserTarget) as any,
  });
  tour.options.disableScrolling = true;
  tour.stepChanged.connect((_: any, data: any) => {
    switch (data.type) {
      case "step:after":
        switch (data.step.target) {
          case "#main":
            commands.execute("launcher:create");
            break;
          case "#filter":
            const advancedOptionsElement = document.getElementsByClassName(
              "fieldsetContainer",
            )[0] as HTMLElement;
            if (advancedOptionsElement.offsetHeight === 0) {
              document.getElementById("toggle-options").click();
            }
            break;
          case "#toggle-options":
            docmanager.openOrReveal(
              "training/exercises/pyramid_volume/pyramid_volume.fr.ipynb",
            );
            break;
          case "#jp-main-dock-panel":
            commands.execute("filebrowser:activate");
            break;
          case fileBrowserTarget:
            labShell.activateById(formPanelId);
            break;
          default:
            break;
        }
    }
  });
  tour.finished.connect(() => {
    tourCleaning(notebookTracker);
  });
  tour.skipped.connect(() => {
    tourCleaning(notebookTracker);
  });
};

export const createTrainingTour = (fileBrowserTarget: string) => {
  return {
    id: "jupyterlab-training:tour",
    label: "Jupyterlab Training Tour",
    hasHelpEntry: true,
    steps: [
      {
        title: i18next.t("Welcome To"),
        content: (
          <section>
            <div className="formation-header">
              <b>TRAINING</b>
            </div>
            <br />
            {i18next.t(
              "This tour will point out some of the main UI components of the platform.",
            )}
          </section>
        ),
        target: "#main",
        placement: "center",
      },
      {
        title: i18next.t("Main area"),
        content: (
          <p>
            {i18next.t(
              "The launcher panel allows you to quickly start a terminal, a python interpreter or to create a file (notebook, python file or text file) to take notes.",
            )}
            <br />
            {i18next.t("Exercices notebooks will appear in this area.")}
          </p>
        ),
        target: "#jp-main-dock-panel",
        placement: "auto",
      },
      {
        title: i18next.t("File Browser"),
        content: (
          <p>
            {i18next.t(
              "The file browser enable you to work with files and directories on your system. This includes opening, creating, deleting, renaming, downloading, copying, and sharing files and directories.",
            )}
            <br />
            <br />
            <b>
              {i18next.t(
                "Only the subdirectories of '/home/jovyan/files/' are backed up.",
              )}
            </b>
            <br />
            {i18next.t(
              "If you want to keep files, be sure to store them in these directories.",
            )}
          </p>
        ),
        target: fileBrowserTarget,
        placement: "right",
      },
      {
        title: i18next.t("Training Menu"),
        content: (
          <p>{i18next.t(`Click here to (re)-open the training menu.`)}</p>
        ),
        target: ".formation-icon",
        placement: "right",
      },
      {
        title: i18next.t("Training Menu"),
        content: (
          <p>
            {i18next.t(
              `This menu contains links to the available exercises. Choose the one that suits you.`,
            )}
          </p>
        ),
        target: "#jupyterlab-training",
        placement: "right",
      },
      {
        title: i18next.t("Search"),
        content: (
          <p>
            {i18next.t(
              `You can filter the exercises by name or tag with the search field.`,
            )}
          </p>
        ),
        target: "#filter",
        placement: "right",
      },
      {
        title: i18next.t("Advanced Options"),
        content: (
          <section>
            {i18next.t(
              `You can access to the advanced options by clicking here.`,
            )}
            <ul>
              <li> {i18next.t(`Choose your language.`)}</li>
              <li> {i18next.t(`Choose your training path`)}</li>
              <li> {i18next.t(`Get the selected notebooks`)}</li>
            </ul>
          </section>
        ),
        target: "#toggle-options",
        placement: "right",
      },
      {
        title: i18next.t("Exercises"),
        content: <p>{i18next.t("Click on an exercise to open it.")}</p>,
        target: ".tab-content",
        placement: "right",
      },
      {
        title: i18next.t("Exercise"),
        content: (
          <p>
            {i18next.t(
              "The exercise opens in the main area and you can start reading the statement.",
            )}
          </p>
        ),
        target: ".jp-Cell.jp-Notebook-cell",
        placement: "bottom",
      },
      {
        title: i18next.t("Your code"),
        target: ".jp-Cell.jp-CodeCell",
        content: (
          <p>
            {i18next.t(
              "This is a cell, this is where you will write your code. A cell has an input and an output area.",
            )}
            <br />
            {i18next.t(
              "You can execute the code in the cell with 'Ctrl-Return'. Printed expressions will be displayed below the text field.",
            )}
            <br />
            {i18next.t(
              "If the last statement in the cell is an expression, its value will be considered as the cell's output.",
            )}
          </p>
        ),
        placement: "bottom",
      },
      {
        title: i18next.t("Unit tests"),
        content: (
          <p>
            {i18next.t(
              "If this exercise has units tests, this button how the unit tests that will test your code.",
            )}
          </p>
        ),
        target: ".toggleFormationCellButton",
        placement: "bottom",
      },
      {
        title: i18next.t("Run unit tests"),
        content: (
          <p>
            {i18next.t("This button will execute the unit tests.")} <br />
            <b>
              {i18next.t(
                "Don't forget to execute your code before running the tests.",
              )}
            </b>
          </p>
        ),
        target: ".jupyter-button",
        placement: "bottom",
      },
      {
        title: i18next.t("Solution"),
        content: (
          <p>{i18next.t("This button display the proposed solution.")}</p>
        ),
        target: ".jp-Cell:nth-child(4) .toggleFormationCellButton",
        placement: "bottom",
      },
      {
        title: i18next.t("Progress"),
        content: (
          <p>
            {i18next.t(
              "You can inform the trainer of your progress by clicking on this button",
            )}
            <ul>
              <li>{i18next.t("mark the exercise as done")}</li>
              <li>{i18next.t("ask for help for this exercise")}</li>
            </ul>
            <br />
          </p>
        ),
        target: ".progress-button",
        placement: "right",
      },
      {
        title: i18next.t("Have a Good Training"),
        content: (
          <p>
            <br />
            <b>
              {i18next.t(
                "And don't forget to stop your App at the end of the session.",
              )}
            </b>
            <br />
            <br />
            <div className="stop-app" />
          </p>
        ),
        target: ".jp-LabShell",
        placement: "center",
      },
    ],
  };
};
