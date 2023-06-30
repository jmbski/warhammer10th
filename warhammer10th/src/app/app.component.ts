import { Component } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { DataService } from "./services/data-service";
import { Any, DataSheet, ListItem, Profile, Weapon } from "./data/types";

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
export const ArmyData: BehaviorSubject<Any> = new BehaviorSubject<Any>({});
export const ArmyOptions: BehaviorSubject<ListItem[]> = new BehaviorSubject<
  ListItem[]
>([]);

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"]
})
export class AppComponent {
  constructor(private dataService: DataService) {}

  ngOnInit() {
    this.dataService.loadJsonFile("../assets/data-files/armies.json");
  }
}
