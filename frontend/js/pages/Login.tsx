import React, {useState, use, useEffect} from "react";
import {AuthContext} from "../components/AuthProvider";
import {useNavigate} from "react-router-dom";

export const Login: React.FC = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { handleLogin } = use(AuthContext);

  useEffect(() => {
    console.log("Login | Mounted component")

    return () => console.log("Login | Unmounted component")
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    try {
      await handleLogin({ username, password });
      console.log("Login successful");
      // Redirect or perform additional actions upon successful login
      navigate("/");
    } catch (e) {
      setError("Invalid username or password. Please try again."); // Show error message
    }
  };

  return (
    <div className="text-center min-vh-100 max-vh-100" id="login-wrap">
      <main className="form-signin w-100 m-auto">
        <form onSubmit={handleSubmit}>
          <h1 className="h3 mb-3 fw-normal">Please sign in</h1>

          {error && <div className="alert alert-danger">{error}</div>}

          <div className="form-floating mb-3">
            <input
              type="text"
              name="username"
              className="form-control"
              id="username"
              placeholder="Username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <label htmlFor="username">Username</label>
          </div>
          <div className="form-floating mb-3">
            <input
              type="password"
              name="password"
              className="form-control"
              id="password"
              placeholder="Password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <label htmlFor="password">Password</label>
          </div>

          <button className="w-100 btn btn-lg btn-primary" type="submit">
            Sign in
          </button>
          <p className="mt-5 mb-3 text-muted">©2025</p>
        </form>
      </main>
    </div>
  );
};

export default Login;