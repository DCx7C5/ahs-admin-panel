import {apiClient} from "../../hooks/useAHSApi";
import React, {use, useActionState, useState} from "react";
import {CForm, CFormInput, CFormLabel} from "@coreui/react";
import {DataContext} from "../../components/DataProvider";






export const WebAuthnRegistration: React.FC = () => {
    const api = use(DataContext)?.apiCli as apiClient;
    const [isOpen, setIsOpen] = useState(false);
    const [authAttachment, setAuthAttachment] = useState<AuthenticatorAttachment>("platform");
    const [pubKeyCredParams, setPubKeyCredParams] = useState<{ value: COSEAlgorithmIdentifier; label: string; selected: boolean }[]>([
        { value: -7, label: "ECDSA w/ SHA-256 (default)", selected: true },
        { value: -257, label: "RSASSA-PKCS1-v1_5 w/ SHA-256", selected: false },
    ]);

    const [formState, formAction, isPending] = useActionState(
        async (prevState, formData) => {
            const userName = formData.get("username") as string;
            const pkCredParams = pubKeyCredParams.filter((param) => param.selected).map((param) => param.value);

            const response = await api?.post('api/auth/webauthn/register/', {
                username: JSON.stringify(userName),
                pubkeycredparams: JSON.stringify(pkCredParams),
                authattachment: JSON.stringify(authAttachment),
            })

            console.log('OPTIONS_RESPONSE',response)

            //const credentials = await navigator.credentials.create({ publicKey: options }) as PublicKeyCredential;

            //console.log('CREDENTIALS',credentials)

            return { ...prevState, error: null };
        },
        { error: null }
    );

    const toggleOpen = () => setIsOpen(!isOpen);

    const handlePubKeyCredsChange = (index: number) => {
        setPubKeyCredParams((prevParams) =>
            prevParams.map((param, i) => (i === index ? { ...param, selected: !param.selected } : param))
        );
    };

    const getWebAuthnOptions = async (
        userName: string,
        pkCredParams: number[],
        authAttachment: string | AuthenticatorAttachment
    ) => {



        console.log(api?.data)

        return api?.data
    }

    const verifyCredentials = async (credentials: Credential) => {
        await api?.post('api/auth/webauthn/verify/', {
            credentials: JSON.stringify(credentials),
        })
    }

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
                {isPending ? "Creating account..." : "Register"}
            </button>
        </CForm>
            <button onClick={toggleOpen}>
                Advanced Options
            </button>
            {isOpen && (
                <div>

                    {/* Authenticator Attachment (select input) */}
                    <div>
                        <label htmlFor="authAttachment">Authenticator Type:</label>
                        <select
                            id="authAttachment"
                            value={authAttachment}
                            onChange={(e) => setAuthAttachment(e.target.value as AuthenticatorAttachment)}
                        >
                            <option value="platform">Platform (e.g., Built-in, Touch ID)</option>
                            <option value="cross-platform">Cross-Platform (e.g., USB, Security Key)</option>
                        </select>
                    </div>

                    {/* Public Key Credential Parameters (checkboxes) */}
                    <div>
                        <label>Supported Algorithms:</label>
                        <div>
                            {pubKeyCredParams.map((param, index) => (
                                <div key={param.value}>
                                    <label>
                                        <input
                                            type="checkbox"
                                            checked={param.selected}
                                            onChange={() => handlePubKeyCredsChange(index)}
                                        />
                                        {param.label}
                                    </label>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};