import React, {useEffect, useState} from "react";


interface WebAuthnOptionsProps {
    onOptionsChange: (options: PublicKeyCredentialCreationOptions | null) => void;
    userName: string;
    userId: ArrayBuffer;
    challenge: ArrayBuffer;
}


export const WebAuthnOptions: React.FC<WebAuthnOptionsProps> = (
    {onOptionsChange, userName, userId, challenge}
) => {
    // State for controlling the visibility of the form
    const [isOpen, setIsOpen] = useState(false);

    // State for authenticator attachment (select input)
    const [authAttachment, setAuthAttachment] = useState<AuthenticatorAttachment>("platform");

    // State for supported public key algorithms (checkboxes)
    const [pubKeyCredParams, setPubKeyCredParams] = useState<{ value: COSEAlgorithmIdentifier; label: string; selected: boolean }[]>([
        { value: -7, label: "ECDSA w/ SHA-256 (default)", selected: true },
        { value: -257, label: "RSASSA-PKCS1-v1_5 w/ SHA-256", selected: false },
    ]);

    // Mock user entity (in real scenarios, this would come from backend or user selection)
    const [user, setUser] = useState<PublicKeyCredentialUserEntity>({
        id: userId,
        name: userName,
        displayName: `${location.hostname}`.includes('localhost')
            ? `${userName}`
            : `${userName}@${location.hostname}`,
    });

    // State for the generated WebAuthn creation options
    const [options, setOptions] = useState<PublicKeyCredentialCreationOptions>({
        challenge: challenge,
        user: user,
        pubKeyCredParams: pubKeyCredParams.map((param) => ({ type: "public-key", alg: param.value })),
        authenticatorSelection: {
            authenticatorAttachment: authAttachment,
        },
        timeout: 60000,
        rp: { name: "AHS", id: location.hostname },
    });

    // Toggle the form visibility
    const toggleOpen = () => setIsOpen(!isOpen);

    // Handle user updates to pubKeyCredParams (for checkboxes)
    const handlePubKeyChange = (index: number) => {
        setPubKeyCredParams((prevParams) =>
            prevParams.map((param, i) => (i === index ? { ...param, selected: !param.selected } : param))
        );
    };

    useEffect(() => {
        onOptionsChange(options)
    }, [options]);

    useEffect(() => {
        setUser(
            {
                id: userId,
                name: userName,
                displayName: userName,
            })
    }, [userName]);

    return (
        <>
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
                                            onChange={() => handlePubKeyChange(index)}
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

export default WebAuthnOptions;