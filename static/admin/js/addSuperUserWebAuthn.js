
const baseUrl = `${window.location.origin}/`;
const optUrl = `${baseUrl}api/auth/webauthn/register/`;
const verifyUrl = `${baseUrl}api/auth/webauthn/register/verify/`;


function str2ab(str) {
  const buf = new ArrayBuffer(str.length);
  const bufView = new Uint8Array(buf);
  for (let i = 0, strLen = str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}


function ab2str(buffer) {
  const bufView = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
  let result = '';
  for (let i = 0; i < bufView.length; i++) {
    result += String.fromCharCode(bufView[i]);
  }
  return result;
}


function base64Encode(value, safe = false) {
    if (typeof value !== "string") {
        value = ab2str(value);
    }
    let b64str = btoa(value);

    if (safe) {
        b64str = b64str.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    }
    return b64str
}


function base64DecodeToString(value) {
    if (!/^[A-Za-z0-9\-_]+$/.test(value)) {
        throw new Error('Invalid Base64 URL-safe string');
    }
    let padded = value.replace(/-/g, '+').replace(/_/g, '/');
    const padLength = (4 - (padded.length % 4)) % 4;
    padded += '='.repeat(padLength);
    return atob(padded);
}


function base64Decode(value) {
    return str2ab(base64DecodeToString(value));
}


const cleanUpEventListeners = async () => {
    await document.removeEventListener("DOMContentLoaded", cleanUpEventListeners);
    await document.removeEventListener("click", cleanUpEventListeners);
};

(async () => {
    document.addEventListener("DOMContentLoaded", async () => {
        const addWebAuthnButton = document.getElementById("addWebauthnButton");
        if (addWebAuthnButton) {
            const userName = JSON.parse(document.getElementById("webauthn-username").textContent);
            const userUid = JSON.parse(document.getElementById("webauthn-useruid").textContent);

            console.log(userName, userUid);
            addWebAuthnButton.addEventListener("click", async (event) => {
                event.preventDefault(); // Prevent page navigation

                const authenticatorType = document.getElementById("authenticatorType").value;


                const optData = JSON.stringify({
                    pubkeycredparams: [-7, -8, -257],
                    authattachment: authenticatorType,
                    username: userName,
                })
                let decResponse;
                try {
                    console.log("OPT DATA", optData);
                    const response = await fetch(optUrl, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json; charset=utf-8'},
                        body: optData,
                    });
                    if (!response.ok) throw new Error('Request failed');
                    decResponse = await response.json();
                } catch (error) {
                    console.error(error);
                    return;
                }
                const options = JSON.parse(decResponse.options);
                options.challenge = base64Decode(options.challenge);
                console.log("CHALLENGE", options.challenge);
                options.user.id = base64Decode(options.user.id);
                console.log("USER ID", options.user.id);
                options.authenticatorSelection.requireResidentKey = false;
                console.log('OPTIONS',options);
                const attestation = await navigator.credentials.create({publicKey: options});

                console.log("ATTESTATION", attestation);
                const authResponse = attestation.response;

                const serializedCredential = JSON.stringify({
                    id: attestation.id,
                    rawId: base64Encode(attestation.rawId, true),
                    response: {
                        clientDataJSON: base64Encode(authResponse.clientDataJSON, true),
                        attestationObject: base64Encode(authResponse.attestationObject, true),
                    },
                    type: attestation.type,
                })

                let verifyResp;
                try {
                    const response = await fetch(verifyUrl, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json; charset=utf-8'},
                        body: JSON.stringify({
                            credential: serializedCredential,
                            random: decResponse.random,
                        })
                    });
                    if (!response.ok) throw new Error('Request failed');
                    verifyResp = await response.json();
                } catch (error) {
                    console.error(error);
                    return;
                }

                console.log(verifyResp);
                    try {
                        alert("WebAuthn credential successfully added to Administrator account");
                    } catch (error) {
                        console.error("WebAuthn error:", error);
                        alert(`Error: ${error.message}`);
                    }
                    await cleanUpEventListeners();
            });
        }
    });
})();
