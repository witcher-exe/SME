import { createContext } from 'react';
import type { Store } from './store';

// Keep context identity outside the provider's React refresh boundary.
// Provider edits must not disconnect already-mounted consumers.
export const AuraContext = createContext<Store | null>(null);