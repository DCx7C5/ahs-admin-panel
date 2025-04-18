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
 * @return {string} The resulting string.
 */
export function ab2str(buffer: ArrayBuffer | Uint8Array): string {
  const bufView = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
  let result = '';
  for (let i = 0; i < bufView.length; i++) {
    result += String.fromCharCode(bufView[i]);
  }
  return result;
}


const BASE64_URL_SAFE_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';


/**
 * A `Uint8Array` instance named `lookup` that provides an array with a fixed length of 256 bytes.
 * Commonly used to store or lookup values based on an 8-bit unsigned integer key, where each element is a number between 0 and 255.
 */
const lookup = new Uint8Array(256);
for (let i = 0; i < BASE64_URL_SAFE_CHARS.length; i++) {
  lookup[BASE64_URL_SAFE_CHARS.charCodeAt(i)] = i;
}


/**
 * Encodes the given ArrayBuffer into a Base64 URL-safe string.
 *
 * @param {ArrayBuffer} arraybuffer - The input array buffer to be encoded.
 * @return {string} The URL-safe Base64 encoded string.
 */
// Encode ArrayBuffer to Base64 URL-safe string
export function base64UrlEncode(arraybuffer: ArrayBuffer): string {

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


/**
 * Decodes a Base64 URL-safe string into an ArrayBuffer.
 *
 * @param {string} base64 - The Base64 URL-safe encoded string to decode. It should only contain characters
 * in the set [A-Za-z0-9\-_].
 * @return {ArrayBuffer} The decoded data as an ArrayBuffer.
 * @throws {Error} Throws an error if the input string is not a valid Base64 URL-safe encoded string.
 */
export function base64UrlDecode(base64: string): ArrayBuffer {

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

  return bytes.buffer;
}

export { inspectFunction };