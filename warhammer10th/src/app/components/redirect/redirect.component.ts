import { Component } from '@angular/core';

@Component({
  selector: 'redirect',
  templateUrl: './redirect.component.html',
  styleUrls: ['./redirect.component.scss']
})
export class RedirectComponent {
    ngOnInit() {
        console.log('Redirect');
    }
}
