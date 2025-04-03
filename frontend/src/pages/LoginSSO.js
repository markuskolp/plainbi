import React, { useRef, useEffect, useState } from "react";
import { message, Typography  } from 'antd';
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import LoadingMessage from "../components/LoadingMessage";
import Axios from "axios";
//import useToken from "../components/useToken";

//const { token, removeToken, setToken } = useToken();

const { Link, Text, Title } = Typography;

//const navigate = useNavigate();

const LoginSSO = (props) => {
  

  //let { code } = useParams(); // get URL parameters - get the relevant values 
  let [searchParams, setSearchParams] = useSearchParams();
  const code = searchParams.get("code");
  const client_info = searchParams.get("client_info");
  const state = searchParams.get("state");
  const session_state = searchParams.get("session_state");
  const tok = searchParams.get("access_token");
  //console.log("code",code);
  console.log("client_info",client_info);
  console.log("state",state);
  console.log("session_state",session_state);
  //console.log("LoginSSO param - code: " + code);
  //console.log("LoginSSO token:" + tok);

  const paramsObject = Object.fromEntries(searchParams.entries());
  
  const [loading, setLoading] = useState(false);
  //const [loading, setLoading] = useState(true);

  // todo: endpoint POST /api/login_sso aufrufen mit URL-parameter (?code=...) im Body
  // wenn ich Token zurückbekomme, dann setToken (sollte dann auf richtige Seite springen z.B. Startseite - analog zu Login.js)
  
  useEffect(() => {
    logMeIn();
  }, []);
  
  function logMeIn(event) {
    console.log("logMeIn");
    setLoading(true);
    Axios({
      method: "POST",
      url:"/api/login_sso",
      data : paramsObject
      //data:{
      //  code: code,
      //  client_info: client_info,
      //  state: state,
      //  session_state: session_state
      // }
    })
    .then((response) => {
      console.log("logMeIn SUCCESS");
      console.log("logMeInResponse token: "+response.data.access_token);
      props.setToken(response.data.access_token);
      console.log("logMeIn after setToken");
      //props.setRole(response.data.role ? response.data.role.toUpperCase() : 'ADMIN');
      localStorage.setItem('role', response.data.role ? response.data.role.toUpperCase() : 'USER');
      //localStorage.setItem('role', 'ADMIN');
      //props.setRole('ADMIN');
  
    }).catch((error) => {
      console.log("logMeIn ERROR");
      console.log(error);
      if (error.response) {
        console.log(error.response);
        console.log(error.response.status);
        console.log(error.response.headers);
        }
        setLoading(false);
//message.error('Fehler: ' + error.response.data.message);
    
      })

    //event.preventDefault()
  }

  //return <LoadingMessage />;
  console.log("logMeInResponse token:  ");
  return <Link href="/"> weiter </Link>

}

export default LoginSSO;
