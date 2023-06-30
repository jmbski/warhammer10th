import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import {
  Army,
  DataObject,
  DataSheet,
  ListItem,
  Profile,
  Weapon
} from "../data/types";
import {
  AllDataSheets,
  AllProfiles,
  AllWeapons,
  ArmyData,
  ArmyOptions,
  LoadingSubject
} from "../app.component";
import { BehaviorSubject } from "rxjs";

@Injectable({
  providedIn: "root"
})
export class DataService {
  constructor(private http: HttpClient) {}

  public async loadJsonFile(filePath: string) {
    LoadingSubject.next(true);
    return new Promise<any>((resolve, reject) => {
      const getConfig = this.http.get(filePath);
      getConfig.subscribe({
        next: (response) => {
          Object.keys(response).forEach((armyName) => {
            const data: any = (response as any)[armyName];
            if (data) {
              const army: Army = new Army(data);
              if (army) {
                const armyData: DataObject = ArmyData.getValue();
                armyData[armyName] = army;
                Object.keys(army).forEach((unitName) => {
                  const allUnits: any = AllDataSheets.getValue();
                  allUnits.push(army[unitName]);
                  AllDataSheets.next(allUnits.slice());
                });
                ArmyData.next(armyData);
                const options: ListItem[] = ArmyOptions.getValue();
                options.push({
                  name: armyName,
                  value: armyName
                });
                ArmyOptions.next(options.slice());
              }
            }
          });
          /* if (Array.isArray(response)) {
                        response.forEach(datasheetJson => {
                            const datasheet: any = JSON.parse(datasheetJson, this.reviver)
                            console.log(datasheet)
                        })
                    } */
          //ConfigSettings.next(settings);
          LoadingSubject.next(false);
          resolve(true);
        },
        error: (err) => {
          console.error(err, "load()", "error loading config");
          reject(false);
        }
      });
    });
  }

  public static addItemToGlobalLists(item: any, sourceName: string) {
    let currentData: any[] = [];
    let subject: BehaviorSubject<any> | undefined = undefined;
    switch (sourceName) {
      case "weapon":
        subject = AllWeapons;
        break;
      case "profile":
        subject = AllProfiles;
        break;
      case "datasheet":
        subject = AllDataSheets;
        break;
    }

    if (subject != undefined) {
      currentData = subject.getValue();
      currentData.push(item);
      subject.next(currentData.slice());
    }
  }

  public reviver(key: string, value: any) {
    let result: any = value;
    if (typeof value === "string") {
      try {
        const parsed: any = JSON.parse(value);
        if (parsed) {
          result = parsed;
          // only Weapon class has the property category
          if (result.category) {
            result = new Weapon(result);
            DataService.addItemToGlobalLists(result, "weapon");
          }
        }
      } catch (err) {
        console.error(err);
      }
    }
    if (typeof value === "object") {
      // only Profile class has movement property

      if (result.movement) {
        result = new Profile(result);
        result.title = key;
        DataService.addItemToGlobalLists(result, "profile");
      }
      // only DataSheet class has unit_name property
      else if (result.unit_name) {
        result = new DataSheet(result);
        DataService.addItemToGlobalLists(result, "datasheet");
      }
    }
    return result;
  }
}
