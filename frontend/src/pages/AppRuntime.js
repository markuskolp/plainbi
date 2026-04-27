import React from "react";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import NoPage from "./NoPage";
import { Alert } from "antd";
import CRUDApp from "../components/CRUDApp";
import LoadingMessage from "../components/LoadingMessage";
import apiClient from "../utils/apiClient";
import useApiState from "../hooks/useApiState";

const AppRuntime = (props) => {

  let { id, page_id } = useParams();
  let start_page_id = (page_id ? page_id : null);

  const { loading, setLoading, error, errorMessage, errorDetail, setApiError, resetError } = useApiState(true);
  const [appNotFound, setAppNotFound] = useState(false);
  const [appMetadata, setAppMetadata] = useState([]);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    resetError();
    apiClient.get("/api/repo/application/" + id)
      .then((res) => {
        const resData = res.data.length === 0 || res.data.length === undefined ? res.data.data[0] : res.data[0];
        try {
          JSON.parse(resData.spec_json).pages;
          setAppMetadata(resData);
        } catch (err) {
          setApiError('Applikations Spezifikation hat einen Fehler.', { response: { data: { detail: err.toString() } } });
        }
        setLoading(false);
      })
      .catch((err) => {
        setAppNotFound(true);
        setLoading(false);
        setApiError('Es gab einen Fehler beim Laden der Applikation', err);
      });
  };

  return appNotFound ? (
    <NoPage />
  ) : error ? (
    <Alert message={errorMessage} description={errorDetail} type="error" showIcon />
  ) : loading ? (
    <LoadingMessage />
  ) : (
    <React.Fragment>
      <CRUDApp
        name={appMetadata.name}
        alias={appMetadata.alias}
        datasource={appMetadata.datasource_id}
        pages={JSON.parse(appMetadata.spec_json).pages}
        token={props.token}
        start_page_id={start_page_id}
      />
    </React.Fragment>
  );
};

export default AppRuntime;
