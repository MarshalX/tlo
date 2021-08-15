import assert from 'assert';

import {ByteSize, get_array_buffer} from './utils';


export class TlSimpleParser {
  public data: ArrayBuffer;
  public data_begin_len: number;
  public data_len: number;

  private offset: number;

  public error: string;
  public error_pos: number;

  constructor(data: Buffer) {
    this.data = get_array_buffer(data);
    this.data_begin_len = data.length;
    this.data_len = data.length;

    this.offset = 0;

    this.error = '';
    this.error_pos = 0;
  }

  set_error = (error_message: string): void => {
    if (this.error != null) {
      assert(error_message != null);
      this.error = error_message;
      this.error_pos = this.data_begin_len - this.offset;
      this.data = new ArrayBuffer(8);
      this.data_len = 0
    } else {
      this.data = new ArrayBuffer(8);
      assert(this.data_len == 0);
    }
  }

  check_len = (len: number): void => {
    if (this.data_len < len) {
      this.set_error('Not enough data to read');
    } else {
      this.data_len -= len;
    }
  }

  get_error = (): string => {
    return this.error;
  }

  get_error_pos = (): number => {
    return this.error_pos;
  }

  fetch_int = (): number => {
    this.check_len(ByteSize.SIZE_OF_INT32);
    const result = new DataView(this.data, this.offset).getUint32(0, true);
    this.offset += ByteSize.SIZE_OF_INT32;
    return result;
  }

  fetch_long = (): bigint => {
    this.check_len(ByteSize.SIZE_OF_INT64);
    const result = new DataView(this.data, this.offset).getBigUint64(0, true);
    this.offset += ByteSize.SIZE_OF_INT64;
    return result;
  }

  unpack_uchar = (offset = 0): number => {
    return new DataView(this.data, this.offset + offset).getInt8(0);
  }

  fetch_string = (): string => {
    this.check_len(4);
    const result_len = this.unpack_uchar();
    if (result_len < 254) {
      this.check_len((result_len >> 2) * 4);

      const result: number[] = [];
      const data_view = new DataView(this.data, this.offset + ByteSize.SIZE_OF_INT8 * 1);
      for (let i = 0; i < result_len; i++) {
        result.push(data_view.getInt8(ByteSize.SIZE_OF_INT8 * i));
      }

      const result_decoded = result.map((e) => String.fromCharCode(e));

      this.offset += ((result_len >> 2) + 1) * 4;

      return result_decoded.join('');
    }

    if (result_len == 254) {
      const result_len = this.unpack_uchar(1) + (this.unpack_uchar(2) << 8) + (this.unpack_uchar(3) << 16);
      this.check_len(((result_len + 3) >> 2) * 4);

      const result: number[] = [];
      const data_view = new DataView(this.data, this.offset + ByteSize.SIZE_OF_INT8 * 4);
      for (let i = 0; i < result_len; i++) {
        result.push(data_view.getInt8(ByteSize.SIZE_OF_INT8 * i));
      }
      const result_decoded = result.map((e) => String.fromCharCode(e));

      this.offset += ((result_len + 7) >> 2) * 4;

      return result_decoded.join('');
    }

    this.set_error('Can\'t fetch string, 255 found');
    return '';
  }

  fetch_end = (): void => {
    if (this.data_len) {
      this.set_error('Too much data to fetch');
    }
  }
}
