import { EnumType, TupleType } from 'typescript';

export class Army {
  [key: string]: DataSheet;

  constructor(init: Partial<Army>) {
    Object.assign(this, init);
  }
}

export interface Keywords {
  [key: string]: string[];
}

export interface KeywordGroup {
  name: string;
  keywords: string[];
}

export interface DataObject {
  [key: string]: Any;
}
export class DataSheet {
  public unit_name: string = '';
  public keywords: Keywords = {};
  public ranged_weapons: { [key: string]: Weapon } = {};
  public melee_weapons: { [key: string]: Weapon } = {};
  public faction_keywords: string[] = [];
  public core_abilities: string[] = [];
  public faction_abilities: string[] = [];
  public unit_abilities: Ability = {};
  public invulnerable_save: string = '';
  public composition: string = '';
  public points: number = 0;
  public wargear_abilities: Ability = {};
  public wargear_options: Ability[] = [];
  public leader: string[] = [];
  public equipped_with: string = '';
  public profiles: { [key: string]: Profile } = {};
  public issue_flag: boolean = false;
  public army_name: string = '';

  constructor(init: Partial<DataSheet>) {
    Object.assign(this, init);
  }
}

export class Profile {
  public movement: string = '';
  public toughness: number = 0;
  public sv: string = '';
  public wounds: number = 0;
  public leadership: string = '';
  public objective_control: number = 0;
  public title?: string = '';

  constructor(init: Partial<Profile>) {
    Object.assign(this, init);
  }
}

export class Weapon {
  public category: string = '';
  public name: string = '';
  public weapon_range: string = '';
  public attacks: number = 0;
  public ws: string = '';
  public bs: string = '';
  public strength: number = 0;
  public ap: number = 0;
  public damage: string = '';
  public core_rules: string[] = [];

  constructor(init: Partial<Weapon>) {
    Object.assign(this, init);
  }
}

export interface Ability {
  [key: string]: Any;
}

export interface ColumnDefinition {
  header: string;
  field: string;
  width?: string;
  [key: string]: unknown;
}

export interface ListItem {
  name: string;
  value: string;
}

export type Any =
  | number
  | boolean
  | string
  | object
  | Array<Any>
  | TupleType
  | EnumType;
