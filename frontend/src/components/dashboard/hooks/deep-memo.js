import { DependencyList, useMemo } from 'react';

import { useDeepDependencies } from './deep-dependencies';

export function useDeepMemo(callback,dependencies) {
  const memoizedDependencies = useDeepDependencies(dependencies);
  return useMemo(callback, memoizedDependencies);
}