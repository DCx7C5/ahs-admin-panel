import {apiClient} from "../../hooks/useApiAxios";
import React, {use, useActionState, useEffect, useState} from "react";
import {CForm, CFormInput, CFormLabel} from "@coreui/react";
import {DataContext} from "../../components/DataProvider";
import {base64Decode, base64Encode} from "../../components/utils";
import {useNavigate} from "react-router-dom";


interface WebAuthnOptionsResponse {
    message: string;
    options: string;
    random: string;
}

interface WebAuthnRegistrationVerifyResponse {
    message: string;
    status: number;
}


export const WebAuthnRegistration: React.FC = () => {
    const api = use(DataContext)?.apiCli as apiClient;
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = useState(false);
    const [authAttachment, setAuthAttachment] = useState<AuthenticatorAttachment>("platform");
    const [registrationSuccess, setRegistrationSuccess] = useState(false);
    const [pubKeyCredParams, setPubKeyCredParams] = useState<{ value: COSEAlgorithmIdentifier; label: string; selected: boolean }[]>([
        { value: -7, label: "ECDSA w/ SHA-256", selected: true },
        { value: -8, label: "Ed25519", selected: true},
        { value: -257, label: "RSASSA-PKCS1-v1_5 w/ SHA-256", selected: true },
    ]);

    const [formState, formAction, isPending] = useActionState(
        async (prevState, formData) => {
            // Get username from form
            const userName = formData.get("username") as string;

            // Get publickey algorithm types from form
            const pkCredParams = pubKeyCredParams.filter((param) => param.selected).map((param) => param.value);

            const optData = JSON.stringify({
                pubkeycredparams: pkCredParams,
                authattachment: authAttachment,
                username: userName,
            })

            console.log("OPTDATA: ", optData)

            // Get registration options from server
            const optResponse: WebAuthnOptionsResponse = await api?.post(
                'api/auth/webauthn/register/',
                optData,
            )
            if (!optResponse.random || !optResponse.options) {
                return { ...prevState, error: "Failed to get options." };
            }

            // Decode response
            const options = JSON.parse(optResponse.options);
            options.challenge = base64Decode(options.challenge);
            options.user.id = base64Decode(options.user.id);
            options.authenticatorSelection.requireResidentKey = false;
            console.log('OPTIONS',options);

            //  Create webauthn credential creation attestation
            const attestation = await navigator.credentials.create(
                { publicKey: options }
            ) as PublicKeyCredential;

            console.log(attestation.getClientExtensionResults())

            // Encode credential for server verification
            const authResponse = attestation.response as AuthenticatorAttestationResponse;
            const serializedCredential = JSON.stringify({
                id: attestation.id,
                rawId: base64Encode(attestation.rawId, true),
                response: {
                    clientDataJSON: base64Encode(authResponse.clientDataJSON, true),
                    attestationObject: base64Encode(authResponse.getAuthenticatorData(), true),

                },
                type: attestation.type,
            })

            const verifyResponse: WebAuthnRegistrationVerifyResponse = await api?.post(
                'api/auth/webauthn/register/verify/',
                JSON.stringify({
                    credential: serializedCredential,
                    random: optResponse.random,
                }))

            if (verifyResponse && verifyResponse.status === 200) {
                setRegistrationSuccess(true);
                console.log("REGISTRATION SUCCESS")
                return { ...prevState, error: null };

            } else {
                return { ...prevState, error: "Failed to register." };
            }
        },
        { error: null }
    );

    const toggleOpen = () => setIsOpen(!isOpen);

    const handlePubKeyCredsChange = (index: number) => {
        setPubKeyCredParams((prevParams) =>
            prevParams.map((param, i) => (i === index ? { ...param, selected: !param.selected } : param))
        );
    };

    useEffect(() => {
        if (registrationSuccess && !isPending) {
            navigate("/accounts/login/", { replace: true })
        }

    }, [registrationSuccess, isPending, navigate]);

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
                <div className="advanced-webauthn-options">

                    {/* Authenticator Attachment (select input) */}
                    <div className="select-input">
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
                    <div className="checkbox-input">
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