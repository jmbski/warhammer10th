import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class TransactionService {
  private backend: string = 'http://31.220.63.217:5000';

  constructor(private http: HttpClient, private cd: ChangeDetectorRef) {}
}
