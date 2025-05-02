import React, {use, useActionState} from "react";
import {CForm, CFormInput, CFormLabel} from "@coreui/react";
import {DataContext} from "../../components/DataProvider";
import {useNavigate} from "react-router-dom";
import {base64UrlDecode, base64UrlEncode} from "../../components/utils";

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
    const {apiCli, } = use(DataContext);
    const navigate = useNavigate();


    const [formState, formAction, isPending] = useActionState(
        async (prevState, formData) => {
            const userName = formData.get("username") as string;

            const optResponse: WebAuthnOptionsResponse = await apiCli?.post('api/auth/webauthn/')
            if (!optResponse.random || !optResponse.options) {
                return { ...prevState, error: "Failed to get options." };
            }

            const options = JSON.parse(optResponse.options);
            options.challenge = base64UrlDecode(options.challenge);

            const assertion = await navigator.credentials.get({
                publicKey: options as PublicKeyCredentialRequestOptions,
            }) as PublicKeyCredential;

            const authResponse = assertion.response as AuthenticatorAssertionResponse;

            const serializedCredential = JSON.stringify({
                id: assertion.id,
                rawId: base64UrlEncode(assertion.rawId),
                response: {
                    clientDataJSON: base64UrlEncode(authResponse.clientDataJSON),
                    attestationObject: base64UrlEncode(authResponse.authenticatorData),
                    signature: base64UrlEncode(authResponse.signature),
                    userHandle: authResponse.userHandle
                        ? base64UrlEncode(authResponse.userHandle)
                        : null,
                },
                type: assertion.type,
            })

            const verifyResponse: WebAuthnAuthenticationVerifyResponse = await apiCli?.post('api/auth/webauthn/verify/', {
                credential: serializedCredential,
                random: optResponse.random,
                username: JSON.stringify(userName),
            })

            if (verifyResponse && verifyResponse.status === 200) {
                // set user
                return { ...prevState, error: null };

            } else {
                return { ...prevState, error: "Failed to register." };
            }
        },
        { error: null }
    );

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
