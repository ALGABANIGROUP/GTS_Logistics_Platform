import { useEffect } from 'react';
import { useCurrencyStore } from '../stores/useCurrencyStore';
import { useAuth } from '../contexts/AuthContext';

/**
 * Hook to sync currency with user's country on login
 * This ensures the currency is updated automatically whenever the user changes
 */
export const useCurrencySync = () => {
    const { user } = useAuth();
    const { currency, initializeCurrencyFromUser } = useCurrencyStore();

    useEffect(() => {
        if (user?.country) {
            // Update currency based on user's country whenever user changes
            initializeCurrencyFromUser(user.country);
        }
    }, [user?.country, initializeCurrencyFromUser]);

    return currency;
};

export default useCurrencySync;
