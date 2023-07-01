import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class TransactionService {
    private backend: string = 'http://127.0.0.1:5000';

    constructor(private http: HttpClient) {}

    private configureHeaders(config?: any) {
        let requestOptions = {};

        if (config ?? false) {
            //TODO: convert input into HttpHeaders object
        } else {
            const headerDict = {
                'Content-Type': 'application/json',
                Accept: '*',
                'Access-Control-Allow-Headers': 'Content-Type',
            };

            requestOptions = {
                headers: new Headers(headerDict),
            };
        }

        return requestOptions;
    }

    public test() {
        const request = this.http.get(this.backend + '/services/test', {
            responseType: 'text',
        });
        request.subscribe({
            next: (value) => {
                console.log('test response:', value);
            },
        });
    }

    public async checkUser(): Promise<boolean> {
        //LoadingSubject.next(true);
        console.log('checking user');
        return new Promise<boolean>((resolve, reject) => {
            const options = this.configureHeaders();
            const uri = this.backend + '/services/checkUser';
            const user = {
                username: 'warskald',
                passkey: '0129uoiwheg',
            };
            const request = this.http.post(uri, user, options);
            request.subscribe({
                next: (response: any) => {
                    console.log('response: ', response);
                    resolve(response?.data?.userStatus ?? false);
                },
                error: (err) => {
                    console.error(err);
                    reject(false);
                },
            });
        });
    }
}
