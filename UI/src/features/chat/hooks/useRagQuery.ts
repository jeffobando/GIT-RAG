import { useMutation } from "@tanstack/react-query";

import { postRagQuery } from "../../../services/api/endpoints";
import type { RagQueryRequest } from "../../../types/api";

export function useRagQuery() {
  return useMutation({
    mutationFn: (payload: RagQueryRequest) => postRagQuery(payload),
  });
}
