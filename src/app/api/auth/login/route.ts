import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';
import bcrypt from 'bcryptjs';
import { signSystemToken } from '@/lib/auth_guard';
import { decryptPayload } from '@/lib/crypto_engine';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    
    // In production, payload should be decrypted here
    // const rawData = decryptPayload(body.encryptedData);
    // const { email, password } = JSON.parse(rawData);
    
    const { email, password } = body; // Simplified for step 2 testing

    const user = await db.user.findUnique({ where: { email } });
    if (!user) {
      return NextResponse.json({ error: 'ACCESS_DENIED' }, { status: 401 });
    }

    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) {
      return NextResponse.json({ error: 'INVALID_CREDENTIALS' }, { status: 401 });
    }

    const token = signSystemToken({ id: user.id, role: user.role });

    const response = NextResponse.json({ success: true, role: user.role });
    response.cookies.set({
      name: 'system_token',
      value: token,
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
    });

    return response;
  } catch (error) {
    return NextResponse.json({ error: 'SYSTEM_ERROR' }, { status: 500 });
  }
}
