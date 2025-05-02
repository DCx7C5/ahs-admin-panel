import React, {useActionState, useState} from "react";
import {apiClient} from "../../hooks/useAHSApi";
import {CForm, CFormInput, CFormLabel} from "@coreui/react";


interface KeybaseAuthenticationProps {
    api: apiClient;
}


export const KeybaseAuthentication: React.FC = ({api}: KeybaseAuthenticationProps) => {
    const [isOpen, setIsOpen] = useState(false);

    const [formState, formAction, isPending] = useActionState(
        async (prevState, formData) => {
            const userName = formData.get("username") as string;

            return { ...prevState, error: null };
        },
        { error: null }
    );

    return (
        <CForm action={formAction} className="form-signin">
            {formState.error && <div className="alert alert-danger">{formState.error}</div>}
            <div className="form-floating mb-3">
                <CFormInput
                    type="text"
                    name="username"
                    className="form-control"
                    id="username"
                    placeholder="Username"
                    required
                />
                <CFormLabel htmlFor="username">Username</CFormLabel>
            </div>
            <button className="w-100 btn btn-lg btn-primary" type="submit" disabled={isPending}>
                {isPending ? "Creating account..." : "Register"}
            </button>
        </CForm>
    );}


export default KeybaseAuthentication;