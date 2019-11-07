import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { Storage } from "@ionic/storage";
import { ChatService } from "src/app/core/chat.service";
import { FormGroup, FormBuilder, Validators } from "@angular/forms";

@Component({
  selector: "app-user-chat",
  templateUrl: "./user-chat.page.html",
  styleUrls: ["./user-chat.page.scss"]
})
export class UserChatPage implements OnInit {
  userGID: number;
  GID: number;
  userChat: any[];
  chat: FormGroup;

  constructor(
    private router: ActivatedRoute,
    private storage: Storage,
    private chatService: ChatService,
    private formBuilder: FormBuilder
  ) {}

  ngOnInit() {
    this.chat = this.formBuilder.group({
      textInput: ["", Validators.required]
    });
    this.router.params.subscribe(params => {
      this.userGID = parseInt(params.userGID, 10);
    });
    setInterval(() => {
      this.fetchUserChat();
    }, 2000);
  }

  /**
   * fetchUserChat
   */
  public fetchUserChat() {
    this.storage.get("GID").then(GID => {
      GID = JSON.parse(GID);
      this.GID = GID;
      this.storage.get(GID + "-" + this.userGID).then(userChatArray => {
        this.userChat = userChatArray;
      });
    });
  }

  /**
   * sendTextMessage
   */
  public sendTextMessage() {
    const messageObject = {
      message: this.chat.get("textInput").value,
      fromGID: this.GID,
      toGID: this.userGID,
      timestamp: Date.now()
    };
    this.storage.get(this.GID + "-" + this.userGID).then(userChatArray => {
      this.userChat = userChatArray;
      this.userChat.push(messageObject);
      this.storage.set(this.GID + "-" + this.userGID, this.userChat);
    });
    this.chatService.sendMessage(messageObject, this.GID).subscribe(
      data => {
        this.chatService.updateStorageWithData(data);
      },
      error => {
        console.log(error);
      }
    );
  }
}
