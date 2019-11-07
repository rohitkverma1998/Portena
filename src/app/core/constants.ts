import { HttpHeaders } from '@angular/common/http';

const LOCAL_LOPY_LOCATION = 'http://192.168.4.1';

const messageHeader = new HttpHeaders()
                        .set('Request-Type', 'send_message');
export {
    LOCAL_LOPY_LOCATION,
    messageHeader
};
