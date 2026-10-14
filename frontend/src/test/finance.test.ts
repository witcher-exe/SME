import { describe, it, expect } from 'vitest';
import { canDispatch, scenarioLimits, stressRunway, makeBlock, verifyBlocks } from '../lib/finance';
describe('Finance controls', () => {
  it('permits a maximum 60-day receivables delay', () => expect(scenarioLimits.delay).toBe(60));
  it('permits a maximum 30% cost surge', () => expect(scenarioLimits.cost).toBe(30));
  it('permits a maximum 40% revenue drop', () => expect(scenarioLimits.revenue).toBe(40));
  it('requires owner approval for external dispatch', () => {expect(canDispatch('pending')).toBe(false); expect(canDispatch('rejected')).toBe(false); expect(canDispatch('approved')).toBe(true);});
  it('reduces runway for delayed collection', () => expect(stressRunway(30)).toBeLessThan(stressRunway(0)));
  it('detects mutated audit blocks', async () => {const b = await makeBlock(1,'Guard','Safety check','genesis'); expect(await verifyBlocks([b])).toBe(true); expect(await verifyBlocks([{...b,tool:'tampered'}])).toBe(false);});
});