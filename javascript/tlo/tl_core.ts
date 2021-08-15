const NODE_TYPE_TYPE = 1;
const NODE_TYPE_NAT_CONST = 2;
const NODE_TYPE_VAR_TYPE = 3;
const NODE_TYPE_VAR_NUM = 4;
const NODE_TYPE_ARRAY = 5;

export const ID_VAR_NUM = 0x70659EFF;
export const ID_VAR_TYPE = 0x2CECF817;
export const ID_INT = 0xA8509BDA;
export const ID_LONG = 0x22076CBA;
export const ID_DOUBLE = 0x2210C154;
export const ID_STRING = 0xB5286E24;
export const ID_VECTOR = 0x1CB5C415;
export const ID_DICTIONARY = 0x1F4C618F;
export const ID_MAYBE_TRUE = 0x3F9C8EF8;
export const ID_MAYBE_FALSE = 0x27930A7B;
export const ID_BOOL_FALSE = 0xBC799737;
export const ID_BOOL_TRUE = 0x997275B5;

export const FLAG_OPT_VAR = 1 << 17;
export const FLAG_EXCL = 1 << 18;
export const FLAG_NOVAR = 1 << 21;
export const FLAG_DEFAULT_CONSTRUCTOR = 1 << 25;
export const FLAG_BARE = 1 << 0;
export const FLAG_COMPLEX = 1 << 1;
export const FLAGS_MASK = (1 << 16) - 1;

export class TlBase {}

export class Arg extends TlBase {
  public name?: string;
  public flags: number;
  public var_num?: number;
  public exist_var_num?: number;
  public exist_var_bit?: number;
  public type?: TlTree;

  constructor(
    name?: string,
    flags?: number,
    var_num?: number,
    exist_var_num?: number,
    exist_var_bit?: number,
    type?: TlTree
  ) {
    super();
    this.name = name
    this.flags = flags || 0
    this.var_num = var_num
    this.exist_var_num = exist_var_num
    this.exist_var_bit = exist_var_bit
    this.type = type
  }
}

export class TlCombinator extends TlBase {
  public id?: number;
  public name?: string;
  public var_count: number;
  public type_id: number;
  public args?: Arg[];
  public result?: TlTree;

  constructor(
    id?: number,
    name?: string,
    var_count?: number,
    type_id?: number,
    args?: Arg[],
    result?: TlTree,
  ) {
    super();
    this.id = id;
    this.name = name;
    this.var_count = var_count || 0;
    this.type_id = type_id || 0;
    this.args = args;
    this.result = result;
  }
}

export class TlType extends TlBase {
  public id?: number;
  public name?: string;
  public arity?: number;
  public flags: number;
  public simple_constructors?: number;
  public constructors_num?: number;
  public constructors?: TlCombinator[];

  constructor(
    id?: number,
    name?: string,
    arity?: number,
    flags?: number,
    simple_constructors?: number,
    constructors_num?: number,
    constructors?: TlCombinator[],
  ) {
    super();
    this.id = id;
    this.name = name;
    this.arity = arity;
    this.flags = flags || 0;
    this.simple_constructors = simple_constructors;
    this.constructors_num = constructors_num;
    this.constructors = constructors;
  }

  add_constructor = (new_constructor: TlCombinator): void => {
    if (this.constructors) {
      this.constructors.push(new_constructor);
    }
  }
}

export class TlTree extends TlBase {
  public flags: number;

  constructor(flags: number) {
    super();
    this.flags = flags;
  }

  get_type = (): number => {
    throw new Error("Not Implemented");
  };
}

export class TlTreeType extends TlTree {
  public type: TlType;
  public children: TlTree[];

  constructor(
    flags: number,
    type: TlType,
    // child_count: number, // unused count of items to create list
  ) {
    super(flags);
    this.type = type;
    this.children = [];
  }

  get_type = (): number => {
    return NODE_TYPE_TYPE;
  }
}

export class TlTreeNatConst extends TlTree {
  public num: number;

  constructor(flags: number, num: number) {
    super(flags);
    this.num = num;
  }

  get_type = (): number => {
    return NODE_TYPE_NAT_CONST;
  }
}

export class TlTreeVarType extends TlTree {
  public var_num: number;

  constructor(flags: number, var_num: number) {
    super(flags);
    this.var_num = var_num;
  }

  get_type = (): number => {
    return NODE_TYPE_VAR_TYPE;
  }
}

export class TlTreeVarNum extends TlTree {
  public var_num: number;
  public diff: number;

  constructor(flags: number, var_num: number, diff: number) {
    super(flags);
    this.var_num = var_num;
    this.diff = diff;
  }

  get_type = (): number => {
    return NODE_TYPE_VAR_NUM;
  }
}

export class TlTreeArray extends TlTree {
  public multiplicity: TlTree;
  public args: Arg[];

  constructor(flags: number, multiplicity: TlTree, a: Arg[]) {
    super(flags);
    this.multiplicity = multiplicity;
    this.args = a;
  }

  get_type = (): number => {
    return NODE_TYPE_ARRAY;
  }
}