import React from "react";
import { useState, useEffect } from "react";

const getData = (url) => {
    const [state, setState] = useState();
  
    useEffect(() => {
      const dataFetch = async () => {
        const data = await (await fetch(url)).json();
        setState(data);
      };
  
      dataFetch();
    }, [url]);

    return { data: state };
  };

  export default getData;