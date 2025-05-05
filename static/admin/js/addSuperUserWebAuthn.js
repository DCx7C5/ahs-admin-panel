
const baseUrl = `${window.location.origin}/`;
const optUrl = `${baseUrl}api/auth/webauthn/register/`;
const verifyUrl = `${baseUrl}api/auth/webauthn/register/verify/`;


const ab2str = async (buffer) => {
  const bufView = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
  let result = '';
  for (let i = 0; i < bufView.length; i++) {
    result += String.fromCharCode(bufView[i]);
  }
  return result;
}

const base64UrlEncode = (arraybuffer) =>  {

  // Convert ArrayBuffer to binary string
  const bytes = new Uint8Array(arraybuffer);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }

  // Use btoa for Base64 encoding and make it URL-safe
  let base64 = btoa(binary);
  base64 = base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

  return base64;
}

const base64UrlDecode = (base64, str_out = false) => {

    // Validate input
    if (!/^[A-Za-z0-9\-_]+$/.test(base64)) {
      throw new Error('Invalid Base64 URL-safe string');
    }

    // Add padding if necessary and convert to standard Base64
    let padded = base64.replace(/-/g, '+').replace(/_/g, '/');
    const padLength = (4 - (padded.length % 4)) % 4;
    padded += '='.repeat(padLength);

    // Decode using atob
    const binary = atob(padded);

    // Convert binary string to ArrayBuffer
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    if (str_out) return ab2str(bytes.buffer);
    return bytes.buffer;
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

            addWebAuthnButton.addEventListener("click", async (event) => {
                const authenticatorType = document.getElementById("authenticatorType").value;
                console.log(authenticatorType);
                event.preventDefault(); // Prevent page navigation

                const dataOpt = new URLSearchParams();
                dataOpt.append('username', userName);
                dataOpt.append('useruid', userUid);
                dataOpt.append('authattachment', authenticatorType);
                              const optResponse = fetch(optUrl, {
                method: 'POST',
                headers: {'Content-Type': 'application/json; charset=utf-8'},
                body: JSON.stringify(dataOpt),
              }).then(
                response => response.json()
              )



            const attestation = await navigator.credentials.create({publicKey: options});
            console.log("ATTESTATION", attestation);
            const authResponse = attestation.response;

            const serializedCredential = JSON.stringify({
                id: attestation.id,
                rawId: base64UrlEncode(attestation.rawId),
                response: {
                    clientDataJSON: base64UrlEncode(authResponse.clientDataJSON),
                    attestationObject: base64UrlEncode(authResponse.attestationObject),
                },
                type: attestation.type,
            })

            const data = new URLSearchParams();
            data.append('credential', serializedCredential);
            data.append('random', random);

            const verifyResponse = fetch(verifyUrl, {
                method: 'POST',
                headers: {'Content-Type': 'application/json; charset=utf-8'},
                body: JSON.stringify(data),
            }).then(
                response => response.json()
            )
            console.log(attestation);

                console.log(verifyResponse);
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
