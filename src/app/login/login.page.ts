import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Storage } from '@ionic/storage';

@Component({
  selector: 'app-login',
  templateUrl: './login.page.html',
  styleUrls: ['./login.page.scss']
})
export class LoginPage implements OnInit {
  gid: number;

  constructor(
    private router: Router,
    private storage: Storage
    ) {
      this.storage.get('GID').then((val) => {
        if (val) {
          this.router.navigate(['dashboard']);
        }
      });
  }
  logForm() {
    this.storage.set('GID', this.gid);
    this.storage.set(this.gid + '-UserChatGIDList', []);
    this.router.navigate(['/dashboard']);
  }
  ngOnInit() {}
}
