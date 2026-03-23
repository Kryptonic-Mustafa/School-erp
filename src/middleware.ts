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
