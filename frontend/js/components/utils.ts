/**
 * Represents the structure of a function parameter's output when inspected.
 *
 * This interface defines the attributes describing the type, name,
 * and optional default value of a parameter.
 *
 * @property type - Indicates the parameter type, either "positional", "rest", or "default".
 * @property name - The name of the parameter as a string.
 * @property defaultValue - The optional default value assigned to the parameter,
 *                          if it exists, represented as a string.
 */
interface inspectFuncOutput {
    type: "positional" | "rest" | "default";
    name: string;
    defaultValue?: string;
}


/**
 * Inspects the parameters of a given function and returns an array of parameter details.
 *
 * @param {Function} func - The function to be inspected.
 * @return {Array<{type: string, name: string, defaultValue?: string}>} An array of objects
 * where each object represents a parameter with properties:
 * - type: The type of the parameter ("positional", "default", or "rest").
 * - name: The name of the parameter.
 * - defaultValue: The default value of the parameter (only for "default" type).
 */
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

type binString = string;
type b64string = string;

/**
 * Converts an ArrayBuffer to its hexadecimal string representation.
 *
 * @param {ArrayBuffer} ab - The ArrayBuffer to be converted to a hexadecimal string.
 * @return {string} A string representing the hexadecimal values of the ArrayBuffer.
 */
export function ab2hex(ab) {
    return Array.prototype.map.call(new Uint8Array(ab), x => ('00' + x.toString(16)).slice(-2)).join('');
}

/**
 * Converts a hexadecimal string into a Uint8Array.
 *
 * @param {string} hex - The hexadecimal string to be converted.
 * @return {Uint8Array} A Uint8Array representation of the hexadecimal string.
 */
export function hex2ab(hex) {
    return new Uint8Array(hex.match(/[\da-f]{2}/gi).map(function (h) { return parseInt(h, 16) }));
}

/**
 * Converts a string to an ArrayBuffer.
 *
 * @param {string} str - The string to be converted.
 * @return {ArrayBuffer} The resulting ArrayBuffer containing the string's character codes.
 */
export function str2ab(str) {
  const buf = new ArrayBuffer(str.length);
  const bufView = new Uint8Array(buf);
  for (let i = 0, strLen = str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}

/**
 * Converts an ArrayBuffer to a string.
 *
 * @param {ArrayBuffer | Uint8Array} buffer - The ArrayBuffer or Uint8Array to be converted.
 * @return {binString} The resulting string.
 */
export function ab2str(buffer: ArrayBuffer | Uint8Array): binString {
  const bufView = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
  let result = '';
  for (let i = 0; i < bufView.length; i++) {
    result += String.fromCharCode(bufView[i]);
  }
  return result;
}

/**
 * Converts a string or binary string to a Base64 (URL-safe) string.
 *
 *
 * */
export function base64Encode(
    value: ArrayBuffer | Uint8Array | string,
    safe: boolean = false
): b64string {
    if (typeof value !== "string") {
        value = ab2str<binString>(value);
    }
    let b64str = btoa(value);

    if (safe) {
        b64str = b64str.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    }
    return b64str
}

/**
 * Converts a Base64 (URL-safe) string to a string.
 *
 *
 * */
export function base64DecodeToString(value: b64string): string {

    // Validate input
    if (!/^[A-Za-z0-9\-_]+$/.test(value)) {
        throw new Error('Invalid Base64 URL-safe string');
    }

    // Add padding if necessary and convert to standard Base64
    let padded = value.replace(/-/g, '+').replace(/_/g, '/');
    const padLength = (4 - (padded.length % 4)) % 4;
    padded += '='.repeat(padLength);
    return atob(padded);

}
/**
 * Converts a Base64 (URL-safe) string to an arraybuffer / bytestring.
 *
 *
 * */
export function base64Decode(value: b64string): ArrayBuffer | Uint8Array {
    return str2ab(base64DecodeToString(value));
}

export { inspectFunction };