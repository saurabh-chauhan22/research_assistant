const API_URL = '/api';

export async function search(query) {
  const encoded = encodeURIComponent(query);
  const response = await fetch(`${API_URL}/search?query=${encoded}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (response.ok) {
    return await response.json();
  }
  const text = await response.text();
  throw new Error(`Search failed: ${response.status} ${response.statusText}. ${text}`);
}
