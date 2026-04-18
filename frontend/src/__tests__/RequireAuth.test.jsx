import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import RequireAuth from '../components/RequireAuth';

vi.mock('../contexts/AuthContext.jsx', () => ({
    useAuth: vi.fn(),
}));

import { useAuth } from '../contexts/AuthContext.jsx';

function renderWithRoutes(initialPath = '/private', roles = undefined) {
    return render(
        <MemoryRouter initialEntries={[initialPath]}>
            <Routes>
                <Route element={<RequireAuth roles={roles} />}>
                    <Route path="/private" element={<div>PRIVATE_PAGE</div>} />
                </Route>
                <Route path="/login" element={<div>LOGIN_PAGE</div>} />
                <Route path="/account-inactive" element={<div>INACTIVE_PAGE</div>} />
                <Route path="/unauthorized" element={<div>UNAUTHORIZED_PAGE</div>} />
            </Routes>
        </MemoryRouter>
    );
}

describe('RequireAuth', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders protected route when authenticated and authorized', () => {
        useAuth.mockReturnValue({
            user: { effective_role: 'admin' },
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('PRIVATE_PAGE')).toBeInTheDocument();
    });

    it('redirects unauthenticated users to login', () => {
        useAuth.mockReturnValue({
            user: null,
            authReady: true,
            isAuthenticated: false,
            accountStatus: null,
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('LOGIN_PAGE')).toBeInTheDocument();
    });

    it('redirects inactive accounts to account inactive page', () => {
        useAuth.mockReturnValue({
            user: { role: 'admin' },
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'inactive',
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('INACTIVE_PAGE')).toBeInTheDocument();
    });

    it('redirects to unauthorized when role does not match', () => {
        useAuth.mockReturnValue({
            user: { role: 'user' },
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('UNAUTHORIZED_PAGE')).toBeInTheDocument();
    });

    it('renders a pending shell while auth state is loading', () => {
        useAuth.mockReturnValue({
            user: null,
            authReady: false,
            isAuthenticated: false,
            accountStatus: null,
        });

        const { container } = renderWithRoutes('/private', ['admin']);

        expect(container.querySelector('[aria-busy="true"]')).not.toBeNull();
    });

    it('renders protected route when roles are not required', () => {
        useAuth.mockReturnValue({
            user: { role: 'user' },
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private');

        expect(screen.getByText('PRIVATE_PAGE')).toBeInTheDocument();
    });

    it('accepts users with role present in roles array', () => {
        useAuth.mockReturnValue({
            user: { roles: ['dispatcher', 'manager'] },
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private', ['manager']);

        expect(screen.getByText('PRIVATE_PAGE')).toBeInTheDocument();
    });

    it('redirects to unauthorized when user has no role metadata and roles are required', () => {
        useAuth.mockReturnValue({
            user: {},
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('UNAUTHORIZED_PAGE')).toBeInTheDocument();
    });

    it('grants access to super_admin even without matching allowed roles', () => {
        useAuth.mockReturnValue({
            user: { effective_role: 'super_admin' },
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('PRIVATE_PAGE')).toBeInTheDocument();
    });

    it('grants access when super_admin is in user.roles array', () => {
        useAuth.mockReturnValue({
            user: { roles: ['super_admin'] },
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('PRIVATE_PAGE')).toBeInTheDocument();
    });

    it('renders children (legacy wrapper pattern) when authorized', () => {
        useAuth.mockReturnValue({
            user: { role: 'admin' },
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        render(
            <MemoryRouter initialEntries={['/anything']}>
                <RequireAuth roles={['admin']}>
                    <div>WRAPPED_CHILD</div>
                </RequireAuth>
            </MemoryRouter>
        );

        expect(screen.getByText('WRAPPED_CHILD')).toBeInTheDocument();
    });

    it('honors legacy allowedRoles prop', () => {
        useAuth.mockReturnValue({
            user: { role: 'admin' },
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        render(
            <MemoryRouter initialEntries={['/anything']}>
                <Routes>
                    <Route element={<RequireAuth allowedRoles={['admin']} />}>
                        <Route path="/anything" element={<div>ALLOWED_ROLES_PAGE</div>} />
                    </Route>
                    <Route path="/unauthorized" element={<div>UNAUTHORIZED_PAGE</div>} />
                </Routes>
            </MemoryRouter>
        );

        expect(screen.getByText('ALLOWED_ROLES_PAGE')).toBeInTheDocument();
    });

    it('honors legacy requiredRole prop', () => {
        useAuth.mockReturnValue({
            user: { role: 'manager' },
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        render(
            <MemoryRouter initialEntries={['/anything']}>
                <Routes>
                    <Route element={<RequireAuth requiredRole="manager" />}>
                        <Route path="/anything" element={<div>MANAGER_PAGE</div>} />
                    </Route>
                    <Route path="/unauthorized" element={<div>UNAUTHORIZED_PAGE</div>} />
                </Routes>
            </MemoryRouter>
        );

        expect(screen.getByText('MANAGER_PAGE')).toBeInTheDocument();
    });

    it('rejects a mismatching requiredRole', () => {
        useAuth.mockReturnValue({
            user: { role: 'user' },
            authReady: true,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        render(
            <MemoryRouter initialEntries={['/anything']}>
                <Routes>
                    <Route element={<RequireAuth requiredRole="admin" />}>
                        <Route path="/anything" element={<div>ADMIN_PAGE</div>} />
                    </Route>
                    <Route path="/unauthorized" element={<div>UNAUTHORIZED_PAGE</div>} />
                </Routes>
            </MemoryRouter>
        );

        expect(screen.getByText('UNAUTHORIZED_PAGE')).toBeInTheDocument();
    });
});
