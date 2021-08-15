import * as fs from 'fs';

import {ByteSize} from './utils';
import {TlConfigParser} from './tl_config_parser';
import {TlConfig} from './tl_config';


const read_tl_config = (data: Buffer | null): TlConfig => {
  if (!data) {
    throw Error('Config data is empty');
  }
  if (data.length % ByteSize.SIZE_OF_INT32 != 0) {
    throw Error(`Config size = ${data.length} is not multiple of ${ByteSize.SIZE_OF_INT32}`);
  }

  const parser = new TlConfigParser(data);
  return parser.parse_config();
};

const read_tl_config_from_file = (file_name: string, callback: { (config: TlConfig): void }): void => {
  fs.readFile(file_name, (err, data) => {
    if (err) throw err;

    callback(read_tl_config(data));
  });
};

export {read_tl_config, read_tl_config_from_file}
