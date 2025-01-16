import { useState } from 'react';

const useTheme = (defaultTheme = 'dark') => {
  const [theme, setTheme] = useState(defaultTheme);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
    document.body.className = theme;
  };

  return [theme, toggleTheme];
};

export default useTheme;