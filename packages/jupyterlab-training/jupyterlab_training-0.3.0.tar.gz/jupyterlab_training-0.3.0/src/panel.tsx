import { ContentsManager } from "@jupyterlab/services";
import { ServerConnection } from "@jupyterlab/services";
import { Widget } from "@lumino/widgets";
import FileSaver from "file-saver";
import JSZip from "jszip";
import * as React from "react";
import { Dropdown } from "react-bootstrap";
import i18next from "./i18n";
import { JDirectory, JFile, WorkspaceTree } from "./model";
import { request, SpinnerPanel } from "./utils";

interface TrainingPanelProps {
  openExercisesNotebook: (path: string, lang: string) => void;
  arboFormation: WorkspaceTree;
  getCurrentWidget: () => Widget;
}

interface TrainingPanelState {
  filter: string[];
  lang: string;
  doneExercises: string[];
  needHelpExercises: string[];
  tab: string;
  paths: string;
  downloaded: boolean;
}

function getUserLanguage() {
  if (i18next.language) {
    return i18next.language;
  }
  if (navigator.language === "fr") {
    return "fr";
  }
  return "en";
}

export class TrainingPanel extends React.Component<
  TrainingPanelProps,
  TrainingPanelState
> {
  private title = "Training";
  constructor(props: TrainingPanelProps) {
    super(props);
    this.state = {
      filter: [],
      lang: getUserLanguage(),
      doneExercises: [],
      needHelpExercises: [],
      tab: "exercises",
      paths: "",
      downloaded: false,
    };
  }

  private updateProgess = () => {
    // read db to update exercises states
    request("coll", "GET", {}, ServerConnection.makeSettings())
      .then((data) => {
        const user_data = data["info"].filter(
          (user_data: any) => user_data[0] === data["user"],
        );
        const doneExercises = user_data[0][3].map(
          (file_info: any) => file_info.name,
        );
        const needHelpExercises = user_data[0][4].map(
          (file_info: any) => file_info.name,
        );
        if (
          this.state.doneExercises.toString() !== doneExercises.toString() ||
          this.state.needHelpExercises.toString() !==
            needHelpExercises.toString()
        ) {
          this.setState({
            doneExercises,
            needHelpExercises,
          });
        }
      })
      .catch(() => {
        console.error("Something went wrong :(");
      });
  };

  private handleFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({
      filter: event.currentTarget.value.toLowerCase().split(" "),
    });
  };

  private handleLanguageChange = (
    event: React.ChangeEvent<HTMLSelectElement>,
  ) => {
    i18next.changeLanguage(event.target.value);
    this.setState({ lang: event.target.value });
  };

  private handlePathChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    this.setState({ paths: event.target.value });
  };

  private addToSearchBar = (event: React.MouseEvent<HTMLAnchorElement>) => {
    let currentTag = event.currentTarget.text.trim();
    if (!isNaN(parseInt(currentTag))) {
      currentTag = "difficulty:" + currentTag;
    }
    const existingTags = this.state.filter;
    if (existingTags.indexOf(currentTag) === -1) {
      existingTags.push(currentTag);
    }
    this.setState({ filter: existingTags });
  };

  private filterOnPaths(dir: JDirectory): boolean {
    if (this.state.paths === "") {
      return true;
    }
    if (dir.metadata && "paths" in dir.metadata) {
      if (dir.metadata["paths"].includes(this.state.paths)) {
        return true;
      }
    }
    return false;
  }

  private filterOnTags(dir: JDirectory): boolean {
    let isIncluded = true;
    const metadata = dir.metadata;
    let tagsString = "";
    if (metadata) {
      let keywords = metadata["topics"].concat(metadata["slug"]);
      if (metadata["slug_fr"]) {
        keywords = keywords.concat(metadata["slug_fr"]);
      }
      keywords.map((tag: string) => {
        tagsString = tagsString + tag.trim() + i18next.t(tag.trim());
      });
      tagsString = ["difficulty:" + metadata["difficulty"], tagsString]
        .join(" ")
        .toLowerCase();
    }
    // exercises are filtered with AND
    this.state.filter.map((word: string) => {
      isIncluded = tagsString.includes(word) && isIncluded;
    });
    return isIncluded;
  }

  private sortByMetadata(
    dir1: JDirectory,
    dir2: JDirectory,
    metadata: string,
  ): number {
    try {
      const difficultyDiff = dir1.metadata[metadata] - dir2.metadata[metadata];
      if (difficultyDiff !== 0) {
        return difficultyDiff;
      }
      const name1 = dir1.name.toLowerCase();
      const name2 = dir2.name.toLowerCase();
      return name1.localeCompare(name2);
    } catch (err) {
      return null;
    }
  }

  private resetFilters = () => {
    this.setState({ filter: [] });
  };

  private convertNbToPDF = async (filename: string) => {
    request(
      "topdf",
      "POST",
      JSON.stringify({
        filename: filename,
      }),
      ServerConnection.makeSettings(),
    );
  };

  private addNotebookToZipFolder = async (
    zip: JSZip,
    filePath: string,
    filename: string,
  ) => {
    const contentsManager = new ContentsManager();
    const filecontent = (
      await contentsManager.get(filePath, { type: "file", content: true })
    ).content;
    zip.file(filename, filecontent);
  };

  private addPDFToZipFolder = async (
    zip: JSZip,
    file: JFile,
    filename: string,
  ) => {
    const contentsManager = new ContentsManager();
    const pdfFile = await contentsManager.get(file.path, {
      type: "file",
      content: true,
      format: "base64",
    });
    zip.file(filename, atob(pdfFile.content), { binary: true });
  };

  private createAndAddPDF = async (
    zipFolder: JSZip,
    nb: JFile,
    targetFileName: string,
  ) => {
    const exo_name = nb.path.split("/").pop();
    const nbName = `${exo_name}.${this.state.lang}.ipynb`;
    await this.convertNbToPDF(`${nb.path}/${nbName}`)
      .then(async () => {
        const pdfName = `${exo_name}.${this.state.lang}.pdf`;
        const contents = new ContentsManager();
        const pdfFile = await contents.get(`${nb.path}/${pdfName}`, {
          type: "file",
          format: "base64",
        });
        await this.addPDFToZipFolder(
          zipFolder,
          pdfFile,
          `${targetFileName}.pdf`,
        );
      })
      .catch(() => {
        console.error(`Error with the generation of ${targetFileName}`);
      });
  };

  private addSelectedNotebooksToZipFolder = async (
    zipFolder: JSZip,
    notebooks: JDirectory[],
    includePDF: boolean,
  ) => {
    for (const nb of notebooks) {
      const exo_name = nb.path.split("/").pop();
      if (this.state.doneExercises.indexOf(exo_name) !== -1) {
        const nbName = `${exo_name}.${this.state.lang}.ipynb`;
        const ipynbFile = `${nb.path}/${nbName}`;
        const i18nSlug = "slug_" + this.state.lang;
        let targetFileName =
          i18nSlug in nb.metadata ? nb.metadata[i18nSlug] : nb.metadata["slug"];
        targetFileName = targetFileName.replace(" ", "_");
        if (includePDF) {
          await this.createAndAddPDF(zipFolder, nb, targetFileName);
        }
        await this.addNotebookToZipFolder(
          zipFolder,
          ipynbFile,
          `${targetFileName}.ipynb`,
        );
      }
    }
  };

  private async buildZip(includePDF: boolean) {
    this.setState({ downloaded: true });
    const zip = new JSZip();
    try {
      const zipFolder = zip.folder("logilab-training-notebooks");
      await this.addSelectedNotebooksToZipFolder(
        zipFolder,
        this.props.arboFormation.exos,
        includePDF,
      );
    } finally {
      this.setState({ downloaded: false });
    }
    return zip;
  }

  private nbDownload = async () => {
    const zip = await this.buildZip(false);
    const content = await zip.generateAsync({ type: "blob" });
    FileSaver.saveAs(content, "notebooks.zip");
  };

  private nbPDFDownload = async () => {
    const zip = await this.buildZip(true);
    const content = await zip.generateAsync({ type: "blob" });
    FileSaver.saveAs(content, "notebooks_and_pdf.zip");
  };

  private getTrainingPaths(exos: JDirectory[]) {
    const trainingPaths = new Set();
    exos.map((exo: JDirectory) => {
      if (exo.metadata.paths) {
        for (const p of exo.metadata.paths) {
          trainingPaths.add(p);
        }
      }
    });
    return trainingPaths;
  }

  private getButtonTitle(dir: JDirectory) {
    const suffix = ".".concat(this.state.lang, "ipynb");
    let buttonTitle = dir.path.replace(suffix, "").replace(/^.*_/, "");
    if (dir.metadata) {
      buttonTitle = dir.metadata["slug"];
      if (`slug_${this.state.lang}` in dir.metadata) {
        buttonTitle = dir.metadata[`slug_${this.state.lang}`];
      }
    }
    if (buttonTitle.includes("__")) {
      buttonTitle = buttonTitle.split("__")[1];
    }
    return buttonTitle;
  }

  private getIsActiveButtonClass(name: string, currentWidget: any) {
    // To activate the button of the current notebook
    let activeButton = "";
    if (currentWidget !== null) {
      if (
        name ===
        currentWidget.context.path.split("/").slice(-2).pop().split(".")[0]
      ) {
        activeButton = "current-button";
      }
    }
    return activeButton;
  }

  private renderAdvancedOptions(trainingPaths: string[]) {
    return (
      <div>
        <div className="showHide">
          <label
            htmlFor="toggle"
            id="toggle-options"
            className="dropdown-toggle"
          >
            {i18next.t("Advanced options")}
          </label>
          <div className="fieldsetContainer">
            <fieldset>
              <form>
                <div className="form-group">
                  <div className="form-group">
                    <label htmlFor="lang">{i18next.t("Language")}</label>{" "}
                    <select
                      id="lang"
                      className="form-control-sm custom-select"
                      onChange={this.handleLanguageChange}
                      value={this.state.lang}
                    >
                      <option value="en">en</option>
                      <option value="fr">fr</option>
                    </select>
                  </div>
                  <select
                    className="form-control-sm custom-select"
                    id="path"
                    onChange={this.handlePathChange}
                    value={this.state.paths}
                  >
                    <option value="">{i18next.t("Select your path")}</option>
                    {trainingPaths.map((path: string) => {
                      return (
                        <option value={path} key={path}>
                          {i18next.t(path)}
                        </option>
                      );
                    })}
                  </select>
                </div>
                <div className="form-group">
                  <Dropdown>
                    <Dropdown.Toggle
                      className="form-control-sm custom-dropdown"
                      size="sm"
                      id="dropdown"
                    >
                      {i18next.t("Get selected notebooks")}
                    </Dropdown.Toggle>
                    <Dropdown.Menu alignRight>
                      <Dropdown.Item
                        className="form-control-sm"
                        href="#"
                        onClick={this.nbDownload}
                      >
                        {i18next.t("Only notebooks")}
                      </Dropdown.Item>
                      <Dropdown.Item
                        className="form-control-sm"
                        href="#"
                        onClick={this.nbPDFDownload}
                      >
                        {i18next.t("Notebooks and PDF")}
                      </Dropdown.Item>
                    </Dropdown.Menu>
                  </Dropdown>
                  {this.state.downloaded ? <SpinnerPanel /> : null}
                </div>
              </form>
            </fieldset>
          </div>
        </div>
      </div>
    );
  }

  public renderArbo(
    arbo: JDirectory[],
    openNotebook: any,
    orderby: string,
    getCurrentWidget: () => Widget,
  ) {
    const handledCategories = new Set();
    return arbo
      .sort((dir1: JDirectory, dir2: JDirectory) =>
        this.sortByMetadata(dir1, dir2, orderby),
      )
      .filter((dir: JDirectory) => this.filterOnTags(dir))
      .filter((dir: JDirectory) => this.filterOnPaths(dir))
      .map((dir: JDirectory, exoIndex: number) => {
        const buttonTitle = this.getButtonTitle(dir);
        const difficultyString = dir.metadata ? dir.metadata.difficulty : "";
        const currentWidget = getCurrentWidget();
        const isActive = this.getIsActiveButtonClass(
          dir.path.split("/").slice(-1)[0],
          currentWidget,
        );
        const dirCategory = dir.metadata ? dir.metadata.category : "More";
        const isNewCategory = !handledCategories.has(dirCategory);
        if (isNewCategory) {
          handledCategories.add(dirCategory);
        }
        let progessIconClass = "fa-play-circle";
        let progressMessage = "";
        if (this.state.doneExercises.indexOf(dir.name.split("/")[1]) > -1) {
          progessIconClass = "fa-check-circle";
          progressMessage = "success";
        }
        let need_help = false;
        if (this.state.needHelpExercises.indexOf(dir.name.split("/")[1]) > -1) {
          need_help = true;
        }
        let difficultyColor = "#8be757";
        switch (parseInt(difficultyString)) {
          case 2:
            difficultyColor = "#8bb527";
            break;
          case 3:
            difficultyColor = "#f2e501";
            break;
          case 4:
            difficultyColor = "#fdc50c";
            break;
          case 5:
            difficultyColor = "#ffa400";
            break;
          case 6:
            difficultyColor = "#ee8f1c";
            break;
          case 7:
            difficultyColor = "#ee7621";
            break;
          case 8:
            difficultyColor = "#ff6347";
            break;
          case 9:
            difficultyColor = "#b52a2a";
            break;
          case 10:
            difficultyColor = "#8b0000";
            break;
        }
        return (
          <div key={`category-${exoIndex}`}>
            {isNewCategory ? (
              <div className="category">
                <h2>{i18next.t(dirCategory)}</h2>
              </div>
            ) : null}
            <div
              key={`exo-${exoIndex}`}
              className={`list-group-item list-group-item-action ${isActive}`}
            >
              <div>
                <div className="form-check form-check-inline">
                  <i
                    className={`fa ${progessIconClass}`}
                    title={progressMessage}
                  ></i>
                  <a
                    href="#"
                    onClick={() => openNotebook(dir.path, this.state.lang)}
                    className="button-title"
                  >
                    {i18next.t(buttonTitle)}
                  </a>
                </div>
                <div className={"float-right my-2"}>
                  {need_help && (
                    <i className={"fa fa-hand-stop-o"} title="need help"></i>
                  )}
                  <a
                    href="#"
                    onClick={this.addToSearchBar}
                    className="badge badge-pill badge-secondary button-difficulty"
                    title={`This ${dir.type} is difficulty ${difficultyString}`}
                    style={{
                      marginLeft: "0.5em",
                      backgroundColor: difficultyColor,
                    }}
                  >
                    {difficultyString}
                  </a>
                </div>
              </div>
              <div className="button-tags">
                {dir.metadata &&
                  dir.metadata["topics"].map(
                    (tag: string, tagIndex: number) => {
                      return (
                        <a
                          href="#"
                          key={["tag", exoIndex, tagIndex].join("-")}
                          onClick={this.addToSearchBar}
                          className="badge badge-light"
                        >
                          {i18next.t(tag)}
                        </a>
                      );
                    },
                  )}
              </div>
            </div>
          </div>
        );
      });
  }

  public render() {
    const { arboFormation, openExercisesNotebook, getCurrentWidget } =
      this.props;
    if (!arboFormation) {
      return (
        <div className="jp-TableOfContents" id="jupyterlab-training">
          <header className="formation-header">{this.title}</header>
          <h2>Error</h2>
          <h3>Cannot find workspace</h3>
        </div>
      );
    }
    this.updateProgess();
    const trainingPaths = this.getTrainingPaths(arboFormation.exos);

    return (
      <div className="jp-TableOfContents" id="jupyterlab-training">
        <header className="formation-header">{this.title}</header>
        <div className="input-group mb-3" id="filter">
          <input
            className="form-control"
            placeholder="Search"
            onChange={this.handleFilterChange}
            value={this.state.filter.join(" ")}
          />
          <div className="input-group-append">
            <div className="input-group-text">
              <button
                type="button"
                className="btn close"
                aria-label="Remove content"
                onClick={this.resetFilters}
              >
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
          </div>
        </div>
        <input type="checkbox" id="toggle" />
        {this.renderAdvancedOptions([...trainingPaths] as string[])}
        <ul className="nav nav-tabs nav-justified" role="tablist">
          <li className="nav-item">
            <a
              className={
                "nav-link" + (this.state.tab === "exercises" ? " active" : "")
              }
              id="exercises-tab"
              onClick={() => this.setState({ tab: "exercises" })}
            >
              {i18next.t("exercises")}
            </a>
          </li>
          <li className="nav-item">
            <a
              className={
                "nav-link" + (this.state.tab === "courses" ? " active" : "")
              }
              id="courses-tab"
              onClick={() => this.setState({ tab: "courses" })}
            >
              {i18next.t("courses")}
            </a>
          </li>
        </ul>
        <div className="tab-content">
          <div
            className={
              "tab-pane fade" +
              (this.state.tab === "exercises" ? " show active" : "")
            }
          >
            <div
              id="exercises"
              className="exercises list-group list-group-flush"
            >
              {this.renderArbo(
                arboFormation.exos,
                openExercisesNotebook,
                "order",
                getCurrentWidget,
              )}
            </div>
          </div>
          <div
            className={
              "tab-pane fade" +
              (this.state.tab === "courses" ? " show active" : "")
            }
          >
            <div
              id="exercises"
              className="exercises list-group list-group-flush"
            >
              {this.renderArbo(
                arboFormation.courses,
                openExercisesNotebook,
                "order",
                getCurrentWidget,
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }
}
