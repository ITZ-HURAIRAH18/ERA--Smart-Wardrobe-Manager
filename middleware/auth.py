from django.shortcuts import redirect


def auth_middleware(get_response):
    """Middleware to protect authenticated routes.
    
    Excludes public pages (login, signup, home, etc.) from authentication check.
    """
    # One-time configuration and initialization.

    def middleware(request):
        # Paths that don't require authentication
        public_paths = [
            '/login',
            '/signup',
            '/admin',
            '/admin/',
            '/admin/login',
        ]
        
        # Check if current path is public
        is_public = any(request.path.startswith(path) for path in public_paths)
        
        if not is_public and not request.session.get('customer_id'):
            return redirect('login')
        
        response = get_response(request)
        return response

    return middleware