export const enum ByteSize {
  SIZE_OF_BOOLEAN = 1,
  SIZE_OF_INT8 = 1,
  SIZE_OF_INT16 = 2,
  SIZE_OF_INT32 = 4,
  SIZE_OF_INT64 = 8,
  SIZE_OF_UINT8 = 1,
  SIZE_OF_UINT16 = 2,
  SIZE_OF_UINT32 = 4,
  SIZE_OF_FLOAT32 = 4,
  SIZE_OF_FLOAT64 = 8
}

export const get_array_buffer = (data: Buffer): ArrayBuffer => {
  const ab = new ArrayBuffer(data.length);
  const view = new Uint8Array(ab);
  for (let i = 0; i < data.length; ++i) {
    view[i] = data[i];
  }
  return ab;
}
