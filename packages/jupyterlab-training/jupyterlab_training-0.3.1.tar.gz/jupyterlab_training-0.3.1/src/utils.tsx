import { URLExt } from "@jupyterlab/coreutils";
import { ServerConnection } from "@jupyterlab/services";
import * as React from "react";

export async function request(
  path: string,
  method: string,
  body: any,
  settings: ServerConnection.ISettings,
): Promise<any> {
  const fullUrl = URLExt.join(settings.baseUrl, "jupyterlab-training", path);
  let init: any = { method, credentials: "include" };
  if (method === "POST") {
    init = { body, method, credentials: "include" };
  }
  return ServerConnection.makeRequest(fullUrl, init, settings).then(
    async (response) => {
      if (response.status !== 200) {
        return response.text().then((data) => {
          throw new ServerConnection.ResponseError(response, data);
        });
      }
      return response.json();
    },
  );
}

export class SpinnerPanel extends React.Component {
  public render() {
    return (
      <div className="jp-Spinner">
        <div className="jp-SpinnerContent">Loading...</div>
      </div>
    );
  }
}
