import { useQuery } from "@tanstack/react-query";

import { getIngestStatus } from "../services/api/endpoints";

export function useIngestStatus() {
  return useQuery({
    queryKey: ["ingest-status"],
    queryFn: getIngestStatus,
    staleTime: 10_000,
  });
}
