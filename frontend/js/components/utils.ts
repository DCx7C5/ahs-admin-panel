

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

export { inspectFunction };