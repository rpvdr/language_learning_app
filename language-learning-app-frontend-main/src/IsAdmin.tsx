import { type ReactNode } from 'react';
import { useAuth } from './api/ApiConfigContext';

interface IsAdminProps {
    children: ReactNode;
}

export default function IsAdmin({ children }: IsAdminProps) {
    const { roles } = useAuth();
    if (roles.includes('admin')) {
        return <>{children}</>;
    }
    return null;
}
