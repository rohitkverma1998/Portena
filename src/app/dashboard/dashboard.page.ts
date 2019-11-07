import { Component, OnInit } from '@angular/core';
import { ChatService } from '../core/chat.service';
import { Storage } from '@ionic/storage';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.page.html',
  styleUrls: ['./dashboard.page.scss'],
})
export class DashboardPage implements OnInit {

  constructor(private chatService: ChatService, private storage: Storage) { }

  ngOnInit() {

  }

}
