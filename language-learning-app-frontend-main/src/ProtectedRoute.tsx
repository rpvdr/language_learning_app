import React from 'react';
import { useAuth } from './api/ApiConfigContext';
import { Navigate, useLocation } from 'react-router-dom';

export function ProtectedRoute({ children }: { children: React.ReactElement }) {
    const { token } = useAuth();
    const location = useLocation();
    if (!token) {
        return <Navigate to="/auth" state={{ from: location }} replace />;
    }
    return children;
}
