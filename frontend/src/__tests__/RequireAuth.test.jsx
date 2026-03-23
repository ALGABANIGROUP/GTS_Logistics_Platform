import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import RequireAuth from '../routes/RequireAuth';

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
                <Route path="/403" element={<div>FORBIDDEN_PAGE</div>} />
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
            loading: false,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('PRIVATE_PAGE')).toBeInTheDocument();
    });

    it('redirects unauthenticated users to login', () => {
        useAuth.mockReturnValue({
            user: null,
            loading: false,
            isAuthenticated: false,
            accountStatus: null,
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('LOGIN_PAGE')).toBeInTheDocument();
    });

    it('redirects inactive accounts to account inactive page', () => {
        useAuth.mockReturnValue({
            user: { role: 'admin' },
            loading: false,
            isAuthenticated: true,
            accountStatus: 'inactive',
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('INACTIVE_PAGE')).toBeInTheDocument();
    });

    it('redirects to forbidden when role does not match', () => {
        useAuth.mockReturnValue({
            user: { role: 'user' },
            loading: false,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('FORBIDDEN_PAGE')).toBeInTheDocument();
    });

    it('returns null while auth state is loading', () => {
        useAuth.mockReturnValue({
            user: null,
            loading: true,
            isAuthenticated: false,
            accountStatus: null,
        });

        const { container } = renderWithRoutes('/private', ['admin']);

        expect(container).toBeEmptyDOMElement();
    });

    it('renders protected route when roles are not required', () => {
        useAuth.mockReturnValue({
            user: { role: 'user' },
            loading: false,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private');

        expect(screen.getByText('PRIVATE_PAGE')).toBeInTheDocument();
    });

    it('accepts users with role present in roles array', () => {
        useAuth.mockReturnValue({
            user: { roles: ['dispatcher', 'manager'] },
            loading: false,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private', ['manager']);

        expect(screen.getByText('PRIVATE_PAGE')).toBeInTheDocument();
    });

    it('redirects to forbidden when user has no role metadata and roles are required', () => {
        useAuth.mockReturnValue({
            user: {},
            loading: false,
            isAuthenticated: true,
            accountStatus: 'active',
        });

        renderWithRoutes('/private', ['admin']);

        expect(screen.getByText('FORBIDDEN_PAGE')).toBeInTheDocument();
    });
});
