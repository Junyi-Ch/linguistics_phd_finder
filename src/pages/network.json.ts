import { networkJson } from '../lib/network';
export const prerender = true;
export function GET() {
  return new Response(JSON.stringify(networkJson()), { headers: { 'Content-Type': 'application/json' } });
}
