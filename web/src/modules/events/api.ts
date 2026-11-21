import { apiRequest } from "../../core/api";

export interface EventItem {
  id: number;
  camera_id: string;
  type: string;
  ts: string;
  zone_id: string | null;
  score: number | null;
}

export function listRecentEvents(limit: number): Promise<EventItem[]> {
  return apiRequest<EventItem[]>(`/events?limit=${limit}`);
}
