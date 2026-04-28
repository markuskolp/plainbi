import React, { useRef, useEffect, useState } from "react";
import { message, Typography, Space } from 'antd';
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import LoadingMessage from "../components/LoadingMessage";
import apiClient from "../utils/apiClient";

//import useToken from "../components/useToken";
//const { token, removeToken, setToken } = useToken();

const { Link, Text, Title } = Typography;

const LoginSSO = (props) => {
  
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  //let { code } = useParams(); // get URL parameters - get the relevant values 
  let [searchParams, setSearchParams] = useSearchParams();
  const code = searchParams.get("code");
  const client_info = searchParams.get("client_info");
  const state = searchParams.get("state");
  const session_state = searchParams.get("session_state");
  const tok = searchParams.get("access_token");
  //console.log("code",code);
  //console.log("LoginSSO param - code: " + code);
  //console.log("LoginSSO token:" + tok);

  const paramsObject = Object.fromEntries(searchParams.entries());
  
  const [loading, setLoading] = useState(false);
  //const [loading, setLoading] = useState(true);

  // todo: endpoint POST /api/login_sso aufrufen mit URL-parameter (?code=...) im Body
  // wenn ich Token zurückbekomme, dann setToken (sollte dann auf richtige Seite springen z.B. Startseite - analog zu Login.js)
  
  useEffect(() => {
    const performLogin = async () => {
      try {
        const response = await apiClient.post('/api/login_sso', paramsObject);
        props.setToken(response.data.access_token);
        localStorage.setItem('role', response.data.role ? response.data.role.toUpperCase() : 'USER');
        setSuccess(true);
        setLoading(false);
      } catch (err) {
        setError(err.response?.data?.message || err.message || 'Login failed');
        setLoading(false);
      }
    }
    performLogin();
  }, []);
  
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => {
        navigate('/', { state: { refresh: true}});
        window.location.reload();
      },1000);
      return () => clearTimeout(timer);
    }
  }, [success, navigate]);

  if (error) {
    return (
      <div className="center">
       <Title level={5} style={{color:'red' }}>Fehler bei Anmeldung</Title>
      </div>
   )
  }

  if (success) {
    return (
       <div className="center">
        <Title level={5}>Anmeldung erfolgreich - es wird weitergeleitet...</Title>
       </div>
    );
  }

  return null;

        
    
};

export default LoginSSO;
