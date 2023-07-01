import { Injectable } from '@angular/core';
import {
    ActivatedRouteSnapshot,
    CanActivate,
    Router,
    RouterStateSnapshot,
} from '@angular/router';
import { OAuthService } from 'angular-oauth2-oidc';

@Injectable({
    providedIn: 'root',
})
export class AuthService {
    constructor(private oauthService: OAuthService, private router: Router) {}

    canActivate(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot
    ): boolean {
        if (this.oauthService.hasValidIdToken()) {
            return true;
        }
        else {
            this.oauthService.initCodeFlow();
        }

        this.router.navigate(['/page-not-found']);
        return false;
    }
}
