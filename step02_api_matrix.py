import os
import sys

PROJECT_NAME = "school-os"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Injected: {path}")

def step02_deploy():
    print("====================================================")
    print("     M.A.C.DevOS: API MATRIX & AUTH DEPLOYMENT      ")
    print("====================================================")

    if os.path.basename(os.getcwd()) == PROJECT_NAME:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.join(os.getcwd(), PROJECT_NAME)

    if not os.path.exists(project_dir):
        print(f"[!] Critical Error: Directory '{PROJECT_NAME}' not found.")
        sys.exit(1)

    print(f"\n[*] Target System: {project_dir}")
    print("\n>>> INJECTING SECURITY AND API ROUTES...")

    # 1. Auth Guard (JWT Logic)
    auth_guard_content = """
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
    """
    create_file(os.path.join(project_dir, "src/lib/auth_guard.ts"), auth_guard_content)

    # 2. Login API Route
    login_route_content = """
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
    """
    create_file(os.path.join(project_dir, "src/app/api/auth/login/route.ts"), login_route_content)

    # 3. Logout API Route
    logout_route_content = """
import { NextResponse } from 'next/server';

export async function POST() {
  const response = NextResponse.json({ success: true });
  response.cookies.delete('system_token');
  return response;
}
    """
    create_file(os.path.join(project_dir, "src/app/api/auth/logout/route.ts"), logout_route_content)

    # 4. Face Registration API Route
    face_register_content = """
import { NextResponse } from 'next/server';
import { db } from '@/lib/db_client';

export async function POST(req: Request) {
  try {
    const { studentId, vectorData } = await req.json();

    if (!studentId || !vectorData || !Array.isArray(vectorData)) {
      return NextResponse.json({ error: 'INVALID_PAYLOAD' }, { status: 400 });
    }

    const embedding = await db.faceEmbedding.create({
      data: {
        studentId,
        vectorData,
      }
    });

    await db.auditLog.create({
      data: {
        action: 'FACE_REGISTERED',
        userId: studentId, // Assuming studentId maps to a user action for now
      }
    });

    return NextResponse.json({ success: true, embeddingId: embedding.id });
  } catch (error) {
    return NextResponse.json({ error: 'DATA_WRITE_FAILED' }, { status: 500 });
  }
}
    """
    create_file(os.path.join(project_dir, "src/app/api/face/register/route.ts"), face_register_content)

    # 5. Overwrite Middleware with actual protection logic
    middleware_content = """
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Edge runtime cannot use standard 'jsonwebtoken' easily, so we do a soft check here
// and handle hard validation in layout/page data fetching or API routes.
const protectedPrefixes = ['/admin', '/teacher', '/student', '/attendance', '/reports'];

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  
  const requiresAuth = protectedPrefixes.some(prefix => pathname.startsWith(prefix));
  
  if (requiresAuth) {
    const token = req.cookies.get('system_token')?.value;
    
    if (!token) {
      return NextResponse.redirect(new URL('/login', req.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
    """
    create_file(os.path.join(project_dir, "src/middleware.ts"), middleware_content)

    print("\n====================================================")
    print(" [SUCCESS] API MATRIX DEPLOYED.")
    print(" Next Step: Constructing the Front-End UI.")
    print("====================================================\n")

if __name__ == "__main__":
    step02_deploy()