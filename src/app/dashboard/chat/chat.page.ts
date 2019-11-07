import { Component, OnInit } from '@angular/core';
import { Storage } from '@ionic/storage';
import { Router, NavigationStart, NavigationEnd } from '@angular/router';
import { ChatService } from 'src/app/core/chat.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.page.html',
  styleUrls: ['./chat.page.scss'],
})
export class ChatPage implements OnInit {
  UserChatList: any[];

  constructor(private storage: Storage, private router: Router, private chatService: ChatService) {}

  ngOnInit(): void {

    setTimeout(() => {
      this.FetchUserChatList();
    }, 1000);

    this.storage.get('GID').then(GID => {
      setInterval(() => {
        this.chatService.checkForNewMessages(GID).subscribe((data: any) => {
          this.chatService.updateStorageWithData(data);
        }, error => {
          console.log(error);
        });
      }, 5000);
    });
   }

  /**
   * FetchUserChatList
   */
  public FetchUserChatList() {
    this.storage.get('GID').then(GID => {
      GID = JSON.parse(GID);
      this.storage.get(GID + '-UserChatGIDList').then(userList => {
        this.UserChatList = userList;
      });
    });
  }
}
