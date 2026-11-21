import { apiRequest } from "../../core/api";
import { getToken } from "../../core/auth";
import { API_URL } from "../../core/config";

export interface Camera {
  id: string;
  online: boolean;
}

export function listCameras(): Promise<Camera[]> {
  return apiRequest<Camera[]>("/cameras");
}

/** MJPEG stream URL for an <img>; the token goes in the query because <img> cannot send headers. */
export function streamUrl(cameraId: string): string {
  const token = encodeURIComponent(getToken() ?? "");
  return `${API_URL}/cameras/${encodeURIComponent(cameraId)}/stream?token=${token}`;
}
