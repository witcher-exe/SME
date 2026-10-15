import { useEffect, useState } from 'react';

export type Theme = 'light' | 'dark';
export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    try {
      const saved = localStorage.getItem('auracfo-theme');
      if (saved === 'light' || saved === 'dark') return saved;
    } catch { /* Storage unavailable */ }
    return 'dark';
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  function changeTheme(next: Theme) {
    setTheme(next);
    try {
      localStorage.setItem('auracfo-theme', next);
    } catch { /* Session-only preference */ }
  }

  return { theme, changeTheme };
}