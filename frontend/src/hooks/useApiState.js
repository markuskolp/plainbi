import { useState } from 'react';

const extractErrorDetail = (err) => {
  const data = err?.response?.data;
  if (!data) return '';
  const msg = data.message || '';
  const detail = data.detail ? ': ' + data.detail : '';
  return msg + detail;
};

const useApiState = (initialLoading = false) => {
  const [loading, setLoading] = useState(initialLoading);
  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [errorDetail, setErrorDetail] = useState('');

  const setApiError = (msg, err) => {
    setLoading(false);
    setError(true);
    setErrorMessage(msg);
    setErrorDetail(extractErrorDetail(err));
  };

  const resetError = () => {
    setError(false);
    setErrorMessage('');
    setErrorDetail('');
  };

  return { loading, setLoading, error, errorMessage, errorDetail, setApiError, resetError };
};

export default useApiState;
