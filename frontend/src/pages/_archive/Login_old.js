import { useState } from 'react';
import axios from "axios";

function Login(props) {

    const [loginForm, setloginForm] = useState({
      username: "",
      password: ""
    })

    function logMeIn(event) {
      axios({
        method: "POST",
        url:"/api/login",
        data:{
          username: loginForm.username,
          password: loginForm.password
         }
      })
      .then((response) => {
        props.setToken(response.data.access_token)
      }).catch((error) => {
        if (error.response) {
          console.log(error.response)
          console.log(error.response.status)
          console.log(error.response.headers)
          }
      })

      setloginForm(({
        username: "",
        password: ""}))

      event.preventDefault()
    }

    function handleChange(event) { 
      const {value, name} = event.target
      setloginForm(prevNote => ({
          ...prevNote, [name]: value})
      )}

    return (
      <div>
        <h1>Bitte anmelden ...</h1>
          <form className="login">
            <input onChange={handleChange} 
                  type="text"
                  text={loginForm.username} 
                  name="username" 
                  placeholder="username" 
                  value={loginForm.username} />
            <input onChange={handleChange} 
                  type="password"
                  text={loginForm.password} 
                  name="password" 
                  placeholder="Password" 
                  value={loginForm.password} />

          <button onClick={logMeIn}>Login</button>
        </form>
      </div>
    );
}

export default Login;
