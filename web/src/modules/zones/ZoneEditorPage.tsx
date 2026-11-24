"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState, type PointerEvent } from "react";
import { Card } from "../../components/Card";
import { ApiError } from "../../core/api";
import { usePolling } from "../../core/usePolling";
import { listCameras, streamUrl } from "../cameras/api";
import { createZone, deleteZone, listZones, updateZone, type Point, type Zone, type ZoneInput, type ZoneKind } from "./api";
import styles from "./ZoneEditorPage.module.css";

const CAMERA_REFRESH_MS = 5_000;
const LINE_POINTS = 2;
const MIN_ZONE_POINTS = 3;
const MAX_ZONE_POINTS = 32;
const SIDE_LABEL_OFFSET = 0.07; // distance of the IN / OUT labels from the middle of a count line, as a fraction of the picture
const KIND_LABEL: Record<ZoneKind, string> = { zone: "Zone", line: "Count line" };
const HINT: Record<ZoneKind, string> = {
  line: "Draw the line on the floor, a step inside the door, across the path people walk: click its two ends. People are counted by where their feet are, so they must be visible on both sides of the line; a line on the door itself counts nothing. IN must be on the inside of the store: use Swap IN / OUT if it is not.",
  zone: "Click each corner of the area on the floor, where people's feet are. Drag a point to move it.",
};

// The shape being drawn or changed; id is set when it is already saved
interface Draft extends ZoneInput {
  id?: number;
}

const errorMessage = (e: unknown) => (e instanceof ApiError ? e.message : "Unexpected error");
const clamp = (value: number) => Math.min(1, Math.max(0, value));
const percent = (value: number) => `${value * 100}%`;

/** Where the IN and OUT labels of a count line go: IN is on the side the backend counts as in. */
function sideLabels(draft: Draft): { text: string; at: Point }[] {
  const [a, b] = draft.points;
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const length = Math.hypot(dx, dy) || 1;
  const nx = (-dy / length) * draft.in_side * SIDE_LABEL_OFFSET;
  const ny = (dx / length) * draft.in_side * SIDE_LABEL_OFFSET;
  const middle = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
  return [
    { text: "IN", at: { x: clamp(middle.x + nx), y: clamp(middle.y + ny) } },
    { text: "OUT", at: { x: clamp(middle.x - nx), y: clamp(middle.y - ny) } },
  ];
}

export function ZoneEditorPage() {
  const cameraId = decodeURIComponent(useParams<{ cameraId: string }>().cameraId);
  const { data: cameras } = usePolling(listCameras, CAMERA_REFRESH_MS);
  const camera = cameras?.find((c) => c.id === cameraId);
  const [zones, setZones] = useState<Zone[] | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const picture = useRef<HTMLDivElement>(null);
  const dragged = useRef<number | null>(null); // index of the point being dragged

  const reload = useCallback(
    () =>
      listZones(cameraId)
        .then(setZones)
        .catch((e: unknown) => setError(errorMessage(e))),
    [cameraId],
  );
  useEffect(() => {
    reload();
  }, [reload]);

  const pointAt = (e: PointerEvent): Point => {
    const box = picture.current!.getBoundingClientRect();
    return { x: clamp((e.clientX - box.left) / box.width), y: clamp((e.clientY - box.top) / box.height) };
  };

  const onPointerDown = (e: PointerEvent<HTMLDivElement>) => {
    if (!draft) return;
    const index = (e.target as HTMLElement).dataset.index;
    if (index !== undefined) {
      dragged.current = Number(index);
      e.currentTarget.setPointerCapture(e.pointerId);
      return;
    }
    const limit = draft.kind === "line" ? LINE_POINTS : MAX_ZONE_POINTS;
    if (draft.points.length < limit) setDraft({ ...draft, points: [...draft.points, pointAt(e)] });
  };

  const onPointerMove = (e: PointerEvent<HTMLDivElement>) => {
    const index = dragged.current;
    if (!draft || index === null) return;
    const moved = pointAt(e);
    setDraft({ ...draft, points: draft.points.map((p, i) => (i === index ? moved : p)) });
  };

  const stopDragging = () => {
    dragged.current = null;
  };

  const run = async (action: () => Promise<unknown>) => {
    setBusy(true);
    setError(null);
    try {
      await action();
      setDraft(null);
      await reload();
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  const save = () => {
    if (!draft) return;
    const { id, ...input } = draft;
    run(() => (id === undefined ? createZone(cameraId, input) : updateZone(id, input)));
  };

  const remove = (zone: Zone) => {
    if (window.confirm(`Delete "${zone.name}"?`)) run(() => deleteZone(zone.id));
  };

  const start = (kind: ZoneKind) => setDraft({ name: "", kind, points: [], in_side: 1 });
  const complete =
    draft !== null &&
    draft.name.trim() !== "" &&
    (draft.kind === "line" ? draft.points.length === LINE_POINTS : draft.points.length >= MIN_ZONE_POINTS);
  const outline = draft?.points.map((p) => `${p.x},${p.y}`).join(" ");

  return (
    <div className={styles.page}>
      <Link href="/" className={styles.back}>
        ← Dashboard
      </Link>

      <Card title={`Zones and count lines · ${cameraId}`}>
        {error && <p className={styles.error}>{error}</p>}
        {cameras && !camera && <p className={styles.error}>Camera {cameraId} is not configured.</p>}

        <div className={styles.toolbar}>
          {draft ? (
            <>
              <input
                className={styles.name}
                value={draft.name}
                onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                placeholder={draft.kind === "line" ? "Name, e.g. Front door" : "Name, e.g. Billing counter"}
                maxLength={64}
                autoFocus
              />
              {draft.kind === "line" && (
                <button className={styles.button} onClick={() => setDraft({ ...draft, in_side: draft.in_side === 1 ? -1 : 1 })}>
                  Swap IN / OUT
                </button>
              )}
              <button
                className={styles.button}
                onClick={() => setDraft({ ...draft, points: draft.points.slice(0, -1) })}
                disabled={draft.points.length === 0}
              >
                Undo point
              </button>
              <button className={styles.primary} onClick={save} disabled={!complete || busy}>
                {busy ? "Saving…" : "Save"}
              </button>
              <button className={styles.button} onClick={() => setDraft(null)} disabled={busy}>
                Cancel
              </button>
            </>
          ) : (
            <>
              <button className={styles.primary} onClick={() => start("line")} disabled={!camera?.online}>
                Draw count line
              </button>
              <button className={styles.primary} onClick={() => start("zone")} disabled={!camera?.online}>
                Draw zone
              </button>
            </>
          )}
        </div>

        <div
          ref={picture}
          className={draft ? styles.pictureDrawing : styles.picture}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={stopDragging}
          onPointerCancel={stopDragging}
        >
          {camera?.online ? (
            <img className={styles.video} src={streamUrl(cameraId)} alt={`Live view of ${cameraId}`} draggable={false} />
          ) : (
            <div className={styles.offline}>No signal: the camera must be online to draw on its picture</div>
          )}
          {draft && (
            <svg className={styles.overlay} viewBox="0 0 1 1" preserveAspectRatio="none">
              {draft.kind === "zone" && draft.points.length >= MIN_ZONE_POINTS ? (
                <polygon className={styles.shape} points={outline} />
              ) : (
                <polyline className={styles.shape} points={outline} />
              )}
            </svg>
          )}
          {draft?.points.map((p, i) => (
            <span key={i} data-index={i} className={styles.handle} style={{ left: percent(p.x), top: percent(p.y) }} />
          ))}
          {draft?.kind === "line" &&
            draft.points.length === LINE_POINTS &&
            sideLabels(draft).map(({ text, at }) => (
              <span key={text} className={styles.side} style={{ left: percent(at.x), top: percent(at.y) }}>
                {text}
              </span>
            ))}
        </div>

        <p className={styles.muted}>
          {draft ? HINT[draft.kind] : "Saved lines and zones appear on the live picture within a few seconds."}
        </p>
      </Card>

      <Card title="Saved">
        {zones?.length === 0 && <p className={styles.muted}>Nothing drawn on this camera yet</p>}
        <ul className={styles.list}>
          {zones?.map((zone) => (
            <li key={zone.id} className={styles.item}>
              <span className={styles.itemName}>{zone.name}</span>
              <span className={styles.muted}>{KIND_LABEL[zone.kind]}</span>
              <button
                className={styles.button}
                onClick={() => setDraft({ id: zone.id, name: zone.name, kind: zone.kind, points: zone.points, in_side: zone.in_side })}
                disabled={busy || !camera?.online}
              >
                Edit
              </button>
              <button className={styles.danger} onClick={() => remove(zone)} disabled={busy}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
