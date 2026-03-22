 ///////////////////////////////////////////////////////////////
// SWZL2.JS - Browser JavaScript port of the SWZLv2 library. //
//////////////////////////////////////////////////////////////

const SWZL2 = (() => {
  const MAGIC = [0x53, 0x4D]; // "SM"
  const FLAG_ALPHA = 0b00000001;

  // --- Encoder ---
  function encode(source, { forceAlpha = false } = {}) {
    // draw source onto an offscreen canvas to read pixel data
    const canvas = new OffscreenCanvas(source.width, source.height);
    const ctx = canvas.getContext("2d");
    ctx.drawImage(source, 0, 0);

    const { width, height } = canvas;
    const imageData = ctx.getImageData(0, 0, width, height);
    const rgba = imageData.data;

    let sourceHasAlpha = forceAlpha;
    if (!sourceHasAlpha) {
      for (let i = 3; i < rgba.length; i += 4) {
        if (rgba[i] < 255) { sourceHasAlpha = true; break; }
      }
    }

    const hasAlpha = sourceHasAlpha;
    const bpp = hasAlpha ? 4 : 3;
    const flags = hasAlpha ? FLAG_ALPHA : 0;
    const pixelCount = width * height;

    const out = new Uint8Array(2 + 1 + 4 + pixelCount * bpp);
    let offset = 0;

    out[offset++] = MAGIC[0];
    out[offset++] = MAGIC[1];

    out[offset++] = flags;

    out[offset++] = (width >>> 0) & 0xFF;
    out[offset++] = (width >>> 8) & 0xFF;
    out[offset++] = (width >>> 16) & 0xFF;
    out[offset++] = (width >>> 24) & 0xFF;

    // pixel data
    for (let i = 0; i < pixelCount; i++) {
      const base = i * 4;
      out[offset++] = rgba[base];     // R
      out[offset++] = rgba[base + 1]; // G
      out[offset++] = rgba[base + 2]; // B
      if (hasAlpha) out[offset++] = rgba[base + 3]; // and of course, A
    }

    console.log(`[encode_v2] Mode: ${hasAlpha ? "RGBA" : "RGB"} | Size: ${width}x${height} | Written: ${(out.byteLength / 1024).toFixed(1)} KB`);
    return out;
  }


  // --- Decoder ---
  function decode(buffer) {
    const data = buffer instanceof ArrayBuffer ? new Uint8Array(buffer) : buffer;

    if (data[0] !== MAGIC[0] || data[1] !== MAGIC[1]) {
      throw new Error(`[!] Invalid magic bytes: 0x${data[0].toString(16)} 0x${data[1].toString(16)}`);
    }

    const flags = data[2];
    const hasAlpha = Boolean(flags & FLAG_ALPHA);

    const width =
      data[3] |
      (data[4] << 8) |
      (data[5] << 16) |
      (data[6] << 24);

    const pixelData = data.slice(7);
    const bpp = hasAlpha ? 4 : 3;
    const totalPixels = Math.floor(pixelData.length / bpp);

    if (totalPixels % width !== 0) {
      throw new Error(`[!] Corrupt file: pixel count ${totalPixels} not divisible by width ${width}`);
    }

    const height = totalPixels / width;
    const mode = hasAlpha ? "RGBA" : "RGB";

    console.log(`[decode_v2] Mode: ${mode} | Size: ${width}x${height}`);

    const imgData = new ImageData(width, height);
    const out = imgData.data;

    for (let i = 0; i < totalPixels; i++) {
      const srcBase = i * bpp;
      const dstBase = i * 4;
      out[dstBase]     = pixelData[srcBase];
      out[dstBase + 1] = pixelData[srcBase + 1];
      out[dstBase + 2] = pixelData[srcBase + 2];
      out[dstBase + 3] = hasAlpha ? pixelData[srcBase + 3] : 255;
    }

    return imgData;
  }


  // --- Inspector ---
  function inspect(buffer) {
    const data = buffer instanceof ArrayBuffer ? new Uint8Array(buffer) : buffer;

    if (data[0] !== MAGIC[0] || data[1] !== MAGIC[1]) {
      console.warn("[inspect] Not a valid SWZLv2 file");
      return null;
    }

    const flags = data[2];
    const hasAlpha = Boolean(flags & FLAG_ALPHA);

    const width =
      data[3] |
      (data[4] << 8) |
      (data[5] << 16) |
      (data[6] << 24);

    const pixelData = data.slice(7);
    const bpp = hasAlpha ? 4 : 3;
    const totalPixels = Math.floor(pixelData.length / bpp);
    const height = width ? Math.floor(totalPixels / width) : "?";
    const fileSizeKB = (data.byteLength / 1024).toFixed(1);

    const info = {
      mode: hasAlpha ? "RGBA" : "RGB",
      width,
      height,
      pixels: totalPixels,
      fileSizeKB: parseFloat(fileSizeKB),
    };

    console.log("[inspect]");
    console.log(`  Mode:      ${info.mode}`);
    console.log(`  Width:     ${info.width}`);
    console.log(`  Height:    ${info.height}`);
    console.log(`  Pixels:    ${info.pixels}`);
    console.log(`  Filesize:  ${info.fileSizeKB} KB`);

    return info;
  }

  function toCanvas(imageData) {
    const canvas = document.createElement("canvas");
    canvas.width = imageData.width;
    canvas.height = imageData.height;
    canvas.getContext("2d").putImageData(imageData, 0, 0);
    return canvas;
  }

  function download(bytes, filename = "image.swzl2") {
    const blob = new Blob([bytes], { type: "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  return { encode, decode, inspect, toCanvas, download };
})();


 ///////////////////////////////////////////////
//////// AUTOMATIC SWZL2 IMAGE DECODER ////////
//////////////////////////////////////////////

async function decodeSWZL2Img(img) {
  const src = img.getAttribute("src");
  if (!src?.endsWith(".swzl2")) return;

  try {
    const response = await fetch(src);
    const buffer = await response.arrayBuffer();
    const imageData = SWZL2.decode(buffer);
    const canvas = SWZL2.toCanvas(imageData);
    canvas.className = img.className;
    canvas.style.cssText = img.style.cssText;
    img.replaceWith(canvas);
  } catch (err) {
    console.error(`[SWZL2] Failed to decode ${src}:`, err);
  }
}

const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    for (const node of mutation.addedNodes) {
      if (node.nodeType !== Node.ELEMENT_NODE) continue;

      if (node.tagName === "IMG") decodeSWZL2Img(node);

      for (const img of node.querySelectorAll?.("img[src$='.swzl2']") ?? []) {
        decodeSWZL2Img(img);
      }
    }
  }
});

observer.observe(document.documentElement, {
  childList: true,
  subtree: true,
});

// also catch any already-present images on script load
document.querySelectorAll("img[src$='.swzl2']").forEach(decodeSWZL2Img);
