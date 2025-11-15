const Base_URL = "http://127.0.0.1:8000/api/DynamicPricing";

export async function fetchSimulate() {
    const url = `${Base_URL}/simulate`.replace(/([^:]\/)\/+/g, "$1");
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`Request failed: ${res.status} ${res.statusText} ${txt}`);
    }
    return res.json();
}
