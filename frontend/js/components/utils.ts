

interface inspectFuncOutput {
    type: "positional" | "rest" | "default";
    name: string;
    defaultValue?: string;
}


function inspectFunction(func: Function){
    const funcStr = func.toString();
    const paramMatch = funcStr.match(/\(([^)]*)\)/); // Extract argument list inside parentheses
    if (!paramMatch) return [];

    return paramMatch[1]
        .split(",")           // Split by commas
        .map(param => param.trim()) // Remove whitespace
        .filter(Boolean)      // Remove empty values
        .map(param => {
            if (param.startsWith("...")) {
                // Treat rest parameters specially
                return { type: "rest", name: param.slice(3) } as inspectFuncOutput;
            } else if (param.includes("=")) {
                // Default parameters
                const [name, defaultValue] = param.split("=");
                return { type: "default", name: name.trim(), defaultValue: defaultValue.trim() } as inspectFuncOutput;
            } else {
                // Positional arguments
                return { type: "positional", name: param } as inspectFuncOutput;
            }
        });
}

export function ab2hex(ab) {
    return Array.prototype.map.call(new Uint8Array(ab), x => ('00' + x.toString(16)).slice(-2)).join('');
}

export function hex2ab(hex) {
    return new Uint8Array(hex.match(/[\da-f]{2}/gi).map(function (h) { return parseInt(h, 16) }));
}

export function str2ab(str) {
  const buf = new ArrayBuffer(str.length);
  const bufView = new Uint8Array(buf);
  for (let i = 0, strLen = str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}


export function base64UrlEncode(str) {
    return btoa(str) // Convert to Base64
        .replace(/\+/g, '-') // Replace + with -
        .replace(/\//g, '_') // Replace / with _
        .replace(/=+$/, ''); // Remove padding
}

export function base64UrlDecode(str) {
    str = str.replace(/-/g, '+').replace(/_/g, '/'); // Convert back to Base64
    while (str.length % 4) {
        str += '='; // Add padding if needed
    }
    return atob(str); // Decode Base64
}

export { inspectFunction };