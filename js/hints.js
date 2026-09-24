/**
 * Hint helpers are primarily built at data-build time (tools/build_koroks.py).
 * Runtime only needs light display utilities.
 */
export function formatCoords(k) {
  return `X ${k.x.toFixed(1)} · Y ${k.y.toFixed(1)} · Z ${k.z.toFixed(1)}`;
}
