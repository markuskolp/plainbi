import deepEquals from "fast-deep-equal"
import { useRef } from "react"

export function useDeepDependencies(dependencies) {
  const memo = useRef()

  if (!deepEquals(memo.current, dependencies)) {
    memo.current = dependencies
  }

  return memo.current
}
