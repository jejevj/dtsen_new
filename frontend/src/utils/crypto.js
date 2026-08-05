const SECRET_KEY = "21SDSKL#Must4h1k@2026";

function base64ToBytes(base64) {

    const binary = atob(
        base64.replace(/-/g, "+").replace(/_/g, "/")
    );

    return Uint8Array.from(binary, c => c.charCodeAt(0));
}

function bytesToBase64(bytes) {

    return btoa(String.fromCharCode(...bytes))
        .replace(/\+/g, "-")
        .replace(/\//g, "_");
}

export function encrypt(text) {

    const encoder = new TextEncoder();

    const data = encoder.encode(text);

    const key = encoder.encode(SECRET_KEY);

    const result = new Uint8Array(data.length);

    for (let i = 0; i < data.length; i++) {

        let x = data[i];

        x ^= key[i % key.length];

        x = (x + ((i * 17) % 256)) % 256;

        x ^= 0x5A;

        result[i] = x;
    }

    return bytesToBase64(result);
}

export function decrypt(cipher) {

    const data = base64ToBytes(cipher);

    const key = new TextEncoder().encode(SECRET_KEY);

    const result = new Uint8Array(data.length);

    for (let i = 0; i < data.length; i++) {

        let x = data[i];

        x ^= 0x5A;

        x = (x - ((i * 17) % 256) + 256) % 256;

        x ^= key[i % key.length];

        result[i] = x;
    }

    return new TextDecoder().decode(result);
}