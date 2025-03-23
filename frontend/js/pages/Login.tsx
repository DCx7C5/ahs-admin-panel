import React, {use, useActionState, useEffect, useOptimistic} from "react";
import { DataContext } from "../components/DataProvider";
import { useNavigate } from "react-router-dom";
import "@/../css/register.scss";


export const Login: React.FC = () => {
  const { isAuthenticated, apiClient, cryptoClient } = use(DataContext);
  const navigate = useNavigate();

  const [formState, formAction, isPending] = useActionState(
    async (prevState, formData) => {
      const username = formData.get("username") as string;
      const password = formData.get("password") as string;

      const salt = cryptoClient.generateRandomSalt() as Uint8Array;

      try {
        const response = await apiClient.post("api/login/", {
          username: username,
          publicKey: password
        });
        console.log(response)
        if (response.status === 200) {
          localStorage.setItem("access", response.data.access);
          //window.location.href = "/"; // Redirect on success
          navigate('/')
          return { ...prevState, error: null };
        } else {
          throw new Error("Invalid credentials");
        }
      } catch (error) {
        return { ...prevState, error: "Login failed. Check credentials." };
      }
    },
    { error: null }
  );

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/", )
    }
  }, []);

  return (
    <div className="text-center min-vh-100 max-vh-100" id="login-wrap">
        <form
          action={formAction}
        >
          <h1 className="h3 mb-3 fw-normal">Please log in</h1>

          {formState.error && <div className="alert alert-danger">{formState.error}</div>}

          <div className="form-floating mb-3">
            <input
              type="text"
              name="username"
              className="form-control"
              id="username"
              placeholder="Username"
              required
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
            />
            <label htmlFor="password">Password</label>
          </div>

          <button className="w-100 btn btn-lg btn-primary" type="submit" disabled={isPending}>
            {isPending ? "Signing in..." : "Sign in"}
          </button>
          <p className="mt-5 mb-3 text-muted">©2025</p>
        </form>
    </div>
  );
};

export default Login;
