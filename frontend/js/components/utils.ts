

function inspectFunction(func: Function): Array<{ type: string; name: string; defaultValue?: string }> {
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
                return { type: "rest", name: param.slice(3) };
            } else if (param.includes("=")) {
                // Default parameters
                const [name, defaultValue] = param.split("=");
                return { type: "default", name: name.trim(), defaultValue: defaultValue.trim() };
            } else {
                // Positional arguments
                return { type: "positional", name: param };
            }
        });
}

export { inspectFunction };