import {
  ILabShell,
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from "@jupyterlab/application";
import { IDocumentManager } from "@jupyterlab/docmanager";
import { INotebookTracker } from "@jupyterlab/notebook";
import { IRenderMimeRegistry } from "@jupyterlab/rendermime";
import { IMainMenu } from "@jupyterlab/mainmenu";
import { MainAreaWidget, ICommandPalette } from "@jupyterlab/apputils";
import { Menu } from "@lumino/widgets";

import "../style/bootstrap/dist/css/bootstrap.css";
import "../style/index.css";

import { FormationTOC } from "./menu";
import { Flake8Button } from "./flake8";
import { ProgressButtons } from "./progressButton";
import { StatsWidget } from "./statsWidget";
import { addTour } from "./tour";

/**
 * Initialization data for the jupyterlab-formation Panel extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: "jupyterlab-training",
  autoStart: true,
  requires: [
    IDocumentManager,
    ILabShell,
    ILayoutRestorer,
    INotebookTracker,
    IRenderMimeRegistry,
    ICommandPalette,
    IMainMenu,
  ],
  activate: activate,
};

/**
 * Activate the formation extension.
 */
function activate(
  app: JupyterFrontEnd,
  docmanager: IDocumentManager,
  labShell: ILabShell,
  restorer: ILayoutRestorer,
  notebookTracker: INotebookTracker,
  rendermime: IRenderMimeRegistry,
  palette: ICommandPalette,
  mainMenu: IMainMenu,
): void {
  // Create the formation panel widget.
  const formationPanel = new FormationTOC({
    docmanager,
    rendermime,
    notebookTracker,
  });
  // Add the formation panel to the left area.
  formationPanel.title.iconClass =
    "lm-TabBar-tabIcon formation-icon jp-SideBar-tabIcon";
  formationPanel.title.caption = "Training Menu";
  formationPanel.id = "tab-manager";
  app.shell.add(formationPanel, "left", { rank: 10 });
  // Add the formation widget to the application restorer.
  restorer.add(formationPanel, formationPanel.id);
  // Change the LogilabPanel when the active widget changes.
  notebookTracker.currentChanged.connect(() => {
    formationPanel.currentWidget = notebookTracker.currentWidget;
    formationPanel.update();
  });
  // flake8 buttonExtension
  app.docRegistry.addWidgetExtension("Notebook", new Flake8Button());

  // progress button
  function updateMenu(): void {
    formationPanel.updateMenu();
  }

  const progressButtons = new ProgressButtons();
  progressButtons.stateChanged.connect(updateMenu);
  app.docRegistry.addWidgetExtension("Notebook", progressButtons);

  // stats buttonExtension
  const { commands } = app;
  const command = "training:stats";
  commands.addCommand(command, {
    label: "Display Student Statistics",
    caption: "Display students statistics",
    execute: () => {
      const content = new StatsWidget();
      const widget = new MainAreaWidget<StatsWidget>({ content });
      widget.title.label = "Students statistics";
      app.shell.add(widget, "main");
    },
  });
  palette.addItem({ command, category: "Training" });
  const statsMenu = new Menu({ commands });
  statsMenu.title.label = "Trainer";
  statsMenu.id = "training";
  mainMenu.addMenu(statsMenu, { rank: 80 });
  statsMenu.addItem({ command });

  app.restored.then(() => {
    // open formation panel by default
    labShell.activateById(formationPanel.id);
    // add extension tour
    addTour(app, labShell, notebookTracker, docmanager, formationPanel.id);
  });
}

export default extension;
