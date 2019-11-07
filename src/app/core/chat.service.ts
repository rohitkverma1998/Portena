import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { map } from 'rxjs/operators';
import { LOCAL_LOPY_LOCATION, messageHeader } from './constants';
import { Storage } from '@ionic/storage';

const headers = new HttpHeaders({
  'Content-Type': 'application/json'
});

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  GID: number;
  constructor(private http: HttpClient, private storage: Storage) {
    this.storage.get('GID').then(GID => {
      GID = JSON.parse(GID);
      this.GID = GID;
    });
  }

  /**
   * sendMessage
   */
  public sendMessage(message, GID) {
    return this.http
      .post('/api', message, {
        headers: headers
          .append('fromGID', GID)
          .append('toGID', message['toGID'])
      })
      .pipe(
        map((res: any) => {
          console.log(res);
          if (res.length === 0) {
            return res;
          }
          return res;
        })
      );
  }

  /**
   * checkForNewMessages
   */
  public checkForNewMessages(GID) {
    return this.http
      .get('/api', {
        headers: headers
          .append('clientGID', GID)
      })
      .pipe(
        map((res: any) => {
          return res;
        })
      );
  }


  /**
   * updateStorageWithData
   */
  public updateStorageWithData(data) {
    console.log(this.GID);
    data.forEach(messagePacket => {
      this.storage.get(this.GID + '-UserChatGIDList').then(userList => {
        userList.forEach(userGID => {
          userGID = parseInt(userGID, 10);
          if (messagePacket['fromGID'] !== userGID) {
            userList.push(messagePacket['fromGID']);
            this.storage.set(this.GID + '-' + messagePacket['fromGID'], []);
          }
        });
        this.storage.set(this.GID + '-UserChatGIDList', userList);
      });
      this.storage.get(messagePacket['toGID'] + '-' + messagePacket['fromGID'])
      .then(userChatList => {
        userChatList.push(messagePacket);
        this.storage.set(messagePacket['toGID'] + '-' + messagePacket['fromGID'], userChatList);
      });
    });
  }
}
