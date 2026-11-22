import "server-only";

/**
 * Lightweight in-memory protections for the order endpoint.
 * They live per server instance — enough for a single cafe site. For
 * multi-instance / serverless scale, move them to Redis (e.g. Upstash).
 */

const RATE_WINDOW_MS = 10 * 60 * 1000;
const RATE_MAX_ORDERS = 6;
const IDEMPOTENCY_TTL_MS = 30 * 60 * 1000;

const hits = new Map<string, number[]>();

/** Returns true when the client may place another order. */
export function checkRateLimit(key: string, now = Date.now()): boolean {
  const recent = (hits.get(key) ?? []).filter((time) => now - time < RATE_WINDOW_MS);
  if (recent.length >= RATE_MAX_ORDERS) {
    hits.set(key, recent);
    return false;
  }
  recent.push(now);
  hits.set(key, recent);
  if (hits.size > 5000) {
    for (const [k, times] of hits) {
      if (times.every((time) => now - time >= RATE_WINDOW_MS)) hits.delete(k);
    }
  }
  return true;
}

const completed = new Map<string, { at: number; value: unknown }>();
const inFlight = new Map<string, Promise<unknown>>();

/**
 * Runs `task` once per idempotency key: repeated submits of the same
 * checkout (double click, flaky network retry) return the first result.
 */
export async function once<T>(
  key: string,
  task: () => Promise<T>,
  shouldCache: (value: T) => boolean = () => true,
  now = Date.now(),
): Promise<T> {
  for (const [k, entry] of completed) {
    if (now - entry.at > IDEMPOTENCY_TTL_MS) completed.delete(k);
  }
  const done = completed.get(key);
  if (done) return done.value as T;

  const pending = inFlight.get(key);
  if (pending) return pending as Promise<T>;

  const promise = task();
  inFlight.set(key, promise);
  try {
    const value = await promise;
    // Failed attempts are not cached, so the customer can simply retry.
    if (shouldCache(value)) completed.set(key, { at: Date.now(), value });
    return value;
  } finally {
    inFlight.delete(key);
  }
}
