// Self-test fixture: 故意引用不存在的组件 → orphan-detector 应报 FAIL
import { DeletedPage } from './pages/DeletedPage';
import { describe, it, expect } from 'vitest';

describe('DeletedPage', () => {
  it('should render', () => {
    expect(true).toBe(true);
  });
});
