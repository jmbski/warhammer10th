import {
    ChangeDetectorRef,
    Component,
    QueryList,
    ViewChildren,
} from '@angular/core';
import { Subscription } from 'rxjs';
import {
    AllDataSheets,
    ArmyData,
    ArmyOptions,
    LoadingSubject,
} from 'src/app/app.component';
import { Army, ArmyList, DataSheet, ListItem } from 'src/app/data/types';
import { AutoComplete, AutoCompleteCompleteEvent } from 'primeng/autocomplete';
import { listify } from 'src/app/services/utils';
import { TransactionService } from 'src/app/services/transaction.service';
import { OAuthService } from 'angular-oauth2-oidc';

@Component({
    selector: 'home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss'],
})
export class HomeComponent {
    public dataSheet?: DataSheet;

    public dataSheets?: DataSheet[];

    private _selectedSheet?: DataSheet = new DataSheet({});
    get selectedSheet() {
        return this._selectedSheet;
    }
    set selectedSheet(input: DataSheet | undefined) {
        this._selectedSheet = input;

        localStorage.setItem('selectedSheet', JSON.stringify(input ?? {}));
        this.cd.detectChanges();
    }
    private _selectedArmy?: ListItem;
    get selectedArmy() {
        return this._selectedArmy;
    }
    set selectedArmy(input: ListItem | undefined) {
        this._selectedArmy = input;
        console.log(input);
        if (input) {
            this.dataSheets = listify<DataSheet>(this.armyData[input.value]);
            localStorage.setItem('selectedArmy', input.value);
        }
        this.cd.detectChanges();
    }

    public armyData: ArmyList = {};
    public filteredSheets: DataSheet[] = [];
    public filteredArmies: ListItem[] = [];

    public armyOptions: ListItem[] = [];

    private _datasheetTextBox?: string = '';
    get datasheetTextBox() {
        return this._datasheetTextBox;
    }
    set datasheetTextBox(input: string | undefined) {
        this._datasheetTextBox = input;
        if (input) {
            this.filterSheetsByName(input);
        } else {
            this.selectedSheet = undefined;
        }
    }

    public autoCompleteOptions: Partial<AutoComplete> = {
        showEmptyMessage: true,
        appendTo: 'body',
        showClear: true,
        forceSelection: true,
        dropdown: true,
    };

    get sideBarDatasheets() {
        return this.filteredSheets?.length > 0
            ? this.filteredSheets
            : this.dataSheets;
    }

    public sidebarVisible: boolean = false;

    private subscription?: Subscription;

    @ViewChildren(AutoComplete) autocompleteFields?: QueryList<AutoComplete>;

    constructor(
        private cd: ChangeDetectorRef,
        private txService: TransactionService,
        private oauthService: OAuthService,
    ) {
        this.oauthService.initCodeFlow();
        this.txService.checkUser();
    }

    ngAfterViewInit() {
        if (this.autocompleteFields) {
            this.autocompleteFields.forEach((field) => {
                Object.assign(field, this.autoCompleteOptions);
                this.cd.detectChanges();
            });
        }
        /* const unsub: Function = () => {

        } */
        this.subscription = LoadingSubject.subscribe((value) => {
            if (!value) {
                this.dataSheets = AllDataSheets.getValue();
                this.armyData = ArmyData.getValue();
                this.armyOptions = ArmyOptions.getValue();

                this.armyOptions.sort((a, b) => {
                    return a.name > b.name ? 1 : -1;
                });

                const lastArmyData: string | null =
                    localStorage.getItem('selectedArmy');
                if (lastArmyData) {
                    const _lastArmyDataObj: ListItem = {
                        name: lastArmyData,
                        value: lastArmyData,
                    };
                    this.selectedArmy = _lastArmyDataObj;
                    this.cd.detectChanges();
                }

                const lastDataSheetString: string | null =
                    localStorage.getItem('selectedSheet');
                if (lastDataSheetString) {
                    const data: Partial<DataSheet> =
                        JSON.parse(lastDataSheetString);
                    if (data) {
                        this.selectedSheet = new DataSheet(data);
                        this.cd.detectChanges();
                    }
                }
                this.subscription?.unsubscribe();
            }
        });
    }

    public clearSelectedSheet() {
        this.selectedSheet = undefined;
        this.cd.detectChanges();
    }

    public updateSelectedDatasheet(datasheet: DataSheet) {
        if (datasheet) {
            this.selectedSheet = datasheet;
            this.sidebarVisible = false;
            this.cd.detectChanges();
        }
    }

    public filterArmies(event: AutoCompleteCompleteEvent) {
        const filtered: ListItem[] = [];
        const query: string = event.query;
        console.log(event);

        for (let i = 0; i < this.armyOptions.length; i++) {
            const army: ListItem = (this.armyOptions as ListItem[])[i];
            if (army.name.toLowerCase().includes(query.toLowerCase())) {
                filtered.push(army);
            }
        }

        this.filteredArmies = filtered;
    }

    public filterSheetsByName(event: string) {
        if (this.dataSheets) {
            const filtered: DataSheet[] = [];
            const query: string = event;

            for (let i = 0; i < this.dataSheets.length; i++) {
                const datasheet: DataSheet = (this.dataSheets as DataSheet[])[
                    i
                ];
                if (
                    datasheet.unit_name
                        .toLowerCase()
                        .includes(query.toLowerCase())
                ) {
                    filtered.push(datasheet);
                }
            }

            this.filteredSheets = filtered;
        }
    }

    public searchKeywords(dataSheet: DataSheet, keyword: string) {
        let result: boolean = false;
        const breakError = {};
        try {
            Object.keys(dataSheet.keywords).forEach((key) => {
                const keywords: string[] = dataSheet.keywords[key];
                if (keywords.includes(keyword)) {
                    result = true;
                    throw breakError;
                }
            });
        } catch (err) {
            if (err != breakError) {
                console.error(err);
            }
        }
        return result;
    }
}
