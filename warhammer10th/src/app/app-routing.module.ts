import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { AuthService } from './services/auth/auth.service';
import { RedirectComponent } from './components/redirect/redirect.component';
import { LoginComponent } from './components/login/login.component';
import { OktaAuthGuard, OktaCallbackComponent } from '@okta/okta-angular';
import { OAuthModule, OAuthModuleConfig } from 'angular-oauth2-oidc';
import { OktaAuthModule, OKTA_CONFIG } from '@okta/okta-angular';
import { OktaAuth } from '@okta/okta-auth-js';


const routes: Routes = [
    { path: 'home', component: HomeComponent, canActivate: [OktaAuthGuard] },
    { path: 'redirect', component: RedirectComponent },
    { path: 'login', component: LoginComponent },
    { path: 'login/callback', component: OktaCallbackComponent },
    { path: '', redirectTo: 'home', pathMatch: 'full' },
    { path: '**', redirectTo: 'home' }
];


@NgModule({
    imports: [
        RouterModule.forRoot(routes)],
    exports: [RouterModule],
    providers: [
        //OktaAuthGuard
    ]
})
export class AppRoutingModule {}
