import { ContentsManager } from "@jupyterlab/services";
import * as jsyaml from "js-yaml";

interface JFile {
  name: string;
  path: string;
}

interface JDirectory {
  name: string;
  type: string;
  path: string;
  metadata: any;
}

/**
 * Parse formation workspace
 */
class WorkspaceTree {
  constructor(public exos: JDirectory[], public courses: JDirectory[]) {}

  private static async getNotbooksCategoriesPromise(
    contents: ContentsManager,
    nbType: "exercises" | "courses",
  ): Promise<JDirectory[]> {
    const nbDir = "training";
    const modelTraining = await contents.get(nbDir);
    const metadataFile = modelTraining.content.find(
      (elt: JFile) => elt.name === "workspace.yml",
    );
    return await this.getArboFromMetadataFile(
      contents,
      nbType,
      metadataFile.path,
      nbDir,
    );
  }

  private static async getArboFromMetadataFile(
    contents: ContentsManager,
    nbType: string,
    metadataFilepath: string,
    dirPath: string,
  ): Promise<JDirectory[]> {
    const directory: JDirectory[] = [];
    const metadataFileContent = (await contents.get(metadataFilepath)).content;
    const globalMetadata = jsyaml.safeLoad(metadataFileContent);
    for (const [name, metaData] of (Object as any).entries(globalMetadata)) {
      if (name.includes(nbType)) {
        const nbPath = `${dirPath}/${name}`;
        directory.push({
          name: name,
          type: nbType,
          path: nbPath,
          metadata: metaData,
        });
      }
    }
    return directory;
  }

  public static async create(): Promise<WorkspaceTree> {
    const contents = new ContentsManager();
    return new WorkspaceTree(
      await this.getNotbooksCategoriesPromise(contents, "exercises"),
      await this.getNotbooksCategoriesPromise(contents, "courses"),
    );
  }
}

export { JFile, JDirectory, WorkspaceTree };
