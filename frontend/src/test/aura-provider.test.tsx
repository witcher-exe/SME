import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { AuraProvider, useAura } from '@/components/aura/store';
import { AuraContext } from '@/components/aura/context';

function Consumer() {
  const store = useAura();
  return <><span>{store.company}</span><button onClick={() => store.setCompany('Shenzhen Importer')}>Switch company</button></>;
}

afterEach(cleanup);
describe('Aura shared state', () => {
  it('provides company state to descendants and retains updates on rerender', () => {
    const view = render(<AuraProvider><Consumer /></AuraProvider>);
    expect(screen.getByText('Bengal Craft & Retail Ltd.')).toBeDefined();
    fireEvent.click(screen.getByText('Switch company'));
    view.rerender(<AuraProvider><Consumer /></AuraProvider>);
    expect(screen.getByText('Shenzhen Importer')).toBeDefined();
  });
  it('uses the same context when the provider module is reloaded', async () => {
    vi.resetModules();
    vi.doMock('@/components/aura/context', () => ({ AuraContext }));
    const refreshed = await import('@/components/aura/store');
    function RefreshedConsumer() {
      const store = refreshed.useAura();
      return <span>{store.company}</span>;
    }
    render(<AuraProvider><RefreshedConsumer /></AuraProvider>);
    expect(screen.getByText('Bengal Craft & Retail Ltd.')).toBeDefined();
    vi.doUnmock('@/components/aura/context');
  });
});
