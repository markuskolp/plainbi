import { useContext, useEffect, useState, useRef } from 'react';
import { isQueryPresent, areQueriesEqual } from '@cubejs-client/core';
import CubeContext from './CubeContext';
import { useIsMounted } from './is-mounted';

// based on:
// https://github.com/cube-js/cube/blob/f29c592931c280f1f1e1b021c7b0cefbbd0c029b/packages/cubejs-client-react/src/hooks/cube-query.js#L8

export function useQuery(query, options = {}) {
  const mutexRef = useRef({});
  const isMounted = useIsMounted();
  const [currentQuery, setCurrentQuery] = useState(null);
  const [isLoading, setLoading] = useState(false);
  const [resultSet, setResultSet] = useState(null);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);
  const context = useContext(CubeContext);

  let subscribeRequest = null;

  const progressCallback = ({ progressResponse }) => setProgress(progressResponse);
  
  useEffect(() => {
    if (options.cubejsApi && !options.cubeApi) {
      console.warn('"cubejsApi" is deprecated and will be removed in the following version. Use "cubeApi" instead.');
    }
  }, [options.cubeApi, options.cubejsApi]);

  async function fetch() {
    const { resetResultSetOnChange } = options;
    const cubeApi = options.cubeApi || options.cubejsApi || context?.cubeApi || context?.cubejsApi;

    if (!cubeApi) {
      throw new Error('Cube API client is not provided');
    }

    if (resetResultSetOnChange) {
      setResultSet(null);
    }

    setError(null);
    setLoading(true);
    
    try {
      const response = await cubeApi.load(query, {
        mutexObj: mutexRef.current,
        mutexKey: 'query',
        progressCallback,
        castNumerics: Boolean(typeof options.castNumerics === 'boolean' ? options.castNumerics : context?.options?.castNumerics)
      });

      if (isMounted()) {
        setResultSet(response);
        setProgress(null);
      }
    } catch (error) {
      if (isMounted()) {
        setError(error);
        setResultSet(null);
        setProgress(null);
      }
    }

    if (isMounted()) {
      setLoading(false);
    }
  }

  //console.log("useQuery() - query");
  //console.log(query);

  useEffect(() => {
    //console.log("useQuery() - useEffect()");
    const { skip = false, resetResultSetOnChange } = options;

    const cubeApi = options.cubeApi || options.cubejsApi || context?.cubeApi || context?.cubejsApi;

    if (!cubeApi) {
      throw new Error('Cube API client is not provided');
    }

    async function loadQuery() {
      if (!skip && isQueryPresent(query)) {
        if (!areQueriesEqual(currentQuery, query)) {
          if (resetResultSetOnChange == null || resetResultSetOnChange) {
            setResultSet(null);
          }
          setCurrentQuery(query);
        }
        setResultSet(null);
        setCurrentQuery(query);

        setError(null);
        setLoading(true);

        try {
          //console.log("useQuery() - query: ");
          //console.log(query);
          //console.log("useQuery() - fetching...");

            await fetch();
          
        } catch (e) {
          if (isMounted()) {
            setError(e);
            setResultSet(null);
            setLoading(false);
            setProgress(null);
          }
        }
      }
    }

    loadQuery();

  //}, useDeepCompareMemoize([query, Object.keys((query && query.order) || {}), options, context]));
  }, [query.limit, query.filters, query.measures, query.order, query.segments]);

  return {
    isLoading,
    resultSet,
    error,
    progress,
    previousQuery: currentQuery,
    refetch: fetch
  };
}