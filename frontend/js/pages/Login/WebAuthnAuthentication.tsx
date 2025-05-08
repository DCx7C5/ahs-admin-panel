import React, {use, useActionState, useEffect, useState} from "react";
import {CForm, CFormInput, CFormLabel} from "@coreui/react";
import {DataContext} from "../../components/DataProvider";
import {useNavigate} from "react-router-dom";
import {base64Decode, base64Encode} from "../../components/utils";
import {apiClient} from "../../hooks/useApiAxios";

interface WebAuthnOptionsResponse {
    message: string;
    options: string;
    random: string;
}

interface WebAuthnAuthenticationVerifyResponse {
    message: string;
    status: number;
}


export const WebAuthnAuthentication: React.FC = () => {
    const api = use(DataContext)?.apiCli as apiClient;
    const navigate = useNavigate();
    const [authSuccess, setAuthSuccess] = useState(false);

    const [formState, formAction, isPending] = useActionState(
        async (prevState, formData) => {
            const userName = formData.get("username") as string;

            // Request webauthn authentication options
            const optResponse: WebAuthnOptionsResponse = await api?.post(
                'api/auth/webauthn/',
                JSON.stringify({
                    username: userName,
                })
            );

            if (!optResponse.random || !optResponse.options) {
                return { ...prevState, error: "Failed to get options." };
            }

            //
            const options = JSON.parse(optResponse.options);
            options.challenge = base64Decode(options.challenge);

            const assertion = await navigator.credentials.get({
                publicKey: options as PublicKeyCredentialRequestOptions,
            }) as PublicKeyCredential;

            const authResponse = assertion.response as AuthenticatorAssertionResponse;

            const serializedCredential = JSON.stringify({
                id: assertion.id,
                rawId: base64Encode(assertion.rawId, true),
                response: {
                    clientDataJSON: base64Encode(authResponse.clientDataJSON, true),
                    authenticatorData: base64Encode(authResponse.authenticatorData, true),
                    signature: base64Encode(authResponse.signature, true),
                    userHandle: authResponse.userHandle
                        ? base64Encode(authResponse.userHandle, true)
                        : null,
                },
                type: assertion.type,
            })

            const verifyResponse: WebAuthnAuthenticationVerifyResponse = await api?.post(
                'api/auth/webauthn/verify/',
                JSON.stringify({
                    credential: serializedCredential,
                    random: optResponse.random,
                    username: userName,
                })
            )
            console.log("VERIFY RESPONSE: ", verifyResponse, "")
            if (verifyResponse && verifyResponse.status === 200) {
                setAuthSuccess(true);
                // set user
                console.log("AUTH SUCCESS")
                return { ...prevState, error: null };

            } else {
                return { ...prevState, error: "Failed to register." };
            }
        },
        { error: null }
    );

    useEffect(() => {
        if (authSuccess && !isPending) {
            navigate("/", { replace: true })
        }

    }, [authSuccess, isPending, navigate]);

    return (
        <>
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
                    {isPending ? "Logging in..." : "Login"}
                </button>
            </CForm>
        </>
    );
};
