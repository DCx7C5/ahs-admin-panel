import {useCallback, useState} from "react";
import axios from "axios";


const useAHSApi = (baseUrl = "") => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const request = useCallback(
    async (endpoint, method = "GET", requestData = {}, config = {}) => {
      setLoading(true);
      setError(null);

      try {
        // Dynamically make the request with axios
        const response = await axios({
          url: `${baseUrl}${endpoint}`,
          method,
          data: requestData,
          ...config,
        });

        // Set response data
        setData(response.data);
        return response.data;
      } catch (err) {
        // Handle errors
        setError(err.response?.data?.message || err.message || "Something went wrong");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [baseUrl]
  );

  return [request, { loading, error, data }];
};

export default useAHSApi;