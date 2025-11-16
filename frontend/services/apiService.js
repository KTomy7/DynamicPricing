const Base_URL = "http://127.0.0.1:8000/api/DynamicPricing";

async function handleFetch(endpoint) {
    const url = `${Base_URL}/${endpoint}`.replace(/([^:]\/)\/+/g, "$1");
    const response = await fetch(url);
    if (!response.ok) { 
        const txt = await response.text().catch(() => "");
        throw new Error(`Request failed: ${response.status} ${response.statusText} ${txt}`);
    }
    return response.json();
}

export async function fetchSimulate() {
    return handleFetch("simulate");
}

export async function fetchAnalysis() {
    return handleFetch("analyze");
}
