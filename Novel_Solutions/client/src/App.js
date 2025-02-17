import React, { useState, useEffect } from "react";

import Login from "./login";

function App() {

  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/login')
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        console.log(data)
      });
  }, []);

  return (
    <div>
      {(typeof data.Login == "undefined") ? (
        <Login />
      ) : (
        <div>
          <h1>{data.Login}</h1>
        </div>
      )}
    </div>
  );
}

export default App;