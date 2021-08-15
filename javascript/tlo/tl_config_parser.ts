import assert from 'assert';

import * as tl_core from './tl_core';
import {TlConfig} from './tl_config';
import {TlSimpleParser} from './tl_simple_parser';
import {TlCombinator, TlTree, TlType} from './tl_core';

const TLS_SCHEMA_V2 = 0x3A2F9BE2;
const TLS_SCHEMA_V3 = 0xE4A8604B;
const TLS_SCHEMA_V4 = 0x90AC88D7;
const TLS_TYPE = 0x12EB4386;
const TLS_COMBINATOR = 0x5C0A1ED5;
const TLS_COMBINATOR_LEFT_BUILTIN = 0xCD211F63;
const TLS_COMBINATOR_LEFT = 0x4C12C6D9;
const TLS_COMBINATOR_RIGHT_V2 = 0x2C064372;
const TLS_ARG_V2 = 0x29DFE61B;

const TLS_EXPR_NAT = 0xDCB49BD8;
const TLS_EXPR_TYPE = 0xECC9DA78;

const TLS_NAT_CONST_OLD = 0xDCB49BD8;
const TLS_NAT_CONST = 0x8CE940B1;
const TLS_NAT_VAR = 0x4E8A14F0;
const TLS_TYPE_VAR = 0x0142CEAE;
const TLS_ARRAY = 0xD9FB20DE;
const TLS_TYPE_EXPR = 0xC1863D08;


export class TlConfigParser extends tl_core.TlBase {
  public p: TlSimpleParser;
  public schema_version: number;
  public config: TlConfig;

  constructor(data: Buffer) {
    super();
    this.p = new TlSimpleParser(data);
    this.schema_version = -1;
    this.config = new TlConfig();
  }

  parse_config = (): TlConfig => {
    this.schema_version = this.get_schema_version(this.try_parse_int());
    if (this.schema_version < 2) {
      throw Error(`Unsupported tl-schema version ${this.schema_version}`);
    }

    this.try_parse_int(); // date
    this.try_parse_int(); // version

    const types_n = this.try_parse_int();
    let constructors_total = 0;
    for (let i = 0; i < types_n; i++) {
      const tl_type = this.read_type();
      this.config.add_type(tl_type);
      constructors_total += tl_type.constructors_num || 0;
    }

    const constructors_n = this.try_parse_int();
    assert(constructors_n == constructors_total);
    for (let i = 0; i < constructors_n; i++) {
      const tl_combinator = this.read_combinator();
      this.config.get_type(tl_combinator.type_id).add_constructor(tl_combinator);
    }

    const functions_n = this.try_parse_int();
    for (let i = 0; i < functions_n; i++) {
      this.config.add_function(this.read_combinator());
    }

    this.p.fetch_end();
    this.try_parse(0);

    return this.config;
  }

  get_schema_version = (version_id: number): number => {
    switch (version_id) {
      case TLS_SCHEMA_V4: {
        return 4;
      }
      case TLS_SCHEMA_V3: {
        return 3;
      }
      case TLS_SCHEMA_V2: {
        return 2;
      }
      default: {
        return -1;
      }
    }
  }

  read_type = (): TlType => {
    const t = this.try_parse_int();
    if (t != TLS_TYPE) {
      throw Error(`Wrong tls_type magic ${t}`);
    }

    const tl_type = new TlType();
    tl_type.id = this.try_parse_int();
    tl_type.name = this.try_parse_string();
    tl_type.constructors_num = this.try_parse_int();
    tl_type.constructors = [];

    tl_type.flags = this.try_parse_int();
    tl_type.flags &= ~(1 | 8 | 16 | 1024);
    if (tl_type.flags != 0) {
      throw Error(`Type ${tl_type.name} has non-zero flags: ${tl_type.flags}`);
    }

    tl_type.arity = this.try_parse_int();

    this.try_parse_long(); // unused

    return tl_type;
  }

  read_combinator = (): TlCombinator => {
    const t = this.try_parse_int()
    if (t != TLS_COMBINATOR) {
      throw Error(`Wrong tls_combinator magic ${t}`);
    }

    const tl_combinator = new TlCombinator();
    tl_combinator.id = this.try_parse_int();
    tl_combinator.name = this.try_parse_string();
    tl_combinator.type_id = this.try_parse_int();
    tl_combinator.var_count = 0;

    const left_type = this.try_parse_int();
    if (left_type == TLS_COMBINATOR_LEFT) {
      tl_combinator.args = this.read_args_list(tl_combinator);
    } else {
      if (left_type != TLS_COMBINATOR_LEFT_BUILTIN) {
        throw Error(`Wrong tls_combinator_left magic ${left_type}`);
      }
    }

    const right_ver = this.try_parse_int();
    if (right_ver != TLS_COMBINATOR_RIGHT_V2) {
      throw Error(`'Wrong tls_combinator_right magic ${right_ver}`);
    }

    tl_combinator.result = this.read_type_expr(tl_combinator);

    return tl_combinator;
  }

  read_num_const = (): tl_core.TlTreeNatConst => {
    const num = this.try_parse_int();
    return new tl_core.TlTreeNatConst(tl_core.FLAG_NOVAR, num);
  }

  read_num_var = (tl_combinator: TlCombinator): tl_core.TlTreeVarNum => {
    const diff = this.try_parse_int();
    const var_num = this.try_parse_int();

    if (var_num >= tl_combinator.var_count) {
      tl_combinator.var_count = var_num + 1;
    }

    return new tl_core.TlTreeVarNum(0, var_num, diff);
  }

  read_nat_expr = (tl_combinator: TlCombinator): TlTree => {
    const tree_type = this.try_parse_int();
    switch (tree_type) {
      case TLS_NAT_CONST_OLD:
      case TLS_NAT_CONST: {
        return this.read_num_const();
      }
      case TLS_NAT_VAR: {
        return this.read_num_var(tl_combinator);
      }
      default: {
        throw Error(`tree_type = ${tree_type}`);
      }
    }
  }

  read_expr = (tl_combinator: TlCombinator): TlTree => {
    const tree_type = this.try_parse_int();
    switch (tree_type) {
      case TLS_EXPR_NAT: {
        return this.read_nat_expr(tl_combinator);
      }
      case TLS_EXPR_TYPE: {
        return this.read_type_expr(tl_combinator);
      }
      default: {
        throw Error(`tree_type = ${tree_type}`);
      }
    }
  }

  read_args_list = (tl_combinator: TlCombinator): tl_core.Arg[] => {
    const schema_flag_opt_field = 2 << (this.schema_version >= 3 ? 1 : 0);
    const schema_flag_has_vars = schema_flag_opt_field ^ 6;

    const args_num = this.try_parse_int();
    const args_list: tl_core.Arg[] = [];
    for (let i = 0; i < args_num; i++) {
      const arg = new tl_core.Arg();

      const arg_v = this.try_parse_int();
      if (arg_v != TLS_ARG_V2) {
        throw Error(`Wrong tls_arg magic ${arg_v}`);
      }

      arg.name = this.try_parse_string();
      arg.flags = this.try_parse_int();

      let is_optional = false;
      if (arg.flags & schema_flag_opt_field) {
        arg.flags &= ~schema_flag_opt_field;
        is_optional = true;
      }
      if (arg.flags & schema_flag_has_vars) {
        arg.flags &= ~schema_flag_has_vars;
        arg.var_num = this.try_parse_int();
      } else {
        arg.var_num = -1;
      }

      if (arg.var_num >= tl_combinator.var_count) {
        tl_combinator.var_count = arg.var_num + 1;
      }

      if (is_optional) {
        arg.exist_var_num = this.try_parse_int();
        arg.exist_var_bit = this.try_parse_int();
      } else {
        arg.exist_var_num = -1;
        arg.exist_var_bit = 0;
      }

      arg.type = this.read_type_expr(tl_combinator);
      if (arg.type.flags & tl_core.FLAG_NOVAR) {
        arg.flags |= tl_core.FLAG_NOVAR;
      }

      args_list.push(arg);
    }

    return args_list;
  }

  read_type_expr = (tl_combinator: TlCombinator): TlTree => {
    const tree_type = this.try_parse_int();
    switch (tree_type) {
      case TLS_TYPE_VAR: {
        return this.read_type_var(tl_combinator);
      }
      case TLS_TYPE_EXPR: {
        return this.read_type_tree(tl_combinator);
      }
      case TLS_ARRAY: {
        return this.read_array(tl_combinator);
      }
      default: {
        throw Error(`tree_type = ${tree_type}`);
      }
    }
  }

  read_type_var = (tl_combinator: TlCombinator): tl_core.TlTreeVarType => {
    const var_num = this.try_parse_int();
    const flags = this.try_parse_int();

    if (var_num >= tl_combinator.var_count) {
      tl_combinator.var_count = var_num + 1;
    }

    assert (!(flags & (tl_core.FLAG_NOVAR | tl_core.FLAG_BARE)));
    
    return new tl_core.TlTreeVarType(flags, var_num);
  }

  read_type_tree = (tl_combinator: TlCombinator): tl_core.TlTreeType => {
    const tl_type = this.config.get_type(this.try_parse_int());
    assert(tl_type != undefined);
    const flags = this.try_parse_int() | tl_core.FLAG_NOVAR;
    const arity = this.try_parse_int();
    assert(tl_type.arity == arity);

    const tl_tree_type = new tl_core.TlTreeType(flags, tl_type); // the arity unused

    for (let i = 0; i < arity; i++) {
      const child = this.read_expr(tl_combinator);

      tl_tree_type.children.push(child);

      if (!(child.flags & tl_core.FLAG_NOVAR)) {
        tl_tree_type.flags &= ~tl_core.FLAG_NOVAR;
      }
    }

    return tl_tree_type;
  }

  read_array = (tl_combinator: TlCombinator): tl_core.TlTreeArray => {
    const flags = tl_core.FLAG_NOVAR;
    const multiplicity = this.read_nat_expr(tl_combinator);

    const tl_tree_array = new tl_core.TlTreeArray(flags, multiplicity, this.read_args_list(tl_combinator));

    for (let i = 0; i < tl_tree_array.args.length; i++) {
      if (!(tl_tree_array.args[i].flags & tl_core.FLAG_NOVAR)) {
        tl_tree_array.flags &= ~tl_core.FLAG_NOVAR;
      }
    }

    return tl_tree_array
  }

  try_parse = <T>(res: T): T => {
    if (this.p.get_error()) {
      throw Error(`Wrong TL-scheme specified: ${this.p.get_error()} at ${this.p.get_error_pos()}`);
    }

    return res;
  }

  try_parse_int = (): number => {
    return this.try_parse(this.p.fetch_int());
  }

  try_parse_long = (): bigint => {
    return this.try_parse(this.p.fetch_long());
  }

  try_parse_string = (): string => {
    return this.try_parse(this.p.fetch_string());
  }
}
