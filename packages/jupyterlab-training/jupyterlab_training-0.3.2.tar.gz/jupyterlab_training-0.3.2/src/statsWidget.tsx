import React, { useState, useEffect, useRef } from "react";
import { DateTime } from "luxon";
import { ReactWidget } from "@jupyterlab/apputils";
import { ServerConnection } from "@jupyterlab/services";

import { request } from "./utils";

interface Exercise {
  state: string;
  name: string;
  url: string;
}

export const StatsComponent = (): JSX.Element => {
  const [data, setData] = useState<any[]>([]);
  const [userName, setUserName] = useState("");
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [allow, setAllow] = useState(false);
  const inputElement = useRef(null);

  const update = () => {
    request("coll", "GET", {}, ServerConnection.makeSettings())
      .then((data) => {
        setData(data["info"]);
        setUserName("");
      })
      .catch(() => {
        console.error("Something went wrong :(");
      });
  };

  const resetDatabse = () => {
    request("resetDatabase", "GET", {}, ServerConnection.makeSettings())
      .then(() => {
        setData([]);
        window.location.reload();
      })
      .catch(() => {
        console.error("Something went wrong :(");
      });
  };

  useEffect(() => {
    update();
    if (inputElement.current) {
      inputElement.current.focus();
    }
  }, []);

  const select = (
    name: string,
    done_exos: Exercise[],
    need_help_exos: Exercise[],
  ) => {
    setUserName(name);
    setExercises(done_exos.concat(need_help_exos));
  };

  const validatePassword = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.currentTarget.value === "Logilab") {
      setAllow(true);
    }
  };
  return (
    <div>
      <h1>Students statistics</h1>
      {allow ? (
        <div>
          <div className="update-stats-div">
            <button
              className="btn btn-sm btn-danger float-right-button"
              onClick={(): void => {
                resetDatabse();
              }}
            >
              Reset database
            </button>
            <button
              className="btn btn-sm btn-primary float-right-button"
              onClick={(): void => {
                update();
              }}
            >
              Update
            </button>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th scope="col">User Name</th>
                <th scope="col">Nb of done Exercises</th>
                <th scope="col">Nb of need help Exercises</th>
                <th scope="col">Last update</th>
              </tr>
            </thead>
            <tbody>
              {data.map((stats) => (
                <tr
                  key={stats[1]}
                  onClick={() => select(stats[0], stats[3], stats[4])}
                  className={userName === stats[0] ? "selected" : "default"}
                >
                  <td>{stats[0]}</td>
                  <td>{stats[1]}</td>
                  <td>{stats[2]}</td>
                  <td>
                    {DateTime.fromISO(stats[5]).toLocaleString(
                      DateTime.DATETIME_SHORT,
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {userName && (
            <div>
              <h2>{userName}</h2>
              <b>done</b>
              <ul>
                {exercises
                  .filter((exo) => exo.state === "done")
                  .map((exo) => (
                    <li key={exo.name}>
                      {exo.name}{" "}
                      <a target="_blank" rel="noreferrer" href={exo.url}>
                        view
                      </a>
                    </li>
                  ))}
              </ul>
              <b>need Help</b>
              <ul>
                {exercises
                  .filter((exo) => exo.state === "needHelp")
                  .map((exo) => (
                    <li key={exo.name}>
                      {exo.name}{" "}
                      <a target="_blank" rel="noreferrer" href={exo.url}>
                        view
                      </a>
                    </li>
                  ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div>
          <input
            type="password"
            name="trainnerPassword"
            onChange={validatePassword}
            ref={inputElement}
            placeholder="Password"
          />
        </div>
      )}
    </div>
  );
};

export class StatsWidget extends ReactWidget {
  constructor() {
    super();
    this.addClass("stats-ReactWidget");
  }

  render(): JSX.Element {
    return <StatsComponent />;
  }
}
