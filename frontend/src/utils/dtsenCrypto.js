const DTSEN_SECRET_KEY = "DTSEN#Secure2026";


function base64ToBytes(base64) {

    const binary = atob(
        base64.replace(/-/g, "+").replace(/_/g, "/")
    );

    return Uint8Array.from(
        binary,
        c => c.charCodeAt(0)
    );
}


export function decryptDtsen(cipher) {

    if (!cipher) return null;


    const data = base64ToBytes(cipher);

    const key =
        new TextEncoder()
            .encode(DTSEN_SECRET_KEY);


    const result =
        new Uint8Array(data.length);


    for (let i = 0; i < data.length; i++) {

        let x = data[i];


        // reverse mask
        x ^= 0x5A;


        // reverse shifting
        x =
            (x - ((i * 17) % 256) + 256)
            % 256;


        // reverse xor key
        x ^= key[i % key.length];


        result[i] = x;
    }


    return new TextDecoder()
        .decode(result);
}