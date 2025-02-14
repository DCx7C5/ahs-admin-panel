import axios from "axios";

const api = axios.create({
  baseURL: `${document.location.protocol}://${window.location.host}/api/`,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access"); // Retrieve access token
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 (Unauthorized) and original request is retriable
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem("refresh");

        // Attempt to refresh the token
        const response = await axios.post("http://localhost:8000/api/token/refresh/", {
          refresh: refreshToken,
        });

        const newAccessToken = response.data.access;
        localStorage.setItem("access", newAccessToken);

        // Retry the original request
        originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Log out the user if refresh fails
        console.error("Token refresh failed:", refreshError);
        localStorage.clear();
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;