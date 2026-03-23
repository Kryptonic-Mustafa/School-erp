import jwt from 'jsonwebtoken';

const SECRET = process.env.JWT_SECRET || 'fallback_secret';

export function signSystemToken(payload: object): string {
  return jwt.sign(payload, SECRET, { expiresIn: '12h' });
}

export function verifySystemToken(token: string) {
  try {
    return jwt.verify(token, SECRET);
  } catch (error) {
    return null;
  }
}
