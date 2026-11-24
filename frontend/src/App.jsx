import { useEffect, useState } from "react";

function App() {

  const [message, setMessage] = useState("Connecting...");

  useEffect(() => {

    fetch("http://127.0.0.1:8000/")
      .then(response => response.json())
      .then(data => {
        setMessage(data.message);
      })
      .catch(() => {
        setMessage("Backend connection failed");
      });

  }, []);

  return (
    <div className="min-h-screen bg-slate-950
                    flex items-center justify-center">

      <div className="text-center">

        <h1 className="text-5xl font-bold text-white">
          CloudOps
        </h1>

        <p className="mt-5 text-green-400">
          {message}
        </p>

      </div>

    </div>
  );
}

export default App;