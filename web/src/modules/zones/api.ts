import { apiRequest } from "../../core/api";

export type ZoneKind = "zone" | "line";

// A point in the camera picture as fractions of its width and height (0 to 1)
export interface Point {
  x: number;
  y: number;
}

// What the backend needs to create or change a zone or count line
export interface ZoneInput {
  name: string;
  kind: ZoneKind;
  points: Point[];
  in_side: 1 | -1; // count lines only: which side of the line is IN
}

export interface Zone extends ZoneInput {
  id: number;
  camera_id: string;
}

export function listZones(cameraId: string): Promise<Zone[]> {
  return apiRequest<Zone[]>(`/cameras/${encodeURIComponent(cameraId)}/zones`);
}

export function createZone(cameraId: string, zone: ZoneInput): Promise<Zone> {
  return apiRequest<Zone>(`/cameras/${encodeURIComponent(cameraId)}/zones`, {
    method: "POST",
    body: JSON.stringify(zone),
  });
}

export function updateZone(zoneId: number, zone: ZoneInput): Promise<Zone> {
  return apiRequest<Zone>(`/zones/${zoneId}`, { method: "PUT", body: JSON.stringify(zone) });
}

export function deleteZone(zoneId: number): Promise<null> {
  return apiRequest<null>(`/zones/${zoneId}`, { method: "DELETE" });
}

// IN and OUT totals of one count line
export interface LineCount {
  id: number;
  camera_id: string;
  name: string;
  entered: number;
  left: number;
}

/** Totals of every count line, counting crossings from the given moment onwards. */
export function listLineCounts(since: Date): Promise<LineCount[]> {
  return apiRequest<LineCount[]>(`/zones/line-counts?since=${encodeURIComponent(since.toISOString())}`);
}

// How many people are in one zone right now; people is null while the camera is not being analysed
export interface ZoneOccupancy {
  id: number;
  camera_id: string;
  name: string;
  people: number | null;
}

export function listZoneOccupancy(): Promise<ZoneOccupancy[]> {
  return apiRequest<ZoneOccupancy[]>("/zones/occupancy");
}
