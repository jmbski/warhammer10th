import { APP_INITIALIZER, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';

import { PanelModule } from 'primeng/panel';
import { ToastModule } from 'primeng/toast';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { InputNumberModule } from 'primeng/inputnumber';
import { DropdownModule } from 'primeng/dropdown';
import { MultiSelectModule } from 'primeng/multiselect';
import { DialogService, DynamicDialogModule } from 'primeng/dynamicdialog';
import { AccordionModule } from 'primeng/accordion';
import { TableModule } from 'primeng/table';
import { TabViewModule } from 'primeng/tabview';
import { RadioButtonModule } from 'primeng/radiobutton';
import { InputTextareaModule } from 'primeng/inputtextarea';
import { CheckboxModule } from 'primeng/checkbox';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CardModule } from 'primeng/card';
import { TooltipModule } from 'primeng/tooltip';
import { ListboxModule } from 'primeng/listbox';
import { RippleModule } from 'primeng/ripple';
import { BlockUIModule } from 'primeng/blockui';
import { PasswordModule } from 'primeng/password';
import { ConfirmPopupModule } from 'primeng/confirmpopup';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { ContextMenuModule } from 'primeng/contextmenu';
import { HomeComponent } from './components/home/home.component';
import { DataCardComponent } from './components/data-card/data-card.component';
import { PrimeNGConfig } from 'primeng/api';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { SidebarModule } from 'primeng/sidebar';
import { LocationStrategy, PathLocationStrategy } from '@angular/common';
import { OAuthModule, OAuthModuleConfig } from 'angular-oauth2-oidc';
import { OktaAuth } from '@okta/okta-auth-js';
import { RedirectComponent } from './components/redirect/redirect.component';
import { LoginComponent } from './components/login/login.component';
import { PageNotFoundComponent } from './components/page-not-found/page-not-found.component';
import { OktaAuthGuard, OktaAuthModule, OktaCallbackComponent } from '@okta/okta-angular';
import { RouterModule, Routes } from '@angular/router';

const initializeAppFactory = (primeConfig: PrimeNGConfig) => () => {
    // ......
    primeConfig.ripple = true;
};

const oktaAuth = new OktaAuth({
    issuer: 'https://dev-36530206.okta.com/oauth2/default',
    clientId: '0oaa7ixtbtwQnVnpA5d7',
    redirectUri: 'http://localhost:4200/login/callback',

  });
  const routes: Routes = [
    { path: 'home', component: HomeComponent, canActivate: [OktaAuthGuard] },
    { path: 'redirect', component: RedirectComponent },
    { path: 'login', component: LoginComponent },
    { path: 'login/callback', component: OktaCallbackComponent },
    { path: '', redirectTo: 'home', pathMatch: 'full' },
    { path: '**', redirectTo: 'home' }
];
@NgModule({
    declarations: [AppComponent, HomeComponent, DataCardComponent, RedirectComponent, LoginComponent, PageNotFoundComponent],
    imports: [
        BrowserModule,
        ReactiveFormsModule,
        //AppRoutingModule,
        CommonModule,
        PanelModule,
        ToastModule,
        DynamicDialogModule,
        ButtonModule,
        InputTextModule,
        InputNumberModule,
        DropdownModule,
        MultiSelectModule,
        AccordionModule,
        TableModule,
        TabViewModule,
        RadioButtonModule,
        InputTextareaModule,
        CheckboxModule,
        FormsModule,
        CardModule,
        TooltipModule,
        ListboxModule,
        RippleModule,
        BlockUIModule,
        PasswordModule,
        ConfirmPopupModule,
        ConfirmDialogModule,
        ContextMenuModule,
        HttpClientModule,
        BrowserAnimationsModule,
        AutoCompleteModule,
        SidebarModule,
        RouterModule.forRoot(routes),
        OAuthModule.forRoot(),
        OktaAuthModule.forRoot({ oktaAuth }),
    ],
    providers: [
        DialogService,
        {
            provide: APP_INITIALIZER,
            useFactory: initializeAppFactory,
            deps: [PrimeNGConfig],
            multi: true,
        },
        { provide: LocationStrategy, useClass: PathLocationStrategy },
    ],
    bootstrap: [AppComponent],
})
export class AppModule {}
