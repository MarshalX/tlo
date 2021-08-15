import {TlBase, TlType, TlCombinator} from './tl_core';


export class TlConfig extends TlBase {
  public types: TlType[];
  public id_to_type: { [id: number]: TlType };
  public name_to_type: { [name: string]: TlType };
  public functions: TlCombinator[];
  public id_to_function: { [id: number]: TlCombinator };
  public name_to_function: { [name: string]: TlCombinator };

  constructor() {
    super();
    this.types = [];
    this.id_to_type = {};
    this.name_to_type = {};
    this.functions = [];
    this.id_to_function = {};
    this.name_to_function = {};
  }

  add_type = (type: TlType): void => {
    if (type.id && type.name) {
      this.types.push(type);
      this.id_to_type[type.id] = type;
      this.name_to_type[type.name] = type;
    }
  }

  get_type = (type_id_or_name: number | string): TlType => {
    if (typeof type_id_or_name == 'number') {
      return this.id_to_type[type_id_or_name];
    } else {
      return this.name_to_type[type_id_or_name];
    }
  }

  add_function = (func: TlCombinator): void => {
    if (func.id && func.name) {
      this.functions.push(func);
      this.id_to_function[func.id] = func;
      this.name_to_function[func.name] = func;
    }
  }

  get_function = (function_id_or_name: number | string): TlCombinator => {
    if (typeof function_id_or_name == 'number') {
      return this.id_to_function[function_id_or_name];
    } else {
      return this.name_to_function[function_id_or_name];
    }
  }

  get_type_count = (): number => {
    return this.types.length;
  }

  get_type_by_num = (num: number): TlType => {
    return this.types[num];
  }

  get_function_count = (): number => {
    return this.functions.length;
  }

  get_function_by_num = (num: number): TlCombinator => {
    return this.functions[num];
  }
}
