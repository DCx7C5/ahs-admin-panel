import {apiClient} from "../../hooks/useAHSApi";
import React, {use, useActionState, useEffect, useState} from "react";
import {CForm, CFormInput, CFormLabel} from "@coreui/react";
import {base64UrlDecode, base64UrlEncode} from "../../components/utils";
import {DataContext} from "../../components/DataProvider";
import WebAuthnOptions from "./WebAuthnOptions";




interface Window {
    __AHS_DATA__: {
        challenge: string,
        uuid: string,
    };
}



export const WebAuthnRegistration: React.FC = () => {
    const api = use(DataContext)?.apiCli;
    const [usernameValue, setUsernameValue] = useState<string>("");
    const [options, setOptions] = useState<PublicKeyCredentialCreationOptions>(null)
    // Decode Base64URL data (challenge and UUID)
    const challenge = base64UrlDecode(window.__AHS_DATA__.challenge);
    const uuid = base64UrlDecode(window.__AHS_DATA__.uuid);

    const [formState, formAction, isPending] = useActionState(
        async (prevState, formData) => {
            const username = formData.get("username") as string;
            console.log("Decoded Challenge:", challenge);
            console.log("Decoded UUID:", uuid);
            console.log(location.hostname)



            try {
                const creds = await navigator.credentials.create(
                    {publicKey: options}
                ) as PublicKeyCredential;

                if (!creds || !api || !creds.hasOwnProperty('response')) {
                    return {...prevState, error: "Registration failed. Check credentials."};
                }

                const resp = await api.post("api/signup/", {
                    id: creds.id,
                    type: creds.type,
                    clientDataJSON: base64UrlEncode(creds.response.clientDataJSON),
                    attestationObject: base64UrlEncode(creds.response.clientDataJSON),
                })

                console.log("RESPONSE:", resp);

            } catch (error) {
                console.error("Registration Error:", error);
                return { ...prevState, error: "Registration failed. Check credentials." };
            }

            return { ...prevState, error: null };
        },
        { error: null }
    );

    const handleUsernameChange = (event) => {
        setUsernameValue(event.target.value);
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
                    value={usernameValue}
                    onChange={handleUsernameChange}
                    required
                />
                <CFormLabel htmlFor="username">Username</CFormLabel>
            </div>
            <button className="w-100 btn btn-lg btn-primary" type="submit" disabled={isPending}>
                {isPending ? "Creating account..." : "Register"}
            </button>
        </CForm>
        <WebAuthnOptions onOptionsChange={(opt) => setOptions(opt)}
                         userName={usernameValue}
                         userId={uuid}
                         challenge={challenge}
        />
        </>
    );
};