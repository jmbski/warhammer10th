import {
    ChangeDetectorRef,
    Component,
    EventEmitter,
    Input,
    Output,
} from '@angular/core';
import { AllDataSheets } from 'src/app/app.component';
import {
    Ability,
    Any,
    ColumnDefinition,
    DataObject,
    DataSheet,
    KeywordGroup,
    Keywords,
    ListItem,
    Profile,
    Weapon,
} from 'src/app/data/types';

@Component({
    selector: 'data-card',
    templateUrl: './data-card.component.html',
    styleUrls: ['./data-card.component.scss'],
})
export class DataCardComponent {
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

    private _properties: Any[] = [];
    get properties() {
        return this._properties;
    }
    set properties(input: Any[]) {
        this._properties = input;
    }

    public rangedWeaponList: Weapon[] = [];
    public meleeWeaponList: Weapon[] = [];

    public profileList: Profile[] = [];
    public profileColumns: ColumnDefinition[] = [
        {
            header: 'M',
            field: 'movement',
        },
        {
            header: 'T',
            field: 'toughness',
        },
        {
            header: 'SV',
            field: 'sv',
        },
        {
            header: 'W',
            field: 'wounds',
        },
        {
            header: 'LD',
            field: 'leadership',
        },
        {
            header: 'OC',
            field: 'objective_control',
        },
        {
            header: 'Model',
            field: 'title',
        },
    ];

    public rangedWeaponColumns: ColumnDefinition[] = [
        {
            header: 'Weapon Name',
            field: 'name',
        },
        {
            header: 'Rules',
            field: 'core_rules',
        },
        {
            header: 'Range',
            field: 'weapon_range',
        },
        {
            header: 'A',
            field: 'attacks',
        },
        {
            header: 'BS',
            field: 'bs',
        },
        {
            header: 'S',
            field: 'strength',
        },
        {
            header: 'AP',
            field: 'ap',
        },
        {
            header: 'D',
            field: 'damage',
        },
    ];

    public meleeWeaponColumns: ColumnDefinition[] = [
        {
            header: 'Weapon Name',
            field: 'name',
        },
        {
            header: 'Rules',
            field: 'core_rules',
        },
        {
            header: 'Range',
            field: 'weapon_range',
        },
        {
            header: 'A',
            field: 'attacks',
        },
        {
            header: 'WS',
            field: 'ws',
        },
        {
            header: 'S',
            field: 'strength',
        },
        {
            header: 'AP',
            field: 'ap',
        },
        {
            header: 'D',
            field: 'damage',
        },
    ];

    public keywordGroups: KeywordGroup[] = [];

    public unitAbilities: ListItem[] = [];
    public leaderOptions: ListItem[] = [];
    public wargearAbilities: ListItem[] = [];
    public unitCompositionOptions: ListItem[] = [];
    public wargearOptions: ListItem[] = [];

    public hasCoreAbilities: boolean = false;
    public hasFactionAbilities: boolean = false;
    public hasLeaderOptions: boolean = false;
    public hasUnitAbilities: boolean = false;
    public hasWargearAbilities: boolean = false;
    public hasComposition: boolean = false;
    public hasWargearOptions: boolean = false;

    public test: boolean = false;

    private _dataSheet?: DataSheet;
    @Input()
    get dataSheet(): DataSheet | undefined {
        return this._dataSheet;
    }
    set dataSheet(input: DataSheet | undefined) {
        this._dataSheet = input;
        Object.assign(this, input);
        if (this.profiles) {
            this.profileList = [];
            Object.keys(this.profiles).forEach((profile) => {
                this.profileList.push(this.profiles[profile]);
            });
        }
        if (this.ranged_weapons) {
            this.rangedWeaponList = [];
            Object.keys(this.ranged_weapons).forEach((profile) => {
                this.rangedWeaponList.push(this.ranged_weapons[profile]);
            });
            this.addSpaces(this.rangedWeaponList);
        }
        if (this.melee_weapons) {
            this.meleeWeaponList = [];
            Object.keys(this.melee_weapons).forEach((profile) => {
                this.meleeWeaponList.push(this.melee_weapons[profile]);
            });
            this.addSpaces(this.meleeWeaponList);
        }

        if (Object.keys(this.unit_abilities).length > 0) {
            this.unitAbilities = this.toListItem(this.unit_abilities);
            this.hasUnitAbilities = true;
        }

        if (Object.keys(this.wargear_abilities).length > 0) {
            this.wargearAbilities = this.toListItem(this.wargear_abilities);
            this.hasWargearAbilities = true;
        }

        if (Object.keys(this.composition).length > 0) {
            this.unitCompositionOptions = this.toListItem(this.composition);
            this.hasComposition = true;
        }

        if (Object.keys(this.wargear_options).length > 0) {
            this.wargearOptions = this.toListItem(this.wargear_options);
            this.hasWargearOptions = true;
        }

        if (this.core_abilities.length > 0) {
            this.hasCoreAbilities = true;
        }

        if (this.faction_abilities.length > 0) {
            this.hasFactionAbilities = true;
        }

        if (this.leader.length > 0) {
            this.hasLeaderOptions = true;
        }

        if (this.keywords != undefined) {
            this.keywordGroups = [];
            Object.keys(this.keywords).forEach((modelGroup) => {
                const keywordGroup: KeywordGroup = {
                    name: modelGroup,
                    keywords: this.keywords[modelGroup],
                };
                this.keywordGroups.push(keywordGroup);
            });
        }
    }

    @Output() datasheetEvent: EventEmitter<DataSheet> = new EventEmitter();

    constructor(private cd: ChangeDetectorRef) {}

    public useStatBox(colField: string, value?: string) {
        let result: boolean = true;
        if (['title', 'name', 'core_rules'].includes(colField)) {
            result = false;
        } else if (
            colField === 'weapon_range' &&
            value &&
            value.toLowerCase() === 'melee'
        ) {
            result = false;
        }
        return result;
    }

    public addSpaces(input: Weapon[]) {
        if (input && input.length > 0) {
            input.forEach((weapon: Weapon) => {
                if (
                    weapon.core_rules != undefined &&
                    weapon.core_rules.length > 0
                ) {
                    weapon.core_rules.forEach((rule, index) => {
                        if (index > 0) {
                            weapon.core_rules[index] = ' ' + rule;
                        }
                    });
                }
            });
        }
    }

    public toListItem(input: DataObject | string | Array<Any>) {
        const result: ListItem[] = [];
        if (Array.isArray(input)) {
            input.forEach((element) => {
                result.push({
                    name: element.toString(),
                    value: element.toString(),
                });
            });
        } else if (typeof input !== 'string') {
            Object.keys(input).forEach((key) => {
                const value: Any = input[key];
                if (value) {
                    const selectItem: ListItem = {
                        name: key,
                        value: value.toString(),
                    };
                    result.push(selectItem);
                }
            });
        } else {
            const items: string[] = input.split(',');
            items.forEach((item) => {
                result.push({
                    name: item,
                    value: item,
                });
            });
        }
        return result;
    }

    public linkToDatasheet(unitName: string) {
        console.log(unitName);
        const datasheet: DataSheet | undefined = AllDataSheets.getValue().find(
            (sheet) => sheet.unit_name.toLowerCase() === unitName.toLowerCase()
        );
        if (datasheet) {
            this.datasheetEvent.emit(datasheet);
        }
    }
}
