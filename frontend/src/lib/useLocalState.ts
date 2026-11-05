'use client';

import { useEffect, useState, type Dispatch, type SetStateAction } from 'react';

export function useLocalState<T>(key: string, initialValue: T): [T, Dispatch<SetStateAction<T>>] {
  const [value, setValue] = useState(initialValue);
  const [loaded, setLoaded] = useState(false);
  useEffect(() => {
    try {
      const saved = localStorage.getItem(key);
      if (saved !== null) setValue(JSON.parse(saved) as T);
    } catch { /* Keep the default if storage is unavailable. */ }
    setLoaded(true);
  }, [key]);
  useEffect(() => {
    if (!loaded) return;
    try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* The current session remains usable. */ }
  }, [key, value, loaded]);
  return [value, setValue];
}
