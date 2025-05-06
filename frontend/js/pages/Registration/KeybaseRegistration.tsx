import React, {useActionState} from "react";
import {apiClient} from "../../hooks/useApiAxios";
import {CForm, CFormInput, CFormLabel} from "@coreui/react";


interface KeybaseRegistrationProps {
    api: apiClient;
}


export const KeybaseRegistration: React.FC = ({api}: KeybaseRegistrationProps) => {
    const [formState, formAction, isPending] = useActionState(
        async (prevState, formData) => {
            const userName = formData.get("username") as string;
            console.log("UserName: ", userName, "");
            await alert("Not implemented yet.")
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


export default KeybaseRegistration;