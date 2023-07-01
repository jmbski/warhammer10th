export function listify<T>(input: any) {
    const result: T[] = [];
    Object.keys(input as any).forEach((property) => {
        const value: T = (input as any)[property] as T;
        if (value) {
            result.push(value);
        }
    });
    return result;
}
