import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { useTheme } from '@/components/aura/use-theme';
function ThemeControl(){const {theme,changeTheme}=useTheme();return <><span>{theme}</span><button onClick={()=>changeTheme('dark')}>Dark</button><button onClick={()=>changeTheme('light')}>White</button></>}
afterEach(()=>{cleanup();localStorage.clear();document.documentElement.classList.remove('dark')});
describe('Appearance preference',()=>{
 it('keeps dark mode as the default on initial load',()=>{render(<ThemeControl/>);expect(screen.getByText('dark')).toBeDefined();expect(document.documentElement.classList.contains('dark')).toBe(true)});
 it('applies dark mode and remembers it for the next visit',()=>{const view=render(<ThemeControl/>);fireEvent.click(screen.getByText('Dark'));expect(document.documentElement.classList.contains('dark')).toBe(true);expect(localStorage.getItem('auracfo-theme')).toBe('dark');view.unmount();render(<ThemeControl/>);expect(screen.getByText('dark')).toBeDefined()});
 it('restores white mode without retaining dark styles',()=>{localStorage.setItem('auracfo-theme','dark');render(<ThemeControl/>);fireEvent.click(screen.getByText('White'));expect(document.documentElement.classList.contains('dark')).toBe(false);expect(localStorage.getItem('auracfo-theme')).toBe('light')});
});
