import { Component } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { DataService } from './services/data-service';
import {
    ArmyList,
    DataObject,
    DataSheet,
    ListItem,
    Profile,
    Weapon,
} from './data/types';
import { OAuthService } from 'angular-oauth2-oidc';
import { JwksValidationHandler } from 'angular-oauth2-oidc-jwks';
export const LoadingSubject: BehaviorSubject<boolean> = new BehaviorSubject(
    false
);
export const AllWeapons: BehaviorSubject<Weapon[]> = new BehaviorSubject<
    Weapon[]
>([]);
export const AllProfiles: BehaviorSubject<Profile[]> = new BehaviorSubject<
    Profile[]
>([]);
export const AllDataSheets: BehaviorSubject<DataSheet[]> = new BehaviorSubject<
    DataSheet[]
>([]);
export const ArmyData: BehaviorSubject<ArmyList> =
    new BehaviorSubject<ArmyList>({});
export const ArmyOptions: BehaviorSubject<ListItem[]> = new BehaviorSubject<
    ListItem[]
>([]);

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss'],
})
export class AppComponent {
    constructor(
        private dataService: DataService
    ) {
    }

    ngOnInit() {
        this.dataService.loadJsonFile('../assets/data-files/armies.json');
    }
}
