// Simplistic AES Mock for Step 1 (Will be expanded in API step)
export function encryptPayload(data: string): string {
  if (typeof window !== 'undefined') {
    return btoa(data); // Browser mock
  }
  return Buffer.from(data).toString('base64');
}

export function decryptPayload(data: string): string {
  if (typeof window !== 'undefined') {
    return atob(data); // Browser mock
  }
  return Buffer.from(data, 'base64').toString('utf-8');
}
