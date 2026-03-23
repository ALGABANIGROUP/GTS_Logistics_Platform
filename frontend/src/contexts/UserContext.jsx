import React, { createContext, useContext } from "react";
import { useAuth } from "./AuthContext";

const UserContext = createContext(null);

export const UserProvider = ({ children }) => {
    const auth = useAuth();

    const value = {
        user: auth.user,
        loading: !auth.authReady || auth.loading,
        login: auth.login,
        logout: auth.logout,
        updateUser: auth.setUser,
    };

    return (
        <UserContext.Provider value={value}>
            {children}
        </UserContext.Provider>
    );
};

export const useUser = () => {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error("useUser must be used within a UserProvider");
    }
    return context;
};
