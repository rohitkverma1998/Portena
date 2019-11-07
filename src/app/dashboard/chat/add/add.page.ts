import { Component, OnInit } from '@angular/core';
import { Storage } from '@ionic/storage';
import { Router } from '@angular/router';

@Component({
  selector: 'app-add',
  templateUrl: './add.page.html',
  styleUrls: ['./add.page.scss'],
})
export class AddPage implements OnInit {

  newCustomerGID: number;

  constructor(private storage: Storage, private router: Router) { }

  ngOnInit() { }

  /**
   * AddUserWithGID
   */
  public AddUserWithGID() {
    this.storage.get('GID').then(GID => {
      GID = JSON.parse(GID);
      this.storage.get(GID + '-UserChatGIDList').then(userList => {
        userList.push(this.newCustomerGID);
        this.storage.set(GID + '-' + this.newCustomerGID, []);
        this.storage.set(GID + '-UserChatGIDList', userList);
      });
    });
    this.router.navigate(['/dashboard/chat']);
  }

}
