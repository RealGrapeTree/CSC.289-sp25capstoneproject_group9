import React, { useState, useEffect } from 'react';

function App() {
  const [data, setData] = useState([{}]);

  useEffect(() => {
    fetch('/').then(
      res => res.json())
      .then(
        data => {
          setData(data);
          console.log(data)
        }
      ).catch(
        err => console.log(err)
      )
  }, []);


  return (
    <div>

      <h2>Welcome to the POS System</h2>
      <p><a href="{{ url_for('login') }}">Login Here</a></p>
    </div>
  );


}

export default App;