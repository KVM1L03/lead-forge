const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function GET(): Promise<Response> {
  try {
    const res = await fetch(`${API_BASE}/health`, {
      signal: AbortSignal.timeout(3000),
      cache: "no-store",
    });
    if (!res.ok) {
      return new Response(null, { status: 503 });
    }
    return new Response(null, { status: 200 });
  } catch {
    return new Response(null, { status: 503 });
  }
}
