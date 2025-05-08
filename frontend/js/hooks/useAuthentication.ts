import {useCallback, useState} from "react";

interface User {
  userName: string | null;
  firstName: string | null;
  lastName: string | null;
  isSuperUser: boolean;
  isStaff: boolean;
  email: string | null;
}

interface Authentication {
  user: User;
  register: () => void;
  authenticate: () => void;
}


export const useAuthentication = (): Authentication => {
    const [user, setUser] = useState<User>({
        userName: null,
        firstName: null,
        lastName: null,
        isSuperUser: false,
        isStaff: false,
        email: null,
    });

    const webauthn_register = useCallback(() => {

    }, [])

    const webauthn_authenticate = useCallback(() => {

    }, [])

    return {
        user,
        register: webauthn_register,
        authenticate: webauthn_authenticate,
    };
};

export default useAuthentication;
