import { getDatabase } from "../database/db";

export type SyncQueueItem = {
    id: number;
    method: string;
    endpoint: string;
    payload: string | null;
    created_at: string;
    synced: number;
};

export async function addToSyncQueue(
    method: string,
    endpoint: string,
    payload?: unknown
) {
    const db = await getDatabase();

    await db.runAsync(
        `
      INSERT INTO sync_queue (
        method,
        endpoint,
        payload,
        created_at,
        synced
      )
      VALUES (?, ?, ?, ?, 0)
    `,
        method,
        endpoint,
        payload ? JSON.stringify(payload) : null,
        new Date().toISOString()
    );
}

export async function getPendingSyncItems() {
    const db = await getDatabase();

    return db.getAllAsync<SyncQueueItem>(
        `
      SELECT *
      FROM sync_queue
      WHERE synced = 0
      ORDER BY id ASC
    `
    );
}

export async function markAsSynced(
    id: number
) {
    const db = await getDatabase();

    await db.runAsync(
        `
      UPDATE sync_queue
      SET synced = 1
      WHERE id = ?
    `,
        id
    );
}

export async function getPendingSyncCount() {
    const db = await getDatabase();

    const result = await db.getFirstAsync<{
        count: number;
    }>(
        `
      SELECT COUNT(*) AS count
      FROM sync_queue
      WHERE synced = 0
    `
    );

    return result?.count ?? 0;
}