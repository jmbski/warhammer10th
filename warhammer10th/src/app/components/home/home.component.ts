import { ChangeDetectorRef, Component, QueryList, ViewChildren } from '@angular/core';
import { Subscription } from 'rxjs';
import { AllDataSheets, AllProfiles, ArmyData, ArmyOptions, LoadingSubject } from 'src/app/app.component';
import { Army, DataSheet, Keywords, ListItem } from 'src/app/data/types';
import { AutoComplete, AutoCompleteCompleteEvent } from 'primeng/autocomplete';
import { listify } from 'src/app/services/utils';

@Component({
    selector: 'home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.scss']
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
            this.dataSheets = listify<DataSheet>(this.armyData[input.value])
            localStorage.setItem('selectedArmy', input.value);
        }
        this.cd.detectChanges();
    }

    public armyData: { [key: string]: Army } = {}
    public filteredSheets: DataSheet[] = []
    public filteredArmies: string[] = []

    public armyOptions: ListItem[] = [];

    private _datasheetTextBox?: string = '';
    get datasheetTextBox() {
        return this._datasheetTextBox;
    }
    set datasheetTextBox(input: string | undefined) {
        this._datasheetTextBox = input;
        if (input) {
            this.filterSheetsByName(input);
        }
        else {
            this.selectedSheet = undefined;
        }
    }

    public autoCompleteOptions: Partial<AutoComplete> = {
        showEmptyMessage: true,
        appendTo: 'body',
        showClear: true,
        forceSelection: true,
        dropdown: true,

    }

    get sideBarDatasheets() {
        return this.filteredSheets?.length > 0 ? this.filteredSheets : this.dataSheets;
    }

    public sidebarVisible: boolean = false;

    @ViewChildren(AutoComplete) autocompleteFields?: QueryList<AutoComplete>;

    constructor(
        private cd: ChangeDetectorRef
    ) {

    }

    ngAfterViewInit() {
        if (this.autocompleteFields) {
            this.autocompleteFields.forEach(field => {
                Object.assign(field, this.autoCompleteOptions);
                this.cd.detectChanges();
            })
        }
        const subscription: Subscription = LoadingSubject.subscribe(value => {
            if (!value) {
                this.dataSheets = AllDataSheets.getValue();
                this.armyData = ArmyData.getValue();
                this.armyOptions = ArmyOptions.getValue();

                this.armyOptions.sort((a, b) => {
                    return a.name > b.name ? 1 : -1;
                });

                let lastArmyData: any = localStorage.getItem('selectedArmy');
                if (lastArmyData) {
                    if (typeof lastArmyData === 'string') {
                        lastArmyData = {
                            name: lastArmyData,
                            value: lastArmyData
                        }
                    }
                    this.selectedArmy = lastArmyData;
                    this.cd.detectChanges();
                }

                const lastDataSheetString: string | null = localStorage.getItem('selectedSheet');
                if (lastDataSheetString) {
                    const data: any = JSON.parse(lastDataSheetString);
                    if (data) {
                        this.selectedSheet = new DataSheet(data);
                        this.cd.detectChanges();
                    }
                }
                subscription.unsubscribe();
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
        let filtered: any[] = [];
        let query = event.query;
        console.log(event)

        for (let i = 0; i < (this.armyOptions as any[]).length; i++) {
            let army: ListItem = (this.armyOptions as ListItem[])[i];
            if (army.name.toLowerCase().includes(query.toLowerCase())) {
                filtered.push(army);
            }
        }

        this.filteredArmies = filtered;
    }


    public filterSheetsByName(event: string) {
        let filtered: any[] = [];
        let query = event;

        for (let i = 0; i < (this.dataSheets as any[]).length; i++) {
            let datasheet: DataSheet = (this.dataSheets as DataSheet[])[i];
            if (datasheet.unit_name.toLowerCase().includes(query.toLowerCase())) {
                filtered.push(datasheet);
            }
        }

        this.filteredSheets = filtered;
    }

    public searchKeywords(dataSheet: DataSheet, keyword: string) {
        let result: boolean = false;
        let breakError = {}
        try {
            Object.keys(dataSheet.keywords).forEach(key => {
                const keywords: string[] = dataSheet.keywords[key];
                if (keywords.includes(keyword)) {
                    result = true;
                    throw breakError
                }
            })
        }
        catch (err) {
            if (err != breakError) {
                console.error(err);
            }
        }
        return result
    }
}
