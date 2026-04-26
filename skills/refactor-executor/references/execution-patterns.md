# Execution Patterns — Step-by-Step Refactoring Recipes

## Pattern: Extract Validation Utils

**When**: Validation logic scattered across a component or duplicated

**Steps**:
1. Create `src/utils/<domain>Validation.ts`
2. Move constants (ALLOWED_TYPES, MAX_SIZE, etc.)
3. Move pure validation functions (validateX, formatY)
4. Add TypeScript types for validation results: `{ valid: boolean; error?: string }`
5. Update original file imports
6. Verify: `npx tsc --noEmit && npm test`

**Template**:
```typescript
// src/utils/fooValidation.ts
export const MAX_FOO_SIZE = 1024;
export const ALLOWED_FOO_TYPES = ['a', 'b', 'c'] as const;

export interface ValidationResult {
  valid: boolean;
  error?: string;
}

export function validateFoo(input: unknown): ValidationResult {
  // Pure validation logic — no side effects, no toast, no logging
  if (!input) return { valid: false, error: 'Input required' };
  return { valid: true };
}
```

## Pattern: Extract Service

**When**: Business logic mixed into components or monolithic service

**Steps**:
1. Create interface: `src/services/interfaces/IFooService.ts`
2. Create service: `src/services/FooService.ts` implementing the interface
3. Move methods one at a time (compile after each)
4. Service methods return typed results — no toast, no UI updates
5. Update orchestrator to delegate to new service
6. Wire into dependency injection if applicable
7. Verify: `npx tsc --noEmit && npm test`

**Template**:
```typescript
// src/services/interfaces/IFooService.ts
export interface IFooService {
  doThing(input: string): Promise<ThingResult>;
  getThings(): Promise<Thing[]>;
}

// src/services/FooService.ts
import type { IFooService } from './interfaces/IFooService';

export class FooService implements IFooService {
  constructor(private supabase: SupabaseClient) {}

  async doThing(input: string): Promise<ThingResult> {
    // Business logic only — no toast, no setState
    const { data, error } = await this.supabase.from('foo').insert({ input });
    if (error) throw error;
    return data;
  }
}
```

## Pattern: Extract Sub-Component

**When**: Component renders distinct UI sections that could be isolated

**Steps**:
1. Identify the JSX block to extract (look for natural boundaries)
2. Create `src/components/<domain>/FooSection.tsx`
3. Define minimal props interface (only what this section needs)
4. Move JSX and any section-specific handlers
5. Import and render in parent, passing props
6. Verify: `npx tsc --noEmit && npm test`

**Template**:
```typescript
// src/components/domain/FooSection.tsx
interface FooSectionProps {
  items: Item[];
  onDelete: (id: string) => void;
}

export function FooSection({ items, onDelete }: FooSectionProps): JSX.Element {
  return (
    <div className="space-y-3">
      {items.map((item) => (
        <FooItem key={item.id} item={item} onDelete={onDelete} />
      ))}
    </div>
  );
}
```

## Pattern: Extract Custom Hook

**When**: Component has complex state management, effects, and handlers

**Steps**:
1. Create `src/hooks/useFoo.ts`
2. Define return type interface
3. Move all useState, useEffect, useCallback, useMemo
4. Move all event handlers
5. Return only what the component needs
6. Replace in component: `const { x, y, z } = useFoo(config)`
7. Verify: `npx tsc --noEmit && npm test`

**Template**:
```typescript
// src/hooks/useFoo.ts
interface UseFooConfig {
  onComplete?: (result: Result) => void;
}

interface UseFooReturn {
  items: Item[];
  isLoading: boolean;
  handleAdd: (item: Item) => void;
  handleDelete: (id: string) => void;
}

export function useFoo({ onComplete }: UseFooConfig = {}): UseFooReturn {
  const [items, setItems] = useState<Item[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // All state management and effects here
  // Component only sees the return value

  return { items, isLoading, handleAdd, handleDelete };
}
```

## Pattern: Recompose Thin Orchestrator

**When**: After extracting all sub-pieces, rebuild the parent as a thin coordinator

**Steps**:
1. Remove all extracted code from original file
2. Add imports for extracted modules
3. Call hook for state
4. Render sub-components with hook state
5. The file should now read like a table of contents
6. Verify: `npx tsc --noEmit && npm test`

**Target**: The orchestrator should be readable top-to-bottom in under 30 seconds.

**Template**:
```typescript
// Thin orchestrator — ~80-120 lines max
import { useFoo } from '@/hooks/useFoo';
import { FooHeader } from '@/components/domain/FooHeader';
import { FooList } from '@/components/domain/FooList';
import { FooStatus } from '@/components/domain/FooStatus';

export function FooPage(): JSX.Element {
  const { items, isLoading, handleAdd, handleDelete } = useFoo();

  return (
    <div className="space-y-6">
      <FooHeader onAdd={handleAdd} />
      <FooStatus items={items} />
      <FooList items={items} onDelete={handleDelete} isLoading={isLoading} />
    </div>
  );
}
```

## Pattern: Wire Service Delegation

**When**: Monolithic service needs to delegate to extracted sub-services

**Steps**:
1. Import sub-service classes
2. Add sub-service instances as constructor parameters or private fields
3. Replace inline logic with sub-service method calls, one method at a time
4. Remove now-unused private methods from orchestrator
5. Remove now-unused imports
6. Verify after each method migration: `npx tsc --noEmit && npm test`

**Important**: Don't replace all delegations at once. Do one method, verify, commit. Then the next.

## Pattern: Fix Polling Dependency Bug

**When**: useEffect with setInterval includes mutable state in dependency array

**Steps**:
1. Move the mutable value to a `useRef`
2. Keep the ref updated via a separate useEffect
3. The polling effect depends only on stable values
4. Verify the polling doesn't restart on state changes

```typescript
// BEFORE (bug): restarts interval on every state change
const [items, setItems] = useState([]);
useEffect(() => {
  const id = setInterval(() => checkItems(items), 5000);
  return () => clearInterval(id);
}, [items]); // <-- items changes -> interval restarts

// AFTER (fixed): stable polling
const [items, setItems] = useState([]);
const itemsRef = useRef(items);
useEffect(() => { itemsRef.current = items; }, [items]);
useEffect(() => {
  const id = setInterval(() => checkItems(itemsRef.current), 5000);
  return () => clearInterval(id);
}, []); // <-- stable, no restart
```

## Pattern: Normalize Error Handling

**When**: Inconsistent error handling across similar operations

**Steps**:
1. Identify the error handling pattern most operations use
2. Create a helper: `function handleError(err: unknown, context: string): void`
3. The helper should: set error state + toast + throw (or return, depending on pattern)
4. Replace ad-hoc error handling with helper calls
5. Verify: `npx tsc --noEmit && npm test`

## Safety Protocol

After EVERY extraction step:
1. `npx tsc --noEmit` — catches type errors from moved/renamed exports
2. `npm test` — catches behavior changes
3. If either fails, fix before proceeding
4. If fix isn't obvious, revert the step and try a different approach

Never skip verification. The cost of fixing a cascade of errors from multiple unverified steps is much higher than verifying each step.
