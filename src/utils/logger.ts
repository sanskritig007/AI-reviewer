export const logger = {
    info: (message: string, meta?: any) => {
        console.log(JSON.stringify({
            level: "info",
            timestamp: new Date(),
            message,
            ...meta
        }));
    },

    error: (message: string, meta?: any) => {
        console.error(JSON.stringify({
            level: "error",
            timestamp: new Date(),
            message,
            ...meta
        }));
    },

    warn: (message: string, meta?: any) => {
        console.warn(JSON.stringify({
            level: "warn",
            timestamp: new Date(),
            message,
            ...meta
        }));
    }
};
