import { useEffect, useState } from 'react';

export type Theme = 'light' | 'dark';
export function useTheme() {
  const [theme, setTheme] = useState<Theme>('light');
  useEffect(() => {
    try {
      const saved = localStorage.getItem('auracfo-theme');
      if (saved === 'dark') setTheme('dark');
    } catch { /* White mode remains the default when preferences are unavailable. */ }
  }, []);
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);
  function changeTheme(next: Theme) {
    setTheme(next);
    try { localStorage.setItem('auracfo-theme', next); } catch { /* Session-only preference. */ }
  }
  return { theme, changeTheme };
}