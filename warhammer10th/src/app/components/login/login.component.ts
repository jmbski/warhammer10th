import { Component, Inject } from '@angular/core';
import { Router } from '@angular/router';
import OktaAuth, { AuthState } from '@okta/okta-auth-js';
import { Observable, filter, map } from 'rxjs';
import { OktaAuthStateService, OKTA_AUTH } from '@okta/okta-angular';

@Component({
  selector: 'login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
    public isAuthenticated$!: Observable<boolean>;

    constructor(private _router: Router, private _oktaStateService: OktaAuthStateService, @Inject(OKTA_AUTH) private _oktaAuth: OktaAuth) { }
  
    public ngOnInit(): void {
      this.isAuthenticated$ = this._oktaStateService.authState$.pipe(
        filter((s: AuthState) => !!s),
        map((s: AuthState) => s.isAuthenticated ?? false)
      );
    }
  
    public async signIn() : Promise<void> {
      await this._oktaAuth.signInWithRedirect();
    }
  
    public async signOut(): Promise<void> {
      await this._oktaAuth.signOut();
    }
}
